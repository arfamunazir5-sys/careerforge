import json
from app.plan.plan_store import load_plan, save_plan
from app.state.state_builder import get_current_state, MOCK_STATE_PATH
from app.tracker.reward import compute_reward
from app.tracker.reward_log import append_reward


def mark_task(task_id: str, new_status: str) -> dict:
    """new_status is 'done' or 'ignored'. Updates the stored plan,
    computes the reward, and updates completed/ignored/streak counters
    in mock_state.json so next week's state reflects this week's progress."""
    plan = load_plan()
    state = get_current_state()

    task = next((t for t in plan.tasks if t.id == task_id), None)
    if task is None:
        raise ValueError(f"No task found with id {task_id}")
    if task.status != "pending":
        raise ValueError(f"Task {task_id} has already been marked as '{task.status}'")

    task.status = new_status
    save_plan(plan)

    reward = compute_reward(new_status, state.streak_count)

    with open(MOCK_STATE_PATH, "r") as f:
        state_data = json.load(f)

    if new_status == "done":
        state_data["completed_tasks_last_week"] += 1
        state_data["streak_count"] += 1
    elif new_status == "ignored":
        state_data["ignored_tasks_last_week"] += 1
        state_data["streak_count"] = 0

    with open(MOCK_STATE_PATH, "w") as f:
        json.dump(state_data, f, indent=2)

    result = {"task_id": task_id, "status": new_status, "reward": reward}
    append_reward(result)
    return result