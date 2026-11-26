# Copyright (C) 2018-2026 by xcentaurix
# License: GNU General Public License v3.0


import re
from collections import namedtuple
import urllib.parse

# How a track of an HLS stream is downloaded (see MovieFile.getHLSTracks and DownloadJob):
# TRACK_FILE: (TRACK_FILE, url) - its segments are the byte ranges of one file, one after the other from its start (a CMAF
#   playlist): the file itself is downloaded, in one request
# TRACK_SEGMENTS: (TRACK_SEGMENTS, [HLSSegment, ...]) - its segments are files of their own, downloaded one after the other;
#   the first is the initialization section (EXT-X-MAP) if the playlist has one
TRACK_FILE = "file"
TRACK_SEGMENTS = "segments"

# Define data structures using namedtuple for Python 2.7 compatibility
HLSSegment = namedtuple('HLSSegment', [
    'url', 'duration', 'sequence', 'discontinuity', 'byterange', 'key'
])

# audio: the GROUP-ID of the audio renditions of the variant (EXT-X-MEDIA TYPE=AUDIO), if its audio is not in its own segments
HLSVariant = namedtuple('HLSVariant', [
    'url', 'bandwidth', 'resolution', 'codecs', 'frame_rate', 'audio'
])

# An alternative rendition of a master playlist (EXT-X-MEDIA): an audio track that is not in the segments of the variants.
# url is None if the rendition is in the variants themselves.
HLSRendition = namedtuple('HLSRendition', [
    'type', 'group_id', 'name', 'language', 'default', 'url'
])

# Helper functions to create objects with default values


def create_hls_segment(url, duration, sequence, discontinuity=False, byterange=None, key=None):
    """Create HLSSegment with default values. byterange: (length, offset) of the segment in the file of url, or None."""
    return HLSSegment(url, duration, sequence, discontinuity, byterange, key)


def create_hls_variant(url, bandwidth, resolution=None, codecs=None, frame_rate=None, audio=None):
    """Create HLSVariant with default values"""
    return HLSVariant(url, bandwidth, resolution, codecs, frame_rate, audio)


class HLSParser:
    """Parser for HLS M3U8 files that extracts all variants and segments"""

    def __init__(self, base_url=""):
        self.base_url = base_url

    def parse_m3u8(self, content):
        """
        Parse M3U8 content and return variants and segments

        Args:
            content (str): Raw M3U8 file content

        Returns:
            Dictionary with 'variants' and 'segments' keys
        """
        lines = [line.strip() for line in content.splitlines() if line.strip()]

        if not lines or not lines[0].startswith('#EXTM3U'):
            raise ValueError("Invalid M3U8 file format")

        # Check if this is a master playlist or media playlist
        is_master = any(line.startswith('#EXT-X-STREAM-INF') for line in lines)

        if is_master:
            variants = self._parse_master_playlist(lines)
            return {'variants': variants, 'segments': [], 'renditions': self._parse_renditions(lines), 'init': None}
        segments, init = self._parse_media_playlist(lines)
        return {'variants': [], 'segments': segments, 'renditions': [], 'init': init}

    def _parse_renditions(self, lines):
        """The alternative renditions of a master playlist (EXT-X-MEDIA)"""
        renditions = []
        for line in lines:
            if line.startswith('#EXT-X-MEDIA:'):
                attrs = self._parse_attributes(line)
                uri = attrs.get('URI')
                renditions.append(HLSRendition(
                    type=attrs.get('TYPE'),
                    group_id=attrs.get('GROUP-ID'),
                    name=attrs.get('NAME'),
                    language=attrs.get('LANGUAGE'),
                    default=attrs.get('DEFAULT') == 'YES',
                    url=self._resolve_url(uri) if uri else None
                ))
        return renditions

    @staticmethod
    def _parse_byterange(value, previous_end):
        """ "length[@offset]" -> (length, offset); without an offset the range follows the previous one of the same file."""
        length, _, offset = value.strip().strip('"').partition('@')
        return int(length), int(offset) if offset else previous_end

    def _parse_master_playlist(self, lines):
        """Parse master playlist and extract variant streams"""
        variants = []
        i = 0

        while i < len(lines):
            line = lines[i]

            if line.startswith('#EXT-X-STREAM-INF'):
                # Parse stream info attributes
                attrs = self._parse_attributes(line)

                # Get the URL from next line
                i += 1
                if i < len(lines) and not lines[i].startswith('#'):
                    url = self._resolve_url(lines[i])

                    # Convert bandwidth to int, default to 0 if not present
                    bandwidth = int(attrs.get('BANDWIDTH', 0))

                    # Get frame rate as float if present
                    frame_rate = None
                    if 'FRAME-RATE' in attrs:
                        try:
                            frame_rate = float(attrs['FRAME-RATE'])
                        except (ValueError, TypeError):
                            frame_rate = None

                    # Remove quotes from codecs if present
                    codecs = attrs.get('CODECS', '').strip('"')

                    variant = create_hls_variant(
                        url=url,
                        bandwidth=bandwidth,
                        resolution=attrs.get('RESOLUTION'),
                        codecs=codecs if codecs else None,
                        frame_rate=frame_rate,
                        audio=attrs.get('AUDIO')
                    )
                    variants.append(variant)

            i += 1

        return variants

    def _parse_media_playlist(self, lines):
        """Parse media playlist and extract segments: (segments, init), init being the media initialization section
        (EXT-X-MAP) as a segment of duration 0, or None.

        The tags of a segment (EXTINF, EXT-X-BYTERANGE, EXT-X-DISCONTINUITY) come before its URI, in any order: they are
        collected until the URI line, which makes the segment (RFC 8216, 4.3.2) - a CMAF playlist has EXT-X-BYTERANGE
        between EXTINF and the URI."""
        segments = []
        init = None
        sequence = 0
        current_key = None
        duration = None
        byterange = None
        discontinuity = False
        range_end = {}   # url -> where its last byte range ended, for a range without an offset

        for line in lines:
            if line.startswith('#EXT-X-MEDIA-SEQUENCE'):
                sequence = int(line.split(':')[1])

            elif line.startswith('#EXT-X-KEY'):
                current_key = self._parse_attributes(line)

            elif line.startswith('#EXT-X-MAP'):
                attrs = self._parse_attributes(line)
                if attrs.get('URI'):
                    url = self._resolve_url(attrs['URI'])
                    map_range = self._parse_byterange(attrs['BYTERANGE'], 0) if attrs.get('BYTERANGE') else None
                    init = create_hls_segment(url=url, duration=0.0, sequence=-1, byterange=map_range)

            elif line.startswith('#EXTINF'):
                duration_match = re.search(r':([\d.]+)', line)
                duration = float(duration_match.group(1)) if duration_match else 0.0

            elif line.startswith('#EXT-X-BYTERANGE'):
                byterange = line.split(':', 1)[1]

            elif line.startswith('#EXT-X-DISCONTINUITY'):
                discontinuity = True

            elif not line.startswith('#') and duration is not None:
                # the URI of the segment the tags above describe
                url = self._resolve_url(line)
                segment_range = None
                if byterange is not None:
                    segment_range = self._parse_byterange(byterange, range_end.get(url, 0))
                    range_end[url] = segment_range[1] + segment_range[0]
                segments.append(create_hls_segment(
                    url=url,
                    duration=duration,
                    sequence=sequence,
                    discontinuity=discontinuity,
                    byterange=segment_range,
                    key=dict(current_key) if current_key else None
                ))
                sequence += 1
                duration = None
                byterange = None
                discontinuity = False

        return segments, init

    def _parse_attributes(self, line):
        """Parse attribute string from M3U8 line"""
        attrs = {}
        if ':' not in line:
            return attrs

        attr_part = line.split(':', 1)[1]

        # Regular expression to match key=value pairs
        pattern = r'([A-Z-]+)=([^,]*(?:"[^"]*"[^,]*)*)'
        matches = re.findall(pattern, attr_part)

        for key, value in matches:
            # Remove quotes if present
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
            attrs[key] = value

        return attrs

    def _resolve_url(self, url):
        """Resolve relative URLs against base URL"""
        if url.startswith(('http://', 'https://')):
            return url

        if self.base_url:
            return urllib.parse.urljoin(self.base_url, url)

        return url


def decode_hls_m3u8(m3u8_content, base_url=""):
    """
    Decode HLS M3U8 file and return all variants and segments

    Args:
        m3u8_content (str): Raw M3U8 file content as string
        base_url (str): Base URL for resolving relative URLs

    Returns:
        Dictionary containing:
        - 'variants': List of HLSVariant objects (for master playlists)
        - 'renditions': List of HLSRendition objects (for master playlists: separate audio tracks, ...)
        - 'segments': List of HLSSegment objects (for media playlists)
        - 'init': the media initialization section (EXT-X-MAP) as an HLSSegment, or None (for media playlists)

    Example:
        with open('playlist.m3u8', 'r') as f:
            content = f.read()

        result = decode_hls_m3u8(content, 'https://example.com/hls/')

        # Access variants
        for variant in result['variants']:
            print("Bandwidth: {}, URL: {}".format(variant.bandwidth, variant.url))

        # Access segments
        for segment in result['segments']:
            print("Duration: {}s, URL: {}".format(segment.duration, segment.url))
    """
    parser = HLSParser(base_url)
    return parser.parse_m3u8(m3u8_content)

# Example usage and test function


def example_usage():
    """Example of how to use the HLS decoder"""

    # Example master playlist
    master_playlist = """#EXTM3U
#EXT-X-VERSION:3
#EXT-X-STREAM-INF:BANDWIDTH=1280000,RESOLUTION=720x480,CODECS="avc1.42e01e,mp4a.40.2"
low/playlist.m3u8
#EXT-X-STREAM-INF:BANDWIDTH=2560000,RESOLUTION=1280x720,CODECS="avc1.42e01e,mp4a.40.2"
high/playlist.m3u8
"""

    # Example media playlist
    media_playlist = """#EXTM3U
#EXT-X-VERSION:3
#EXT-X-TARGETDURATION:10
#EXT-X-MEDIA-SEQUENCE:0
#EXTINF:9.009,
segment0.ts
#EXTINF:9.009,
segment1.ts
#EXTINF:3.003,
segment2.ts
#EXT-X-ENDLIST
"""

    # Parse master playlist
    print("Master playlist variants:")
    result = decode_hls_m3u8(master_playlist, "https://example.com/hls/")
    for variant in result['variants']:
        print(f"  Bandwidth: {variant.bandwidth}, Resolution: {variant.resolution}")

    # Parse media playlist
    print("\nMedia playlist segments:")
    result = decode_hls_m3u8(media_playlist, "https://example.com/hls/")
    for segment in result['segments']:
        print(f"  Duration: {segment.duration}s, Sequence: {segment.sequence}")


if __name__ == "__main__":
    example_usage()
