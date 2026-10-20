# Pre-demo checklist

## The day before
- [ ] `git status` is clean on main (only `mock_state.json` may differ) and `git log -1` matches what is deployed.
- [ ] Vercel shows the latest deployment as Ready, and Render shows the backend Live.
- [ ] Run one full rehearsal on the LIVE site: Profile -> Command Center -> Weekly Plan -> mark tasks -> Generate New Plan -> Adaptation card.
- [ ] Time the rehearsal (target 3 minutes). Write your rehearsed numbers in docs/DEMO_SCRIPT.md.
- [ ] Record a backup screen capture of a successful run (Win+G, then Record).
- [ ] Charge the laptop, and note a phone hotspot as a network backup.

## 10 minutes before
- [ ] `python backend\scripts\demo_reset.py` (wakes Render, then resets to baseline). Note whether a plan still exists.
- [ ] Open https://careerforge-five-tau.vercel.app/ in a normal window and confirm the nav loads with no banner.
- [ ] If a plan still exists after reset, click "Generate New Plan" once now.
- [ ] Open your resume text and GitHub username in Notepad, ready to paste.
- [ ] Close extra tabs and notifications. Zoom the browser to 110% so it reads on a projector.
- [ ] Open /dashboard-classic in a spare tab as a fallback.

## If something breaks live
- "Waking up the server" banner: wait, it clears itself.
- Red error card: click Try again.
- Server dead: play the backup recording.
- Never edit code on stage. Fix after, on a branch.

## After
- [ ] `python backend\scripts\demo_reset.py` to restore the baseline.