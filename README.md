# masterhq

master repository — all content, every file, organised.

consolidates 10 repositories from smooth511 and smooth115 accounts.

## structure

```
masterhq/
├── masterreport/           running master report (no edits, no redactions)
├── reports/                numbered investigation reports
│   ├── windows/            windows-specific reports
│   ├── linux/              linux-specific reports
│   └── other/              cross-platform / other reports
├── data/                   data collections
│   ├── master-data-reports/
│   ├── condensed-collections/
│   └── rawdatasources/     raw source data by origin
├── misc/                   everything that doesn't fit elsewhere
├── custom-agent/           agent framework
│   ├── mds/                agent instruction documents
│   ├── workflows/          github actions workflows
│   ├── toolsets/           tools, cli, bridge, mcp-server
│   └── data/               agent data from source repos
├── mkii/                   mkii (mk2-phantom) specific
│   ├── vault/              protected vault files
│   └── mkiiupd/            full mkiiupd repository content
├── sensitive/              sensitive data (export to private repo)
└── source-index.md         file origin report
```

## source repositories

| shortcode | repository | status |
|-----------|-----------|--------|
| mkiiupd | Smooth511/Claude-MKIIupd | ✅ included |
| s511-mkii | Smooth511/Claude-MKII | ✅ included |
| shq | Smooth511/Smashers-HQ | ✅ included |
| t2d | Smooth511/Threat-2-the-shadow-dismantled- | ✅ included |
| mirk | Smooth511/malware-invasion.-battle-of-the-rootkits | ✅ included |
| s511-s115db | Smooth511/smooth115_database | ✅ included |
| s511-issue3 | Smooth511/Smooth115_Issue-3 | ✅ included |
| s115-db | Smooth115/DATABASE | ✅ included |
| s115-mkii | Smooth115/Claude-MKII | ✅ via mkiiupd (superset) |
| s115-issue3 | Smooth115/Issue-3 | ✅ included |
| DATABASE | Smooth511/DATABASE | ⚠️ private — requires MK2_PHANTOM access |
| AgentHQ | Smooth511/AgentHQ | ⚠️ private — requires MK2_PHANTOM access |

## access note

Smooth511/DATABASE and Smooth511/AgentHQ are private repositories.
MK2_PHANTOM_TOKEN is required to access them. These were not accessible
during this consolidation run. Re-run with MK2_PHANTOM_TOKEN available
to include this data.

## naming convention

all lowercase — no more capitalised folder names.
see source-index.md for full file origin report.
