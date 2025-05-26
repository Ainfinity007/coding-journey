import os
import subprocess

def open_reflection_file(problem_folder):
    reflection_path = os.path.join(problem_folder, "reflection.md")
    
    # Create reflection.md if it doesn't exist
    if not os.path.exists(reflection_path):
        with open(reflection_path, "w", encoding="utf-8") as f:
            f.write("# Reflection\n\nWrite your thoughts here...")

    # Open reflection.md in VS Code on Windows
    os.system(f'start code "{reflection_path}"')


def main():
    # After processing submission and archiving files:
    problem_folder = r"C:\Users\<You>\leetcode-uploader\archived\001_two_sum"

    # Trigger the reflection step (opens editor)
    open_reflection_file(problem_folder)

    # You can add code here to wait/poll for the reflection file to be saved
    # before moving on to git commit/push steps.

if __name__ == "__main__":
    main()
