from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

from flask import Flask, render_template, request

app = Flask(__name__)

# --- Firebase (Firestore) optional setup ---
# This app will try to connect to Firebase if you set:
#   FIREBASE_SERVICE_ACCOUNT=C:\path\to\serviceAccount.json
#   FIREBASE_PROJECT_ID=your-project-id
# Otherwise it falls back to in-memory dummy data.

FIREBASE_READY = False
_firestore = None

try:
    import firebase_admin
    from firebase_admin import credentials, firestore

    service_account = os.getenv("FIREBASE_SERVICE_ACCOUNT", "").strip()
    project_id = os.getenv("FIREBASE_PROJECT_ID", "").strip()

    if service_account and project_id:
        if not firebase_admin._apps:
            cred = credentials.Certificate(service_account)
            firebase_admin.initialize_app(cred, {"projectId": project_id})
        _firestore = firestore.client()
        FIREBASE_READY = True
except Exception:
    # Keep the app running even if Firebase isn't configured.
    FIREBASE_READY = False
    _firestore = None


DUMMY_COURSES: List[Dict[str, Any]] = [
    {
        "id": "python-101",
        "title": "Python 101",
        "category": "Programming",
        "level": "Beginner",
        "duration": "6 weeks",
        "price": "Free",
        "instructor": "Ava Lin",
        "rating": 4.8,
        "lessons": 24,
        "projects": 3,
        "summary": "Learn Python from scratch with hands-on projects.",
        "outline": [
            "Variables and data types",
            "Control flow",
            "Functions and modules",
            "Files and APIs",
            "Mini-projects",
        ],
        "outcomes": [
            "Build 3 mini projects",
            "Write scripts that automate tasks",
            "Understand core Python syntax",
        ],
    },
    {
        "id": "web-flask",
        "title": "Flask Web Studio",
        "category": "Web Development",
        "level": "Intermediate",
        "duration": "4 weeks",
        "price": "$19",
        "instructor": "Nico Patel",
        "rating": 4.6,
        "lessons": 18,
        "projects": 2,
        "summary": "Build production-ready Flask apps with blueprints and APIs.",
        "outline": [
            "Flask fundamentals",
            "Templates and forms",
            "Databases",
            "Deployments",
        ],
        "outcomes": [
            "Design REST APIs",
            "Organize Flask apps",
            "Deploy to a cloud host",
        ],
    },
    {
        "id": "data-visual",
        "title": "Data Visualization",
        "category": "Data",
        "level": "All Levels",
        "duration": "3 weeks",
        "price": "$12",
        "instructor": "Rina Gomez",
        "rating": 4.7,
        "lessons": 15,
        "projects": 1,
        "summary": "Tell stories with data using Plotly and Matplotlib.",
        "outline": [
            "Chart types",
            "Color and perception",
            "Dashboards",
        ],
        "outcomes": [
            "Build a data story",
            "Design a dashboard",
            "Explain insights visually",
        ],
    },
]


def _load_courses() -> List[Dict[str, Any]]:
    if not FIREBASE_READY or _firestore is None:
        return DUMMY_COURSES

    # Firestore: collection "courses"
    try:
        docs = list(_firestore.collection("courses").stream())
        if not docs:
            # Seed dummy courses if collection is empty
            for course in DUMMY_COURSES:
                _firestore.collection("courses").document(course["id"]).set(course)
            return DUMMY_COURSES
        return [doc.to_dict() for doc in docs]
    except Exception:
        return DUMMY_COURSES


def _get_course(course_id: str) -> Optional[Dict[str, Any]]:
    if not FIREBASE_READY or _firestore is None:
        return next((c for c in DUMMY_COURSES if c["id"] == course_id), None)

    try:
        doc = _firestore.collection("courses").document(course_id).get()
        if doc.exists:
            return doc.to_dict()
    except Exception:
        return next((c for c in DUMMY_COURSES if c["id"] == course_id), None)
    return None


@app.get("/")
def index():
    courses = _load_courses()

    firebase_web_config = {
        "apiKey": os.getenv("FIREBASE_WEB_API_KEY", "").strip(),
        "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN", "").strip(),
        "projectId": os.getenv("FIREBASE_PROJECT_ID", "").strip(),
        "appId": os.getenv("FIREBASE_APP_ID", "").strip(),
        "messagingSenderId": os.getenv("FIREBASE_MESSAGING_SENDER_ID", "").strip(),
    }
    firebase_web_ready = all(firebase_web_config.values())

    return render_template(
        "index.html",
        courses=courses,
        firebase_ready=FIREBASE_READY,
        firebase_web_ready=firebase_web_ready,
        firebase_web_config=firebase_web_config,
    )


@app.get("/courses/<course_id>")
def course_detail(course_id: str):
    course = _get_course(course_id)
    if not course:
        return render_template("course.html", course=None), 404
    return render_template("course.html", course=course)


@app.post("/login")
def login():
    # Demo-only endpoint: no real auth performed
    email = request.form.get("email", "")
    return f"Logged in as {email}. (Server demo only)"


@app.post("/signup")
def signup():
    # Demo-only endpoint: no real auth performed
    name = request.form.get("name", "")
    email = request.form.get("email", "")
    return f"Account created for {name} ({email}). (Server demo only)"


if __name__ == "__main__":
    app.run(debug=True)
