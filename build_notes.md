# Forklift Fleet Data Report: Build Notes

A running log of what I built, why I built it that way, and what I learned. I use it for my README, my resume, and for explaining the project out loud in interviews.

**Legend:** `[STEP]` = something I did or built. `[CONCEPT]` = something I learned or understood along the way. Some lines are both.

---

## ORIGIN STORY (for interviews)

> "I started with a forklift fleet report built on static local JSON. I picked forklifts because it's equipment data I already understand from my field work. The goal was to take raw per-forklift readings and turn them into something a fleet manager could act on: a health score, a fleet summary, and a prioritized alert list. Once that worked, I saw that the next step was replacing the local file with an API. I didn't want to build my own API before I understood how real ones behave, so I built a GitHub REST API client first to learn authentication, status codes, and error handling from the consumer side. Now I'm coming back to this project to build the API layer myself with FastAPI and have this report consume it."

**Progression:** static forklift data → Python processing and reporting → consuming a real external API (GitHub client) → building my own API (FastAPI) → the report becomes a client of that API → the API feeds the Connected Operations Integration Hub.

---

## PHASE 1: STATIC DATA REPORT (complete)

### Why a forklift fleet project

* `[CONCEPT]` I chose a forklift fleet problem because it connects directly to my field application engineering work. I already know what matters on a warehouse floor (battery state, speed, whether a truck is down), so I could focus on the Python instead of guessing at the domain.
* `[CONCEPT]` The goal wasn't Python syntax practice. It was taking raw equipment data, applying business rules to it, and producing information someone managing a fleet could use.
* `[CONCEPT]` It keeps me close to the industrial/customer environment I want to work in as a Solutions Engineer.

### Smallest possible version first

* `[STEP]` Started by printing a single forklift's fields with an f-string (kept in `scratched code.py`), then generalized to a list of forklifts processed in a loop.
* `[CONCEPT]` Used static local data instead of an API on purpose. That separated the *data-processing* problem from the *integration* problem, so I only had one new thing to debug at a time.
* `[CONCEPT]` The smallest useful pipeline was: load data → loop over records → apply rules → aggregate → print a readable report. Get the core working first, then add complexity one layer at a time. I later used the same approach on the GitHub client.

### The data: `forklift_data.json`

* `[STEP]` Created `forklift_data.json`: a JSON **array of objects**, one object per forklift, each with the same five keys: `forklift_id`, `location`, `battery` (%), `speed` (mph), `status` (`active` / `charging` / `offline`).
* `[CONCEPT]` **Why a list of dictionaries?** Each forklift's data stays together as one record. The alternative is parallel lists (`ids[]`, `batteries[]`, `speeds[]`), where index 3 in one list has to line up with index 3 in every other list. With a list of dicts, adding a field or a forklift can't knock anything out of alignment. It's also the exact shape most REST APIs return, which is why I recognized it immediately when I built the GitHub client.
* `[CONCEPT]` **Why a separate JSON file instead of hard-coding the data in `main.py`?** It keeps data apart from logic. I can change the fleet without touching code, and later I can swap where the data comes from (a file today, an HTTP response tomorrow) without rewriting the analysis.
* `[CONCEPT]` The data is fake on purpose (`RAY-xxx` IDs). The point was the processing, and I didn't want to expose or depend on real customer or company data.
* `[CONCEPT]` I built the sample data to hit the edge cases: one forklift under 10% battery (critical), one under 20% (warning), one over the speed limit, and one offline. That way every alert path actually runs when I test the report.

### Loading the data: `load_forklift_data()`

* `[STEP]` Wrote a function that opens the file with `with open(...)` and returns `json.load(file)`, which turns the JSON array into a Python list of dicts.
* `[CONCEPT]` **Why `with open(...)`?** The context manager closes the file automatically, even if something fails partway through. No manual `file.close()` to forget.
* `[CONCEPT]` **Why wrap loading in its own function?** The rest of the program only knows "call this, get a list of forklifts." It doesn't care where they came from. This is the seam where the file will be replaced by an API call later. Only this one function should have to change.

### Business rules: `analyze_fleet(forklifts)`

* `[STEP]` Looped once over every forklift, pulled each field into a named variable (`battery = forklift["battery"]`, etc.), and applied the rules:
  * battery `< 10` → `CRITICAL` alert
  * battery `< 20` → `WARNING` alert
  * speed `> 6.0` mph → speed warning
  * status `offline` → offline alert, and the ID is added to the offline list
  * status `active` → the ID is added to the active list
  * location `Charging Station` → the ID is added to the charging list
* `[CONCEPT]` **Why `if` / `elif` for battery, and why check `< 10` first?** A forklift at 8% is also under 20%. With two separate `if`s it would get *both* a critical and a warning alert. With `elif`, and the most severe check first, each forklift gets exactly one battery alert at the right severity. Order matters in tiered rules.
* `[CONCEPT]` **Why separate `if`s for battery, speed, and status?** Those are independent problems. One forklift can be low on battery *and* speeding, and the report should show both.
* `[CONCEPT]` **Why collect IDs in lists instead of just incrementing counters?** A list tells me *which* forklifts are offline, not just *how many*. `len()` still gives me the count for the summary, and I keep the detail for free.
* `[CONCEPT]` **Why build an `alerts` list instead of printing alerts immediately?** Analysis and output stay separate. The function decides *what's wrong*, and a different function decides *how to show it*. That's what lets me show a total alert count in the summary before listing the alerts themselves.
* `[CONCEPT]` Alert strings start with the severity (`CRITICAL`, `WARNING`) so the most important information is the first thing a person reads.

### Fleet health score: `fleet_health(forklifts)`

* `[STEP]` Started at 100 and subtracted points per problem: −10 for low battery (< 20%), −10 for offline, −5 for speeding. Returned `max(health_score, 0)`.
* `[CONCEPT]` **Why a single score?** A fleet manager wants one number for "how are we doing" before looking at details. It's the same idea as a KPI tile on a dashboard.
* `[CONCEPT]` **Why weight speeding lower?** Low battery and offline trucks directly cost uptime. Speeding is a safety and behavior issue, but the truck is still working. The weights are my judgment call, and I can defend them.
* `[CONCEPT]` **Why `max(..., 0)`?** It clamps the score so a bad day can't produce a negative health score, which would be meaningless to a reader.

### Report output: `print_report(...)` and `print_alerts(alerts)`

* `[STEP]` Printed a header with a generated timestamp, the fleet health score, a summary block (total / active / charging / offline / alert count), a per-forklift section, then an alerts section.
* `[STEP]` `print_alerts` prints a **"NO ALERTS"** block when the list is empty instead of printing nothing.
* `[CONCEPT]` **Why the order summary → details → alerts?** It goes from high level to granular, the way someone actually reads a report.
* `[CONCEPT]` **Why an explicit "no alerts" message?** Silence is ambiguous. It could mean "all good" or "the check didn't run." An explicit message removes that doubt.
* `[CONCEPT]` **Why triple-quoted f-strings?** They let me lay out the report in the code roughly the way it looks on screen, so the output is easy to read and edit.
* `[CONCEPT]` **Why a timestamp?** A report without a time is useless the next day, because you can't tell how fresh it is.
* `[CONCEPT]` The report is the last layer of the pipeline: raw data → business rules → summarized information → human-readable output. Customers don't care that JSON loaded. They care what the data means and what to do about it. That's the SE mindset.

### Program flow (bottom of `main.py`)

* `[STEP]` The script runs top to bottom: load → score → analyze → print report → print alerts. Each step's output is passed into the next as arguments. There are no global variables inside the functions.
* `[CONCEPT]` Passing data in and returning results out makes each function testable on its own. I can hand `fleet_health()` a fake two-forklift list and check the number.

### Python concepts practiced

* `[CONCEPT]` Lists and dictionaries (a list of dicts as the core data structure)
* `[CONCEPT]` `for` loops over records; `if` / `elif` for tiered rules
* `[CONCEPT]` Functions with a single responsibility, parameters, and return values (including returning multiple values as a tuple)
* `[CONCEPT]` File handling with `with open` and the `json` module
* `[CONCEPT]` f-strings and multi-line output formatting
* `[CONCEPT]` `datetime` for timestamps; `len()` and `max()` built-ins
* `[CONCEPT]` The whole project connected individual Python fundamentals into one workflow instead of learning each in isolation.

---

## REVIEW BEFORE PHASE 2 (what I'd change, and why)

I reviewed the Phase 1 code before building the API on top of it. These are real findings I can talk about in an interview ("here's what I'd do differently and why"):

* `[CONCEPT]` **Charging count bug.** `analyze_fleet` counts "charging" by `location == "Charging Station"` instead of by `status == "charging"`. With the current data, the "Charging: 1" in the report is RAY-500, which is actually *offline*. RAY-205 (status `charging`) isn't counted anywhere, so it's in none of the buckets. The totals only add up to 5 by coincidence. Lesson: pick **one** source of truth for state (the `status` field) and don't infer it from a different field.
* `[CONCEPT]` **Top-level script code.** The load/analyze/print calls run as soon as the file is imported. Once FastAPI imports my analysis functions, that would print a report every time the server starts. The fix is the `if __name__ == "__main__":` guard.
* `[CONCEPT]` **Duplicated thresholds ("magic numbers").** `20` and `6.0` appear in both `analyze_fleet` and `fleet_health`. If I change the speed limit in one place, the alerts and the score disagree. They should be named constants defined once (e.g. `LOW_BATTERY_PCT = 20`).
* `[CONCEPT]` **Unused variables in `fleet_health`.** It unpacks `forklift_id`, `location`, etc., then uses `forklift["battery"]` directly anyway. That's leftover from copying the loop.
* `[CONCEPT]` **Misleading names.** `number_active` is a list of IDs, not a number. `active_ids` says what it actually holds.
* `[CONCEPT]` **Five-value tuple return.** `analyze_fleet` returns five values that must be unpacked in exactly the right order, and `print_report` takes seven arguments. Returning one dictionary (`{"total": ..., "active_ids": [...], "alerts": [...]}`) is safer, and a dict is exactly what an API endpoint returns as JSON.
* `[CONCEPT]` **The health score doesn't scale with fleet size.** A fixed −10 per problem means 10 low-battery trucks zero out a 200-truck fleet the same as a 10-truck fleet. Worth deciding whether it should be a percentage of the fleet.
* `[CONCEPT]` **No error handling on load.** A missing file, bad JSON, or a record missing a key would crash with a raw traceback. Same principle as the GitHub client: fail with a clear message.
* `[CONCEPT]` **Relative file path.** `open("forklift_data.json")` only works if I run the script from the project folder. Building the path from the script's own location fixes that.
* `[CONCEPT]` **Timestamp.** `datetime.today()` is naive and prints microseconds. I already learned to use `datetime.now(timezone.utc)` in the GitHub client, and a formatted string reads better in a report.

---

## VERSION CONTROL SETUP (Git + GitHub)

Repo: `DJH333/FORKLIFT-FLEET-API`. I chose one repo for the whole project rather than a separate repo for Phase 1, so the commit history shows the progression from a static report to an API.

### What I did

* `[STEP]` Checked Git was installed (`git --version`) and confirmed my commit identity (`user.name` / `user.email`). I updated `user.email` to match the email now on my GitHub account.
* `[STEP]` `git init` to turn the project folder into a repo.
* `[STEP]` Created a root `.gitignore` *before* the first commit (`.venv/`, `.idea/`, `__pycache__/`, `*.pyc`, `scratched code.py`).
* `[STEP]` Ran `git status` before staging to confirm only the four real project files showed up.
* `[STEP]` Staged files by name (`git add .gitignore main.py forklift_data.json build_notes.md`) instead of `git add .`, then made the first commit: "Add Phase 1 static forklift fleet report."
* `[STEP]` `git branch -M main` to rename the local branch from `master` to match GitHub's default.
* `[STEP]` Connected the remote with `git remote add origin`, and verified it with `git remote -v`.
* `[STEP]` First push was rejected because the GitHub repo already had a commit (the Python `.gitignore` template). I pulled with `--allow-unrelated-histories`, resolved the resulting merge conflict, committed the merge, and pushed with `git push -u origin main`.
* `[STEP]` Tagged the Phase 1 snapshot: `git tag -a v1-static-report`, pushed with `git push origin v1-static-report`.
* `[STEP]` Verified with `git log --oneline --graph`: my commit and GitHub's initial commit join at the merge commit, and `main`, `origin/main`, and the tag all point to the same place.

### What I learned

* `[CONCEPT]` **Why `.gitignore` before the first commit?** Once a file is committed, it stays in history even if I ignore it later. `.venv/` is hundreds of MB anyone can rebuild, and `.idea/` is personal PyCharm config (I've already seen corrupted `.idea` folders break a project after a move).
* `[CONCEPT]` **A `.gitignore` only applies to its own folder and below.** At first I was looking at `.venv/.gitignore`, which is auto-generated by the virtual environment (it contains `*` to ignore itself). My project needed its own `.gitignore` at the root.
* `[CONCEPT]` **`git add` stages a snapshot of the file at that moment, not the file itself.** PyCharm staged my `.gitignore` while it was still empty, so `git status` showed it as both "new file" (staged, empty) and "modified" (my real content). Running `git add` again staged the current version.
* `[CONCEPT]` **Git doesn't check a remote URL when you add it.** I accidentally saved a placeholder URL as `origin`. `remote add` succeeded anyway, and the next `remote add` failed with "remote origin already exists." The fix was `git remote set-url origin <real URL>`, not adding it again.
* `[CONCEPT]` **Why the push was rejected ("fetch first").** GitHub had a commit my local repo didn't have. Git refuses to push if it would overwrite remote history. I had to bring the remote commit in first.
* `[CONCEPT]` **Merge conflicts.** Both histories created `.gitignore` (an "add/add" conflict), and Git won't guess which version wins. The `<<<<<<< HEAD` / `=======` / `>>>>>>>` markers separate my version from the incoming one. I resolved it in PyCharm's merge tool by taking **both** sides: my rules (`.idea/`, `scratched code.py`) plus GitHub's Python template, which covers `.env`. That matters once the API has configuration or secrets. Resolving a conflict means editing the file to the version I actually want, then committing that.
* `[CONCEPT]` **Commit email links commits to my GitHub account.** GitHub matches commits by author email, so `user.email` has to be an email on my account, or commits won't show my profile or count on my contribution graph. Changing my GitHub email also means older commits made with the previous email no longer link unless that email is added back as a secondary address.
* `[CONCEPT]` **`-u` on the first push** links local `main` to `origin/main`, so later I can just run `git push` / `git pull`.
* `[CONCEPT]` **Tags aren't pushed by a normal `git push`.** They need their own push. The `v1-static-report` tag gives anyone a fixed snapshot of Phase 1 to compare against later work.
* `[CONCEPT]` The PyCharm prompt to exclude ignored directories is an IDE indexing setting, not Git. Git already ignores those folders via `.gitignore`.

---

## PHASE 2: API LAYER (in progress)

* `[CONCEPT]` The goal is to replace the local file with an HTTP API that I build myself in FastAPI. The report then becomes a *client* of that API, so I see both sides of the same request.
* `[CONCEPT]` The Phase 1 design already set this up: `load_forklift_data()` is the only function that should need to change. The analysis functions don't care whether the list came from a file or a `requests.get()`.

*(Log Phase 2 steps here as I build them.)*
