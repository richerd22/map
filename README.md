# map.cold.fyi

Every public site in the cold.fyi / Third Polar Arch universe on one page. GitHub Pages from `main`, repo root.

- `data/sites.json` - the approved list: host, name, one-line blurb, group. Only public, live, meant-to-be-seen sites. Never admin panels, health endpoints, aliases, or unfinished builds.
- `build.py` - regenerates `index.html`, `sites.json` (public feed) and `sitemap.xml`. No dependencies.
- `map.css` - cold.fyi palette: #0a0a10, white, one cold blue, DM Mono, grain.

## How sites get added

1. A new hostname appears in the Notion Domain Registry (CommonCTRL's monthly "sites scan" and Stem's checks feed it).
2. Daily Digest prep compares the Registry's live, canonical rows with `data/sites.json` and stages "Map: add X?" with a drafted name, blurb and group.
3. Richard replies `Map: approve`, `Map: skip X`, or edits a blurb (`Map: X = new blurb`).
4. Next prep run adds approved rows to `data/sites.json`, runs `python3 build.py`, commits and pushes.

Removal: delete the row, rebuild, push. Full guide: Notion, "Map - map.cold.fyi (READ FIRST)".
