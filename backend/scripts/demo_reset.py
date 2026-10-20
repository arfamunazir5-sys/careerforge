"""Warm up the backend and restore the demo baseline.

Run from the project root (venv active):
  python backend\\scripts\\demo_reset.py                 # live Render backend: warm up, then reset
  python backend\\scripts\\demo_reset.py --warmup-only   # live backend: warm up only, no reset
  python backend\\scripts\\demo_reset.py --local         # local backend at http://127.0.0.1:8000
"""
import json
import sys
import time
import urllib.error
import urllib.request

LIVE = "https://careerforge-backend-lo7f.onrender.com"
LOCAL = "http://127.0.0.1:8000"


def call(base, path, method="GET", timeout=60):
    data = b"" if method == "POST" else None
    req = urllib.request.Request(base + path, method=method, data=data)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")


def warm_up(base):
    print(f"Warming up {base} ...")
    start = time.time()
    for attempt in range(1, 13):
        try:
            status, _ = call(base, "/", timeout=30)
            if status == 200:
                print(f"  server is awake ({time.time() - start:.1f}s, attempt {attempt})")
                return True
            print(f"  attempt {attempt}: status {status}, retrying...")
        except Exception as e:
            print(f"  attempt {attempt}: {type(e).__name__}, retrying...")
        time.sleep(5)
    print("  could not reach the server. Check the Render dashboard.")
    return False


def main():
    args = sys.argv[1:]
    base = LOCAL if "--local" in args else LIVE

    if not warm_up(base):
        sys.exit(1)
    if "--warmup-only" in args:
        print("Done (warm-up only, nothing was reset).")
        return

    status, body = call(base, "/reset", method="POST")
    print(f"POST /reset -> {status}")
    if status != 200:
        print(body[:300])
        sys.exit(1)

    status, body = call(base, "/state")
    if status == 200:
        s = json.loads(body)
        print("State after reset:")
        print(f"  role={s.get('target_role')}  hours={s.get('available_hours')}  week={s.get('week_number')}  streak={s.get('streak_count')}")
        print(f"  resume={s.get('resume_score')}  portfolio={s.get('portfolio_score')}  networking={s.get('networking_score')}  interview={s.get('interview_score')}")

    status, body = call(base, "/plan")
    if status == 404:
        print("Plan after reset: none (the app will show 'No plan yet').")
    elif status == 200:
        tasks = json.loads(body).get("tasks", [])
        pending = sum(1 for t in tasks if t.get("status") == "pending")
        print(f"Plan after reset: still exists ({len(tasks)} tasks, {pending} pending).")
        print("  If you want a fresh start on stage, click 'Generate New Plan' once before presenting.")
    else:
        print(f"GET /plan -> {status}")

    print("Ready.")


if __name__ == "__main__":
    main()