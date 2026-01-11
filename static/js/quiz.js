let questions = [];
let currentIdx = 0;
let score = 0;
let startTime = Date.now();

async function initQuiz() {
    const res = await fetch('/api/quiz');
    questions = await res.json();
    render();
}

function render() {
    const container = document.getElementById('quiz-content');

    if (currentIdx >= questions.length) {
        container.innerHTML = "<h2>Analyzing Results...</h2>";
        submitToML();
        return;
    }

    const q = questions[currentIdx];
    container.innerHTML = `
        <h2 style="margin-bottom:20px;">${q.question}</h2>
        <div class="options-grid">
            ${q.options
                .map(
                    opt =>
                        `<button class="option-btn" onclick="handleAns('${opt}')">${opt}</button>`
                )
                .join("")}
        </div>
    `;
}

function handleAns(selected) {
    if (selected === questions[currentIdx].answer) {
        score++;
    }
    currentIdx++;
    render();
}

// ---------------- ML + FUTURE SCORE ----------------
async function submitToML() {
    const timeTaken = Math.floor((Date.now() - startTime) / 1000);
    const finalScore = (score / questions.length) * 100;

    try {
        // ---------- 1️⃣ Tutoring Recommendation ----------
        const res = await fetch('/api/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                score: finalScore,
                time_taken: timeTaken
            })
        });

        const data = await res.json();

        localStorage.setItem('userScore', finalScore.toFixed(2));
        localStorage.setItem('mlMessage', data.message);

        // ---------- 2️⃣ Future Score Prediction ----------
        const futureRes = await fetch('/api/future-score', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                score: finalScore,
                max_score: 100,
                time_taken: timeTaken,
                attempt_number: 1,
                subject_encoded: 1,
                grade_level_encoded: 10
            })
        });

        const futureData = await futureRes.json();

        if (futureData.future_score !== undefined) {
            localStorage.setItem(
                'futureScore',
                futureData.future_score.toFixed(2)
            );
        }

        // ---------- 3️⃣ Redirect ----------
        window.location.href = '/result';

    } catch (error) {
        console.error("ML Error:", error);
        alert("Something went wrong while analyzing your result.");
    }
}

initQuiz();
