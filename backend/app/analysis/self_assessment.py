"""Short self-assessment: a role-specific interview quiz, a networking check and a
confidence rating. Scores come from the user's own answers, not from seeded numbers."""
from typing import Dict


class AssessmentError(ValueError):
    """Raised when submitted answers are incomplete or invalid."""


def _q(qid, topic, prompt, options, answer):
    return {"id": qid, "topic": topic, "prompt": prompt, "options": options, "answer": answer}


INTERVIEW_BANK = {
    "swe_backend": [
        _q("be-1", "HTTP status codes", "Which HTTP status code means a resource was successfully created?",
           ["200 OK", "201 Created", "204 No Content", "301 Moved Permanently"], 1),
        _q("be-2", "SQL grouping", "Which SQL clause filters rows AFTER they have been grouped?",
           ["WHERE", "HAVING", "ORDER BY", "LIMIT"], 1),
        _q("be-3", "Database indexes", "What is the main purpose of a database index?",
           ["Speed up reads on the indexed columns", "Encrypt the column", "Enforce foreign keys", "Compress the table"], 0),
        _q("be-4", "REST principles", "A request that can be repeated many times with the same effect as doing it once is called:",
           ["Stateless", "Idempotent", "Cached", "Asynchronous"], 1),
        _q("be-5", "Git basics", "Which git command saves your staged changes to the local history?",
           ["git push", "git fetch", "git commit", "git stash"], 2),
        _q("be-6", "Containers", "What does Docker mainly let you do?",
           ["Write unit tests automatically", "Package an app with its dependencies to run the same way anywhere",
            "Host a relational database only", "Compile Python to machine code"], 1),
    ],
    "data_analyst": [
        _q("da-1", "Descriptive statistics", "Which measure of the centre is least affected by extreme outliers?",
           ["Mean", "Median", "Range", "Standard deviation"], 1),
        _q("da-2", "SQL joins", "Which SQL join returns all rows from the left table, even without a match on the right?",
           ["INNER JOIN", "CROSS JOIN", "LEFT JOIN", "UNION"], 2),
        _q("da-3", "Data visualisation", "Which chart is best for showing how a value changes over time?",
           ["Pie chart", "Word cloud", "Venn diagram", "Line chart"], 3),
        _q("da-4", "pandas basics", "In pandas, which method summarises count, mean, std, min and quartiles of numeric columns?",
           ["df.head()", "df.describe()", "df.shape", "df.columns"], 1),
        _q("da-5", "Correlation vs causation", "Two variables are strongly correlated. What can you conclude?",
           ["One causes the other", "They are linked, but correlation alone does not prove causation",
            "Both are caused by time", "The data must contain errors"], 1),
        _q("da-6", "SQL aggregation", "Which SQL function counts the rows in a group?",
           ["SUM()", "AVG()", "ROUND()", "COUNT()"], 3),
    ],
    "frontend_dev": [
        _q("fe-1", "CSS box model", "In the CSS box model, which part sits between the content and the border?",
           ["Margin", "Padding", "Outline", "Gap"], 1),
        _q("fe-2", "JavaScript equality", "In JavaScript, what does the === operator check?",
           ["Value only", "Type only", "Value and type", "Memory address only"], 2),
        _q("fe-3", "React state", "In React, what do you use to store a value that changes and re-renders the component?",
           ["A normal variable", "document.getElementById", "A CSS class", "useState"], 3),
        _q("fe-4", "Semantic HTML", "Which HTML element is the most appropriate for the main navigation links?",
           ["<div>", "<nav>", "<span>", "<section>"], 1),
        _q("fe-5", "Flexbox", "Which CSS declaration makes a container lay out its children as a flexible row or column?",
           ["position: fixed", "float: both", "overflow: auto", "display: flex"], 3),
        _q("fe-6", "Async JavaScript", "What does async/await help you do?",
           ["Run code on several CPU cores", "Write asynchronous code that reads like sequential code",
            "Block the page until all requests finish", "Compile JavaScript faster"], 1),
    ],
}

from app.analysis.quiz_banks_tech import EXTRA_BANKS  # noqa: E402

INTERVIEW_BANK.update(EXTRA_BANKS)

# For networking, the points for an answer equal its option index (0 to 3).
NETWORKING_QUESTIONS = [
    {"id": "net-1", "prompt": "In the last 30 days, how many people in your field did you contact (message, email or conversation)?",
     "options": ["None", "1 to 2", "3 to 5", "6 or more"]},
    {"id": "net-2", "prompt": "How complete is your LinkedIn (or similar) professional profile?",
     "options": ["I do not have one", "Created but mostly empty", "Mostly complete", "Complete and recently updated"]},
    {"id": "net-3", "prompt": "How many tech events, meetups or hackathons did you attend in the last 3 months?",
     "options": ["None", "1", "2 to 3", "4 or more"]},
    {"id": "net-4", "prompt": "Is there a mentor, senior or professional you could ask for career advice?",
     "options": ["No one", "Someone, but I have not asked", "Yes, I have asked once", "Yes, I talk with them regularly"]},
]


def public_questions(role: str) -> dict:
    """Questions for a role, without the answer key."""
    bank = INTERVIEW_BANK.get(role)
    if not bank:
        raise AssessmentError("There is no interview quiz for this role yet.")
    return {
        "role": role,
        "interview": [{"id": q["id"], "prompt": q["prompt"], "options": q["options"]} for q in bank],
        "networking": NETWORKING_QUESTIONS,
    }


def _check_choice(choice, n_options: int, qid: str) -> None:
    if not isinstance(choice, int) or not 0 <= choice < n_options:
        raise AssessmentError(f"Invalid option for question {qid}.")


def score_interview(role: str, answers: Dict[str, int]) -> dict:
    bank = INTERVIEW_BANK.get(role)
    if not bank:
        raise AssessmentError("There is no interview quiz for this role yet.")
    by_id = {q["id"]: q for q in bank}
    for qid in answers:
        if qid not in by_id:
            raise AssessmentError(f"Unknown question: {qid}")
    if len(answers) != len(bank):
        raise AssessmentError(f"Answer all {len(bank)} interview questions, or skip that section.")

    correct, missed = 0, []
    for q in bank:
        choice = answers[q["id"]]
        _check_choice(choice, len(q["options"]), q["id"])
        if choice == q["answer"]:
            correct += 1
        else:
            missed.append(q["topic"])
    return {
        "score": round(correct / len(bank) * 100),
        "correct": correct,
        "total": len(bank),
        "missed_topics": missed,
    }


def score_networking(answers: Dict[str, int]) -> dict:
    by_id = {q["id"]: q for q in NETWORKING_QUESTIONS}
    for qid in answers:
        if qid not in by_id:
            raise AssessmentError(f"Unknown question: {qid}")
    if len(answers) != len(by_id):
        raise AssessmentError(f"Answer all {len(by_id)} networking questions, or skip that section.")

    points = 0
    for qid, q in by_id.items():
        choice = answers[qid]
        _check_choice(choice, len(q["options"]), qid)
        points += choice
    return {"score": round(points / (3 * len(by_id)) * 100)}