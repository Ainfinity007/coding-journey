# detect_submission.py
import os
import shutil
import json
import time
from datetime import datetime

SUBMISSION_DIR = r"C:\Users\Infinity\leetcode-uploader\submissions"
ARCHIVE_DIR = r"C:\Users\Infinity\leetcode-uploader\archived"


def slugify(name):
    return name.lower().replace(" ", "_")


def detect_latest_file():
    files = [f for f in os.listdir(SUBMISSION_DIR) if os.path.isfile(os.path.join(SUBMISSION_DIR, f))]
    if not files:
        print("No new submissions found.")
        return None
    latest_file = max(files, key=lambda x: os.path.getctime(os.path.join(SUBMISSION_DIR, x)))
    return latest_file


def extract_metadata(file_name):
    parts = file_name.split("_")
    if len(parts) < 3:
        return None
    problem_id = parts[0]
    title = " ".join(parts[1:-1])
    slug = slugify(title)
    extension = parts[-1].split(".")[-1]
    return problem_id, title, slug, extension


def archive_submission(file_name):
    meta = extract_metadata(file_name)
    if not meta:
        print("Invalid filename format.")
        return
    problem_id, title, slug, extension = meta
    problem_dir = os.path.join(ARCHIVE_DIR, f"{problem_id}_{slug}")
    os.makedirs(problem_dir, exist_ok=True)

    # Move file to archive dir
    src_path = os.path.join(SUBMISSION_DIR, file_name)
    dst_path = os.path.join(problem_dir, f"my_solution.{extension}")
    shutil.move(src_path, dst_path)

    # Create empty performance.json
    perf_data = {
        "runtime_ms": None,
        "memory_mb": None,
        "timestamp": datetime.now().isoformat()
    }
    with open(os.path.join(problem_dir, "performance.json"), "w") as f:
        json.dump(perf_data, f, indent=2)

    # Create placeholder README
    with open(os.path.join(problem_dir, "README.md"), "w") as f:
        f.write(f"# {title}\n\nProblem ID: {problem_id}\n\nLink: <URL_TO_PROBLEM>\n")

    # Create empty reflection
    with open(os.path.join(problem_dir, "reflection.md"), "w") as f:
        f.write("## Reflection\n\nTODO: Write your thought process here.")

    # Open reflection
    os.system(f"start code {os.path.join(problem_dir, 'reflection.md')}")

    print(f"Archived and opened reflection for: {problem_id}_{slug}")


if __name__ == '__main__':
    file = detect_latest_file()
    if file:
        archive_submission(file)
