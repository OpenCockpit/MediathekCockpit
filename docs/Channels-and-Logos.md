# Channels and Logos

MediathekCockpit knows the broadcasters by the names that MediathekViewWeb uses: `ARD`, `ZDF`, `3Sat`, `ARTE.DE`,
`KiKA`, `ARD-alpha`, and so on. Two small data sets make them look right on your box.

## Logos

The list shows a logo next to each entry. The files are in the plugin's `logos/` folder, one PNG per broadcaster. The
file name is the channel name in capitals with spaces removed:

| Channel name | Logo file |
|---|---|
| `ARD` | `ARD.png` |
| `Radio Bremen TV` | `RADIOBREMENTV.png` |
| `ARTE.DE` | `ARTE.DE.png` |
| `ZDF-tivi` | `ZDF-TIVI.png` |

Included: 3sat, ARD, ARD-alpha, ARTE (DE, EN, ES, FR, IT, PL), BR, DW, Funk.net, HR, KiKA, MDR, NDR, ONE, ORF, Phoenix,
Radio Bremen TV, RBB, RBTV, SR, SRF, SRF Podcast, SWR, tagesschau24, WDR, ZDF, ZDF-tivi.

A channel without a logo file simply shows no picture. To add one, put a PNG with the right name in the `logos/` folder
(it is read when the list is built, so reopen the plugin).

## Channel mapping (service references)

A downloaded file should look like a recording of the channel it came from. For that, the `.meta` file needs the
**service reference** of that channel on your box. `channels/mtc_service_refs.json` provides it:

```json
{
  "ARD": { "name": "Das Erste HD", "service": "1:0:19:283D:3FB:1:C00000:0:0:0:" },
  "ZDF": { "name": "ZDF HD",      "service": "1:0:19:2B66:3F3:1:C00000:0:0:0:" },
  "SRF": {}
}
```

The key is the channel name from MediathekViewWeb. `name` is for humans, `service` is the Enigma2 service reference that is
written into the downloaded file's `.meta`. A broadcaster with `{}` (as `SRF` above) has no mapping: the file is saved
without a service reference.

The delivered file maps 24 broadcasters. The references belong to one particular channel list (satellite). On your box the
channel may have a different reference, or be missing.

### Adapting it to your channel list

1. Find the service reference of the channel you want on your box (for example in the channel list's info, or in
   `/etc/enigma2/lamedb`).
2. Edit `/usr/lib/enigma2/python/Plugins/Extensions/MediathekCockpit/channels/mtc_service_refs.json` and put the reference
   in the `service` field of that broadcaster. Keep the JSON valid (quotes and commas).
3. The mapping is read each time a download or a playback starts. New downloads use the change; existing files keep the old reference in their `.meta`.

What the service reference gives you: MovieCockpit shows the **channel logo** (picon) for the file in its list.

## The channel list for the selection

The channel selection (**GREEN**) asks MediathekViewWeb for the current broadcasters. If the service does not answer, or
answers with an empty list, MediathekCockpit uses `channels/mtc_channels.json`, a list of the known channel names delivered
with the plugin:

```json
{"error": null, "channels": ["ARD", "ZDF", "SRF", "SWR", "NDR", "BR", "SR", "KiKA", ...]}
```

So the selection works without a connection (the search itself still needs one). Edit the file to add or remove names
for that fallback.
