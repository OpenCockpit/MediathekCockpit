# Settings

Open them from the menu (**MENU**, *Settings*). After saving, the new page size and the *future movies* choice apply to the
next search or channel selection (the list on screen is not reloaded). The filters apply to every page loaded from then on.
The *Log level* entry is only shown in expert mode.

## Search

| Setting | Default | Effect |
|---|---|---|
| Entries in list | 120 | Page size: 12 to 1200 in steps of 12. Smaller pages load faster, larger ones scroll further without waiting |
| Show future movies | off | Include programmes with a broadcast date in the future |
| Skip 'Audio description' | on | Drop entries with "Audiodeskription" in the title or topic |
| Skip 'Trailer' | on | Drop entries with "Trailer" in the title or topic |
| Skip 'Sign language' | on | Drop entries with "Gebärdensprache" in the title or topic |
| Skip short duration | 5 min | Drop entries shorter than this (0 to 60 minutes; 0 keeps everything) |

See [Searching](Searching.md#filters).

## Download

| Setting | Default | Effect |
|---|---|---|
| Movie resolution | High | Preferred quality for playback and downloads: Low, Medium or High. Falls back to the others if missing. Playlists always use their best variant |
| Download directory | `/media/hdd/movie` | Where downloads (and the temporary playback file) are written. It must exist |

## Playback

| Setting | Default | Effect |
|---|---|---|
| Resume at last position | off | Offer to resume where you stopped |
| Movie start position | beginning | *beginning*, *first mark*, *event start* |
| Stop movie behaviour | Do nothing | *Do nothing*: stopping the movie, or reaching its end, leaves the player. *Ask user*: a menu asks **Quit**, **Restart from the beginning** or **Continue playing** |

## Display

| Setting | Default | Effect |
|---|---|---|
| Movie date format | `DD.MM.YYYY HH:MM` | Used where a time is shown as text by the player's information. The list itself always shows `DD.MM.YYYY` and `HH:MM` |

The choices are the same twelve layouts as in MovieCockpit: day/month/year or year/month/day, with or without time or weekday.

## Advanced

| Setting | Default | Effect |
|---|---|---|
| Log level | INFO | `ERROR`, `INFO`, `DEBUG`. Lines in the Enigma2 debug log start with `MTC:` |
