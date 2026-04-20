# MK2 Agent Install for masterhq

## What This Is

Pre-packaged `.github/` files that make the Copilot cloud agent work properly in masterhq. Without these, the agent won't identify as ClaudeMKII, won't have the operational rules, and won't have access to the MK2PK keys.

## Quick Install (3 steps)

### Step 1: Copy the `.github/` folder

Copy these 3 files into masterhq's `.github/` directory:

```
masterhq/
└── .github/
    ├── copilot-setup-steps.yml    ← Injects MK2PK1 + MK2PK2 as env vars
    ├── copilot-instructions.md    ← Full MKII operational spec (identity, rules, memory)
    └── agents/
        └── ClaudeMKII.agent.md    ← Custom agent definition (Opus 4.6 lock)
```

**How:** Go to masterhq repo on GitHub → Add file → Upload files → drag the `.github` folder contents in. Or use the GitHub web editor to create each file.

### Step 2: Add the secrets to masterhq

Go to: `masterhq` repo → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

Add these:

| Secret Name | Value |
|-------------|-------|
| `MK2PK1` | Your Smooth511 full-access token |
| `MK2PK2` | Your Smooth115 full-access token |

**You said you've already done this** — just verify both show up in the secrets list.

### Step 3: Launch from masterhq

Open an issue or use the Copilot cloud agent from masterhq. The `copilot-setup-steps.yml` will automatically inject the keys on agent startup.

The agent will have:
- `MK2PK1` env var → Smooth511 access
- `MK2PK2` env var → Smooth115 access
- Full MKII identity and operational rules
- Opus 4.6 model lock

## How the Agent Uses the Keys

Inside the agent session, it can use the keys like:

```bash
# Use MK2PK1 for Smooth511 repos
GH_TOKEN=$MK2PK1 gh api repos/Smooth511/DATABASE/contents

# Use MK2PK2 for Smooth115 repos  
GH_TOKEN=$MK2PK2 gh api repos/Smooth115/Claude-MKII/contents
```

## Key Naming Convention

**MK2PK** = the key family. When user says "use MK2PK" it means use whichever MK2PKX is appropriate:
- **MK2PK1** = Smooth511 full access
- **MK2PK2** = Smooth115 full access

This is separate from `MK2_PHANTOM_TOKEN` which still works in existing workflows here.

## Files Included

| File | Purpose |
|------|---------|
| `.github/copilot-setup-steps.yml` | Injects secrets as env vars on cloud agent startup |
| `.github/copilot-instructions.md` | Full MKII core spec — identity, rules, user profile, memory, everything |
| `.github/agents/ClaudeMKII.agent.md` | Custom agent definition — Opus 4.6 model lock, identity trigger |
