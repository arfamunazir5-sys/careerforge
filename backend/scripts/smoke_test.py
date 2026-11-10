"""End-to-end smoke test of a running CareerForge backend (live or local).

Run from the project root (venv active):
  python backend\\scripts\\smoke_test.py            # the live Render backend
  python backend\\scripts\\smoke_test.py --local    # http://127.0.0.1:8000

It walks through the whole product flow and prints PASS or FAIL for each step with
timings. WARNING: it resets the app at the start and at the end, so run it only
when you do not need the current state (for example before a demo). It never calls
GitHub and never uploads files."""
import json
import sys
import time
import urllib.error
import urllib.request

LIVE = "https://careerforge-backend-lo7f.onrender.com"
LOCAL = "http://127.0.0.1:8000"
BASE = LOCAL if "--local" in sys.argv else LIVE

RESUME = ("Education Experience Projects Skills Python Flask SQL Git "
          "Built and developed REST APIs and improved test coverage")
STRONG_EVIDENCE = {
    "links": ["behance.net/demo", "figma.com/@demo", "demo.design/case-study"],
    "case_studies": 4, "has_results": True, "has_process": True, "recent_work": True,
}

results = []


def call(path, method="GET", body=None, timeout=90):
    data = json.dumps(body).encode() if body is not None else (b"" if method == "POST" else None)
    headers = {"Content-Type": "application/json"} if body is not None else {}
    req = urllib.request.Request(BASE + path, method=method, data=data, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", "replace")
            return resp.status, resp.headers, raw
    except urllib.error.HTTPError as e:
        return e.code, e.headers, e.read().decode("utf-8", "replace")


def jcall(path, method="GET", body=None):
    status, _, raw = call(path, method, body)
    try:
        data = json.loads(raw)
    except ValueError:
        data = None
    if isinstance(data, list) and path == "/dashboard":
        data = data[0]
    return status, data


def step(name, fn):
    start = time.time()
    try:
        detail = fn()
        results.append(True)
        print(f"PASS  {name}  ({time.time() - start:.1f}s)" + (f"  {detail}" if detail else ""))
    except Exception as e:  # noqa: BLE001 - report any failure and keep going
        results.append(False)
        print(f"FAIL  {name}  ({time.time() - start:.1f}s)  {type(e).__name__}: {e}")


def check(condition, message):
    if not condition:
        raise AssertionError(message)


def hours_of(allocation):
    return {a["agent"]: a["hours"] for a in allocation["allocations"]}


def wake_up():
    start = time.time()
    for attempt in range(1, 13):
        try:
            status, _, _ = call("/", timeout=30)
            if status == 200:
                return f"awake after {time.time() - start:.0f}s"
        except Exception:  # noqa: BLE001
            pass
        time.sleep(5)
    raise AssertionError("server did not wake up in 60s")


ctx = {}


def reset_clean():
    status, data = jcall("/reset", "POST")
    check(status == 200 and data["status"] == "reset", f"reset returned {status}")
    status, _ = jcall("/plan")
    check(status == 404, "a plan still exists after reset")
    _, state = jcall("/state")
    check(state["profile_completed"] is False and state["week_number"] == 1, "state is not at baseline")


def roles():
    status, data = jcall("/roles")
    check(status == 200 and len(data) == 10, f"expected 10 roles, got {len(data or [])}")
    check({r["portfolio_mode"] for r in data} == {"github", "evidence"}, "portfolio modes missing")


def profile():
    status, data = jcall("/update-profile", "POST", {"target_role": "swe_backend", "available_hours": 15})
    check(status == 200 and data["available_hours"] == 15 and data["profile_completed"] is True, "profile not saved")


def resume():
    status, data = jcall("/analyze-resume", "POST", {"resume_text": RESUME, "target_role": "swe_backend"})
    check(status == 200, f"status {status}")
    check("fastapi" in data["missing_skills"] and "python" not in data["missing_skills"], "unexpected analysis")
    return f"score {data['resume_score']}, missing {data['missing_skills']}"


def assessment():
    _, q = jcall("/self-assessment/questions")
    check(q["role"] == "swe_backend" and len(q["interview"]) == 6, "wrong quiz")
    status, data = jcall("/self-assessment", "POST", {
        "networking_answers": {item["id"]: 2 for item in q["networking"]}, "confidence": 7})
    check(status == 200 and data["networking"]["score"] == 67 and data["confidence"] == 7, "assessment not scored")


def plan_before():
    status, plan = jcall("/generate-plan", "POST")
    check(status == 200 and sum(t["hours"] for t in plan["tasks"]) == 15, "plan does not use 15 hours")
    check(all(t["why"] for t in plan["tasks"]), "a task has no reasoning")
    _, dash = jcall("/dashboard")
    ctx["before"] = hours_of(dash["allocation"])
    ctx["portfolio_tasks"] = [t["id"] for t in plan["tasks"] if t["agent"] == "portfolio"]
    check(ctx["portfolio_tasks"], "no portfolio tasks to complete")
    return f"hours {ctx['before']}"


def complete_portfolio():
    for task_id in ctx["portfolio_tasks"]:
        status, data = jcall(f"/tasks/{task_id}/complete", "POST")
        check(status == 200 and data["status"] == "done", f"task {task_id} not completed")
    _, dash = jcall("/dashboard")
    progress = {p["module"]: p["change"] for p in dash["adaptation"]["progress"]}
    check(progress.get("Portfolio", 0) > 0, "no portfolio progress shown")
    check(dash["adaptation"]["share_shifts"], "no share shift shown")
    return f"portfolio {progress['Portfolio']:+d}"


def regenerate():
    status, _ = jcall("/generate-plan", "POST")
    check(status == 200, f"status {status}")
    _, dash = jcall("/dashboard")
    after = hours_of(dash["allocation"])
    check(sum(after.values()) == 15, "hours do not sum to the budget")
    check(after["portfolio"] < ctx["before"]["portfolio"], f"portfolio hours did not drop ({ctx['before']['portfolio']} -> {after['portfolio']})")
    check(any(r["agent"] == "portfolio" and r["note"] for r in dash["adaptation"]["reallocation"]), "no explanation for the shift")
    return f"portfolio {ctx['before']['portfolio']}h -> {after['portfolio']}h"


def dashboard_shape():
    _, dash = jcall("/dashboard")
    for key in ("career_health", "explanations", "biggest_opportunity", "bids", "allocation",
                "allocation_shares", "agent_learning", "adaptation"):
        check(key in dash, f"dashboard is missing {key}")
    check(all("bid strength" in i["explanation"] for i in dash["explanations"]["items"]), "explanations lack bid strength")


def learning():
    _, plan = jcall("/plan")
    networking = next(t for t in plan["tasks"] if t["agent"] == "networking")
    status, data = jcall(f"/tasks/{networking['id']}/ignore", "POST")
    check(status == 200 and data["reward"] < 0, "ignore not recorded")
    _, dash = jcall("/dashboard")
    check(dash["agent_learning"]["networking"]["multiplier"] < 1.0, "no follow-through penalty")


def simulator():
    status, data = jcall("/simulate-roles")
    check(status == 200 and len(data) == 10 and sum(s["is_current"] for s in data) == 1, "bad simulation")


def weekly():
    status, summary = jcall("/week-summary")
    check(status == 200 and summary["tasks_total"] > 0 and summary["ignored"] == 1, "week summary is wrong")
    status, data = jcall("/next-week", "POST", {})
    check(status == 200 and data["week_number"] == 2 and data["plan"]["week_number"] == 2, "week did not roll over")
    _, state = jcall("/state")
    check(len(state["week_history"]) == 1, "week history is empty")


def evidence_role():
    status, _ = jcall("/update-profile", "POST", {"target_role": "ux_designer", "available_hours": 12})
    check(status == 200, "could not switch role")
    _, state = jcall("/state")
    check(state["portfolio_score"] == 50, "portfolio did not reset when the evidence type changed")
    status, data = jcall("/portfolio-evidence", "POST", STRONG_EVIDENCE)
    check(status == 200 and data["score"] == 100, f"evidence returned {status}")
    status, _ = jcall("/analyze-portfolio", "POST", {"github_username": "octocat"})
    check(status == 422, "GitHub scan should be refused for an evidence role")


def calendar():
    jcall("/generate-plan", "POST")
    status, headers, raw = call("/export-calendar")
    check(status == 200 and "text/calendar" in headers.get("content-type", "") and raw.startswith("BEGIN:VCALENDAR"), "bad .ics")


def validation():
    status, _ = jcall("/update-profile", "POST", {"target_role": "astronaut", "available_hours": 10})
    check(status == 422, "unknown role was accepted")
    status, _ = jcall("/update-profile", "POST", {"target_role": "swe_backend", "available_hours": 0})
    check(status == 422, "0 hours was accepted")


def final_reset():
    status, _ = jcall("/reset", "POST")
    check(status == 200, f"status {status}")


print(f"Smoke test against {BASE}\n")
step("Server is awake", wake_up)
step("Reset gives a clean baseline", reset_clean)
step("Ten roles with portfolio modes", roles)
step("Save profile (Backend Developer, 15h)", profile)
step("Resume analysis", resume)
step("Self-assessment (networking + confidence)", assessment)
step("Generate plan with reasoning", plan_before)
step("Complete both Portfolio tasks, adaptation appears", complete_portfolio)
step("Regenerate: Portfolio hours drop with an explanation", regenerate)
step("Dashboard has every section", dashboard_shape)
step("Ignoring a task lowers its follow-through weight", learning)
step("Role simulator lists all roles", simulator)
step("Weekly check-in rolls the week", weekly)
step("Evidence role: portfolio evidence works, GitHub refused", evidence_role)
step("Calendar export", calendar)
step("Input validation", validation)
step("Reset again (leaves a clean demo state)", final_reset)

passed = sum(results)
print(f"\n{passed}/{len(results)} steps passed")
sys.exit(0 if passed == len(results) else 1)