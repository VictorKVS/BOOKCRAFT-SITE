# BOOK-CRAFT Asset Inbox Inventory

## Status

Initial inventory of uploaded visual assets.

| Inbox | Intended scope | Files |
|---|---|---:|
| `_inbox` | BOOK-CRAFT | 21 |
| `_inbox2` | FATHER | 11 |
| `_inbox3` | Mixed assets for all projects | 62 |
| **Total** |  | **94** |

## Sorting policy

Assets are sorted only after project/purpose can be identified with sufficient confidence.

Statuses:
- `SELECTED` — chosen for active use
- `CANDIDATE` — good alternate
- `REFERENCE` — visual reference only
- `DRAFT` — work in progress
- `UNUSED` — not currently used
- `ARCHIVE` — retained but removed from active set
- `NEEDS_VISUAL_REVIEW` — filename is insufficient to classify safely

## Target structure

```text
public/assets/
├── bookcraft/
│   ├── hero/
│   ├── backgrounds/
│   ├── cards/
│   ├── modules/
│   ├── props/
│   └── archive/
├── father/
│   ├── brand/
│   ├── hero/
│   ├── agents/
│   ├── architecture/
│   ├── dashboards/
│   ├── illustrations/
│   └── archive/
└── projects/
    ├── alina/
    ├── makar/
    ├── osint/
    ├── secgraph/
    ├── otus/
    ├── media/
    ├── games/
    ├── shared/
    └── archive/
```

## Current rule

Do not guess project assignment from opaque UUID/timestamp filenames. Those files remain in their inbox until visual review is completed. Original filenames remain recoverable from Git history after rename/move.
