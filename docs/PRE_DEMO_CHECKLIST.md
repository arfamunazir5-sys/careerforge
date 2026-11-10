# Pre-demo checklist

## The day before

- [ ] `git status` is clean on main (only `mock_state.json` may differ) and `git log -1` matches what is deployed.
- [ ] Vercel shows the latest deployment as Ready, and Render shows the backend Live.
- [ ] Run `python backend\scripts\smoke_test.py` and check it ends with `17/17 steps passed`. (It resets the app twice, so only run it when you do not need the current state.)
- [ ] Run one full timed rehearsal of the 3-minute demo on the LIVE site, following docs/DEMO_SCRIPT.md, and write your numbers in it.
- [ ] Rehearse the "Likely questions" out loud, at least the first five.
- [ ] Record a backup screen capture of a successful run (Win+G, then Record).
- [ ] Capture or refresh the screenshots in docs/screenshots if the interface changed.
- [ ] Charge the laptop, and note a phone hotspot as a network backup.

## 10 minutes before

- [ ] `python backend\scripts\demo_reset.py` (wakes Render, then resets to baseline).
- [ ] `python backend\scripts\smoke_test.py`, expect `17/17 steps passed`. It also leaves the app in a clean state.
- [ ] Open https://careerforge-five-tau.vercel.app/ in a normal window. You should see the nav, no "Waking up" banner, the blue "sample data" banner and "No plan yet".
- [ ] Have the demo resume text (or the PDF) and, if you will use it, your GitHub username ready.
- [ ] Close extra tabs and notifications. Zoom the browser to 110% so it reads on a projector.
- [ ] Open /dashboard-classic in a spare tab as a fallback.

## If something breaks live

- "Waking up the server" banner: wait, it clears itself.
- Red error card: click Try again.
- Server dead: play the backup recording.
- Never edit code on stage. Fix after, on a branch.

## After

- [ ] `python backend\scripts\demo_reset.py` to restore the baseline.