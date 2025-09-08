// Helpers
const $ = (s) => document.querySelector(s);
const show = (id) => document.querySelectorAll('.screen').forEach(el => el.id === id ? el.classList.remove('hidden') : el.classList.add('hidden'));
const loading = (on) => $('#loading').classList.toggle('hidden', !on);

// State
let total = 5;
let current = 1;

// Elements
const startBtn = $('#startBtn');
const setupForm = $('#setupForm');
const counter = $('#counter');
const questionEl = $('#question');
const answerEl = $('#answer');
const progressFill = $('#progressFill');
const submitBtn = $('#submitBtn');
const skipBtn = $('#skipBtn');
const continueBtn = $('#continueBtn');

// Feedback elements
const scoreVal = $('#scoreVal');
const feedbackText = $('#feedbackText');
const strengths = $('#strengths');
const improvements = $('#improvements');

// Summary elements
const overallScore = $('#overallScore');
const perfLevel = $('#perfLevel');
const qScores = $('#qScores');
const sumStrengths = $('#sumStrengths');
const sumImprovements = $('#sumImprovements');
const recs = $('#recs');
const restartBtn = $('#restartBtn');

// Navigation
startBtn.addEventListener('click', () => show('setupScreen'));

setupForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  const role = $('#role').value;
  const interviewType = setupForm.mode.value;
  const domain = $('#domain').value || '';
  loading(true);
  try {
    const res = await fetch('/api/start-interview', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ role, interviewType, domain })
    });
    const data = await res.json();
    total = data.total_questions;
    current = data.question_number;
    updateCounter();
    questionEl.textContent = data.question;
    answerEl.value = '';
    show('interviewScreen');
  } finally {
    loading(false);
  }
});

function updateCounter() {
  counter.textContent = `Question ${current} of ${total}`;
  progressFill.style.width = `${Math.round((current-1)/total*100)}%`;
}

async function submitAnswer(skip=false) {
  const answer = skip ? '' : answerEl.value.trim();
  loading(true);
  try {
    const res = await fetch('/api/submit-answer', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ answer })
    });
    const data = await res.json();

    // Show per-question feedback
    scoreVal.textContent = data.evaluation.score.toFixed(0);
    feedbackText.textContent = data.evaluation.feedback;
    strengths.innerHTML = (data.evaluation.strengths || []).map(s => `<li>${s}</li>`).join('');
    improvements.innerHTML = (data.evaluation.improvements || []).map(s => `<li>${s}</li>`).join('');
    show('feedbackScreen');

    // If complete, prep summary on continue
    continueBtn.onclick = async () => {
      if (data.complete) {
        loading(true);
        const sumRes = await fetch('/api/get-summary');
        const summary = await sumRes.json();
        loading(false);
        overallScore.textContent = summary.overall_score.toFixed(1);
        perfLevel.textContent = summary.performance_level;
        qScores.innerHTML = summary.question_scores.map((s, i) => `<span class="chip">Q${i+1}: ${s}/5</span>`).join(' ');
        sumStrengths.innerHTML = summary.strengths.map(s => `<li>${s}</li>`).join('');
        sumImprovements.innerHTML = summary.improvements.map(s => `<li>${s}</li>`).join('');
        recs.innerHTML = summary.recommendations.map(s => `<li>${s}</li>`).join('');
        show('summaryScreen');
      } else {
        // Next question
        current = data.question_number;
        updateCounter();
        questionEl.textContent = data.next_question;
        answerEl.value = '';
        show('interviewScreen');
      }
    };
  } finally {
    loading(false);
  }
}

submitBtn.addEventListener('click', () => submitAnswer(false));
skipBtn.addEventListener('click', () => submitAnswer(true));
restartBtn?.addEventListener('click', () => location.reload());
