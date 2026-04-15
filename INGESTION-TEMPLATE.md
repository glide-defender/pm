# Defender — Ingestion IIFE Template

Apply this to all 19 sections. Goal: read `window.__PAYLOAD__` when present, fall back to hardcoded demo data when absent or malformed. No big-bang migration — ship ingestion everywhere, flip on live data by populating the Glide template column.

---

## The Template

Inject at the **top of the `<script>` block**, immediately after `<script>` opens and before any other declarations. This runs before the section's existing mock data gets assigned, so ingestion can overwrite it.

```js
// ═══ PAYLOAD INGESTION ═══
// Reads window.__PAYLOAD__ if present, maps into section's variables.
// Falls through to hardcoded demo data on empty/malformed payload.
// Logs boot warning so devtools shows which sections are live.
(function ingestPayload(){
  try {
    const P = window.__PAYLOAD__;
    if (!P) return; // no payload → keep demo data

    // Version check — warn only, never hard-fail
    const expectedVersion = 1;
    const actualVersion = P?.meta?.payload_version;
    if (actualVersion != null && actualVersion !== expectedVersion) {
      console.warn(`[${SECTION_NAME}] payload v${expectedVersion} expected, got v${actualVersion} — rendering best-effort`);
    }

    // ─── SECTION-SPECIFIC MAPPING GOES HERE ───
    // Use optional chaining with defensive defaults.
    // Only overwrite section variables if the payload path exists and has data.

    console.warn('Payload ingestion active:', SECTION_NAME);
  } catch (err) {
    console.warn(`[${SECTION_NAME}] payload ingestion failed, falling back to demo data:`, err);
  }
})();
```

Replace `SECTION_NAME` (in 3 places) with the section's own string identifier: `'tasks'`, `'risks'`, `'punch'`, etc.

---

## Per-Section Mappings

Drop the right lines into the `SECTION-SPECIFIC MAPPING GOES HERE` block for each file. Note: per **Pattern #6** below, sections with consolidated JSON counterparts must read from either the top-level path or the `*Json` path.

| File | Variable(s) to overwrite | Payload path(s) |
|---|---|---|
| `section-actions.html` | `items`, `MS` | `P.tasks`, `P.milestones` |
| `section-schedule.html` | `milestones` (tree + gantt) | `P.milestones` |
| `section-punch.html` | `items` | `P.punch_list` ‖ `P.punchListJson` |
| `section-observations.html` | `obs` | `P.observations` ‖ `P.observationsJson` |
| `section-risks.html` | `items` | `P.risks` ‖ `P.riskTrackerJson` |
| `section-rfi.html` | `items` | `P.rfi` ‖ `P.rfiJson` |
| `section-raci.html` | RACI matrix data | `P.raci` ‖ `P.raciJson` |
| `section-materials.html` | `items` | `P.materials` ‖ `P.materialTrackerJson` |
| `section-deployment.html` | templates + items | `P.deployment_templates`, `P.deployment_items` |
| `section-assets.html` | `deployed`, `INVENTORY` | `P.deployed_assets`, `P.lookups.inventory` |
| `section-finance.html` | `items` | `P.finance_line_items` |
| `section-contacts.html` | `contacts` | `P.contacts` |
| `section-meetings.html` | `meetings` | `P.meetings` |
| `section-time.html` | `entries` | `P.time_entries` |
| `section-files.html` | file tree + `__links` | `P.files`, `P.links` |
| `section-activity.html` | feed | `P.activity` |
| `section-audit.html` | log | `P.audit_log` |
| `section-scorecards.html` | `dimensions` | `P.scorecards.dimensions`, `P.project.health_weights` |
| `section-mywork.html` | filtered views across domains | `P.tasks`, `P.risks`, `P.punch_list` ‖ `P.punchListJson`, `P.time_entries` — filter where `owner_email === P.loggedin_user_email` |

---

## Shell-Level Updates (workspace.html)

### 1. @-mention ordering in `window.__wireMention`

Priority: `P.contacts[]` first (project-scoped), then `P.lookups.all_contacts` as fallback, de-duplicated.

```js
const projectContacts = (window.__PAYLOAD__?.contacts || []).map(c => c.name);
const allContacts = (window.__PAYLOAD__?.lookups?.all_contacts || []).map(c => c.name);
const ordered = [...new Set([...projectContacts, ...allContacts])];
// use `ordered` instead of the hardcoded window.__CONTACTS__ default when payload is present
```

### 2. `computeProgress()` reads `health_weights`

```js
const weights = window.__PAYLOAD__?.project?.health_weights || {
  schedule: 20, deployment: 15, materials: 25, punch: 20, observations: 10, risks: 10
};
// Validate sum ≈ 100; if not, apply defaults and console.warn
```

### 3. Session fields at boot

```js
window.__USER__ = {
  email: window.__PAYLOAD__?.loggedin_user_email || 'demo@adrm-security.com',
  name: window.__PAYLOAD__?.loggedin_user_name || 'Demo User',
  role: window.__PAYLOAD__?.loggedin_user_role || 'PM'
};
```

### 4. Footer last-updated timestamp

```js
const lu = window.__PAYLOAD__?.meta?.last_updated;
if (lu) document.getElementById('footer-updated').textContent = `Last updated ${new Date(lu).toLocaleString()}`;
```

---

## Defensive Principles (apply everywhere)

1. **Optional chaining with defaults** — every payload read uses `?.` and has a fallback, never assumes a field exists.
2. **Try/catch at the ingestion boundary** — one bad field shouldn't blank the section. Log loudly, fall through to demo.
3. **Warn, never throw** — `payload_version` mismatch, malformed arrays, missing user session — all warn to console, never crash the render.
4. **Only overwrite on presence** — `if (P.tasks?.length) items = P.tasks;` — empty arrays from the payload shouldn't wipe demo data (lets you test live ingestion on a freshly-created project without a black screen).

---

## Locked Patterns (apply to every section)

These patterns were established across earlier sections in the ingestion pass. Every subsequent section must follow them.

### Pattern #1 — Normalize-in / emit-out

Internal section variables keep whatever shape the existing UI code uses. **Inbound:** map schema → internal at the ingestion boundary. **Outbound:** map internal → schema at every save / bulk / convert / delete handler. UI code in between never touches schema fields directly. This isolates the schema contract from the UI and means any schema field rename only touches the ingestion + outbound boundaries, never the rendering code.

### Pattern #2 — String IDs are default

Glide IDs are strings (`"MS-01"`, `"TSK-104"`, `"OB-03"`, `"PL-07"`, `"CON-01"`). Never use `+value` coercion or `Math.max(...ids)` — both break on strings. Use `String(a) === String(b)` for comparisons. New client-side IDs use `tmp-${Date.now()}-${idx}` until the Make scenario returns the real one. Use `JSON.stringify` when embedding IDs in inline `onclick` handlers so quoting works for both string and numeric IDs.

### Pattern #3 — `esc()` on all interpolated payload strings

Add an `esc()` helper and apply to every `${...}` interpolation of a payload-derived string (titles, names, notes, status values, contact names, locations, severities, etc.). Prevents broken rendering when payload data contains HTML-significant characters and prevents XSS.

### Pattern #4 — `owner_email` / `assignee_email` pass-through

Every entity with an owner or assignee must expose the email in its internal shape so cross-cutting features (My Work filtering, @-mentions, notifications) can find them. Never let display-name-only be the indicator. Seed it on demo data too so cross-section flows work in dev.

### Pattern #5 — Node smoke tests on hot paths

Each section ships with smoke tests (exposed as `window.__<SECTION>_SMOKE__()`). **jsdom-backed coverage is strongly preferred over plain Node** for sections with meaningful interactivity — RACI's 92-test jsdom battery and Contacts' 94-test battery proved the quality delta over plain Node by catching subtle bugs (e.g. rename-migrates-selection) that were invisible to logic-only tests. See the **Smoke test coverage** checklist below for required cases.

### Pattern #6 — Consolidated JSON fallback

Sections with consolidated counterparts per the architecture must read from either top-level or the `*Json` field:

- `punch` ← `P.punch_list` or `P.punchListJson`
- `observations` ← `P.observations` or `P.observationsJson`
- `risks` ← `P.risks` or `P.riskTrackerJson`
- `rfi` ← `P.rfi` or `P.rfiJson`
- `materials` ← `P.materials` or `P.materialTrackerJson`
- `raci` ← `P.raci` or `P.raciJson`

Pattern: try top-level first, fall back to `*Json` if absent. The consolidated field is what production Glide will populate — the top-level form is a convenience for testing. Relational sections (Contacts, Finance, Meetings, Time, etc.) do NOT have a `*Json` variant — Pattern #6 is N/A for those.

### Pattern #7 — Render-or-expose schema fields

If `PAYLOAD-SCHEMA.md` specifies a field the UI doesn't currently render, **add the column or drawer field rather than silently dropping it.** Severity and due-date on punch would have been lost without this rule. Slightly busier UI is better than data loss. If a field genuinely doesn't fit the UX, surface it in the drawer at minimum.

### Pattern #8 — Field casing matches PAYLOAD-SCHEMA.md exactly

Most schema fields are snake_case (`owner_email`, `milestone_id`, `assignee_email`, `percent_complete`, `duration_days`, `observed_by`, `observed_at`, `asked_by`, `answered_at`, `qty_ordered`, `is_internal`, etc.) **but `originFrom` / `originId` are camelCase outliers** in every entity that supports cross-entity conversion (tasks, punchListJson, riskTrackerJson, observationsJson, rfiJson).

Read `PAYLOAD-SCHEMA.md` before emitting any outbound field name. Never guess. Never normalize across cases. The casing rule applies to every outbound payload — saves, bulk operations, conversions, deletes.

### Pattern #9 — Bridge-not-collapse for schema↔internal shape mismatches

When the UI's internal representation differs from the schema (e.g. 5-point UI scale vs 3-point schema scale), or when the UI computes a value that the schema also stores explicitly, use **bidirectional bridge functions** plus **dirty-flag preservation**.

Bridge functions (e.g. `SCHEMA_TO_INTERNAL`, `INTERNAL_TO_SCHEMA`) translate at the ingest/emit boundaries — never mutate the internal shape to match the schema or vice-versa.

Dirty-flag preservation (e.g. `__scoreDirty`, `__statusDirty`) tracks whether the user has explicitly overridden a computed value. Outbound payload emits the schema's stored value verbatim if the user hasn't touched the relevant inputs; only recomputes when the dirty flag is set. This means a save with no real edit roundtrips byte-identically — critical for "did anything actually change" diff logic in Make scenarios.

**Reference implementations:**
- `section-risks.html` — `SCHEMA_TO_SCALE` / `SCALE_TO_SCHEMA` for likelihood-impact, plus `__scoreDirty` for `score` preservation
- `section-materials.html` — `SCHEMA_TO_DISPLAY` / `computeSchemaStatus` plus `__statusDirty` for `Installed` status preservation

Most relevant upcoming candidates: Scorecards (composite vs dimension scores), Schedule (rolled-up `percent_complete` vs manual `percent_manual` override on milestones).

---

## Per-Section Audit Checklist

Every section ingestion pass must verify all items below pass before shipping. **"Pass" means the behavior works in the bundled app, not just that the code looks right.** If an item is genuinely N/A for a structurally-unique section (e.g. RACI matrix, Files explorer, Activity feed), flag why explicitly in the before/after table.

### Data flow
- [ ] Defensive guards on every payload read (optional chaining, defaults, try/catch)
- [ ] Consolidated JSON fallback working (both top-level and `*Json` paths ingest identically)
- [ ] Outbound save handler emits schema shape
- [ ] Bulk handlers emit schema shape (if bulk applies)
- [ ] Convert-to-X handler emits schema shape with correct origin casing (if conversion applies)

### Pattern-specific verifications
- [ ] Pattern #1 — `buildSavePayload()` is the single outbound boundary
- [ ] Pattern #2 — String IDs throughout, no numeric coercion, no `Math.max(...ids)`
- [ ] Pattern #3 — `esc()` on every interpolated payload string
- [ ] Pattern #4 — `owner_email` / `assignee_email` pass-through (or flag as schema gap if schema lacks one)
- [ ] Pattern #5 — Node/jsdom smoke tests present and all green
- [ ] Pattern #6 — Consolidated JSON fallback (if applicable)
- [ ] Pattern #7 — All schema fields rendered in UI (no silent drops)
- [ ] Pattern #8 — Field casing matches `PAYLOAD-SCHEMA.md` verbatim
- [ ] Pattern #9 — Bridge logic for schema↔UI shape mismatches (if applicable)

### UI integration (verify in-browser, not just code)

These are the items most often missed when focus stays on payload logic. **Verify each by actually loading the bundle and using the section.**

- [ ] **Bulk select checkboxes render on each row** — hover a row, checkbox visible on the left, clicking it selects the row. If your section has bulk actions in the code but the checkboxes aren't rendering, the UI is incomplete — fix it.
- [ ] **Bulk action bar appears when 1+ rows selected** — counter shows "N selected", Mark Closed / Delete / Cancel buttons visible, buttons trigger expected handlers
- [ ] **Select-all control** — header-level toggle (always visible, next to filters) + mirror in bulk bar once active. Three states: none / some (indeterminate) / all-visible-selected, with appropriate icons and dynamic label ("Select all (N)" vs "Deselect all"). **Must scope to `filtered()` not the full dataset** — selecting "all" while filtered must only select visible rows, and the label count reflects visible rows only. Disabled state (50% opacity, unclickable) when filter/search returns empty. Reference implementation: `section-contacts.html`.
- [ ] **Bulk select handles string IDs** — selecting rows with IDs like `"RK-01"`, running bulk action, and Cancel-clearing all work correctly
- [ ] **Row menu (⋯)** opens and all menu items work (Update, Convert, Delete, etc.)
- [ ] **Drawer opens, saves, and closes** without errors
- [ ] **Origin breadcrumb pill renders** when `originFrom` is present in ingested data (if applicable)
- [ ] **Cross-section deep links** functional — click the origin breadcrumb pill, verify it posts `navigate` message to shell
- [ ] **@-mention autocomplete** orders project contacts first, then account-wide
- [ ] **Status filter / search dropdown** applies correctly to post-ingestion data (not just demo)
- [ ] **Empty state** renders correctly (no items after filter → correct "No items" message, correct `colspan`)
- [ ] **Rename-migrates-selection** — if a row is selected and then renamed in the drawer, the selection set updates to the new identifier (does not orphan). Only applies to sections where the selection key is a mutable field (e.g. RACI keys on `workstream` name). String-ID-keyed sections are immune.

### Regression check
- [ ] All existing features work without payload (demo mode)
- [ ] All existing features work with payload (live mode)
- [ ] No console errors in either mode
- [ ] Section renders identically when switching between top-level and `*Json` payload paths

### Smoke test coverage (`window.__<SECTION>_SMOKE__()`)

Minimum cases for every section:
1. No payload (`window.__PAYLOAD__ = null`)
2. Missing payload (`window.__PAYLOAD__` undefined)
3. Malformed payload (e.g. `items: "not an array"`)
4. Valid schema-shape payload
5. Version mismatch (`meta.payload_version: 99`)
6. Consolidated JSON alias (if applicable per Pattern #6)
7. Outbound builder shape matches schema
8. Round-trip stability (ingest → save → re-ingest identical)
9. String-ID safety (IDs like `"OB-03"` flow through filter/find/save without coercion)

Plus section-specific cases:
- **Conversion flows:** test the converted entity outbound shape (e.g. observation → risk, rfi → risk, punch → task, meeting decision → task)
- **Pattern #9 bridge:** test schema-value preservation until dirty flag tripped
- **Multi-origin:** dual-origin roundtrip (one from each possible source entity)
- **UI-only field exclusion:** assert internal-only fields are not present in outbound payload
- **Rename-migrates-selection:** if section has bulk selection + mutable identifier, test that rename updates selection set

**jsdom coverage strongly preferred** for sections with meaningful interactivity (bulk selection, drawer state, rename flows, XSS invariants, deep-link receiver). Plain Node tests are acceptable for simpler read/transform-only sections (Activity, Audit Log). Reference jsdom test batteries: `section-raci.html` (92 cases), `section-contacts.html` (94 cases).

All tests must pass before the section ships.

---

## Mid-Pass Handoff Protocol

If you hit tool/context limits mid-section, **do not ship a file you couldn't verify end-to-end.** Instead:

1. **Write a detailed handoff note** describing:
   - What you built (feature list + file location if it persists)
   - What tests you wrote and which passed
   - What design decisions you made and why
   - Schema gaps you surfaced
   - What's left: verification, smoke test execution, `present_files` emission
2. **Explicitly note** that the sandbox file may not persist to the next chat, and that a fresh chat should re-execute from your handoff notes (design is locked, rebuild from spec) rather than redesigning from scratch.
3. Matt's pattern: start a new chat in the Defender Project with the handoff note as the prompt, the original pre-ingestion section file as the attachment, and an explicit instruction: "design is locked, re-execute from this handoff, don't redesign."

This is a feature, not a failure. Honest stops + detailed handoffs produce better outcomes than pressing through a context squeeze and shipping unverified code.

---

## Mechanical Pass Workflow

For each of the 19 section files:

1. Open the section file from `~/Documents/defender_projects_html_v2/sections/`.
2. Find the `<script>` opening tag.
3. Inject the ingestion IIFE at the appropriate location (typically post-declaration, pre-render — see notes below).
4. Fill in `SECTION_NAME` (3 places).
5. Add section-specific mapping lines from the table above, including consolidated JSON fallback per Pattern #6 where applicable.
6. Apply all 9 locked patterns.
7. Run the full Per-Section Audit Checklist above. Every item must pass or be flagged N/A with a reason.
8. Run smoke tests (Pattern #5) — jsdom-backed where interactivity warrants, plain Node otherwise. All green before shipping.
9. Save.

Then apply the four shell updates to `workspace.html` (only needed once, not per section).

Rebundle using `python3 bundle.py`. The bundler uses base64 encoding so escape concerns (template literals, `</script>`, octal escapes) don't apply at the bundling layer — but section files themselves should still be clean HTML.

### IIFE placement note

The template says "top of the `<script>` block" but in practice that hits the temporal dead zone when sections use `let`/`const` declarations for their data variables. **Place the IIFE post-declaration but pre-render** — typically right before the first `renderAll()` call. Same net effect: payload overwrites demo before paint.

For `const` data references (e.g. `const MS = [...]`), use in-place mutation: `MS.length = 0; MS.push(...newItems);` rather than reassignment.

---

## Browser Smoke Test (after rebundling)

After rebundling, open `http://localhost:8000/workspace-all.html` and run through these scenarios:

1. With no payload injected — console should be clean (no "Payload ingestion active" warnings), all sections render demo data normally.
2. Inject a test payload via devtools: `window.__PAYLOAD__ = {...}` then reload — console should show "Payload ingestion active" warnings (one per section as it boots in its iframe), sections display payload data.
3. Inject a payload with `meta.payload_version: 99` — console shows version mismatch warnings, rendering continues best-effort.
4. Inject a payload with a malformed field (e.g. `tasks: "not an array"`) — console shows ingestion-failed warning for that section only, others continue working.
5. For sections with consolidated JSON: test both `P.<top_level>` and `P.<*Json>` paths — both should produce identical rendering.
6. For sections with cross-entity conversion: trigger a conversion and verify the outbound payload uses correct casing per Pattern #8 (`originFrom`/`originId` camelCase, everything else snake_case).
7. For sections with bulk actions: verify checkboxes render, select-all works across filter/search changes, bulk action bar shows correct count, delete emits schema-shape payload with correct IDs.

If all seven pass for a given section, that section's ingestion is production-ready.
