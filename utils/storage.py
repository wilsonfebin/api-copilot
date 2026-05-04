import json
import os

THREAD_FILE = "data/threads.json"


def load_threads():
    if not os.path.exists(THREAD_FILE):
        return []

    with open(THREAD_FILE, "r") as f:
        return json.load(f)


def save_threads(threads):
    os.makedirs("data", exist_ok=True)

    with open(THREAD_FILE, "w") as f:
        json.dump(threads, f, indent=2)
