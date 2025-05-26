import os
from pathlib import Path

def generate_readme(problem_id_slug):
    folder = Path(f"archived/{problem_id_slug}")
    reflection_file = folder / "reflection.md"
    my_solution_file = next(folder.glob("my_solution.*"), None)
    best_solution_file = next(folder.glob("best_solution.*"), None)
    
    readme_path = folder / "README.md"

    readme_lines = []

    # Extract Title from folder name
    problem_id, slug = problem_id_slug.split("_", 1)
    title = slug.replace("-", " ").title()
    link = f"https://leetcode.com/problems/{slug}"

    readme_lines.append(f"# {title}")
    readme_lines.append(f"\n**Problem ID:** {problem_id}")
    readme_lines.append(f"\n**Link:** [{link}]({link})\n")

    readme_lines.append("## 🧠 Reflection\n")
    if reflection_file.exists():
        readme_lines.append(reflection_file.read_text())
    else:
        readme_lines.append("_Reflection not found._")

    readme_lines.append("\n---\n## 💻 My Solution\n")
    if my_solution_file:
        readme_lines.append(f"```{my_solution_file.suffix[1:]}\n{my_solution_file.read_text()}\n```")
    else:
        readme_lines.append("_My solution not found._")

    readme_lines.append("\n---\n## 🚀 Best Solution (LLM / GPT)\n")
    if best_solution_file:
        readme_lines.append(f"```{best_solution_file.suffix[1:]}\n{best_solution_file.read_text()}\n```")
    else:
        readme_lines.append("_Best solution not found._")

    # Write the README
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write("\n".join(readme_lines))

    print(f"✅ README generated for {problem_id_slug}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python generate_readme.py <problem_id_slug>")
    else:
        generate_readme(sys.argv[1])
