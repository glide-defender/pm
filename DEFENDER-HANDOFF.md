# Defender — Project Context Handoff

## The Project

I'm Matt Isgur, working at **ADRM Security**. I'm building **Defender** — a security project management app delivered as a Glide embed with Make.com as the backend automation layer.

The mandate: build the greatest security project management app ever created. My aesthetic bar is high and enterprise-grade. I've been iterating this across multiple long sessions with Claude.

**The file you need:** `workspace-all.html` (bundle, ~515KB). This is the complete working demo. All 19 sections are embedded inside it via a `window.__SECDOCS__` object.

---

## Visual / Aesthetic Rules (firm)

- Background: `#171717`
- Primary button: slate `#3c4756` (NOT amber — amber is for accents only)
- Amber `#F59E0B` for progress bars, active tab underlines, KPI left-borders, focus rings, sidebar completion bar
- **No purple, no gradients (except one subtle hero background), no confetti, no animations**
- Red/Yellow/Green dot convention (🔴🟡🟢) for status across all sections
- Terminology: use **"Update"** not "Edit" everywhere
- Font: `ui-sans-serif, system-ui, sans-serif`

---

## Architecture

### Table strategy (Glide tables)

**Consolidated into JSON on Projects table** (delete these as standalone tables):
- Punch List → `punchListJson`
- Material Tracker → `materialTrackerJson`
- Observations → `observationsJson`
- Risk Tracker → `riskTrackerJson`
- RACI (+ Companies JOIN) → `raciJson`
- RFI → `rfiJson`

**Kept relational:** Projects, Milestones, Tasks, Finance Line Items, Time Entries, Deployment Templates + Items, Contacts, Attachments, Meetings.

### Deployment sub-architecture

- Templates relational (account-level)
- Template Steps → `stepsJson` on Templates
- Deployment Items relational (project-scoped)
- Responses → `responsesJson` on Items
- **Snapshot-on-add**: asset copies steps at creation; template edits don't retroactively affect; "Sync to Latest" button per asset

### Progress engine (duration-weighted, MS Project-style)

```
Action Item % → Milestone % (weighted avg by duration) → Phase % → Schedule Work % (60%)
+ Deployment 12% + Materials 10% + Punch 7% + Observations 5% + Risks 3% + RFI 3%
Empty trackers redistribute weight proportionally.
```

Exposed via `window.computeProgress(P)`. Milestone % is calculated when >0 action items; editable fallback otherwise.

### Shared utilities (all on `window.__X__`)

```js
window.__STATUSES__            // status options per entity type
window.__TYPES__               // project types (Install, Service, Assessment, Upgrade, Decommission, Maintenance)
window.__CONTACTS__            // contact list (powers @-mentions)
window.__COMMENTS__            // { 'task:5': [...], 'risk:1': [...] }
window.__ATTACHMENTS__         // same keying as comments
window.__NOTIFICATIONS__       // inbox feed
window.__PROJECT__             // project data the progress engine reads
window.commentsWidget(entityType, entityId)
window.attachmentsWidget(entityType, entityId)
window.showRowMenu(btn, actions)
window.healthDot(status)
window.originLink(entity)      // breadcrumb for converted entities
window.toast(msg, kind)
window.computeProgress(P)
window.__openInbox()
window.__openExport()
window.__wireMention(inputId, hostId)
```

---

## Section Inventory (19 sections)

**Plan:** My Work · Overview (with ECharts dashboard) · Schedule (3 sub-tabs: Tree / Milestone List / Gantt) · Tasks

**Execute:** Commissioning · Deployed Assets · Materials · Punch List · Observations

**Govern:** Risks · RFI · RACI · Finance (with ECharts treemap) · Scorecard (radar + weighted composite)

**Workspace:** Contacts · Files (Miller column + Links sub-tab) · Time · Meetings · Activity · Audit Log

---

## Feature Coverage Matrix (current)

| Feature | Coverage |
|---|---|
| Per-entity comments with @-mention autocomplete | 11 sections (Tasks, Risks, Observations, Punch, RFI, Materials, Finance, Meetings, Contacts, Assets, Milestones) |
| Per-entity attachments | 10 sections |
| Row action menus (⋯) | 12 sections — Update always first, Delete always red+last with divider above |
| Cross-entity conversions | 4 flows: Observation→Risk, Punch→Task, RFI→Risk, Meeting decision→Task. Track `originFrom`/`originId`. Drawer shows blue breadcrumb "↳ Converted from Punch Item #3" |
| Colored status dots (🔴🟡🟢) | 8 sections |
| Status filter dropdowns | 4 sections (Tasks, Punch, RFI, Observations) |
| Bulk actions + Import | 10 sections (Tasks, Punch, RFI, Materials, Risks, Finance, Contacts, Meetings, Observations, Time). Sticky bottom action bar with Mark Closed / Delete / Cancel + CSV-row paste Import |
| ECharts visuals | 5 total — Overview: Project Vitals concentric rings, Issue Landscape polar, Owner→Milestone→Status Sankey. Finance: Budget Allocation treemap. Scorecards: Radar |
| Smart Inbox (🔔 bell in topbar) | 6 notification types: mention / assigned / due / comment / status / overdue, unread badge, mark-all-read |
| Export Hub | PDF / Excel / Shareable Link / JSON — triggered via Export button or `E` key |
| Command Palette (docked in sidebar, not modal — iframe-safe) | Fuzzy search sections + create actions, ⌘K focuses, arrow/Enter/Esc |
| Keyboard shortcuts | ⌘K search, `/` focus search, `N` new, `G+letter` jump (t/s/r/p/o/m/f/c/h), `E` export, `I` inbox, `?` help, `Esc` close |
| Toast notifications | Every save → success toast (parent.postMessage from iframes) |
| Cross-section deep links | Shell ↔ iframe postMessage plumbing; Tasks drawer has "View milestone in Schedule" link |

---

## Pattern Reference

### Row action menu
```
[Update — always first] / [Entity-specific action(s)] / [divider] / [Delete — red, always last]
```

### Row click pattern
Click row body to open drawer, `⋯` menu button uses `stopPropagation`.

### Drawer footer pattern
`[Cancel] [Save/Update]` right-aligned; conversion buttons (e.g. "→ Convert to Task") flush-left.

### Cross-entity conversions
- Source entity's drawer has a "→ Convert to X" button
- New entity gets `originFrom: 'punch'` / `originId: 3` fields
- Target drawer shows blue breadcrumb pill via `window.originLink(entity)`
- Production Make payload logged via console.log

### Deep link message format
```js
parent.postMessage({ type: 'navigate', section: 'schedule', entityId: 3 }, '*');
```

---

## Bundling Pipeline (critical)

```python
files_map = {'risks':'section-risks.html', 'observations':'section-observations.html', ...}
docs = {k: open(fn).read() for k,fn in files_map.items()}

def esc(s):
    return s.replace('\\','\\\\').replace('`','\\`').replace('${','\\${').replace('</script>','<\\/script>')

entries = ',\n'.join(f'  {k}: `{esc(v)}`' for k,v in docs.items())
inject_block = f'\nwindow.__SECDOCS__ = {{\n{entries}\n}};\n'

shell = open('workspace.html.new').read()
# ... replace show() function to use iframe srcdoc from __SECDOCS__ ...
# ... inject __SECDOCS__ before `const NAV=` ...
open('workspace-all.html','w').write(shell)
```

**CRITICAL:** `</script>` MUST be escaped to `<\/script>` to prevent parent script termination.

---

## Known Quirks / Bug Fixes from Prior Build

1. `<span>` with width/height but no `display:inline-block` didn't render — fix with `inline-block` + `vertical-align`
2. Init IIFE running after `show('overview')` caused KPI to show 0% on first load — reorder so `__PROGRESS__` computed before first render
3. Initial blank-screen bug from `</script>` in srcdoc content — fixed by escaping
4. Command palette: **must be docked in sidebar, NOT modal**. Modals clip inside iframes. We already migrated.
5. Each iframe section has its own scope. Cross-section communication via `parent.postMessage({type, ...})`.
6. Emoji in Python-generated JS: use actual unicode characters, not `\u` escapes (caused surrogate encoding errors).

---

## My Preferences (learned)

- Make it make sense proactively if something doesn't
- OK iterating on styling later; prioritize features
- Don't over-caveat — just build
- Prefer extending patterns over novel solutions
- Each feature that gets added to one section should be considered for all similar sections
- Prefer `postMessage` patterns and shared utilities over duplicated code per section

---

## My Info

- Name: Matt Isgur
- Email: `misgur@adrm-security.com`
- Company: ADRM Security (security integrator)
- Webhook URL pattern: `https://hook.us1.make.com/...`

---

## PENDING Work (prioritized)

### Next major work (best suited for fresh conversation)

1. **Wizard → Make wiring** — wire the existing 4-step New Project wizard to a real webhook. Handle loading/error/success states, navigate to new project. Currently stubs with `alert()`.

2. **Swap mock data for `{{json_payload}}` ingestion** — each section currently has hardcoded demo arrays. Replace with Glide payload reads.

3. **Build Make scenarios (~10 total)** — consistent PATCH pattern per tracker write path.

4. **Row ownership + access filters** on retained Glide tables.

5. **Mobile responsive layout** — sidebar collapses to hamburger, drawers become full-screen sheets, touch-friendly targets.

### Smaller polish items

6. **More cross-section deep links** — Punch origin → Task, RFI origin → Risk, Meeting decision → Task (infrastructure is built, just need to wire the blue breadcrumb pills to postMessage).

7. **Saved Views** — user-defined filter presets per section, persisted.

8. **Dark/light mode toggle** (currently dark only).

---

## Recommended Pickup Prompt

> I'm continuing work on Defender, a security project management app built as a Glide embed with Make.com backend. I've been building the UI with Claude over several sessions. Attached is `workspace-all.html` — the complete bundled workspace. Also attached is `DEFENDER-HANDOFF.md` — comprehensive context on architecture, patterns, aesthetic rules, pending work, and my preferences.
>
> Please read the handoff doc first. Then I want to work on: **[INSERT NEXT TASK]**.
>
> When editing: extract the section file from `window.__SECDOCS__` in the bundle, modify it, then rebundle using the pipeline described in the handoff.

---

## State as of this handoff

- **Bundle size:** ~515KB
- **Sections:** 19
- **All core PM features shipped**
- **Ready for production wiring**

This is a genuinely complete enterprise-grade PM app UI. Next chapter is wiring it to live data.
