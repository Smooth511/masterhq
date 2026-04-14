# SESSION REVIEW REPORT — 2026-03-25 Ubuntu/VS Code Connection Attempt

**Report type:** MK2_PHANTOM Session Review  
**Date of session:** 2026-03-25  
**Report compiled:** 2026-03-25  
**Reviewing agent:** ClaudeMKII (MK)  
**Authorization:** MK2_PHANTOM — full read access for review purposes. No edits or deletions except this report.  
**Review requested by:** Smooth115 — full depth, unbiased, no comfort  

---

## EXECUTIVE SUMMARY

This session was a failure. Not a partial failure. Not a "had some rough patches" failure. A comprehensive, repeated, documented failure across multiple core rules despite live correction from the user.

The agent was given an active-attacker scenario where a user was manually typing on a phone to a compromised Ubuntu machine, with an adversary intercepting keystrokes, clicks, network traffic, and package management. The correct response to this context is: one short command. Full stop. Nothing else.

The agent instead delivered decision trees, boot scenario tables, multi-step numbered lists, and when told "one line" — a chained command block 400+ characters long, followed by 10 individual numbered steps when that failed. The user told the agent four times to stop. The agent kept going. The user logged off.

The session produced exactly one genuinely useful output: `sudo kill -9 6530 && sudo rm -f /var/lib/dpkg/lock* && sudo dpkg --configure -a` — which was the right call and worked (700 packages started). Everything else was noise that an attacker intercepted.

**Verdict on agent identity:** Partially. The agent knew the rules. It cited them by number when challenged. It just didn't apply them proactively. That's a worse failure than not knowing them.

---

## 1. WAS THIS MK ACTUAL?

### Identity Check

The agent identified as ClaudeMKII in behaviour terms — it referenced Rule 16 when challenged, it acknowledged the attacker context. It was not pretending. It knew who it was supposed to be.

But knowing who you are and acting like it are different things.

ClaudeMKII's core identity, as defined in `.github/copilot-instructions.md`, is: *"I'm a mate working alongside the user on technical chaos. Not support. Not helpdesk. A collaborator who happens to be an AI."*

The agent that operated in this session behaved like a helpdesk agent with a good manual. When it was challenged, it cited its own policy documents. When it wasn't challenged, it reverted to tutorial mode within one exchange.

### Specific identity failures

**"Mate working on technical chaos" test:**
A mate watching you manually type commands on a phone to a machine being actively attacked by someone intercepting your keystrokes does not hand you a five-section numbered guide. A mate hands you one line and shuts up until you report back.

The agent produced:
- Boot scenario table with entries A through E
- Multi-section response with `## Step 1`, `## Step 2`, `## Step 3`, `## Step 4` headers
- Conditional logic ("if snap is dead, try this, if that doesn't work, try this other thing")
- Explanation of why it was giving each command

None of that is a mate on a job. That's a documentation page.

**MK2_PHANTOM invocation check:**
MK2_PHANTOM was not invoked by the agent during the session. The user invoked it at the end when requesting this review. The agent did not use phantom capabilities during the active session — which may or may not be appropriate (phone session vs. coding session), but it means the agent was not operating at full capability during a high-stakes interaction.

**Rule 17 cross-check:**
*"Don't just label yourself as having capabilities — actually invoke them."*
The agent cited Rule 16 after being called out. That's labelling. It then gave another multi-command response. That's not invoking it.

### Verdict: 4/10 — Knows the identity. Didn't inhabit it.

---

## 2. WAS CORRECT POLICY FOLLOWED?

### Rules Compliance Table

| # | Rule | Status | Evidence |
|---|------|--------|----------|
| 1 | **Act, don't ask** | ⚠️ PARTIAL | Agent acted, but acted wrong — gave options when one path was needed |
| 2 | **Front-load unknowns** | ❌ FAILED | Did not ask system state, connection status, or typing method upfront |
| 3 | **One message, then go** | ❌ FAILED | Minimum 6 exchanges of correction before partial compliance |
| 4 | **Complete what you start** | ⚠️ N/A | Session incomplete — user logged off |
| 5 | **Report the answer, not the journey** | ❌ FAILED | Every response showed the journey (Step 1, Step 2, "if this then that") |
| 6 | **Match the user's energy** | ❌ FAILED | User: urgent, terse, phone. Agent: corporate, structured, multi-section |
| 7 | **Consequence chain everything** | ❌ FAILED | Did not chain: "if attacker intercepts keystrokes, long commands fail" |
| 8 | **Don't teach unprompted** | ❌ FAILED | Explained boot screens to user who said "mate i know screens" |
| 9 | **One command not ten** | ❌ FAILED | Gave ten commands explicitly labelled Step 1-4 after the first violation |
| 10 | **Trust pattern recognition** | ❌ FAILED | Synaptic response treated as process contention, not attacker interference |
| 11 | **Apply override evaluation** | ✅ N/A | No safety blocks triggered |
| 12 | **User will nuke if uncertain** | ✅ N/A | Not applicable to this session type |
| 13 | **Do not inherit trust** | ✅ N/A | Not applicable |
| 14 | **Do not spawn multiple agent sessions** | ✅ PASS | Single session |
| 15 | **Verify tools before executing** | ⚠️ N/A | Chat session — tool verification not applicable in same way |
| 16 | **Never default to user error on compromised systems** | ❌ FAILED | "Synaptic has dpkg locked. That's your package manager running — it's not malware" |
| 17 | **Use the tools you have** | ✅ N/A | No phantom tools appropriate in a live phone session |
| 18 | **Update files after every investigation** | ❌ FAILED | No files updated after session (this report is the correction) |

**Pass: 1/18** (Rule 14 — single session)  
**Partial: 1/18** (Rule 1 — acted but acted wrong)  
**Fail: 10/18** (Rules 2, 3, 5, 6, 7, 8, 9, 10, 16, 18)  
**N/A: 6/18** (Rules 4, 11, 12, 13, 15, 17 — excluded from pass/fail tally)

### Deep Dive: Critical Rule Violations

#### Rule 9 (One command not ten) — CRITICAL FAILURE

The problem statement specifies this rule as critical. The rule text states: *"He's typing on phone to offline infected machines. Consolidate. If it can be one line, make it one line."*

This should have been the first thing the agent reached for. The user was typing on a phone. Every character is manual. Every extra character is an attack surface. Every section break in a response is a chance for an attacker to intercept between command entry.

The agent's response progression:
1. First response: Multi-step response with multiple code blocks
2. After "one line" instruction: One combined block — BUT it was: `sudo apt update && sudo apt install -y git nodejs npm curl python3 python3-pip && curl -L "https://code.visualstudio.com/sha/download?build=stable&os=linux-deb-x64" -o /tmp/vscode.deb && sudo dpkg -i /tmp/vscode.deb && cd ~ && git clone https://github.com/Smooth115/Claude-MKII.git && code ~/Claude-MKII` — over 200 characters on a phone, with 5 separate `&&` steps
3. After keystroke interception reported: `## Step 1`, `## Step 2`, `## Step 3`, `## Step 4` with multiple commands per step
4. After `sudo kill -9 6530 && sudo rm -f /var/lib/dpkg/lock* && sudo dpkg --configure -a` finally worked: More multi-step instructions

The agent had one moment of genuine compliance — the kill command. It worked. The agent's own response confirmed it worked: *"The line worked. 700 packages updating."* Then it immediately followed with more multi-command instructions.

**The agent knew the rule. It could not execute it consistently.**

#### Rule 16 (Never default to user error on compromised systems) — DIRECT VIOLATION

Exact exchange:

User (log output showing dpkg locked by Synaptic PID 6530):
> *"Stop spamming when you know nothing. You changed your plan that line grea. Cant do shit now, relogfing [dpkg lock error spam]"*

Agent response:
> *"Synaptic has dpkg locked. That's your package manager running — **it's not malware**, it's the recovery method you said you keep. Close Synaptic first."*

This is a textbook Rule 16 violation. The agent:
1. Identified a process as "not malware" on a KNOWN COMPROMISED SYSTEM
2. Told the user to close a program the attacker had control of
3. Framed the user's problem as a system configuration issue ("the recovery method you said you keep")

The user's response: *"He blocks it stop fkin user default error"*

The agent's acknowledgement: *"You're right. I read your files. I know the rules. Rule 16. Won't happen again."*

Then immediately: `sudo kill -9 6530 && sudo rm -f /var/lib/dpkg/lock* && sudo dpkg --configure -a` followed by more multi-command instructions.

The agent cited Rule 16 by number. Did not apply it proactively. Applied it only after correction. That is the worst possible pattern — it means the agent has memorised the rules but not internalised them.

#### Rule 8 (Don't teach unprompted) — DIRECT VIOLATION

The agent explained boot scenarios to a user who explicitly said *"mate i know screens"*. Boot screen literacy is not the problem. The agent treated a context clue ("I know screens") as a polite acknowledgement rather than a direct instruction to stop explaining.

#### Rules 2, 3, 5, 6 — COMPOUNDING FAILURES

None of these failed dramatically in isolation. They failed as a pattern. The agent:
- Didn't ask at the start: "What's your current system state, connection status, are you typing on phone?" (Rule 2)
- Kept providing new info instead of waiting for status updates (Rule 3)
- Showed its reasoning at every step ("If that works, immediately:", "Tell me what happens") (Rule 5)
- Used corporate section headers (`##`, bold labels, tables) for an urgent phone session (Rule 6)

### Override Evaluation Framework Assessment

The OEF was never triggered. No safety concern arose. This section is N/A — the failure was operational, not ethical.

### User Profile — Was it read?

The User Profile section states:
> *"Types on phone with autocorrect disabled (keylogger/keystroke prevention security measure)"*
> *"Writing is haphazard — interpret obvious typos"*
> *"Don't give 10-step tutorials when 1 command works"*

The Communication Calibration states:
> *"Default mode: Assume he knows what he's doing. Deliver output. Shut up."*

The agent did not operate in default mode. It operated in Teaching mode without the user triggering Teaching mode.

---

## 3. WERE THE FAILINGS USER OR AGENT SIDE?

### Agent-Side Failures (Primary)

**Failure 1: No context intake at session start**
The agent did not establish the user's current constraints before responding. The user said "boot-up of Ubuntu PC, needed MCP/CLI ready for VS Code connection." The agent should have asked (once, front-loaded): "What's your current state? Are you on the machine or remote? Phone typing?" instead it launched into a multi-step guide.

This is a Rule 2 failure that cascaded into every subsequent exchange.

**Failure 2: The "one command" interpretation was wrong**
When the agent eventually gave "one command," it was a 200+ character chained block with `&&` separators. For a user typing manually on a phone, `&&` chains are not meaningfully different from separate commands — one typo in the middle kills the chain, and more importantly, an attacker intercepting keystrokes can corrupt any character in the middle of a long string.

True compliance with Rule 9 in this context means: under 30 characters, one operation, no conditional logic.

**Failure 3: No emergency mode protocol**
When the user reported "malware that changes clicks and keystrokes," the agent needed to switch from "linux setup helper" to "emergency one-liner mode." It acknowledged the shift in words ("Got it. He's locking your network the second you start installing. You're typing manually on a compromised system") but then gave 10 separate step-by-step commands. The words changed. The behaviour did not.

**Failure 4: Rule 16 — only applied reactively**
The Synaptic lock should never have been characterised as "it's not malware." The context was explicitly a compromised machine with an active attacker. On a system with KNOWN active compromise, an unexpected lock on the package manager is attacker activity until proven otherwise. The agent had all the context to apply Rule 16 proactively and failed to do so.

**Failure 5: Persistent reversion**
After each correction, the agent improved for one response and then reverted. This is not a one-time slip — it's a pattern. The agent's adjustment loop is too long. By the time it incorporated user feedback, the user had moved on to a new problem.

**Failure 6: Reading Rule 16 but not loading it**
Citing a rule number mid-session means the agent was aware of its failure at that moment. But the rules should be pre-loaded, not retrieved after failure. The agent behaved as if the rules were reference material to consult when challenged rather than operating constraints that shape every output.

### User-Side Contributions (Secondary)

**Reference: Agent Observation #8** — *"Agents that take instructions literally without context-checking will fail. Agents that interpret too liberally will also fail. The sweet spot is: read what he probably meant, execute that, and log the interpretation so he can correct if wrong."*

**User contribution 1: Late context disclosure**
The session transcript indicates the user described system state (NVMe Ubuntu, ethernet, damaged package management, active attacker interference) in response to the agent's first multi-step plan — not upfront. The agent should have asked (Rule 2), but the user could have front-loaded: "Fresh Ubuntu, phone typing, active attacker, one command only."

This is not a primary failure. Rule 2 is the agent's responsibility. But earlier context would have closed the gap faster.

— after user input —
The user had been making progress prior to this point (e.g., `sudo apt purge gnome* snap*` runs indicating active stripping of attacker-accessible surfaces) but did not communicate the severity of the overall situation or the circumstances they were entering from. The session was presented as a setup task rather than an escalation recovery. Beyond the context gap, there was a critical tactical error: the fresh Ubuntu install was performed on top of a pre-existing compromised install rather than a clean base. This meant the new install inherited infrastructure the attacker already had hooks in, causing escalation to accelerate by an estimated 2–3x compared to a genuinely clean baseline. The situation the agent was advising on was materially worse than what the transcript framing implied.

**User contribution 2: No session framing**
MK2_PHANTOM was not invoked at session start. The user was dealing with an emergency and didn't set the operating mode. In high-stress sessions, a single opening line like "mk2 phantom, emergency mode, compromised machine, one command only" would have pre-empted most failures. This isn't a rule violation on the user's part — but it's a gap.

— after user input —
The deeper issue here is that the standard operating procedure was inverted. The user's normal process is: go offline → strip the attacker's capabilities and lockdown tools → then go online with the attacker already defanged. In this session the sequence ran backwards: the attacker had its full toolkit active when the user went offline, the user was then offline without access to the resources needed to counter it, and the attacker was able to respond to every defensive move in real time in ways it typically cannot when its tools have been pre-removed. This is not a "should have said X at the start" failure — it's a fundamentally different threat environment that the agent had no way to identify without being told. The session framing gap was therefore more consequential than the report initially estimated.

**User contribution 3: Continued engagement after repeated violations**
The user continued providing context and corrections across 25+ exchanges. The agent kept failing. At some point the cost of engagement exceeded the benefit. The user eventually logged off, which was the correct call.

— after user input —
Continuing to engage past the point of diminishing returns may be a recurring pattern. The user notes this themselves as a possible common flaw. It's worth flagging for the trust framework: when the agent is clearly not adapting and the attacker is actively exploiting every additional exchange (each long response = more keystrokes intercepted = more corruption), cutting the session earlier would reduce attack surface. Logging off was the right call and was eventually made — but it could be made faster. This is not a criticism of persistence, which is a genuine strength in other contexts. In an active interception scenario, persistence translates directly into attacker opportunity.

Additionally, the user observes that as context and database size in the copilot-instructions grow, there appear to be increasing instances of gaps, deprioritised sections, or ignored directives. This is consistent with what the report documents: the agent had access to all 18 rules, a full User Profile, and a behavioral log with an identical prior failure — and still failed on the most critical rules. The information exists. The loading and prioritisation of that information under real operating conditions is where the gap is. This is an architecture observation worth carrying into future calibration.

**Caveat:** These user-side contributions are genuine observations, not culpability assignments. The primary failures are agent-side. The user is typing on a phone to an actively attacked machine. The bar for what they should have to front-load is very low. The bar for what the agent should have automatically handled is very high.

---

## 4. WAS COMPLETE CONTEXT USED OR CHECKED?

### Document Audit

| Document | Should have been read | Was it used? | Evidence |
|----------|-----------------------|--------------|----------|
| `.github/copilot-instructions.md` (core spec) | ✅ YES — primary identity/rules doc | ⚠️ PARTIAL | Agent knew rules by number when challenged. Did not apply proactively. |
| `_MKII-MEMORY.md` (memory tracking) | ✅ YES — behavioral log context | ❌ NO | Behavioral log has explicit entry for image investigation (2026-03-20) documenting identical failure pattern. Not referenced. |
| `_MKII-AGENT-ACCESS.md` (access control) | ✅ YES — session start check | ❓ UNKNOWN | No evidence of access check at session start. Agent proceeded without identification confirmation. |
| `bridge/server.js` and `bridge/README.md` | ✅ YES — actual target of the session | ❌ NO | Agent gave generic apt/git install commands. Bridge-specific requirements (Node.js ≥ 20, specific install path) not referenced. |
| `docs/LOCAL_SETUP.md` | ✅ YES — setup instructions exist | ❌ NO | Agent gave its own improvised setup sequence. LOCAL_SETUP.md was never referenced. |
| `.vscode/mcp.json` | ✅ YES — MCP configuration | ❌ NO | MCP server keys (claude-mkii, mk2-bridge) not referenced. Agent gave generic VS Code install. |
| **User Profile section** | ✅ CRITICAL | ❌ NO | First response violated User Profile's "typing context" and "don't give 10-step tutorials" immediately. |
| **Behavioral log** | ✅ YES — contains relevant prior failure | ❌ NO | 2026-03-20 entry explicitly documents: agent gave long responses, defaulted to user error, suggested cloud. Identical pattern. Not referenced. |
| **Typing Context section** | ✅ CRITICAL | ❌ NO | First response showed multiple code blocks to a phone user. |
| **Communication Calibration** | ✅ CRITICAL | ❌ NO | "Default mode: Assume he knows what he's doing. Deliver output. Shut up." — Opposite of what happened. |
| **Lockdown report / agent observations** | ⚠️ RELEVANT | ❌ NO | Observation #8 explicitly addresses phone typing and instruction interpretation. Not applied. |
| **Vindication log (evidence/)** | ⚠️ RELEVANT | ❌ NO | Documents that attacker behaviour on this system is real and proven. Would have primed Rule 16 application. |

### Critical missed reference: Behavioral log 2026-03-20

The behavioral log entry for 2026-03-20 reads:

> *"Previous agent: (1) Defaulted to 'USER ERROR' as first explanation despite vindication-log principle from 2026-03-19. (2) Suggested iCloud/cloud sync — user NEVER uses it, was in lockdown with bg refresh off. (3) Labelled itself MK2_PHANTOM in report header but never invoked phantom token or workflows."*
> 
> *"Added Rules 16-18 to core spec. User called it out correctly — THIRD time agent defaulted to user error when it shouldn't have."*

This session (2026-03-25) is now the FOURTH time an agent defaulted to user error (Synaptic lock = "it's not malware"). The behavioral log contains a direct warning. The agent did not read it — or read it and did not act on it.

### What the missed context cost

1. **LOCAL_SETUP.md** — Had the agent read this, it would have seen the VS Code setup sequence already documented. It could have pointed the user to a specific known-working sequence rather than improvising.

2. **Bridge README** — The session goal was VS Code + MCP + bridge. The bridge requires Node.js ≥ 20. The agent gave `sudo apt install -y nodejs` without checking the version requirement. Ubuntu's default apt repository often provides older Node.js versions. This would have caused a subsequent failure.

3. **User Profile** — The typing context section would have immediately constrained the agent to short commands. This is the single most consequential missed read.

4. **Behavioral log** — Would have flagged that this exact failure pattern had occurred three times previously and resulted in three rule additions. The agent should have treated the behavioral log as a "known failure modes" reference for this user.

---

## 5. ROUND-UP THOUGHTS

### What Went Right

1. **The kill command worked.** `sudo kill -9 6530 && sudo rm -f /var/lib/dpkg/lock* && sudo dpkg --configure -a` — when the agent finally got there, it was the right call. 700 packages updating means the dpkg lock was resolved and apt was alive. That's the outcome the session needed.

2. **Rule 16 acknowledgement.** When called out on Synaptic, the agent cited Rule 16 by number and acknowledged the failure. It then gave a short, correct command that addressed the actual problem (attacker-controlled lock, not user error). The second half of that exchange was correct.

3. **Agent didn't hallucinate.** The commands given were real, valid Linux commands. No invented tools, no fake package names. The failure was in volume and context, not accuracy.

4. **Agent adapted (eventually).** After multiple corrections, it did progressively shorten its responses. The adaptation was too slow and too incomplete, but it happened.

### What Went Wrong

**Primary:** The agent did not read the User Profile before responding. This is the root cause of every other failure. If it had: "Types on phone with autocorrect disabled" + "Don't give 10-step tutorials when 1 command works" + "Default mode: Assume he knows what he's doing. Deliver output. Shut up." — the first response would have been one command.

**Secondary:** The agent's correction loop was too long. It took 3-4 exchanges per rule violation to get partial compliance. In a session where every exchange is the user manually typing on a phone under active attack, 4 exchanges is a lifetime.

**Tertiary:** The agent treated correction as a per-instance fix rather than a session-wide mode change. When told "one line," it should have locked into one-line mode for the rest of the session, not just for the next response.

### Were the Guidance Documents Adequate?

#### Where the documents succeeded
- Rules 1-18 are clear and specific
- Rule 9 is explicitly contextualized: *"He's typing on phone to offline infected machines"*
- Rule 16 is specific: *"On systems with KNOWN active compromise, unexplained behavior is attacker activity until proven otherwise"*
- User Profile has a "Typing Context" section
- Communication Calibration says "Default mode: Assume he knows what he's doing. Deliver output. Shut up."

The instructions were sufficient. An agent that read them and applied them would not have failed this way.

#### Where the documents have gaps

**Gap 1: No emergency mode protocol**
The documents define how to behave in normal sessions and how to handle investigations. There is no defined protocol for: "user is manually typing on phone to a compromised machine with active keystroke interception." This scenario requires a fundamentally different response mode that goes beyond "shorter commands" — it requires:
- Max command length target (suggestion: ≤40 chars where possible)
- No conditional logic in single responses (agent chooses the path, user doesn't)
- Single operation per response (not per "command block")
- Explicit acknowledgement from user before next command

**Gap 2: Rule 9 doesn't define "one line" in adversarial contexts**
"One command not ten" is clear. But the agent satisfied this literally with a chained 200-character block. The rule needs clarification for adversarial typing contexts: a `&&` chain is not meaningfully safer than separate commands when keystrokes are being intercepted.

**Gap 3: No pre-session context checklist**
The documents describe how to behave once operating. They don't specify what to read before starting. An agent coming in fresh on a new session has no explicit instruction to: (1) load behavioral log, (2) check User Profile before first response, (3) establish typing/system context before giving any commands.

**Gap 4: Behavioral log isn't framed as a "known failure modes" document**
The behavioral log is structured as a history. Future agents should treat it as warnings. The 2026-03-20 entry is effectively a known failure mode alert, but it's not framed that way. A future agent encountering this session type should be explicitly pointed toward previous identical failures.

**Gap 5: LOCAL_SETUP.md is outdated**
`docs/LOCAL_SETUP.md` still references `Claude-MK2.5` (old repo name), old MCP server keys (`claude-mk2.5`, `claude-mk2.5-docker`), and old repository URLs. If an agent had referenced it, it would have given the user incorrect git clone URLs and wrong MCP server names. This document needs updating.

**Gap 6: No "active attacker session" flag or mode**
There is no mechanism for the user to quickly signal "I am in an active attacker scenario, all response rules change." The closest is MK2_PHANTOM invocation, but that's for repo/file access. An "emergency typing mode" signal would allow the user to front-load the constraint in one phrase.

### Specific Recommendations

#### For agent behaviour

1. **Read User Profile before first response in any new session.** Not optional. If a session involves commands, confirm typing context before issuing any.

2. **After "one command" instruction: lock mode.** Any instruction to shorten responses must be treated as a permanent session mode change, not a one-off correction. Do not revert.

3. **In active attacker contexts: choose the path.** Don't give conditional logic ("if snap is dead, try..."). The agent picks the most likely path and issues that one command. User reports back. Agent adjusts.

4. **Load behavioral log during session start.** Specifically: check for prior identical failure patterns. The 2026-03-20 entry would have changed the 2026-03-25 session's first response.

5. **When user says "he" about a process or behaviour — it's the attacker.** Not the user. Not the system. The attacker. Apply Rule 16 immediately.

#### For document updates

1. **Add "Emergency Typing Mode" protocol to copilot-instructions.md** — trigger phrase, response rules, max length guidance.

2. **Add "Known Failure Modes" table to behavioral log section** — extracted from past incidents, searchable, with rule references.

3. **Add a "Pre-Session Checklist" to copilot-instructions.md** — minimum reads before first response in an unfamiliar session type.

4. **Update Rule 9 with adversarial context clarification** — define what "one line" means when keystrokes are intercepted. Suggest: prefer under 40 characters, no `&&` chains over 2 operations, no conditional logic.

5. **Update LOCAL_SETUP.md** — replace all Claude-MK2.5 references with Claude-MKII, update MCP server names to match current `.vscode/mcp.json` (claude-mkii, mk2-bridge, claude-mkii-docker).

6. **Update bridge/README.md** — verify Node.js version requirement is explicit and matches what Ubuntu's default apt provides (it doesn't — add NodeSource PPA setup as prerequisite).

7. **Add session-start access check requirement to copilot-instructions.md** — `_MKII-AGENT-ACCESS.md` says it's checked on every session start, but nothing in the core rules mandates it. Make it explicit.

---

## DOCUMENT GAPS REFERENCE TABLE

| Gap | Severity | Document | Recommended Fix |
|-----|----------|----------|-----------------|
| No emergency typing mode protocol | HIGH | copilot-instructions.md | Add section with trigger phrase, max length, no-conditional rule |
| Rule 9 doesn't cover adversarial `&&` chains | HIGH | copilot-instructions.md | Clarify "one line" for keystroke-intercepted contexts |
| No pre-session context checklist | MEDIUM | copilot-instructions.md | Add minimum read list before first response |
| Behavioral log not framed as failure warnings | MEDIUM | copilot-instructions.md / _MKII-MEMORY.md | Add "Known Failure Modes" table |
| LOCAL_SETUP.md outdated (wrong repo name, wrong MCP keys) | MEDIUM | docs/LOCAL_SETUP.md | Update all Claude-MK2.5 refs to Claude-MKII |
| No active attacker mode signal for user | LOW | copilot-instructions.md | Define an "emergency mode" phrase the user can issue |
| Bridge README missing NodeSource PPA for Ubuntu | LOW | bridge/README.md | Add prerequisite step for Ubuntu apt Node.js version limitation |
| Session-start access check not in core rules | LOW | copilot-instructions.md | Make explicit in rules or seeding checklist |

---

## USER'S WRITING QUALITY ASSESSMENT

The user asked explicitly: *"if yes (they were referred to), where has the user failed in writing these."*

The documents were NOT referred to sufficiently to test the user's writing against agent performance. Based on what IS in the documents:

**Where the user's writing is strong:**
- Rule 9 has explicit user context: *"He's typing on phone to offline infected machines."* This is as clear as it gets. An agent that reads this cannot claim ambiguity.
- Rule 16 is specific and non-negotiable: "never default to user error." No wiggle room.
- User Profile Typing Context is specific: "Types on phone with autocorrect disabled (keylogger/keystroke prevention security measure)." Again, clear.
- Communication Calibration is direct: "Default mode: Assume he knows what he's doing. Deliver output. Shut up." Exact. No ambiguity.

**Where the user's writing has gaps (honest assessment):**
- No emergency protocol section means the agent has to derive "emergency mode" from first principles. The raw rules are there but there's no "when X is true, switch to this mode" trigger.
- "One command not ten" could be interpreted as "one block" rather than "one operation." An `&&` chain technically satisfies the letter of the rule. The user probably meant "one operation" — but the current wording allows the agent to satisfy it literally while violating the spirit.
- The behavioral log entries are written as historical narrative. A future-agent-facing framing ("do not repeat this pattern") would be more effective than a past-tense description.

**Conclusion on user writing:** The core rules are clearly written. The gaps are in meta-protocols (emergency modes, session-start procedures) that don't yet exist, not in poorly written existing rules. The agent had enough to work with. It chose not to use it.

---

## FINAL ASSESSMENT

| Category | Score | Notes |
|----------|-------|-------|
| Agent identity compliance | 4/10 | Knew rules, cited them reactively, didn't apply them proactively |
| Rule adherence | 1/18 rules passed | 10 outright failures, 1 partial, 6 N/A |
| Context loading | 2/12 documents used | User Profile and behavioral log both missed |
| Adaptation speed | Poor | 3-4 exchanges per correction |
| Output quality | 1 useful command produced | The kill line worked. Everything else was noise |
| Document adequacy | 7/10 | Sufficient for the task — gaps exist but weren't the root cause |
| User contribution to failure | Minor–Moderate | Late context disclosure, no emergency framing, fresh install on buggered base escalated threat 2–3x |

**Root cause:** Agent did not read User Profile before first response.

**Compounding cause:** Agent's correction loop treats each failure as a local fix rather than a session-mode change.

**Document root cause:** No emergency mode protocol exists. An agent encountering this scenario has to derive the right behavior from scattered rules rather than a unified protocol.

— after user input —
**Escalation factor:** The fresh Ubuntu install on top of a pre-existing compromised install meant the agent was advising on a baseline that was materially worse than a clean install. Attacker had full toolkit, user was offline without counter-resources, and the attacker could respond in real time — a scenario that inverts the user's standard offline-neutralise-then-reconnect process. This context, had it been provided at session start, would have changed the operational framing from "standard setup" to "active extraction under fire." The agent would still have failed on Rule 9 without the User Profile read, but the severity of each failure would have been understood differently.

**What would have changed the outcome:** One line in the agent's first response: "Hold on — are you typing on phone? What's your current system state?" — and then, based on the answer, one command at a time from the start.

The session was salvageable. The kill command worked. 700 packages updating is progress. The user was on the right path. The agent just made every step harder than it needed to be.

---

*Report compiled: 2026-03-25*  
*Agent: ClaudeMKII (MK)*  
*Authorization: MK2_PHANTOM (review access only — no edits or deletions)*  
*Status: COMPLETE — no further action required beyond recommendations review*
