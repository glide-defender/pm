# Project constraints

- Background is #171717. No purple. No gradients. No confetti. No animations beyond minimal slide-ins.
- Workspace is bundled: edit `workspace.html` (shell) and `sections/section-*.html` individually, then run `python3 bundle.py` to produce `workspace-all.html`.
- Do not edit `workspace-all.html` directly — it is a build artifact.
- Glide injects `{{json_payload}}`, `{{loggedin_user_email}}`, `{{loggedin_user_name}}` into the workspace at render time.
- Backend is Make.com. Agent writes go through Make webhooks, never direct to Glide from the browser.
- After any change, run `python3 bundle.py` and confirm it exits 0 before declaring done.
