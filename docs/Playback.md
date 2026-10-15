# Playback

Press **OK** on an entry to watch it. The programme is played with MovieCockpit's player, so it behaves like a recording:
pause, skip, resume, audio and subtitle selection. This page explains how it works and what to expect.

## What happens when you press OK

1. A **temporary download** of the programme is started in the background. It is an ordinary download job (see
   [Downloads](Downloads.md)) with the same file name and the same companion files, but in a separate job list (`TMP`) so
   that it does not show up as one of your downloads.
2. The player starts at once, in one of two ways, decided once at that moment:

| Mode | When | Plays |
|---|---|---|
| **File** | The video is a progressive MP4 (its index is at the start of the file) and the file is already readable | The partly downloaded file |
| **Stream** | Anything else, including every playlist (`.m3u8`) video | The stream address directly |

3. In stream mode the player gets the length from the programme data. The recording-style position display uses the progress of
   the temporary download.
4. When you **stop** (STOP, EXIT or POWER), the temporary download is aborted, **all** files with the same name stem
   are deleted (video, `.meta`, `.txt`, `.jpg`), the entry is removed from MovieCockpit's cache if it had been added,
   and the channel you were watching before is tuned again.

If the video address is missing or no stream can be found, you get *"No valid stream detected."* or *"Unsupported
video format or no valid stream detected."* for four seconds.

> The temporary file is written to your **download directory** (see [Settings](Settings.md#download)) and is named like a
> download. If that directory is one of MovieCockpit's bookmarks, the file can show up in its list while you
> watch. It disappears again, from the disk and from the list, when you stop.

## Player settings

The player reads these settings (see [Settings](Settings.md#playback)):

| Setting | Default | Effect |
|---|---|---|
| Resume at last position | off | Offer to resume where you stopped |
| Movie start position | beginning | *beginning*, *first mark* or *event start* |
| Stop movie behaviour | Do nothing | With *Ask user*, STOP / EXIT / POWER and the end of the programme open a menu: **Quit**, **Restart from the beginning**, **Continue playing**. The temporary download is only cleaned up when you really quit |

The temporary files are deleted when you stop, so there is nothing to resume from next time. For a long programme
you want to continue later, **download** it and play it from MovieCockpit.

## Smart jump

**CHANNEL+** and **CHANNEL-** skip with steps that shrink as you home in: 5 minutes first, then 1 minute, then 30 and 15
seconds when you change direction. After 5 seconds without a key it starts over.
See [Keys and Buttons](Keys-and-Buttons.md#while-watching).

## What can go wrong

| Symptom | Likely cause |
|---|---|
| Picture starts, then stalls | Slow connection or a busy server. The player has only what the stream delivers; try the *Medium* or *Low* quality (see [Settings](Settings.md#download)) |
| "No valid stream detected" | The entry has no usable video address (press **5** to see the three addresses), or the download directory in the settings does not exist |
