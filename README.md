# simple-card-viewer
A simple application to display images on screen and filter, organise, and sort them based on tags.

## CLI arguments
- `--skip-existing`: skip modifying existing enteries in the meta data db.
- `--modify-existing`: always modify existing enteries in the meta data db.
- `--modify=<file name>`: searches for the card `file name` and modifies only that card.
- `--propery=<property1, ...>`: only modify the listed properties. The options are `cardType`, `subType`, `legendary`, `cmc`, `color`, `p/t`, `keywords`, `abilities`, and `rarity`.
- `--debug`: display debugging information.
