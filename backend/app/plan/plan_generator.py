from typing import List
from app.state.schemas import StateVector
from app.agents.schemas import Allocation
from app.plan.schemas import Task, WeeklyPlan

TASK_TEMPLATES = {
    "skill_building": [
        "Complete a tutorial/module on {next_skill}",
        "Build a small practice exercise using {next_skill}",
        "Read documentation and take notes on {next_skill}",
    ],
    "networking": [
        "Send personalized connection requests to 3 people in your target field",
        "Comment thoughtfully on 5 posts from professionals in your field",
        "Have one informational chat/call with someone in your target role",
    ],
    "portfolio": [
        "Write or improve the README for your strongest GitHub project",
        "Push at least 3 meaningful commits to an active project",
        "Deploy a project demo so it's live and shareable",
    ],
    "interview_prep": [
        "Solve 2 coding/DSA practice problems",
        "Do one mock interview question out loud, timed",
        "Review and refine your answers to 2 common interview questions",
    ],
}


def _split_into_tasks(agent: str, hours: int, next_skill: str) -> List[dict]:
    """Breaks an agent's allocated hours into ~2-hour task chunks,
    cycling through that agent's templates."""
    if hours <= 0:
        return []
    templates = TASK_TEMPLATES[agent]
    tasks = []
    remaining = hours
    i = 0
    while remaining > 0:
        chunk = min(2, remaining)
        title = templates[i % len(templates)].format(next_skill=next_skill)
        tasks.append({"agent": agent, "title": title, "hours": chunk})
        remaining -= chunk
        i += 1
    return tasks


def generate_plan(state: StateVector, allocation: Allocation) -> WeeklyPlan:
    all_tasks = []
    task_counter = 1
    for agent_allocation in allocation.allocations:
        raw_tasks = _split_into_tasks(
            agent_allocation.agent,
            agent_allocation.hours,
            state.skill_progress.next_skill,
        )
        for t in raw_tasks:
            all_tasks.append(
                Task(
                    id=f"t{task_counter}",
                    agent=t["agent"],
                    title=t["title"],
                    hours=t["hours"],
                    status="pending",
                )
            )
            task_counter += 1

    return WeeklyPlan(week_number=state.week_number, tasks=all_tasks)