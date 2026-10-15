# Architecture

For developers.

## Overview

```
 plugin menu / extensions / EPG event info / WHERE_MEDIATHEK_SEARCH
        |
  MediathekCockpit (screen)  = Screen + Menu + ChannelSelection + Search
        |
        +-- MovieList (Query) ---- POST mediathekviewweb.de/api/query ---> rows (tuples)
        |
        +-- MovieFile.download ---- DownloadJob ---> JobCockpit manager "MTC"  (downloads)
        |                                      \--> manager "TMP"            (playback)
        |        DownloadTaskFile / DownloadTaskHLS ---> file + .txt + .meta + .jpg
        |                                              \--> CacheCockpit.loadDatabaseFile  (MVC)
        +-- CockpitPlayer (shared) ---- ServiceCenter(row) for the info bar
```

## Source files

| File | Role |
|---|---|
| `plugin.py` | Five descriptors: auto-start, the plugin / extensions menu entry, the event-info hook (`WHERE_EVENTINFO`), the `WHERE_MEDIATHEK_SEARCH` hook, and skin-change |
| `MediathekCockpit.py` | The screen. Key handling, play, download, page navigation hooks, the two job managers |
| `Menu.py` | The function menu: download manager (via `WHERE_JOBCOCKPIT`), settings, about |
| `Search.py` | The `postdata` dictionary sent to the service; the keyboard and its callback |
| `ChannelSelection.py` | Fetches the broadcaster list from `/api/channels` (falling back to `channels/mtc_channels.json`); sets the channel query |
| `MediathekPlayer.py` | `CockpitPlayer` subclass: with *Stop movie behaviour: Ask user* it shows Quit / Restart / Continue on stop and at the end |
| `Query.py` | The HTTP call and the row builder `getMovieRow`; the title tidying and the filters; `getSeriesEpisode` |
| `MovieList.py` | The `List` source: paging, selection, titles, the growing list |
| `MovieFile.py` | Resolution choice, playlist reading, file name, job creation; `checkMP4Structure` |
| `DownloadJob.py`, `DownloadTask.py` | The job and its two task kinds (single file, HLS); cover and meta preparation; file deletion |
| `HLSParser.py` | Parser for master and media playlists (`HLSVariant`, `HLSSegment`) |
| `ServiceCenter.py` | Stand-in for `eServiceCenter` that answers service-info requests from the selected row |
| `CockpitSeek.py` | Project-specific seek helper for the shared player (length from the row, position from the temporary download) |
| `EventInfo.py`, `MovieInfo.py` | The two information screens |
| `ChannelUtils.py` | Reads `channels/mtc_service_refs.json` |
| `Constants.py` | The `LIST_*` row indices |
| `ConfigInit.py`, `setup.xml`, `SetupScreen.py` | Settings |
| `keymap.xml` | Key maps for the contexts `MTC_Actions` and `CockpitActions` |
| `logos/`, `channels/`, `skin/` | Data and skin |

The player and helper modules (`CockpitPlayer`, `CockpitSmartSeek`, `CutListUtils`, `RecordingUtils`, `WebRequests`,
`WebRequestsAsync`, `JobUtils`, `ParserMetaFile`, ...) are shared sources from the `Common` repository.

## The row

A programme is a tuple of 17 values; `Constants.py` names the indices.

| Index | Name | Content |
|---|---|---|
| 0 | `LIST_CHANNEL` | Broadcaster name |
| 1 | `LIST_TOPIC` | Series / programme name, with an appended `(Snn/Enn)` |
| 2 | `LIST_TITLE` | Title, tidied |
| 3 | `LIST_DESCRIPTION` | Description, cut at the last sentence if truncated |
| 4, 5 | `LIST_TIME`, `LIST_DATE` | `HH:MM`, `DD.MM.YYYY` of the time stamp |
| 6 | `LIST_DURATION` | Seconds |
| 7 | `LIST_SIZE` | Bytes |
| 8 | `LIST_CHANNEL_PIXMAP` | Logo pixmap or `None` |
| 9 | `LIST_ID` | Service id |
| 10, 11, 12 | `LIST_URL_VIDEO_LOW`, `LIST_URL_VIDEO`, `LIST_URL_VIDEO_HD` | The three video addresses |
| 13 | `LIST_URL_WEBSITE` | The programme's page (used for the cover) |
| 14 | `LIST_TIMESTAMP` | Epoch seconds |
| 15 | `LIST_EVENT_NAME` | Topic, or title if no topic: the name used for file names and the info bar |
| 16 | `LIST_SHORT_DESCRIPTION` | The title if it differs from the event name |

The same numbers appear in the skin (`value: 0`, `5`, `4`, `8`, `15`, `16` in the list) so keep the two in sync.

## The query

`Search` owns `postdata`:

```python
{"sortOrder": "desc", "sortBy": "timestamp", "offset": 0, "size": <page size>, "future": <bool>,
 "queries": [{"fields": ["topic", "title"], "query": "<text>"}]}     # or fields ["channel"]
```

`MovieList.getList` posts it, applies the filters in `Query.download`, keeps `raw_offset` (the number of results
received, before filtering) and sets `postdata["offset"] = raw_offset` for the next page. A response is
`{"result": {"results": [...], "queryInfo": {"totalResults", "resultCount", "filmlisteTimestamp"}}}`.

## Playback and the two job managers

`pressOk`:

1. `MovieFile.download(curr, tmp_job_manager)` queues the temporary download and returns `(url, path)`.
2. `playMovie` calls `checkMP4Structure(path)` (looks for the `moov` atom in the first 100 bytes of the file):
   progressive MP4 -> play the file, else play the stream address. A `CockpitPlayer` is opened with
   `stream=<bool>`, `service_center=ServiceCenter(list)` and the plugin's config subsection.
3. `playMovieCallback` aborts all pending `TMP` jobs through `JobCockpit.abortJob`, calls `deleteFile(path)` (removes
   `<stem>.*`), and re-plays the previous service.

`CockpitSeek.getRecordingPosition` uses the `TMP` job's progress as the "recording position" so the info bar can show how
much is available.

## Downloads

`DownloadJob(url, segments, ...)` chooses the task:

- `segments` non-empty -> `DownloadTaskHLS`: one `getContentAsync` per segment, appended to the file; progress is
  segments done over total.
- else -> `DownloadTaskFile`: `downloadFileAsync` with a progress callback.

Both tasks start a thread that downloads the cover and writes the sidecar files (`loadDatabaseFile`: `.txt`,
`ParserMetaFile.updateMeta`, then `FileManager.getInstance("MVC").loadDatabaseFile`). Results from threads are handed to the
main loop with `reactor.callFromThread`. A failure and `abort()` both call `deleteFile`, which removes the `<stem>.*` files
and, if CacheCockpit is available, the `table1` row for the file and the `table2` cover row from the `MVC` cache.

## Skin

Source files are YAML parts (`.ymlinc`) compiled to `skin/default/skin.xml`. Screens: `MediathekCockpit` (1920 x 1080: list at
20,80, description pane at 1260,80), `EventInfo` and `MovieInfo`. The list uses `TemplatedMultiContent` with item height 70:
channel (`value 0`), logo (8), date (5), time (4), event name (15), short description (16, grey).

## Packaging and translations

Autotools. `CONTROL/control` lists the dependencies. `po/de.po` and `po/setup.po` hold the German translations of the
code and of the setup texts.
