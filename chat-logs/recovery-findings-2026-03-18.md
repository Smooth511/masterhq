# Recovery Findings - 2026-03-18

## Verdict

**The chat is not recoverable.** GitHub Copilot chat history is stored server-side on GitHub's infrastructure, tied to the account. Account deleted = chats deleted. GitHub does not include Copilot conversation content in audit log exports. It's gone.

**The repos are not recoverable.** All were private and went down with the account. GitHub confirmed: account doesn't exist.

---

## What We Do Have

The audit log CSV (`export-Literatefool-1773786096.csv`, 7,910 rows) was exported before deletion and is preserved here. It doesn't contain chat content, but it contains the full account activity timeline - every repo created, deleted, transferred, every login, every Copilot integration event.

---

## Timeline of the Final Session (March 18, 2026)

| Timestamp | Event |
|-----------|-------|
| 1773784197439 | Literatefool logged in - passkey "Gitliterate" |
| 1773784212767 | Added to Smooth511/Claude-MKII with write access |
| 1773784212775 | Accepted invitation |
| 1773784598336 | Created OAuth token (Copilot Chat App + SWE Agent scopes) |
| 1773785840611 | **Copilot SWE Agent token created** ← this is when the 2-3hr session ran |
| 1773785963638 | Copilot Chat App token regenerated ← last recorded event |
| (deletion) | Account and all chat history gone |

The write access to Claude-MKII was accepted just before the investigation session ran. The files were never committed. Then account deleted.

---

## Complete Repo Inventory (from audit log)

### Literatefool/ (29 repos)

| Repo | Notes |
|------|-------|
| .github-private | Private org config |
| .github-private2 | Transferred from AM-UI-Process/.github-private |
| Adonis | Roblox framework (NevermoreEngine ecosystem) |
| Alpha | Named deploy/version |
| Bravo | Named deploy/version |
| Cannons | Game mechanic |
| Charlie | Named deploy/version |
| Comprehensive-NPC-System | NPC AI system |
| Copilot-Sign | Copilot integration |
| FoundDataDump | Data preservation repo |
| Local-Seli-WS | Local WebSocket server |
| Local-Seli-WS-Server | WS server variant |
| MasterDataStart-of-Project | Project baseline data |
| My_First_Game | Early Roblox project |
| NevermoreEngine | Fork of NevermoreEngine (Roblox) |
| ObsidianUI | UI framework - deleted then recreated |
| ROBLOX | Main Roblox project |
| Rayfield | UI library - deleted then recreated |
| ScooterHUB | Main hub - transferred to AM-UI-Process then back |
| ScooterHUB2 | Second hub iteration |
| Scooters-Hub | Original hub (deleted) |
| Seliware | Seliware project - deleted then recreated |
| SuperbulletAI---Copy | AI project copy - transferred from AM-UI-Process |
| SuperbulletAI-Copy | AI project copy - transferred from AM-UI-Process |
| awesome-copilot | Copilot config - deleted then recreated |
| cli | CLI tooling |
| ezVisualz | Visualization tools |
| gpt4all | GPT4All integration |
| robloxstudio-mcp | Roblox Studio MCP server |

### AM-UI-Process/ (7 repos - org "snipersquadron", id 544728)

| Repo | Notes |
|------|-------|
| .github-private | Org config - transferred out to Literatefool/.github-private2 |
| Local-Seli-WS-Server | WS server |
| Mid-Point-Assembly | Assembly/integration point |
| ScooterHUB | Transferred from/to Literatefool/ScooterHUB |
| SuperbulletAI---Copy | Transferred to Literatefool |
| SuperbulletAI-Copy | Transferred to Literatefool |
| demo-repository | Created and deleted |

---

## What to Know About AM-UI-Process

Separate GitHub org under the "snipersquadron" enterprise (business_id 544728). The Literatefool repos were moved there and back during development. All repos that ended up in AM-UI-Process were transferred back to Literatefool before deletion. Status of the org itself after account deletion is unknown - if it still exists it may have no repos.

---

## Copilot Activity

- **Copilot for Business** seat was assigned/cancelled (1768987317599 → 1770837826227)
- Multiple Codespace sessions (3 created, 13 connects, 518 suspends - heavy usage)
- Both Copilot Chat App and Copilot SWE Agent were active

---

## Why Files Weren't Committed

The write access to Claude-MKII was granted during the final session. The SWE Agent ran the investigation. The findings existed only in the chat UI. `report_progress` was never called. Account deleted. No commits = no trace.

---

## Bottom Line

Chat: gone. Repos: gone. The audit log is the only surviving record of what existed. The repo inventory above is reconstructed from it.

If anything specific is needed from those repos (code patterns, specific content), the only remaining option is if any of the repo content was ever publicly visible, cached by a search engine, or had forks elsewhere. Given all repos were private, that's unlikely.
