import os
import sys
import json
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
DEESEEK_API_KEY = os.getenv("DEESEEK_API_KEY")

ARCHIVE_DIR = Path("C:/Users/Infinity/leetcode-uploader/archived")


def get_latest_problem_dir():
    dirs = [d for d in ARCHIVE_DIR.iterdir() if d.is_dir()]
    if not dirs:
        return None
    return max(dirs, key=lambda d: d.stat().st_ctime)


def call_deepseek(problem_description, language):
    url = "https://api.deepseek.com/v1/completions"
    headers = {
        "Authorization": f"Bearer {DEESEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    prompt = f"""
You are an expert in {language}.

Write the most optimal solution to the following problem in {language}. Include time and space complexity.

Problem:
{problem_description}
"""
    payload = {
        "model": "deepseek-coder",
        "prompt": prompt,
        "max_tokens": 800
    }
    response = requests.post(url, headers=headers, json=payload)
    result = response.json()
    return result.get("choices", [{}])[0].get("text", "").strip()


def update_readme_with_llm_code(readme_path, code_block, language):
    if not readme_path.exists():
        return
    with open(readme_path, "r", encoding="utf-8") as f:
        content = f.read()

    if "## Best Solution (LLM)" in content:
        content = content.split("## Best Solution (LLM)")[0].strip()

    content += f"\n\n## Best Solution (LLM)\n\n```{language}\n{code_block}\n```"

    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(content)


def fetch_and_save_best_solution(problem_dir):
    readme_path = problem_dir / "README.md"
    lang = "python" if any(f.suffix == ".py" for f in problem_dir.iterdir()) else "cpp"

    with open(readme_path, "r", encoding="utf-8") as f:
        problem_description = f.read()

    print(f"📡 Sending request to DeepSeek for: {problem_dir.name}")
    code = call_deepseek(problem_description, lang)

    output_file = problem_dir / f"best_solution.{ 'py' if lang == 'python' else 'cpp' }"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(code)

    update_readme_with_llm_code(readme_path, code, lang)
    print(f"✅ LLM solution saved to {output_file}")
    print(f"📝 README.md updated with LLM solution.")


if __name__ == "__main__":
    if len(sys.argv) == 2:
        dir_path = Path(sys.argv[1])
    else:
        dir_path = get_latest_problem_dir()
        if not dir_path:
            print("❌ No archived problems found.")
            sys.exit(1)

    fetch_and_save_best_solution(dir_path)
