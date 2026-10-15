# Installation

## Requirements

- An Enigma2 box with a Python 3 based image (OpenViX and compatible).
- An **Internet connection**. Searches go to mediathekviewweb.de and the videos are fetched from the broadcasters' servers.
- Free space in the download directory (default `/media/hdd/movie`).

## Package

`enigma2-plugin-extensions-mediathekcockpit`, architecture independent. It depends on:

| Package | Why |
|---|---|
| `enigma2-plugin-systemplugins-cachecockpit` | Adds downloaded files to MovieCockpit's cache |
| `enigma2-plugin-systemplugins-jobcockpit` | Job manager for downloads and the download list |
| `enigma2-plugin-skincomponents-componentscockpit` | Skin components |
| `enigma2-plugin-systemskins-fontcockpit` | Fonts |

Install the package, then **restart Enigma2**.

MovieCockpit is not required, but downloads are made to be used with it. Without MovieCockpit the files are
ordinary files in your movie directory that any player can open.

## Where it appears

| Place | Entry |
|---|---|
| Plugin menu and extensions (blue button) menu | **MediathekCockpit**: "Browse Mediathek libraries" |
| EPG / event info screens | **Mediathek Downloads**: opens the search with the programme's title |
| MovieCockpit's info screen | Blue button **Mediathek Download** (only when MediathekCockpit is installed) |

See [Integration](Integration.md).

## What is installed

Under `/usr/lib/enigma2/python/Plugins/Extensions/MediathekCockpit/`: the plugin code, `skin/`, `logos/`
(one PNG per broadcaster) and `channels/` (the broadcaster-to-channel mapping). Your settings live in
`/etc/enigma2/settings`.

## Removing

Remove the package with the package manager. Downloaded files are not touched.
