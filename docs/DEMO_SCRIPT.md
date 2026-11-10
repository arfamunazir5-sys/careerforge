# CareerForge demo script

Two versions: a **3-minute core demo** and a **5-minute extended demo** that adds the optional segments. Rehearse the core one until it fits in 3 minutes.

## Demo data (use exactly this so the numbers are repeatable)

- Role: **Backend Developer**, hours: **15**
- Resume text to paste (or save as a PDF and upload):

  ```
  Education Experience Projects Skills Python Flask SQL Git Built and developed REST APIs and improved test coverage
  ```

- Leave GitHub and the self-assessment empty in the core demo (a live GitHub scan depends on rate limits and on your real repositories).

Reference numbers for this data (from the rehearsal run; replace with your own after rehearsing):

| Step | Expected |
| --- | --- |
| After the profile is saved | Resume 73, Career Health 59, Biggest Opportunity: Networking |
| Hours for 15h | Skill Building 6, Networking 3, Portfolio 3, Interview Prep 3 |
| Resume findings | Missing: fastapi, docker. Action words not used: led, designed, implemented, optimized, achieved |
| After completing both Portfolio tasks | Portfolio 50 to 56 (+6). Share of your week: Portfolio 22.7% to 15.8%, Skill Building 37.6% to 44.2% |
| After "Generate New Plan" | Skill Building 6 to 7 hours, Portfolio 3 to 2 hours, with the note "Portfolio improved (50 -> 56), so it needed less time." |

My rehearsed numbers: Portfolio ____ to ____, hours before ____ after ____, total time ____ min ____ s

## 10 minutes before

Follow docs/PRE_DEMO_CHECKLIST.md. The short version: run `python backend\scripts\smoke_test.py`, check it says 17/17, and open the app on a fresh reset (the blue "sample data" banner should be showing).

## The 3 minutes

**0:00 - 0:20, the idea.**
"Career advice usually treats every activity as equally important. CareerForge treats it as a resource-allocation problem: four agents compete for your limited weekly hours, and the plan adapts as you make progress."

**0:20 - 1:00, Profile.**
Pick Backend Developer, set 15 hours, paste the resume (or choose the PDF), click "Analyze Me & Build My Plan". While the steps tick: "This is real input. The resume analysis gives a score, and that score feeds the agents' bids."

**1:00 - 1:50, Command Center (opens automatically).**
- Career Health ring and the Biggest Opportunity card.
- Profile analysis: "It tells me exactly what my resume is missing for this role: fastapi and docker."
- Allocation: "Bid strength is how strongly each agent argued. The share of the week is that bid times the role weight, divided across all four agents."
- "Why this week's allocation": one plain-language reason per agent.

**1:50 - 2:20, Weekly Plan.**
Open one task's "Why this task?". Then mark **both Portfolio tasks** Done. "Completing work raises that domain's score."

**2:20 - 2:50, Adaptation.**
Click "Generate New Plan", then open the Command Center. In Adaptation: Portfolio 50 to 56, the share shift, and the hours shift: "Portfolio improved, so it needed less time. The hour went to Skill Building. Nothing is shown unless something really changed, so there are no invented numbers."

**2:50 - 3:00, close.**
"One connected system: profile, analysis, agents, coordinator, plan, feedback and adaptation. Thank you."

## Optional segments (extended demo, about 20 to 30 seconds each)

- **Self-assessment:** open Assessment, answer the quiz and save. "The interview and networking scores now come from the user, not from sample data."
- **Learning from follow-through:** ignore a Networking task and show the "What CareerForge has learned" card: "If a user keeps skipping an area, that agent gets a smaller share, never below 70%, so the plan stays realistic."
- **Weekly check-in:** open the check-in from the Weekly Plan, close the week and show Week 2 with a fresh plan and the log of past weeks.
- **Another kind of role:** on the Profile, choose UI/UX Designer. "GitHub does not apply to a designer, so the portfolio is scored from links and case studies, which are self-reported. We say so in the interface."
- **Role simulator:** at the bottom of the Command Center, "the same scores under each of the ten roles; nothing is saved".

## If something goes wrong

- "Waking up the server" banner: say "free hosting wakes on the first request" and wait; it clears by itself.
- A red error card: click "Try again".
- A number differs from the script: say "the numbers depend on the inputs", point to the reason text, and carry on.
- Server dead: play the backup recording.
- Never edit code on stage.

## Likely questions

- **Where is the AI?** Four autonomous agents bid using their own state-driven logic, and a coordinator resolves the competition. It is deliberately rule-based, with no model or LLM, so every decision can be explained. That is why the dashboard shows the reasons, and the adaptation comes from updating real scores, the skill roadmap and the user's follow-through.
- **Is it learning?** Yes, in a small, bounded way: the last 20 completed or ignored tasks per agent give a smoothed follow-through rate that trims the weight of agents whose tasks are ignored, down to 70%. It does not use machine learning.
- **Why does Skill Building often win?** Role weights: it has the largest or joint-largest weight in all ten roles. That is a deliberate role-priority choice, shown in the interface.
- **How does it adapt?** Completing tasks raises that domain's score, which lowers its need and its bid, so hours shift to other domains on the next plan. Small changes show up first as a share of the week, because hours are whole numbers.
- **Are the scores real?** Resume, GitHub and the quiz are computed from what the user gives us. Portfolio evidence and the networking answers are self-reported. Task completion adds 3 points to a domain score, which measures activity, not proven skill.
- **How do you handle roles without GitHub?** A different evidence model: links, case studies and a checklist, scored out of 100. Links are checked for format and platform, and never opened.
- **Is it multi-user?** No. State is one shared JSON store, so everyone with the link sees the same data. Accounts need a durable database, which the free hosting does not give us, so it is listed as future work.
- **Why file storage?** It is simple and easy to inspect for a final-year project, with the trade-off that the free host can reset it.
- **What if GitHub is rate limited?** The scan fails with a clear message and never overwrites the stored score, and the rest of the profile still saves.