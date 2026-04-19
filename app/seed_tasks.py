import requests
from datetime import datetime, timezone

BASE_URL = "http://127.0.0.1:8000"
CREATE_TASK_URL = f"{BASE_URL}/create_tasks"

due_date = datetime.now(timezone.utc).isoformat()

tasks = [
    {
        "title": "bath",
        "description": "cleaning our body to stay fresh and hygienic",
        "status": "completed",
        "due_date": due_date
    },
    {
        "title": "lectures",
        "description": "attended various lectures and took detailed notes",
        "status": "completed",
        "due_date": due_date
    },
    {
        "title": "lunch",
        "description": "already done lunch in the campus cafeteria",
        "status": "completed",
        "due_date": due_date
    },
    {
        "title": "meeting someone",
        "description": "in evening, i have to meet someone for discussion",
        "status": "pending",
        "due_date": due_date
    },
    {
        "title": "prepare dataset",
        "description": "prepare dataset for phd work and research",
        "status": "pending",
        "due_date": due_date
    },
    {
        "title": "dinner",
        "description": "do the dinner in the mess with colleagues",
        "status": "pending",
        "due_date": due_date
    },
    {
        "title": "sleep",
        "description": "go to sleep early to rest well",
        "status": "pending",
        "due_date": due_date
    },
    {
        "title": "gym",
        "description": "workout for 45 minutes in the gym",
        "status": "ongoing",
        "due_date": due_date
    },
    {
        "title": "read paper",
        "description": "read one research paper for literature review",
        "status": "ongoing",
        "due_date": due_date
    },
    {
        "title": "revision",
        "description": "revise today's notes for better understanding",
        "status": "pending",
        "due_date": due_date
    }
]

assignees = [
    {"user_id": 1, "name": "Vaibhav", "email": "vaibhav@example.com"},
    {"user_id": 2, "name": "Ananya", "email": "ananya@example.com"},
    {"user_id": 3, "name": "Ravi", "email": "ravi@example.com"},
    {"user_id": 4, "name": "Anshika", "email": "anshika@example.com"}
]

priorities = ["high", "medium", "low"]

def main() -> None:
    created = 0
    for i, task in enumerate(tasks, start=1):
        payload = {
            "title": task["title"],
            "description": task["description"],
            "status": task["status"],
            "due_date": task["due_date"],
            "assignee": assignees[(i - 1) % len(assignees)],
            "tags": [
                {"name": "work", "color": "blue"},
                {"name": "daily", "color": "gray"}
            ]
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