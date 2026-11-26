# Copyright (C) 2018-2026 by xcentaurix
# License: GNU General Public License v3.0


import os
from Components.Task import Job
from .Debug import logger
from .DownloadTask import DownloadTaskFile, DownloadTaskHLS, MuxTask
from .HLSParser import TRACK_FILE


class DownloadJob(Job):

    def __init__(self, url, tracks, target_path, event_name, short_description, description, rec_time, service_ref, length, web_site_url):
        """tracks: the tracks of an HLS stream (see MovieFile.getHLSTracks), [] for a plain file (url). One track is
        downloaded into target_path; video and audio tracks each into a part of their own (target_path without its
        extension, plus .video.part or .audio.part), which a MuxTask then makes the recording of."""
        logger.info("target_path: %s, event_name: %s, short_description: %s",
                    target_path, event_name, short_description)
        logger.debug("tracks: %s", tracks)
        Job.__init__(self, "Download: " + event_name)
        self.target_path = target_path
        self.keep = True
        meta = (event_name, short_description, description, rec_time, service_ref, length, web_site_url)
        if not tracks:
            DownloadTaskFile(self, url, target_path, *meta)
        elif len(tracks) == 1:
            self.addTrackTask(url, tracks[0], target_path, meta, True)
        else:
            base = os.path.splitext(target_path)[0]
            parts = [base + (".video" if i == 0 else ".audio%d" % i if i > 1 else ".audio") + ".part" for i in range(len(tracks))]
            for track, part in zip(tracks, parts):
                self.addTrackTask(url, track, part, meta, False)
            MuxTask(self, parts, target_path, *meta)

    def addTrackTask(self, url, track, path, meta, final):
        kind, data = track
        if kind == TRACK_FILE:
            DownloadTaskFile(self, data, path, *meta, final=final)
        else:
            DownloadTaskHLS(self, url, data, path, *meta, final=final)

    def gettotalbytes(self):
        t = self.tasks[self.current_task]
        return int(t.totalbytes)

    totalbytes = property(gettotalbytes)

    def getrecvbytes(self):
        t = self.tasks[self.current_task]
        return int(t.recvbytes)

    recvbytes = property(getrecvbytes)

    def gethls_segments(self):
        t = self.tasks[self.current_task]
        return t.hls_segments

    hls_segments = property(gethls_segments)
