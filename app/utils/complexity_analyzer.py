import json
import google.generativeai as genai

genai.configure(api_key="AIzaSyDnl4X7zCEOMdTW0oZD7NJERs-oE8i5SIM")

model = genai.GenerativeModel("gemini-2.5-flash")

def analyze_time_complexity(code, problem, language):
    prompt = f"""
You are a DSA expert.

Analyze the following code and determine:
1. Time Complexity used by the code
2. Best possible time complexity for this problem

Respond ONLY in valid JSON. No markdown.

JSON format:
{{
  "used": "O(...)",
  "best": "O(...)",
  "explanation": "short explanation"
}}

Problem:
{problem}

Language:
{language}

Code:
{code}
"""

    response = model.generate_content(prompt)

    raw = response.text.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()

    try:
        return json.loads(raw)   # ✅ RETURN DICT
    except Exception as e:
        return {
            "used": "Unknown",
            "best": "Unknown",
            "explanation": f"AI parsing failed: {str(e)}"
        }
