# Troubleshooting

## Logging

Lines of this plugin in the Enigma2 debug log (usually `/home/root/logs/Enigma2_debug_*.log`) start with `MTC:`. Set
*Log level* to `DEBUG` in the settings (expert mode) to also see the search parameters, the list rows and the download
steps. Set it back to `INFO` afterwards; `DEBUG` is verbose. JobCockpit lines start with `JOC:`.

## The list stays empty / "No movies available"

| Check | What to do |
|---|---|
| Is the box online? | The search goes to mediathekviewweb.de. Try another Internet service from the box |
| Do the filters hide everything? | Turn off *Skip short duration* (set 0) and the three skip switches, then search again |
| Is the search too narrow? | Search for a single word of the title; the text is matched against topic and title |
| Did you choose a channel after a search? | The channel selection replaces the text search. Choose *All channels* |
| The service is down | MediathekViewWeb is run by a third party and can be unavailable. Try later |

## OK shows "No valid stream detected"

- The entry has no usable video address. Press **5** to see the low, medium and HD addresses; at least one must begin with `http`.
- The **download directory** does not exist. Playback first creates a temporary file there and cannot continue without
  it. Check *Download directory* in the settings.

## "Download failed: Please check movie directory in plugin settings"

The download directory in the settings does not exist or is not mounted (a NAS that is switched off, for example). Mount it,
or choose another directory.

## A download stays at 0 %

- The server may be slow to answer. Wait a minute.
- For a playlist (HLS) video the playlist must be read first, then the segments one by one. A large programme can take a while to
  show progress.
- Open *Download Manager* from the menu; a failed job is listed there. Check the debug log for lines with `error_message`.

## The downloaded file will not play

Encrypted playlist streams are downloaded as they are and are not decrypted, so the result cannot be played.
Download a different quality, or watch the programme by streaming (**OK**).

## A file or entry is left behind after stopping

Stopping a playback, cancelling a download and a failed download all delete the files and remove the entry from MovieCockpit's
cache. If a partial file is still there (for example because Enigma2 was restarted while it was downloading), delete it with
MovieCockpit and press **Reload cache** (red, level 3) to drop the stale entry.

## No logo / no channel in MovieCockpit

See [Channels and Logos](Channels-and-Logos.md). A channel without a mapping in `mtc_service_refs.json` gets no service
reference; a channel without a logo file gets no logo.

## The cover is missing

The cover is read from the programme's web page. Some pages do not contain a picture address in the form the plugin
looks for, and some broadcasters change their pages. The download still succeeds without it. Put a `Name.jpg` next to the
file by hand if you want one, then press **Reload cache** in MovieCockpit.

## Limitations

- **German-language offer.** The service lists the German-language Mediatheken. The filter words (Audiodeskription,
  Trailer, Gebärdensprache) are German.
- **No resume of a partial download.** A restart or a failure ends the download.
- **Sequential HLS download.** The segments of a playlist are fetched one after another.
- **Playlist quality.** For playlist videos the best variant is always taken, whatever *Movie resolution* says.
- **No decryption** of encrypted playlists.
- **The search and the channel filter do not combine.**
