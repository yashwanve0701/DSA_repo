import google.generativeai as genai
import os


genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-2.5-flash")


def explain_topic(topic, level, stats):
    """
    stats = {
      accuracy,
      avg_time,
      easy_acc,
      medium_acc,
      hard_acc
    }
    """

    prompt = f"""
You are a DSA mentor helping a student improve.

Topic: {topic}
Current Level: {level}

Performance details:
- Accuracy: {stats['accuracy']:.2f}
- Average time per question: {int(stats['avg_time'])} seconds
- Easy accuracy: {stats['easy_acc']:.2f}
- Medium accuracy: {stats['medium_acc']:.2f}
- Hard accuracy: {stats['hard_acc']:.2f}

Task:
Explain WHY the student is at this level.
Give clear, motivating advice.
Mention what to improve and what to practice next.

Rules:
- Use simple language
- 3–4 sentences only
- No emojis
- No markdown
"""

    response = model.generate_content(prompt)
    return response.text.strip()
