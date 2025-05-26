from pathlib import Path

archived = Path("archived")
readme = Path("README.md")

with open(readme, "w", encoding="utf-8") as f:
    f.write("# 🗂 Problem Archive\n\n")
    f.write("| ID | Title | Link |\n")
    f.write("|----|-------|------|\n")

    for folder in sorted(archived.iterdir()):
        if folder.is_dir():
            parts = folder.name.split("_", 1)
            if len(parts) != 2:
                continue
            pid, slug = parts
            title = slug.replace("-", " ").title()
            url = f"https://leetcode.com/problems/{slug}"
            f.write(f"| {pid} | [{title}]({folder}/README.md) | [🔗]({url}) |\n")
