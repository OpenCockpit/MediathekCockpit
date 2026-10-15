# User Guide

## Opening

- From the plugin menu or the extensions menu: **MediathekCockpit**. The list opens with the **newest** programmes
  of all channels.
- From the EPG info of a programme: **Mediathek Downloads**. A keyboard opens with the programme's title, ready to search.
- From MovieCockpit: **blue** in the info screen. Same keyboard, with the title of the recording.

Leave with **EXIT** or **RED**.

## The screen

```
+---------------------------------------------------------------+
| MediathekCockpit - Movies - Search results - Page: 1/5        |
|                                                               |
|  [logo] ARD                 Tatort (S12/E4)       |  description |
|         21.10.2026 20:15    Der Pott              |  of the      |
|  [logo] ...                                       |  selected    |
|                                                   |  entry       |
|                                                   |  Duration:   |
|                                                   |  90 Minutes  |
|  Exit      Channels      Download       Search    Menu  Info    |
+---------------------------------------------------------------+
```

Each row shows:

| Part | Content |
|---|---|
| Logo and channel | The broadcaster's logo (if there is one for it, see [Channels and Logos](Channels-and-Logos.md)) and the channel name |
| Date and time | When the programme was broadcast (or published), below the channel name |
| Name | The programme or series name, with the season and episode in brackets, e.g. `Tatort (S12/E4)` |
| Second line | The episode title, in grey |

The pane on the right shows the description of the selected entry and its duration in minutes.

## Paging

The list does not load everything. It loads a **page** of as many entries as the setting *Entries in list* says
(default 120) and shows `Page: n/m` in the title.

- Move down past the last entry and the next page is **appended** to the list. Scrolling continues seamlessly.
- **CHANNEL+** / **CHANNEL-** jump up or down by one whole page.
- **LEFT** / **RIGHT** jump by 12 rows.

A new search or channel choice starts again at the first page.

The entries that the filters remove (see [Searching](Searching.md#filters)) are removed from the page after it is loaded,
so a page can show fewer entries than the page size.

## Choosing something to do

| Button | Does |
|---|---|
| **OK** | Watch the selected programme now. See [Playback](Playback.md) |
| **Yellow** | Download it. See [Downloads](Downloads.md) |
| **Blue** | Search again. The keyboard opens with the name of the selected entry |
| **Green** | Choose a channel |
| **MENU** | Download manager, Settings, About |
| **INFO** | Description, time, duration and channel of the selected entry |
| **5** | The raw data of the entry (for troubleshooting) |

## The information screens

**INFO** shows the programme: its name as the title, the date and time, the duration, the channel and the full
description (short description first, then the long one).

**5** (Movie Info) lists every field of the entry as MediathekViewWeb delivered it: channel, topic, title,
description, time, date, duration, size, id, the three video addresses (low, medium, HD), the website address, the time
stamp, the event name and the short description. Use it to see whether a programme has an HD version, or what the
download would fetch.

## The menu

**MENU** opens a short list:

| Entry | Does |
|---|---|
| Download Manager | Opens JobCockpit's list of this plugin's downloads (progress, cancel) |
| Settings | The [settings](Settings.md). Page size and the *future movies* choice apply to the next search |
| About | Version and licence |
