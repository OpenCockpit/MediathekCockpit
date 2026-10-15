# Integration

MediathekCockpit connects to the rest of the box in several ways. This page lists them, from the user's side and from the
plugin author's side.

## Ways in

| From | How | Result |
|---|---|---|
| Plugin menu / extensions menu | **MediathekCockpit** | The list of the newest programmes |
| EPG info and event info screens | The **Mediathek Downloads** entry (`PluginDescriptor.WHERE_EVENTINFO`) | A search keyboard, prefilled with the programme's title. If no event is given, the current programme of the playing service is used; if there is no event, the service's name |
| MovieCockpit | **Blue** button in its info screen: *Mediathek Download* | Same keyboard, with the title of the selected recording |
| Any plugin | The hook `WHERE_MEDIATHEK_SEARCH` (value -96) | Calls MediathekCockpit with a query string |

The search text from the EPG has any `(Snn/Enn)` season/episode tag removed before it is shown, so it finds the series and not
a single episode.

## Calling it from your plugin

MediathekCockpit registers a plugin descriptor for `WHERE_MEDIATHEK_SEARCH`. You find and call it like this (the same
helper MovieCockpit uses):

```python
from Components.PluginComponent import plugins

WHERE_MEDIATHEK_SEARCH = -96

found = plugins.getPlugins(where=WHERE_MEDIATHEK_SEARCH)
if found:
    found[0](session, query="Tatort")      # opens MediathekCockpit and asks to search for "Tatort"
```

The descriptor's function is `main(session, query="")`. With a query it opens the keyboard on the query; without
one it loads the newest programmes. Offer the button only if `found` is not empty.

## What MediathekCockpit uses from others

| Plugin / hook | Used for |
|---|---|
| JobCockpit | Two job managers: `MTC` (your downloads, kept after completion) and `TMP` (the temporary playback download). The *Download Manager* menu entry calls JobCockpit's hook `WHERE_JOBCOCKPIT` (-93) with the id `MTC` |
| CacheCockpit | `FileManager.getInstance("MVC").loadDatabaseFile(path)` after the cover and meta data of a download are ready, so MovieCockpit lists the file. If CacheCockpit cannot be imported, this step is skipped |
| MovieCockpit's player | The shared `CockpitPlayer` plays the programme (see [Playback](Playback.md)) |
| MovieCockpit's list | While a file is being downloaded, MovieCockpit shows a progress bar for it, taken from the `MTC` job |

## Files shared with MovieCockpit

A download writes the same set of companion files that an Enigma2 recording has (`.meta`, `.txt`, `.jpg`), named by the same
rule (`YYYYMMDD HHMM - Channel - Title`). This is deliberate: MovieCockpit's loader does not need to know that the
file did not come from a timer. See [Downloads](Downloads.md#what-else-is-written) and the
[MovieCockpit wiki](../../MovieCockpit/docs/Covers-and-Metadata.md).
