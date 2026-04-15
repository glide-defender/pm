# Defender — `{{json_payload}}` Schema (v1 proposal)

One template column on the **Projects** table. Injected as a JSON string; each iframe parses once at init and exposes on `window.__PROJECT__`.

## Top-level shape

```jsonc
{
  // ─── Session / personalization (same pattern as Personnel Dashboard + LawnApp) ───
  "loggedin_user_email": "misgur@adrm-security.com",
  "loggedin_user_name":  "Matt Isgur",
  "loggedin_user_role":  "PM",              // PM | Field | Exec | Client — drives access filters later
  "server_time":         "2026-04-12T19:30:00Z",

  // ─── Project core ───
  "project": {
    "id":          "PRJ-0042",
    "name":        "Acme HQ — Access Control Upgrade",
    "type":        "Upgrade",               // Install | Service | Assessment | Upgrade | Decommission | Maintenance
    "status":      "In Progress",
    "client":      "Acme Corp",
    "site":        "123 Main St, Stamford CT",
    "pm_email":    "misgur@adrm-security.com",
    "start_date":  "2026-03-01",
    "end_date":    "2026-07-15",
    "budget":      285000,
    "contract_value": 312000,

    // Progress engine cache — written back by window.computeProgress() for fast reads
    "progress_cached": {
      "overall": 47,
      "schedule": 52, "deployment": 38, "materials": 60,
      "punch": 20,    "observations": 75, "risks": 40, "rfi": 0,
      "computed_at": "2026-04-12T19:29:00Z"
    }
  },

  // ─── Relational data (kept as arrays, referenced by id) ───

  "milestones": [
    {
      "id": "MS-01", "name": "Design Approval", "phase": "Design",
      "start": "2026-03-01", "end": "2026-03-21",
      "duration_days": 21,                  // progress engine input — DO NOT FLATTEN
      "status": "Complete",
      "percent_manual": null,               // fallback when no action items
      "owner_email": "misgur@adrm-security.com"
    }
  ],

  "tasks": [
    {
      "id": "TSK-104", "title": "Submit shop drawings", "milestone_id": "MS-01",
      "assignee_email": "jcarter@adrm-security.com",
      "start": "2026-03-05", "end": "2026-03-10",
      "duration_days": 5,                   // progress engine input
      "percent_complete": 100,
      "status": "Done",                     // Not Started | In Progress | Blocked | Done
      "priority": "Normal",
      "originFrom": null, "originId": null  // roundtrip for cross-entity breadcrumbs
    }
  ],

  "finance_line_items": [
    { "id": "FIN-01", "category": "Labor", "description": "Install techs wk 1",
      "budgeted": 12000, "committed": 12000, "actual": 11420,
      "vendor": "ADRM", "date": "2026-03-08" }
  ],

  "time_entries": [
    { "id": "TE-221", "user_email": "jcarter@adrm-security.com",
      "task_id": "TSK-104", "date": "2026-03-08",
      "hours": 7.5, "billable": true, "notes": "Shop dwg rev 2" }
  ],

  "contacts": [
    { "id": "CON-12", "name": "Jane Carter", "email": "jcarter@adrm-security.com",
      "company": "ADRM Security", "role": "Lead Tech", "phone": "+1-203-555-0142",
      "is_internal": true }
  ],

  "meetings": [
    {
      "id": "MTG-05", "title": "Weekly OAC",
      "datetime": "2026-04-10T14:00:00Z", "duration_min": 60,
      "attendees": ["misgur@adrm-security.com","client@acme.com"],
      "agenda": "…", "notes": "…",
      "decisions": [
        { "id":"DEC-1", "text":"Move cutover to 4/22",
          "action_task_id":"TSK-118" }    // if converted → Task, id lives here
      ]
    }
  ],

  // ─── Deployment sub-architecture (relational, per handoff §Deployment) ───

  "deployment_templates": [
    {
      "id": "DT-01", "name": "Card Reader — HID Signo",
      "stepsJson": [
        { "id":"S1", "label":"Mount plate", "order":1 },
        { "id":"S2", "label":"Pull cable",  "order":2 },
        { "id":"S3", "label":"Terminate",   "order":3 },
        { "id":"S4", "label":"Commission",  "order":4 }
      ]
    }
  ],

  "deployment_items": [
    {
      "id": "DI-118", "template_id": "DT-01", "template_version_at_snapshot": 3,
      "asset_tag": "CR-LOBBY-01", "location": "Lobby North",
      "steps_snapshot": [                   // snapshot at add-time (per handoff)
        { "id":"S1","label":"Mount plate","order":1 },
        { "id":"S2","label":"Pull cable", "order":2 },
        { "id":"S3","label":"Terminate",  "order":3 },
        { "id":"S4","label":"Commission", "order":4 }
      ],
      "responsesJson": [                    // per-step status
        { "step_id":"S1","status":"Complete","by":"jcarter@adrm-security.com","at":"2026-03-20T15:02:00Z" },
        { "step_id":"S2","status":"Complete","by":"jcarter@adrm-security.com","at":"2026-03-21T11:40:00Z" },
        { "step_id":"S3","status":"In Progress" }
      ],
      "template_has_updates": true          // drives "Sync to Latest" button
    }
  ],

  // ─── Consolidated JSON trackers (live on Projects in Glide as separate cols, nested here) ───

  "punchListJson": [
    { "id":"PL-07","title":"Door 3 strike aligned wrong","severity":"Medium",
      "status":"Open","assignee_email":"jcarter@adrm-security.com","due":"2026-04-25",
      "location":"Corridor B","originFrom":"observation","originId":"OB-03" }
  ],

  "materialTrackerJson": [
    { "id":"MT-14","item":"HID Signo 20","qty_ordered":24,"qty_received":12,
      "vendor":"Anixter","po":"PO-8821","eta":"2026-04-18","status":"Partial" }
  ],

  "observationsJson": [
    { "id":"OB-03","text":"Strike misaligned on D3","severity":"Medium",
      "status":"Resolved","observed_by":"misgur@adrm-security.com",
      "observed_at":"2026-04-05","photo_attachment_ids":["ATT-91"],
      "originFrom":null,"originId":null }
  ],

  "riskTrackerJson": [
    { "id":"RK-02","title":"Long-lead panels","likelihood":"Medium","impact":"High",
      "score":12,"mitigation":"Early PO + alt vendor","owner_email":"misgur@adrm-security.com",
      "status":"Monitoring","originFrom":"rfi","originId":"RFI-04" }
  ],

  "raciJson": [
    { "workstream":"Design","R":["ADRM Security"],"A":["ADRM Security"],
      "C":["Acme IT"],"I":["Acme Security"] }
  ],

  "rfiJson": [
    { "id":"RFI-04","question":"Confirm panel location in IDF-2","asked_by":"misgur@adrm-security.com",
      "asked_at":"2026-04-02","answered_at":null,"answer":null,"status":"Open",
      "originFrom":null,"originId":null }
  ],

  // ─── Comments, attachments, notifications — keyed by `entityType:entityId` per handoff ───

  "comments": {
    "task:TSK-104": [
      { "id":"CM-1","author_email":"misgur@adrm-security.com","at":"2026-03-06T14:20:00Z",
        "text":"@jcarter any update?","mentions":["jcarter@adrm-security.com"] }
    ],
    "risk:RK-02": []
  },

  "attachments": {
    "observation:OB-03": [
      { "id":"ATT-91","filename":"door3_strike.jpg","size":412003,
        "url":"https://.../door3_strike.jpg","content_type":"image/jpeg",
        "uploaded_by":"misgur@adrm-security.com","uploaded_at":"2026-04-05T09:12:00Z" }
    ]
  },

  "notifications": [
    { "id":"N-1","type":"mention","entity":"task:TSK-104",
      "text":"Matt mentioned you","at":"2026-03-06T14:20:00Z","read":false }
    // types: mention | assigned | due | comment | status | overdue
  ],

  // ─── Audit log (relational, append-only, compliance-critical) ───
  // Lives in its own Glide table — NOT a consolidated JSON column. No
  // `auditLogJson` variant exists. Entries are immutable once written;
  // the UI is read-only (no saves, no bulk, no deletes).
  //
  // `actor_email` MUST be preserved verbatim. If an email doesn't resolve
  // to a current contact, the UI renders the email as-is rather than
  // collapsing to "System" — compliance requires attribution fidelity.
  //
  // `before` / `after` are state snapshots of the affected entity. They
  // can be objects (full row snapshot), strings (freeform), or null
  // (Create has no `before`; Delete has no `after`). Preserve byte-
  // identical on ingest and emit — do NOT re-format JSON.
  //
  // `ip_address` / `user_agent` are optional but expected for security-
  // sensitive deployments. The UI surfaces them via an inline ⓘ toggle
  // on each row when present.
  "audit_log": [
    {
      "id":          "AUD-1042",
      "at":          "2026-04-12T14:32:18Z",
      "actor_email": "lfeula@adrm-security.com",
      "action":      "Updated",              // Created | Updated | Deleted (also accepts C/U/D codes)
      "entity":      "Risk",                 // human-readable entity type label
      "entity_id":   "RK-02",                // string ID of the affected row
      "before":      { "status":"Open",   "likelihood":"High",   "score":16 },
      "after":       { "status":"Closed", "likelihood":"Medium", "score":8  },
      "ip_address":  "10.0.1.42",            // optional
      "user_agent":  "Mozilla/5.0 (Macintosh; …) Chrome/124"  // optional
    }
    // Additional legacy/convenience fields accepted by the ingester but
    // NOT canonical on new writes: `ts` (alias for `at`), `user` (alias
    // for actor display name), `field`/`old`/`new` (field-level diff
    // shape — prefer `before`/`after` snapshots for full fidelity).
  ],

  // ─── Lookup tables (static-ish, per handoff shared utilities) ───

  "lookups": {
    "statuses": {
      "task":        ["Not Started","In Progress","Blocked","Done"],
      "punch":       ["Open","In Progress","Ready for Review","Closed"],
      "rfi":         ["Open","Answered","Closed"],
      "risk":        ["Identified","Monitoring","Mitigating","Closed"],
      "observation": ["Open","In Review","Resolved","Dismissed"],
      "material":    ["Ordered","Partial","Received","Installed"],
      "milestone":   ["Not Started","In Progress","Complete","At Risk"]
    },
    "project_types": ["Install","Service","Assessment","Upgrade","Decommission","Maintenance"],
    "all_contacts":  [ /* mirrors contacts[] — powers @-mention autocomplete globally */ ]
  }
}
```

## Ingestion layer (proposed)

Single entry point added to every section iframe's init:

```js
// At top of each section, before any render:
(function ingest(){
  const raw = `{{json_payload}}`;          // Glide injects; unescaped string
  try {
    const P = JSON.parse(raw);
    window.__PROJECT__      = P.project;
    window.__CONTACTS__     = P.contacts || [];
    window.__COMMENTS__     = P.comments || {};
    window.__ATTACHMENTS__  = P.attachments || {};
    window.__NOTIFICATIONS__= P.notifications || [];
    window.__STATUSES__     = (P.lookups && P.lookups.statuses) || {};
    window.__TYPES__        = (P.lookups && P.lookups.project_types) || [];
    window.__PAYLOAD__      = P;            // full blob for section-specific reads
    window.__USER__         = { email: P.loggedin_user_email, name: P.loggedin_user_name, role: P.loggedin_user_role };
  } catch(e){
    console.error('Payload parse failed', e);
    window.__PAYLOAD__ = null;
    // Sections fall back to their existing mock arrays so dev/demo still works
  }
})();
```

Each section then reads its slice:
- Tasks section: `window.__PAYLOAD__.tasks`
- Punch section: `window.__PAYLOAD__.punchListJson`
- etc.

## Fallback behavior

If `{{json_payload}}` is empty or unparseable (dev mode, broken Glide template), the ingestion block silently leaves `window.__PAYLOAD__ = null` and sections use their existing hardcoded demo arrays. This means **the demo bundle keeps working untouched** and live-data switchover is a single `if (window.__PAYLOAD__)` branch per section.

## Open questions before I build

1. **Attachment URLs** — Glide File columns give you a Glide-hosted URL. Good enough, or do you want a separate `attachments` table with S3-backed URLs for portability?
2. **Payload size** — a project with 200 tasks + 50 punch + comments/attachments could push 200KB+. Glide template columns handle this fine but iframe parse cost matters. I'd add a `compact: true` mode later that strips closed/archived items. Flag if you want that now vs later.
3. **Contact list scope** — is `contacts[]` project-scoped (just people on this project) or account-wide (every ADRM contact)? Affects `@-mention` autocomplete UX. I'd argue **account-wide in `lookups.all_contacts`**, project-scoped in `contacts[]` — let me know if you disagree.
