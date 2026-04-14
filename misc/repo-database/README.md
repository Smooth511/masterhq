# Phantom Database

Central storage for cross-repo data operations via MK2_PHANTOM_TOKEN.

## Two-Way Data Flow

1. **PULL** (`phantom-data-pull.yml`) - Pulls data FROM other repos INTO Claude-MKII's `database/repos/`
2. **PUSH** (`phantom-data-push.yml`) - Pushes data FROM Claude-MKII TO Smooth511/DATABASE repo

## Structure

```
database/
├── INDEX.md          # Auto-generated index of all pulled data
├── manifests/        # Pull operation manifests with timestamps
│   └── pull-YYYY-MM-DD_HH-MM-SS.md
└── repos/            # Per-repo directories
    ├── AgentHQ/
    │   ├── _repo-info.json
    │   ├── _tree.txt
    │   └── README.md
    ├── Claude-MKII/
    ├── malware-invasion/
    ├── Smashers-HQ/
    └── Threat-2/
```

## Usage

### Manual Trigger
Run `phantom-data-pull.yml` workflow from Actions tab:
- **target_repos**: `all` or comma-separated list (e.g., `AgentHQ,Threat-2`)
- **files_to_pull**: Comma-separated file paths (e.g., `README.md,.github/copilot-instructions.md`)
- **include_tree**: Also save directory structure listing

### Automated
Can be scheduled via cron or triggered by other workflows.

## Files Per Repo

- `_repo-info.json` — GitHub API repo metadata
- `_tree.txt` — Full file tree listing (if include_tree=true)
- `README.md` — Repository README
- `.github/copilot-instructions.md` — Copilot config (if exists)
- Additional files as specified in workflow

---

*Managed by mk2-phantom operations*

## Push to DATABASE Repo

**NEW:** Run `phantom-data-push.yml` to copy investigation data TO Smooth511/DATABASE:

### What Gets Pushed
| Source (Claude-MKII) | Target (DATABASE) | Content |
|---------------------|-------------------|---------|
| `evidence/` | `investigations/` + `reports/` | MD files, images |
| `logs/` | `logs/` | Analysis files, MD |
| `investigation/` | `investigations/` | Linux logs, images, analysis |
| `logs1sthour/` | `logs/first-hour/` | EVTX, JSON, text |

### Options
- **source_directories**: Which dirs to copy (default: all)
- **include_images**: Copy PNG/JPG files (default: true)
- **dry_run**: Preview what would be copied without actually pushing

### Run It
1. Go to **Actions** tab
2. Select **Phantom Data Push to DATABASE**
3. Click **Run workflow**
4. Use `dry_run=true` first to preview
