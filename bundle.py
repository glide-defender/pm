#!/usr/bin/env python3
"""
Local bundler for the workspace.

Usage:  python bundle.py
Reads:  ./workspace.html            (shell)
        ./sections/section-<key>.html  (19 files)
Writes: ./workspace-all.html

Uses base64 encoding for section HTML to avoid template literal escape
issues (no worries about backticks, ${}, </script>, octal escapes, etc.).
The shell decodes with atob() at runtime when loading iframe srcdocs.
"""
import pathlib, sys, re, base64

ROOT = pathlib.Path(__file__).parent.resolve()
SHELL = ROOT / "workspace.html"
SECTIONS_DIR = ROOT / "sections"
OUT = ROOT / "workspace-all.html"

SECTION_KEYS = [
    "risks","observations","punch","materials","rfi","raci","actions",
    "schedule","deployment","finance","contacts","activity","files",
    "time","assets","meetings","audit","mywork","scorecards",
]

def main() -> int:
    if not SHELL.exists():
        print(f"ERROR: missing {SHELL}", file=sys.stderr); return 1
    missing = [k for k in SECTION_KEYS
               if not (SECTIONS_DIR / f"section-{k}.html").exists()]
    if missing:
        print(f"ERROR: missing section files: {missing}", file=sys.stderr)
        return 1

    shell = SHELL.read_text(encoding="utf-8")

    # Build __SECDOCS__ with base64-encoded values. No escape worries.
    parts = ["window.__SECDOCS_B64__ = {"]
    for k in SECTION_KEYS:
        raw = (SECTIONS_DIR / f"section-{k}.html").read_text(encoding="utf-8")
        encoded = base64.b64encode(raw.encode("utf-8")).decode("ascii")
        parts.append(f'  {k}: "{encoded}",')
    parts.append("};")
    # Helper: decode base64 to UTF-8 string. Handles multi-byte chars correctly.
    parts.append("""
window.__SECDOCS__ = new Proxy({}, {
  get(_, key) {
    const b64 = window.__SECDOCS_B64__[key];
    if (!b64) return undefined;
    // decode base64 → bytes → UTF-8 string (handles emoji, etc.)
    const bin = atob(b64);
    const bytes = new Uint8Array(bin.length);
    for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
    return new TextDecoder('utf-8').decode(bytes);
  },
  has(_, key) { return key in window.__SECDOCS_B64__; }
});
""")
    secdocs_block = "\n".join(parts)

    # Inject right before `const NAV=` (anchor in the shell).
    anchor_re = re.compile(r'(?=^const NAV=)', re.MULTILINE)
    if not anchor_re.search(shell):
        print("ERROR: could not find `const NAV=` anchor in shell",
              file=sys.stderr); return 1
    bundled = anchor_re.sub(secdocs_block + "\n\n", shell, count=1)

    OUT.write_text(bundled, encoding="utf-8")
    print(f"wrote {OUT}  ({len(bundled):,} chars, {len(SECTION_KEYS)} sections)")
    return 0

if __name__ == "__main__":
    sys.exit(main())
