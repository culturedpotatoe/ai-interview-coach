from flask import Flask, render_template, request, jsonify, session
import os, random, datetime

app = Flask(__name__, static_folder="static", template_folder="templates")
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key")

INTERVIEW_DATA = {
    "roles": ["Software Engineer","Product Manager","Data Analyst","DevOps Engineer","UI/UX Designer"],
    "technical": {
        "Software Engineer": [
            "Explain the difference between stack and queue data structures. When would you use each?",
            "How would you design a system to handle 1 million concurrent users?",
            "What is the time complexity of quicksort? Explain your reasoning.",
            "How would you implement an LRU cache?",
            "Explain the concept of database indexing and its trade-offs."
        ],
        "Product Manager": [
            "How would you prioritize features for a mobile app with limited development resources?",
            "Walk me through how you would launch a new product in a competitive market.",
            "How do you measure product success? What metrics would you track?",
            "Describe how you would conduct user research for a B2B product.",
            "How would you handle conflicting requirements from different stakeholders?"
        ],
        "Data Analyst": [
            "How would you identify and handle outliers in a dataset?",
            "Explain the difference between correlation and causation with examples.",
            "How would you design an A/B test for an e-commerce website?",
            "What statistical methods would you use to predict customer churn?",
            "How do you ensure data quality in your analysis process?"
        ],
        "DevOps Engineer": [
            "Explain the difference between containers and virtual machines.",
            "How would you implement a CI/CD pipeline for a microservices architecture?",
            "What strategies do you use for monitoring and alerting in production?",
            "How do you handle secrets management in a cloud environment?",
            "Explain Infrastructure as Code and its benefits."
        ],
        "UI/UX Designer": [
            "How do you approach designing for accessibility?",
            "Walk me through your design process for a mobile app.",
            "How do you conduct usability testing? What do you look for?",
            "How would you design for both iOS and Android platforms?",
            "How do you balance user needs with business requirements?"
        ]
    },
    "behavioral": [
        "Tell me about a time when you had to work with a difficult team member. How did you handle it?",
        "Describe a situation where you had to meet a tight deadline. What was your approach?",
        "Give me an example of a time when you made a mistake. How did you handle it?",
        "Tell me about a time when you had to learn something new quickly.",
        "Describe a situation where you had to influence someone without direct authority.",
        "Tell me about a project you're particularly proud of. What made it successful?",
        "Describe a time when you had to make a difficult decision with limited information.",
        "Tell me about a time when you had to adapt to a significant change at work."
    ]
}

def eval_technical(answer: str) -> tuple[int, list, list, str]:
    a = answer.lower()
    score = 1
    strengths, improvements = [], []
    if len(answer.split()) >= 80: score += 1; strengths.append("Comprehensive explanation")
    else: improvements.append("Add more detail and depth")
    if any(k in a for k in ["time complexity","big-o","o(","optimiz","scalab","trade-off","cache","index"]):
        score += 2; strengths.append("Good technical concepts referenced")
    elif any(k in a for k in ["algorithm","data structure","testing","example"]):
        score += 1; strengths.append("Solid technical understanding")
    if any(k in a for k in ["first","then","finally","step "]): score += 1; strengths.append("Clear structure")
    else: improvements.append("Organize answer into steps")
    if "example" not in a: improvements.append("Include a concrete example")
    return min(score,5), strengths, improvements, "Technical evaluation based on accuracy, structure, and depth"

def eval_behavioral(answer: str) -> tuple[int, list, list, str]:
    a = answer.lower()
    score = 1
    strengths, improvements = [], []
    got = {k:any(x in a for x in xs) for k,xs in {
        "situation":["situation","context","background"],
        "task":["task","responsib","goal","objective"],
        "action":["i ","decid","led","implemented","created","organized"],
        "result":["result","outcome","impact","increased","decreased","%"]
    }.items()}
    score += sum(1 for v in got.values() if v)
    for k,v in got.items():
        if v: strengths.append(f"{k.capitalize()} described")
        else: improvements.append(f"Add {k} details to complete STAR")
    if any(ch.isdigit() for ch in a): score += 1; strengths.append("Quantified results")
    else: improvements.append("Quantify outcomes where possible")
    return max(1,min(score,5)), strengths, improvements, "Behavioral evaluation using STAR method"

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api/start-interview", methods=["POST"])
def start_interview():
    data = request.get_json(force=True)
    role = data.get("role","")
    mode = data.get("interviewType","technical")
    bank = INTERVIEW_DATA["technical"].get(role, []) if mode=="technical" else INTERVIEW_DATA["behavioral"]
    questions = random.sample(bank, min(5, len(bank))) if bank else bank
    session["interview"] = {
        "role": role, "mode": mode, "questions": questions,
        "idx": 0, "scores": [], "feedback": [], "start": datetime.datetime.utcnow().isoformat()
    }
    return jsonify({
        "success": True,
        "question": questions,
        "question_number": 1,
        "total_questions": len(questions)
    })

@app.route("/api/submit-answer", methods=["POST"])
def submit_answer():
    if "interview" not in session: return jsonify({"error":"No active interview"}), 400
    ans = request.get_json(force=True).get("answer","")
    st = session["interview"]
    q = st["questions"][st["idx"]]
    if st["mode"]=="technical":
        score, strengths, improvements, msg = eval_technical(ans)
    else:
        score, strengths, improvements, msg = eval_behavioral(ans)
    st["scores"].append(score)
    st["feedback"].append({"score":score,"strengths":strengths,"improvements":improvements,"feedback":msg})
    st["idx"] += 1
    session["interview"] = st
    done = st["idx"] >= len(st["questions"])
    return jsonify({
        "success": True,
        "complete": done,
        "evaluation": {"score":score,"strengths":strengths,"improvements":improvements,"feedback":msg},
        "next_question": None if done else st["questions"][st["idx"]],
        "question_number": st["idx"]+1,
        "total_questions": len(st["questions"])
    })

@app.route("/api/get-summary")
def get_summary():
    if "interview" not in session: return jsonify({"error":"No interview"}), 400
    st = session["interview"]
    avg = sum(st["scores"])/len(st["scores"]) if st["scores"] else 0
    def level(s): 
        return "Excellent" if s>=4.5 else "Good" if s>=3.5 else "Average" if s>=2.5 else "Needs Improvement"
    strengths = []
    improvements = []
    for f in st["feedback"]:
        strengths += f.get("strengths",[])
        improvements += f.get("improvements",[])
    strengths = list(dict.fromkeys(strengths))[:6]
    improvements = list(dict.fromkeys(improvements))[:6]
    recs_by_role = {
        "Software Engineer":["LeetCode practice","System Design Primer","Cracking the Coding Interview"],
        "Product Manager":["Decode and Conquer","Exponent PM practice","User research guides"],
        "Data Analyst":["SQL HackerRank","Statistics refresher","Python for Data Analysis"],
        "DevOps Engineer":["Docker & Kubernetes","Cloud cert paths","IaC tutorials"],
        "UI/UX Designer":["Accessibility guidelines","Usability testing playbook","Figma advanced tutorials"]
    }
    recs = recs_by_role.get(st["role"],["Interview prep resources","Role-specific practice"])
    return jsonify({
        "overall_score": round(avg,1),
        "performance_level": level(avg),
        "question_scores": st["scores"],
        "strengths": strengths,
        "improvements": improvements,
        "recommendations": recs,
        "role": st["role"], "interview_type": st["mode"]
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
