import os
import sys
from pathlib import Path

if len(sys.argv) != 2:
    print("Usage: python generate_readme.py <problem_id_slug>")
    exit(1)

problem_dir_name = sys.argv[1]

# Extract id and slug from folder name
if "_" not in problem_dir_name:
    print("Invalid folder name format.")
    exit(1)

problem_id, slug = problem_dir_name.split("_", 1)
problem_name = slug.replace("_", " ").title()
difficulty = "Easy"  # You can improve this by parsing difficulty elsewhere
link = f"https://leetcode.com/problems/{slug}"

archived_dir = Path(f"archived/{problem_dir_name}")
readme_path = archived_dir / "README.md"

with open(readme_path, "w", encoding="utf-8") as f:
    f.write(f"# {problem_name}\n\n")
    f.write(f"**Difficulty:** {difficulty}  \n")
    f.write(f"**Link:** {link}\n\n")
    f.write("## Description\n\nTODO: Add full problem description.\n\n")
    f.write("## My Solution\n\nTODO: Brief explanation of your code.\n\n")
    f.write("## Best Solution (LLM)\n\nTODO: Paste optimal version generated.\n")
