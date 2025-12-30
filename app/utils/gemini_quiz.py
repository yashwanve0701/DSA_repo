import json
import google.generativeai as genai
import os
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def generate_mcq_quiz(topic_title):
    """
    Returns:
    [
      {
        "question": "...",
        "options": ["A", "B", "C", "D"],
        "correct_index": 1
      }
    ]
    """

    prompt = f"""
You are a computer science instructor.

Generate EXACTLY 5 multiple choice questions for the topic:
"{topic_title}"

Rules:
- Difficulty: Medium
- Each question must have 4 options
- Only ONE correct option
- Return ONLY valid JSON
- No markdown
- No explanations

JSON format:
[
  {{
    "question": "...",
    "options": ["...", "...", "...", "..."],
    "correct_index": 0
  }}
]
"""

    model = genai.GenerativeModel("gemini-2.5-flash")
    response = model.generate_content(prompt)

    raw = response.text.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()

    quiz = json.loads(raw)

    # Basic validation
    if not isinstance(quiz, list) or len(quiz) != 5:
        raise ValueError("Invalid quiz format from Gemini")

    return quiz
