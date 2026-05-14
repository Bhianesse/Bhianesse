import requests
import time
import os

OWNER = "Bhianesse"
REPO = "Bhianesse"

TOKEN = os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN")

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/vnd.github+json"
}

SLEEP_AFTER_ALL = 3600  # 5 menit

# 👉
BATCH_SIZE = 3

# 👉
WORKFLOW_LIST = [
    "krtalk2.yml", "krtalk3.yml",
    "krtalk4.yml", "krtalk6.yml",
    "bonmua.yml", "xolax.yml",
    "tructip.yml", "ulangin.yml",
]

# 👉
WORKFLOW_GROUPS = []
temp = []

for wf in WORKFLOW_LIST:

    if wf == "ulangin.yml":
        if temp:
            WORKFLOW_GROUPS.append(temp)
            temp = []

        WORKFLOW_GROUPS.append([wf])

    else:
        temp.append(wf)

        if len(temp) == BATCH_SIZE:
            WORKFLOW_GROUPS.append(temp)
            temp = []

if temp:
    WORKFLOW_GROUPS.append(temp)


def trigger_workflow(workflow):
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/actions/workflows/{workflow}/dispatches"
    data = {"ref": "main"}
    r = requests.post(url, headers=HEADERS, json=data)

    if r.status_code == 204:
        print("Triggered:", workflow)
    else:
        print("Trigger failed:", workflow, r.text)


# 🔥
def get_latest_run(workflow):
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/actions/workflows/{workflow}/runs?per_page=5"

    for _ in range(6):
        r = requests.get(url, headers=HEADERS)

        if r.status_code != 200:
            print("API error:", r.text)
            time.sleep(2)
            continue

        data = r.json()

        for run in data["workflow_runs"]:
            if (
                run["path"].endswith(workflow) and
                run["status"] in ["queued", "in_progress"]
            ):
                return run["id"]

        time.sleep(2)

    return None


def wait_run_finish(run_id):
    while True:
        url = f"https://api.github.com/repos/{OWNER}/{REPO}/actions/runs/{run_id}"
        r = requests.get(url, headers=HEADERS)

        if r.status_code != 200:
            print("API error:", r.text)
            time.sleep(2)
            continue

        status = r.json()["status"]
        print("Run status:", status)

        if status == "completed":
            return

        time.sleep(3)


while True:

    print("===== START WORKFLOW QUEUE =====")

    for group in WORKFLOW_GROUPS:

        run_ids = []

        for wf in group:
            trigger_workflow(wf)

            
            time.sleep(5)

            run_id = get_latest_run(wf)

            if run_id:
                run_ids.append(run_id)

        print("Waiting group:", group)

        for rid in run_ids:
            wait_run_finish(rid)

        print("Group finished:", group)

    print("All workflows finished")
    print("Sleep", SLEEP_AFTER_ALL, "seconds")

    time.sleep(SLEEP_AFTER_ALL)
