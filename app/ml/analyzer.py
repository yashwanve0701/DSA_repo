import os
import joblib
from collections import defaultdict

# ---------------- LOAD MODEL ----------------
MODEL_PATH = os.path.join(
    os.path.dirname(__file__),
    "topic_mastery_model.pkl"
)

model = joblib.load(MODEL_PATH)

# ---------------- CONSTANTS ----------------
LABEL_MAP = {
    0: "Weak",
    1: "Average",
    2: "Strong"
}

TOPICS = [
    "Arrays", "Strings", "Two Pointers", "Stack", "Queue",
    "Linked List", "Binary Search", "Recursion", "Trees",
    "Heap", "Graphs", "Dynamic Programming"
]

EXPECTED_TIME = {
    "easy": 60,
    "medium": 120,
    "hard": 240
}

MAX_TIME_CAP = 600  # ⏱ cap per question (10 min)

PREREQ = {
    "Arrays": [],
    "Strings": ["Arrays"],
    "Two Pointers": ["Arrays"],
    "Stack": ["Arrays"],
    "Queue": ["Arrays"],
    "Linked List": ["Arrays"],
    "Binary Search": ["Arrays"],
    "Recursion": [],
    "Trees": ["Recursion"],
    "Heap": ["Arrays"],
    "Graphs": ["Trees"],
    "Dynamic Programming": ["Recursion"]
}

# ---------------- HELPERS ----------------
def extract_topic(title):
    title = title.lower()
    for t in TOPICS:
        if t.lower() in title:
            return t
    return None


def rule_based_level(accuracy):
    if accuracy >= 0.75:
        return 2
    elif accuracy >= 0.4:
        return 1
    return 0


# ---------------- MAIN ANALYZER ----------------
def analyze_test(test, progress_map):
    topic_stats = defaultdict(lambda: {
        "attempted": 0,
        "passed": 0,
        "total_time": 0,
        "easy": {"passed": 0, "total": 0},
        "medium": {"passed": 0, "total": 0},
        "hard": {"passed": 0, "total": 0},
    })

    # ---------- AGGREGATE QUESTION DATA ----------
    for q in test.questions:
        topic = extract_topic(q.title)
        if not topic:
            continue

        p = progress_map.get(q.id)
        if not p:
            continue

        diff = (q.difficulty or "").lower()
        if diff not in EXPECTED_TIME:
            continue

        stats = topic_stats[topic]

        # ⏱ CAP ABNORMAL TIME
        time_taken = min(p.time_taken or 0, MAX_TIME_CAP)

        stats["attempted"] += 1
        stats["total_time"] += time_taken
        stats[diff]["total"] += 1

        if p.status == "Passed":
            stats["passed"] += 1
            stats[diff]["passed"] += 1

    # ---------- ML + LOGIC ----------
    analysis = {
        "Weak": [],
        "Average": [],
        "Strong": []
    }

    topic_details = {}
    topic_levels = {}

    for topic, s in topic_stats.items():
        if s["attempted"] == 0:
            continue

        accuracy = s["passed"] / s["attempted"]
        avg_time = s["total_time"] / s["attempted"]

        def acc(d):
            return d["passed"] / d["total"] if d["total"] else 0

        easy_acc = acc(s["easy"])
        medium_acc = acc(s["medium"])
        hard_acc = acc(s["hard"])

        time_pressure = (
            EXPECTED_TIME["medium"] / avg_time if avg_time else 0
        )

        consistency = max(0.4, 1 - (hard_acc * 0.2))

        # ---------------- EASY-ONLY FALLBACK ----------------
        only_easy = (
            s["easy"]["total"] > 0 and
            s["medium"]["total"] == 0 and
            s["hard"]["total"] == 0
        )

        if only_easy and accuracy >= 0.8:
            final_level = 1  # Force Average
        else:
            X = [[
                accuracy,
                avg_time,
                s["attempted"],
                easy_acc,
                medium_acc,
                hard_acc,
                time_pressure,
                consistency
            ]]

            ml_level = model.predict(X)[0]
            rule_level = rule_based_level(accuracy)
            final_level = max(ml_level, rule_level)

        topic_levels[topic] = final_level
        analysis[LABEL_MAP[final_level]].append(topic)

        # -------- STORE DETAILS FOR GEMINI --------
        topic_details[topic] = {
            "level": LABEL_MAP[final_level],
            "accuracy": accuracy,
            "avg_time": avg_time,
            "easy_acc": easy_acc,
            "medium_acc": medium_acc,
            "hard_acc": hard_acc
        }

    # ---------- PREREQUISITE LOGIC ----------
    blocked = []
    recommended = None

    for topic, prereqs in PREREQ.items():
        if topic not in topic_levels:
            continue

        for p in prereqs:
            if topic_levels.get(p, 2) == 0:
                blocked.append(topic)

    for topic, level in topic_levels.items():
        if level == 0:
            recommended = topic
            break

    return {
        "analysis": analysis,
        "details": topic_details,
        "blocked": blocked,
        "recommended": recommended
    }
