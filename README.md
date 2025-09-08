# AI Interview Coach

LLM-powered interview simulator for technical and behavioral interviews that asks role-specific questions, scores answers, and provides feedback with a final summary report.  

## Quick start
1) Create a virtualenv and install: `pip install -r requirements.txt`  
2) Copy `.env.example` to `.env` and set `SECRET_KEY`.  
3) Run backend: `python app.py`, then open http://localhost:5000  

## Features
- Role and mode selection (technical/behavioral)  
- 3–5 question session with scoring and feedback  
- Final strengths, improvements, and recommendations  

## Structure
- `app.py` (Flask API and scoring)  
- `templates/index.html` (UI)  
- `static/app.js`, `static/style.css` (logic and styling)  

## Live demo (UI reference)
https://ppl-ai-code-interpreter-files.s3.amazonaws.com/web/direct-files/2378e86623b58defa38c19235897f7a7/9a5e55a9-8a87-4213-9954-84168e9ca2f1/index.html
