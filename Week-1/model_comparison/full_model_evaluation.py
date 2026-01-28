"""
Full Evaluation Script:
- Generates outputs from GPT-4o, Claude Sonnet, Gemini Flash, DeepSeek
- Evaluates them using Claude Sonnet as a judge
- Saves outputs and structured JSON report
"""

import os
import json
import requests
from openai import OpenAI
from anthropic import Anthropic
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ======================
# CONFIGURATION
# ======================

# API Keys must be set in environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY",)
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

# File with evaluation prompt
EVAL_PROMPT_FILE = "evaluation_prompt.txt"

# ======================
# LOAD PROMPT
# ======================

with open(EVAL_PROMPT_FILE, "r") as f:
    PROMPT = f.read()

# ======================
# INITIALIZE CLIENTS
# ======================

# GPT-4o
openai_client = OpenAI(api_key=OPENAI_API_KEY)

# Claude
anthropic_client = Anthropic(api_key=ANTHROPIC_API_KEY)

# Gemini
genai.configure(api_key=GOOGLE_API_KEY)

# ======================
# MODEL CALL FUNCTIONS
# ======================

def run_gpt4o(prompt):
    resp = openai_client.responses.create(
        model="gpt-4o",
        input=prompt,
        max_output_tokens=1500
    )
    return resp.output_text

def run_claude(prompt):
    msg = anthropic_client.messages.create(
        model="claude-3-5-sonnet-latest",
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}]
    )
    return msg.content[0].text

def run_gemini(prompt):
    model = genai.GenerativeModel("gemini-1.5-flash")
    resp = model.generate_content(prompt)
    return resp.text

def run_deepseek(prompt):
    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2
    }
    res = requests.post(url, headers=headers, json=payload)
    return res.json()["choices"][0]["message"]["content"]

# ======================
# GENERATE OUTPUTS
# ======================

outputs = {}

print("Generating outputs from all models...")

outputs["GPT-4o"] = run_gpt4o(PROMPT)
outputs["Claude Sonnet"] = run_claude(PROMPT)
outputs["Gemini Flash"] = run_gemini(PROMPT)
outputs["DeepSeek"] = run_deepseek(PROMPT)

# Save raw outputs
for model, text in outputs.items():
    filename = f"output_{model.replace(' ', '_')}.txt"
    with open(filename, "w") as f:
        f.write(text)
    print(f"Saved {filename}")

# ======================
# JUDGE FUNCTION (Claude)
# ======================

def evaluate_output(model_name, model_output):
    """
    Uses Claude Sonnet to evaluate model output.
    Returns JSON structure with scores and strengths/weaknesses
    """
    eval_prompt = f"""
You are a neutral senior engineer evaluating AI model outputs.

MODEL NAME: {model_name}

OUTPUT:
{model_output}

Score each aspect from 1–5:
- AppDev Code Quality
- SQL Correctness
- DevOps Practicality
- Security & Best Practices
- Clarity & Explanations

List major strengths and weaknesses.
Return STRICT JSON format:
{{
  "model": "{model_name}",
  "scores": {{
    "appdev": 0,
    "sql": 0,
    "devops": 0,
    "security": 0,
    "clarity": 0
  }},
  "strengths": [],
  "weaknesses": [],
  "final_verdict": ""
}}
"""

    response = anthropic_client.messages.create(
        model="claude-3-5-sonnet-latest",
        max_tokens=800,
        messages=[{"role": "user", "content": eval_prompt}]
    )

    try:
        # Attempt to parse JSON from model
        return json.loads(response.content[0].text)
    except json.JSONDecodeError:
        # Fallback if model returns invalid JSON
        return {
            "model": model_name,
            "scores": {
                "appdev": 0,
                "sql": 0,
                "devops": 0,
                "security": 0,
                "clarity": 0
            },
            "strengths": [],
            "weaknesses": ["Invalid JSON returned by judge model"],
            "final_verdict": "Review Needed"
        }

# ======================
# RUN EVALUATION
# ======================

report = {}

print("Evaluating outputs with Claude Sonnet as judge...")

for model, text in outputs.items():
    report[model] = evaluate_output(model, text)
    print(f"Evaluated {model}")

# Save final report
with open("final_evaluation_report.json", "w") as f:
    json.dump(report, f, indent=2)

print("Final evaluation report saved as final_evaluation_report.json")
