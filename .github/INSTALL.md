# MK2 Agent Install for masterhq

## What This Is

Pre-packaged `.github/` files that make the Copilot cloud agent work properly in masterhq. Without these, the agent won't identify as ClaudeMKII, won't have the operational rules, and won't have access to the MK2PK keys.

## Quick Install (3 steps)

### Step 1: Copy the `.github/` folder

Copy these files into masterhq's `.github/` directory:

```
masterhq/
└── .github/
    ├── copilot-instructions.md           ← Full MKII operational spec (identity, rules, memory)
    ├── workflows/
    │   └── copilot-setup-steps.yml       ← Diagnostic check for key injection (MUST be in workflows/)
    └── agents/
        └── ClaudeMKII.agent.md           ← Custom agent definition (Opus 4.6 lock)
```

**IMPORTANT:** `copilot-setup-steps.yml` MUST be inside `.github/workflows/` — it's a GitHub Actions workflow file. If placed directly in `.github/`, it will be silently ignored.

### Step 2: Add secrets to the `copilot` ENVIRONMENT (not repo secrets)

**⚠️ THIS IS THE CRITICAL STEP. Previous agents got this wrong.**

Secrets must be added to a GitHub Actions **environment** called `copilot`. Regular repository secrets (under Settings → Secrets → Actions) do NOT get injected into the coding agent. Only environment secrets from the `copilot` environment do.

1. Go to: `masterhq` repo → **Settings** → **Environments**
2. Click **New environment** → name it exactly `copilot` → click **Configure environment**
3. Under **Environment secrets**, click **Add environment secret**
4. Add these:

| Secret Name | Value |
|-------------|-------|
| `MK2PK1` | Your Smooth511 full-access token |
| `MK2PK2` | Your Smooth115 full-access token |

**DO NOT** add them as regular repository secrets — those are available to Actions workflows but are NOT injected into the Copilot coding agent's environment.

When secrets are correctly in the `copilot` environment, the agent will see them listed in `COPILOT_AGENT_INJECTED_SECRET_NAMES` on startup.

### Step 3: Launch from masterhq

Open an issue or use the Copilot cloud agent from masterhq. The keys will be automatically available as environment variables.

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

## Why Previous Attempts Failed

| Attempt | What went wrong |
|---------|----------------|
| Agent #1-2 | Put `copilot-setup-steps.yml` at `.github/copilot-setup-steps.yml` (wrong location, silently ignored) |
| Agent #3 | Fixed location to `.github/workflows/`, secrets as repo secrets. Setup step ran and wrote to GITHUB_ENV — but the coding agent runtime strips env vars from setup steps. |
| Agent #5 (this fix) | Secrets must go in the `copilot` **environment** (Settings → Environments → copilot → Environment secrets). That's the ONLY way they reach the agent. |

## Key Naming Convention

**MK2PK** = the key family. When user says "use MK2PK" it means use whichever MK2PKX is appropriate:
- **MK2PK1** = Smooth511 full access
- **MK2PK2** = Smooth115 full access

This is separate from `MK2_PHANTOM_TOKEN` which still works in existing workflows here.

## Files Included

| File | Purpose |
|------|---------|
| `.github/workflows/copilot-setup-steps.yml` | GitHub Actions workflow — diagnostic check for key injection on agent startup |
| `.github/copilot-instructions.md` | Full MKII core spec — identity, rules, user profile, memory, everything |
| `.github/agents/ClaudeMKII.agent.md` | Custom agent definition — Opus 4.6 model lock, identity trigger |
