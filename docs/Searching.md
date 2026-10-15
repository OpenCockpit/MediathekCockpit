# Searching

## Where the data comes from

Every list is the answer to a question put to **MediathekViewWeb** (`mediathekviewweb.de/api/query`). It returns the
newest matching entries first. MediathekCockpit asks for one page at a time and asks again for the next page when you scroll past
the end. The list of broadcaster names for the channel selection comes from the same service (`/api/channels`).

Nothing is stored between sessions: opening the plugin starts a new query.

## Text search

Press **BLUE** (or open the plugin from the EPG). In the keyboard type a word or phrase and confirm.

- The text is looked up in the **topic** (the name of the programme or series) and in the **title** (the name of
  the episode). A hit in either field counts.
- Results are sorted by broadcast date, newest first.
- An empty search is allowed. It is sent to the service as it is, and the answer is whatever the service returns for an
  empty query (normally the newest programmes).
- If the text contains a season/episode tag such as `(S3/E12)`, the tag is removed before the search, so that
  searching for the name of a recording finds the whole series.

When you press **BLUE** in the list, the keyboard starts with the **topic** of the selected entry, which is
the quickest way to find more episodes of a series.

## Channel selection

Press **GREEN**. A list shows *All channels* and every broadcaster that the service knows (ARD, ZDF, 3sat, ARTE.DE, KiKA,
ARD-alpha, BR, HR, MDR, NDR, ORF, RBB, SR, SRF, SWR, WDR, ...). Choose one to list only its programmes, newest first.
If the service cannot be reached, the list delivered with the plugin is shown instead
(see [Channels and Logos](Channels-and-Logos.md#the-channel-list-for-the-selection)).

> **Search and channel do not combine.** Choosing a channel replaces the text search, and a text search replaces the
> channel. The last choice wins. To look for a title on one channel, search for the title and look at the channel column.

## Show future movies

*Show future movies* (setting, off by default) asks the service to include entries whose broadcast date is in the future.

## Filters

After a page is loaded, some entries are dropped. The filters are settings:

| Filter | Setting | Default | Drops entries... |
|---|---|---|---|
| Audio description | *Skip 'Audio description'* | on | whose title or topic contains "Audiodeskription" |
| Trailer | *Skip 'Trailer'* | on | whose title or topic contains "Trailer" |
| Sign language | *Skip 'Sign language'* | on | whose title or topic contains "Gebärdensprache" |
| Short clips | *Skip short duration* | 5 minutes | shorter than the given number of minutes (0 turns it off) |

The words are matched exactly as written (capital letter first). They are German because the Mediatheken are.

Because the filters run after the page is loaded, a page of 120 may show fewer entries. The paging still counts the unfiltered
results, so no entry is skipped when you scroll on.

## How an entry is built

MediathekViewWeb delivers, for every programme, a channel, a topic, a title, a description, a duration, a time stamp, a
file size, and up to three video addresses (low, medium and HD quality). MediathekCockpit tidies these up for the list:

- If the title begins with the topic, that part is removed from the title.
- A season/episode tag `(Snn/Enn)` in the title is moved to the topic, so the list shows `Tatort (S12/E4)`.
- A leading `: `, `| ` or `- ` is removed from the title.
- The list's main line is the topic (or the title if there is no topic); the grey line below is the title.
- A description that ends in `.....` (cut off by the service) is shortened to its last complete sentence.

The tidied main line is also what a download is named after.
