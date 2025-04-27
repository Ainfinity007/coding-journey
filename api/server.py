import os
import time
import sqlite3
from flask import Flask, request, jsonify
from git import Repo
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

app = Flask(__name__)
repo = Repo(os.getcwd())

# Initialize CodeLlama
model = AutoModelForCausalLM.from_pretrained(
    os.path.expanduser('~/.cache/huggingface/codellama-7b'),
    device_map="auto",
    torch_dtype=torch.float16
)
tokenizer = AutoTokenizer.from_pretrained("codellama/CodeLlama-7b-hf")

def analyze_code(title, code):
    prompt = f"""Analyze this coding problem:
    Problem: {title}
    Code: {code[:500]}
    
    Tags (comma-separated):
    Difficulty (Easy/Medium/Hard):"""
    
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    output = model.generate(**inputs, max_length=500)
    analysis = tokenizer.decode(output[0], skip_special_tokens=True)
    
    tags = analysis.split('Tags:')[-1].split('Difficulty:')[0].strip().split(',')
    difficulty = analysis.split('Difficulty:')[-1].strip().split('\n')[0]
    
    return tags[:3], difficulty

@app.route('/log', methods=['POST'])
def handle_submission():
    data = request.json()
    
    # Save solution
    filename = f"data/solutions/{data['title'].replace(' ', '_')}.py"
    with open(filename, 'w') as f:
        f.write(data['code'])
    
    # AI Analysis
    tags, difficulty = analyze_code(data['title'], data['code'])
    
    # Update database
    conn = sqlite3.connect('data/solutions.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS problems
                 (title TEXT, tags TEXT, difficulty TEXT, timestamp DATETIME)''')
    c.execute("INSERT INTO problems VALUES (?,?,?,?)",
              (data['title'], ','.join(tags), difficulty, time.time()))
    conn.commit()
    
    # Git commit
    repo.git.add(all=True)
    repo.git.commit('-m', f"Auto: {data['title']}")
    repo.git.push()
    
    return jsonify(status="success")

if __name__ == '__main__':
    app.run(port=5000)
