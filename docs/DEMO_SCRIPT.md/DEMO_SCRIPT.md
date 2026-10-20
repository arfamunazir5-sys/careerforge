# CareerForge demo script (3 minutes)

## 10 minutes before

1. Run `python backend\scripts\demo_reset.py` (warms up Render, resets to baseline).
2. Open https://careerforge-five-tau.vercel.app/ and check the nav loads. Use a normal (not private) window.
3. Have ready: your resume text in a Notepad file, and your GitHub username.
4. If the reset output said a plan still exists, click "Generate New Plan" once now.
5. Keep a backup: a short screen recording of a successful run (Win+G, then Record), plus the screenshots in docs/screenshots.
6. Rehearsed numbers (write them here): agent I will complete: ______  hours before: ____  after: ____

## The 3 minutes

**0:00 - 0:20 The idea.**
"Career advice usually treats every activity as equally important. CareerForge treats it as a resource-allocation problem: four agents compete for the user's limited weekly hours, and the plan adapts as they make progress."

**0:20 - 1:00 Profile (Profile page).**
Pick the target role, set hours, paste the resume, enter the GitHub username, click "Analyze Me & Build My Plan". While the steps tick: "This is real input. The resume and GitHub scan produce scores, and those scores feed the agents' bids."

**1:00 - 1:45 Command Center (opens automatically).**
- Career Health Score and the Biggest Opportunity card.
- The allocation card: "Faded bar is what each agent asked for, solid bar is what it got. The coordinator multiplies bids by role weights, so the target role changes who wins."
- "Why this week's allocation": plain-language reasons.

**1:45 - 2:20 Weekly Plan.**
"The allocation became concrete tasks." Mark every task for ONE agent as Done (the one you rehearsed). Point at the progress meter.

**2:20 - 2:50 Adaptation.**
Click "Generate New Plan", then open the Command Center. Show the Adaptation card: scores before and after, and the hours that shifted. "Nothing is shown unless something really changed, so there are no fake numbers."

**2:50 - 3:00 Close.**
"One connected system: profile, analysis, agents, coordinator, plan, feedback, adaptation. Thank you."

## If something goes wrong

- "Waking up the server" banner: say "free hosting wakes on first request" and wait; it clears by itself.
- A red error card: click "Try again".
- Server dead: switch to the backup recording.

## Likely questions

- **Where is the AI?** Four autonomous agents bid using their own state-driven logic, and a coordinator resolves the competition. The bids are transparent formulas so every decision can be explained, which is why the dashboard shows the reasons.
- **Why does Skill Building often win?** Role weights: it has the largest weight in all three roles. That is a deliberate role-priority choice, shown in the dashboard.
- **How does it adapt?** Completing tasks raises that domain's score, which lowers its need and its bid, so hours shift to other domains on the next plan.
- **What happens when a task is ignored?** The streak resets, which removes the Skill Building agent's momentum bonus. Ignores are stored as one counter, not per agent, which is listed as future work.
- **Is it multi-user?** No. State is a single JSON store; accounts and a database are future work.
- **Why file storage?** Fast to build and easy to inspect for a final-year project, with the trade-off that hosting resets it.