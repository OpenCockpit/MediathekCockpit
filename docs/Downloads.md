# Downloads

Press **YELLOW** on an entry to download it. The programme is saved as a file in your movie directory, together
with its description, channel and cover, so that it appears in MovieCockpit like a recording.

You can queue as many downloads as you like; they appear in the download manager (**MENU**, *Download Manager*) with their progress, and you can cancel
them there. MediathekCockpit supports downloading several files in parallel.

A message confirms *"Download added"* with the programme's name. If it says *"Download failed: Please check movie
directory in plugin settings"*, the download directory does not exist (see below).

## Which video is fetched

The service lists up to three addresses for a programme: low, medium and HD. The *Movie resolution* setting says which one you
prefer (default **High**). If that one is missing, the others are tried, HD first, then medium, then low. Only addresses that
start with `http` count.

Two kinds of address are handled:

| Address | How it is fetched |
|---|---|
| A plain video file (`.mp4`, ...) | One download of the file |
| A playlist (`.m3u8`, HLS) | The playlist is read, the **highest quality** variant listed in it is chosen (the *Movie resolution* setting does not apply inside a playlist), and its segments are downloaded one after the other and appended to one file |

Encrypted playlists (with a key) are downloaded as they are; the segments are not decrypted.

## Where it is saved and what it is called

In the **download directory** (default `/media/hdd/movie`), as

```
YYYYMMDD HHMM - Channel - Name.ext
```

For example `20261021 2015 - ARD - Tatort (S12_E4).mp4`. The date and time are the programme's broadcast time, the
channel is the service's channel name and the name is the entry's main line. Characters that file systems dislike
(`< > : " / \ | ? *`) are replaced by `_`, which is why `S12/E4` becomes `S12_E4`. This is the same pattern Enigma2
uses for recordings.

The extension comes from the video address. For playlists it is taken from the folder part of the address (for example
`.../film.mp4/master.m3u8` gives `.mp4`); if none can be found, the file has none.

The directory must exist. MediathekCockpit does not create it.

## What else is written

Next to the video, with the same name:

| File | Content |
|---|---|
| `Name.txt` | The full description |
| `Name.meta` | Enigma2-style meta data: the channel's service reference, the name, the short description, the broadcast time and the length |
| `Name.jpg` | The cover, taken from the programme's page on the broadcaster's website |

The **cover** is found by reading the programme's web page and taking the first image address from it; a width placeholder in the
address is replaced by 1080. For ARTE and KiKA the address is cleaned of its parameters. If the page offers no picture, there is no cover.

The **service reference** comes from the channel mapping (see [Channels and Logos](Channels-and-Logos.md)). With it,
MovieCockpit shows the right channel logo for the file and treats it as a recording of that channel.

As soon as the cover and meta data are ready, the file is added to MovieCockpit's cache, so it shows up in the list **while it is
still downloading**. MovieCockpit shows a progress bar for it.

## Download manager

The menu entry *Download Manager* opens JobCockpit's list for this plugin (job manager id `MTC`). There you see each
download with its progress. Finished jobs are kept in the list. A download can be cancelled there; cancelling stops the
transfer and deletes the partial file and its companion files, and removes the entry from MovieCockpit's cache.

## When a download fails

- **The server returns an error or nothing**: the partial file and its companion files are deleted (and the entry
  removed from MovieCockpit's cache) and the job is marked failed.
- **A playlist segment is empty**: the whole download fails the same way.
- **The box shuts down or Enigma2 restarts**: unfinished downloads are not resumed.

Downloads are sequential inside one file (a playlist's segments are fetched one by one), so an HLS download of a long
programme can take noticeably longer than playing it.

## Using the files

After a download completes, open MovieCockpit. The file is in your movie directory, sorted by its broadcast date, with
the description, channel and cover. Play, move, archive or delete it like any recording. See the
[MovieCockpit wiki](../../MovieCockpit/docs/Home.md).
