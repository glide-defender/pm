# Defender — Post-Ingestion Punchlist

Cross-cutting polish items surfaced during the ingestion pass that are out of scope for a single section but worth tracking. Each entry is an API/UX consistency item that doesn't block any specific deliverable but keeps the app coherent as it grows.

Append-only. When resolved, mark `RESOLVED <date>` in place.

---

## Low priority

### Drawer footer — audit for `side: 'left' | 'right'` button placement

**Surfaced by:** Commissioning (section-deployment.html) drawer conversion.

**Context.** The Commissioning drawer introduced an explicit `side: 'left' | 'right'` flag on footer button definitions. Left-side buttons flush-left, right-side cluster on the right with a spacer between. This lines up with the handoff's drawer-footer pattern ("Cancel/Save right-aligned; conversions flush-left") but makes it declarative per button rather than implicit by position.

```js
// Commissioning pattern
show(title, body, [
  { label: '↻ Sync to Latest', cls: 'btn',    side: 'left', fn: ... },
  { label: 'Cancel',           cls: 'btn',                  fn: close },
  { label: 'Update',           cls: 'btn bp',               fn: ... }
], subtitle);
```

**What to audit.** Other sections with drawers containing auxiliary actions:
- **Observations → Convert to Risk** — should be `side:'left'`
- **Punch → Convert to Task** — should be `side:'left'`
- **RFI → Convert to Risk** — should be `side:'left'`
- **Meetings → decision Convert to Task** — should be `side:'left'`
- **Risks → Delete** (in drawer footer, if present) — should be `side:'left'` per destructive-action convention
- Any other section with a "Regenerate", "Archive", "Duplicate", or similar non-primary non-cancel action

**Proposed resolution.** Lift the `side`-aware `show()` implementation from `section-deployment.html` into each section's drawer infra (or into a shared shell helper if one exists). Default is `'right'` when omitted, so the change is backward-compatible with every existing section's button definitions.

**Priority rationale.** Low. Nothing broken — existing sections place auxiliary buttons correctly by virtue of argument order. This is purely a readability / declarative-intent improvement. Worth batching into a "drawer consistency pass" if one ever happens, not worth a dedicated sweep.

---

## Meta

When a new cross-cutting polish item surfaces:

1. Add under the appropriate priority section (urgent / medium / low).
2. Note **surfaced by** (section name or feature that exposed the inconsistency).
3. Describe the pattern that works vs. what's inconsistent.
4. List the specific sections that need the adjustment.
5. Set priority based on visible impact, not correctness — these are polish items by definition.
