import requests
from datetime import datetime, timezone

BASE_URL = "http://127.0.0.1:8000"
CREATE_TASK_URL = f"{BASE_URL}/create_tasks"

due_date = datetime.now(timezone.utc).isoformat()

tasks = [
    {
        "title": "bath",
        "description": "cleaninig our body",
        "status": "completed",
        "due_date": due_date,
    },
    {
        "title": "lectures",
        "description": "attended various lectures",
        "status": "completed",
        "due_date": due_date,
    },
    {
        "title": "lunch",
        "description": "already done lunch",
        "status": "completed",
        "due_date": due_date,
    },
    {
        "title": "meeting someone",
        "description": "in evening , i have to meet someone",
        "status": "pending",
        "due_date": due_date,
    },
    {
        "title": "prepare dataset",
        "description": "prepare dataset for phd work",
        "status": "pending",
        "due_date": due_date,
    },
    {
        "title": "dinner",
        "description": "do the dinner in the mess",
        "status": "pending",
        "due_date": due_date,
    },
    {
        "title": "sleep",
        "description": "go to sleep",
        "status": "pending",
        "due_date": due_date,
    },
    {
        "title": "gym",
        "description": "workout for 45 minutes",
        "status": "ongoing",
        "due_date": due_date,
    },
    {
        "title": "read paper",
        "description": "read one research paper",
        "status": "ongoing",
        "due_date": due_date,
    },
    {
        "title": "revision",
        "description": "revise today's notes",
        "status": "pending",
        "due_date": due_date,
    },
]

assignees = [
    {"user_id": 1, "name": "Vaibhav", "email": "vaibhav@example.com"},
    {"user_id": 2, "name": "Ananya", "email": "ananya@example.com"},
    {"user_id": 3, "name": "Ravi", "email": "ravi@example.com"},
    {"user_id": 3, "name": "Anshika", "email": "Anshika@example.com"},
]

priorities = ["high", "medium", "low"]

def main() -> None:
    created = 0
    for i, task in enumerate(tasks, start=1):
        payload = {
            "task": task,
            "assignee": assignees[(i - 1) % len(assignees)],
            "priority": priorities[(i - 1) % len(priorities)],
        }
        try:
            resp = requests.post(CREATE_TASK_URL, json=payload, timeout=10)
            if resp.status_code == 201:
                created += 1
                print(f"[{i}] Created: {task['title']}")
            else:
                print(f"[{i}] Failed ({resp.status_code}): {resp.text}")
        except requests.RequestException as exc:
            print(f"[{i}] Request error: {exc}")

    print(f"\nDone. Created {created}/{len(tasks)} tasks.")

if __name__ == "__main__":
    main()