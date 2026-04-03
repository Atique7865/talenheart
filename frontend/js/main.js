/* ================================================================
   TalentHeart – Main JavaScript
   ================================================================ */

const API = "";   // same origin

/* ── Animate on scroll ── */
const observer = new IntersectionObserver(entries => {
  entries.forEach(e => { if (e.isIntersecting) e.target.classList.add("visible"); });
}, { threshold: 0.1 });
document.querySelectorAll(".fade-up").forEach(el => observer.observe(el));

/* ── Active nav link ── */
document.querySelectorAll(".nav-link[href]").forEach(link => {
  if (link.href === location.href) link.classList.add("active");
});

/* ── Job Listings (jobs.html) ── */
async function loadJobs(country = "", type = "") {
  const container = document.getElementById("jobs-container");
  if (!container) return;
  container.innerHTML = `<div class="col-12 text-center py-5"><div class="spinner-border text-danger"></div></div>`;
  try {
    const params = new URLSearchParams();
    if (country) params.set("country", country);
    if (type)    params.set("type", type);
    const res  = await fetch(`${API}/api/jobs/?${params}`);
    const jobs = await res.json();
    if (!jobs.length) {
      container.innerHTML = `<div class="col-12 text-center py-5 text-muted"><i class="bi bi-briefcase fs-1 d-block mb-3"></i>No jobs found for the selected filters.</div>`;
      return;
    }
    container.innerHTML = jobs.map(job => jobCard(job)).join("");
    // Animate
    container.querySelectorAll(".fade-up").forEach(el => observer.observe(el));
  } catch (e) {
    container.innerHTML = `<div class="col-12 text-center py-5 text-danger">Error loading jobs. Please try again.</div>`;
  }
}

function jobCard(job) {
  const countryColors = { Japan: "danger", UAE: "primary", "Saudi Arabia": "warning", Qatar: "info", Germany: "success", Poland: "secondary" };
  const color = countryColors[job.country] || "secondary";
  return `
  <div class="col-md-6 col-lg-4 fade-up">
    <div class="job-card p-4 h-100 d-flex flex-column">
      <div class="d-flex justify-content-between align-items-start mb-3">
        <span class="job-badge bg-${color} bg-opacity-10 text-${color}">${job.flag || ""} ${job.country}</span>
        <span class="job-badge bg-light text-muted">${job.type}</span>
      </div>
      <h5 class="fw-bold mb-1">${job.title}</h5>
      <p class="salary-text mb-3">${job.salary}</p>
      ${job.salary_bdt ? `<p class="text-muted small mb-3">≈ ${job.salary_bdt}</p>` : ""}
      <ul class="list-unstyled small text-muted mb-4 flex-grow-1">
        ${(job.requirements || []).map(r => `<li class="mb-1"><i class="bi bi-check-circle-fill text-success me-2"></i>${r}</li>`).join("")}
      </ul>
      ${job.deadline ? `<p class="small text-muted mb-3"><i class="bi bi-calendar3 me-1"></i>Deadline: ${job.deadline}</p>` : ""}
      <a href="apply.html?job_id=${job._id}&job_title=${encodeURIComponent(job.title)}&country=${encodeURIComponent(job.country)}"
         class="btn btn-primary-th w-100 mt-auto">Apply Now →</a>
    </div>
  </div>`;
}

/* ── Homepage featured jobs ── */
async function loadFeaturedJobs() {
  const container = document.getElementById("featured-jobs");
  if (!container) return;
  try {
    const res  = await fetch(`${API}/api/jobs/`);
    const jobs = await res.json();
    container.innerHTML = jobs.slice(0, 6).map(job => jobCard(job)).join("");
    container.querySelectorAll(".fade-up").forEach(el => observer.observe(el));
  } catch (e) { /* silent */ }
}

/* ── Apply Form ── */
function initApplyForm() {
  const form = document.getElementById("apply-form");
  if (!form) return;

  // Pre-fill from URL params
  const p = new URLSearchParams(location.search);
  ["job_id","job_title","country"].forEach(k => {
    const el = document.getElementById(k);
    if (el && p.get(k)) el.value = p.get(k);
  });

  form.addEventListener("submit", async e => {
    e.preventDefault();
    const btn = form.querySelector("[type=submit]");
    btn.disabled = true; btn.innerHTML = `<span class="spinner-border spinner-border-sm me-2"></span>Submitting...`;
    try {
      const fd = new FormData(form);
      const res = await fetch(`${API}/api/applications/`, { method: "POST", body: fd });
      const data = await res.json();
      if (res.ok) {
        form.innerHTML = `
          <div class="text-center py-5">
            <div class="fs-1 mb-3">🎉</div>
            <h3 class="fw-bold text-success">Application Submitted!</h3>
            <p class="text-muted mt-2">Thank you <strong>${form.querySelector('[name=name]')?.value || ''}</strong>. We'll contact you within 48 hours.</p>
            <a href="jobs.html" class="btn btn-primary-th mt-3">Browse More Jobs</a>
          </div>`;
      } else {
        alert("Error: " + (data.error || "Submission failed"));
        btn.disabled = false; btn.innerHTML = "Submit Application";
      }
    } catch (err) {
      alert("Network error. Please try again.");
      btn.disabled = false; btn.innerHTML = "Submit Application";
    }
  });
}

/* ── Salary Calculator ── */
function initSalaryCalc() {
  const btn = document.getElementById("calc-btn");
  if (!btn) return;
  btn.addEventListener("click", () => {
    const country = document.getElementById("calc-country").value;
    const job     = document.getElementById("calc-job").value;
    const exp     = parseInt(document.getElementById("calc-exp").value) || 0;

    const base = {
      japan_factory: 160000, japan_construction: 170000, japan_care: 180000,
      uae_engineer: 5000,    uae_driver: 3000,
      saudi_labor: 1200,     saudi_cleaner: 900,
      germany_warehouse: 2200, germany_driver: 2500,
      qatar_electrician: 2500
    };
    const rates = { japan: 0.71, uae: 29.6, saudi: 28.6, germany: 119, qatar: 29.6 };
    const key  = `${country}_${job}`;
    const val  = base[key];
    if (!val) { document.getElementById("calc-result").style.display = "none"; return; }
    const bonus = exp >= 3 ? 1.15 : exp >= 1 ? 1.08 : 1;
    const final = Math.round(val * bonus);
    const rate  = rates[country] || 1;
    const bdt   = Math.round(final * rate).toLocaleString();

    const symbols = { japan: "¥", uae: "AED ", saudi: "SAR ", germany: "€", qatar: "QAR " };
    const sym = symbols[country] || "";
    document.getElementById("calc-amount").textContent = `${sym}${final.toLocaleString()} / month`;
    document.getElementById("calc-bdt").textContent    = `≈ ৳${bdt} BDT`;
    document.getElementById("calc-result").style.display = "block";
  });

  document.getElementById("calc-country")?.addEventListener("change", updateJobOptions);
}

function updateJobOptions() {
  const country = document.getElementById("calc-country").value;
  const jobSel  = document.getElementById("calc-job");
  const opts = {
    japan:   [["factory","Factory Worker"],["construction","Construction Worker"],["care","Care Worker"]],
    uae:     [["engineer","Civil Engineer"],["driver","Truck Driver"]],
    saudi:   [["labor","General Labor"],["cleaner","Cleaner"]],
    germany: [["warehouse","Warehouse Operator"],["driver","Truck Driver"]],
    qatar:   [["electrician","Electrician"]]
  };
  jobSel.innerHTML = (opts[country] || []).map(([v,l]) => `<option value="${v}">${l}</option>`).join("");
}

/* ── Eligibility Quiz ── */
const quizData = [
  { q: "What is your age group?", opts: ["18-25","26-35","36-45","46+"], key: "age" },
  { q: "What is your education level?", opts: ["Primary","SSC/HSC","Diploma","Bachelor's+"], key: "edu" },
  { q: "Do you have a valid passport?", opts: ["Yes, valid 5+ years","Yes, needs renewal","No passport yet"], key: "passport" },
  { q: "What is your work experience?", opts: ["No experience","1-2 years","3-5 years","5+ years"], key: "exp" },
  { q: "Do you speak any foreign language?", opts: ["None","Basic English","Fluent English","Japanese/Arabic/German"], key: "lang" },
];
let quizAnswers = {};
let quizStep = 0;

function initQuiz() {
  const q = document.getElementById("quiz-question");
  if (!q) return;
  renderQuiz();
}

function renderQuiz() {
  const step = quizData[quizStep];
  document.getElementById("quiz-question").textContent = step.q;
  document.getElementById("quiz-step").textContent = `Question ${quizStep + 1} of ${quizData.length}`;
  document.getElementById("quiz-progress-fill").style.width = `${(quizStep / quizData.length) * 100}%`;
  const optsDiv = document.getElementById("quiz-options");
  optsDiv.innerHTML = step.opts.map((o, i) => `
    <div class="quiz-option mb-2 ${quizAnswers[step.key] === i ? 'selected' : ''}" onclick="selectQuizOpt(${i})" data-idx="${i}">
      ${o}
    </div>`).join("");
}

function selectQuizOpt(idx) {
  quizAnswers[quizData[quizStep].key] = idx;
  document.querySelectorAll(".quiz-option").forEach((el, i) => el.classList.toggle("selected", i === idx));
  setTimeout(() => {
    if (quizStep < quizData.length - 1) { quizStep++; renderQuiz(); }
    else showQuizResult();
  }, 400);
}

function showQuizResult() {
  let score = 0;
  const a = quizAnswers;
  if (a.age === 1 || a.age === 0) score += 25;
  else if (a.age === 2) score += 15;
  if (a.edu >= 2) score += 25;
  else if (a.edu === 1) score += 15;
  if (a.passport === 0) score += 20;
  else if (a.passport === 1) score += 10;
  if (a.exp >= 2) score += 20;
  else if (a.exp === 1) score += 12;
  if (a.lang >= 2) score += 10;
  else if (a.lang === 1) score += 5;

  let msg, color, emoji;
  if (score >= 80) { msg = "Excellent! You are highly eligible."; color = "success"; emoji = "🌟"; }
  else if (score >= 55) { msg = "Good. You qualify for many positions."; color = "primary"; emoji = "✅"; }
  else if (score >= 35) { msg = "Moderate. With some preparation, you can qualify."; color = "warning"; emoji = "⚠️"; }
  else { msg = "Don't worry! We can guide you to get started."; color = "danger"; emoji = "💪"; }

  document.getElementById("quiz-body").innerHTML = `
    <div class="text-center py-3">
      <div class="fs-1 mb-2">${emoji}</div>
      <h4 class="fw-bold">Eligibility Score: ${score}/100</h4>
      <div class="progress mb-3" style="height:12px;border-radius:6px">
        <div class="progress-bar bg-${color}" style="width:${score}%"></div>
      </div>
      <p class="text-${color} fw-semibold">${msg}</p>
      <a href="apply.html" class="btn btn-primary-th mt-2">Apply Now</a>
      <button class="btn btn-outline-secondary mt-2 ms-2" onclick="resetQuiz()">Retake Quiz</button>
    </div>`;
}

function resetQuiz() {
  quizStep = 0; quizAnswers = {};
  document.getElementById("quiz-body").innerHTML = `
    <p id="quiz-step" class="text-muted small mb-3"></p>
    <div class="quiz-progress mb-4"><div id="quiz-progress-fill" class="quiz-progress-fill" style="width:0%"></div></div>
    <p id="quiz-question" class="fw-bold fs-5 mb-4"></p>
    <div id="quiz-options"></div>`;
  renderQuiz();
}

/* ── Contact Form ── */
function initContactForm() {
  const form = document.getElementById("contact-form");
  if (!form) return;
  form.addEventListener("submit", async e => {
    e.preventDefault();
    const btn = form.querySelector("[type=submit]");
    btn.disabled = true;
    btn.innerHTML = `<span class="spinner-border spinner-border-sm me-2"></span>Sending...`;
    try {
      const fd = new FormData(form);
      const body = {};
      fd.forEach((v, k) => { body[k] = v; });
      const res = await fetch(`${API}/api/contact/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body)
      });
      const data = await res.json();
      if (res.ok) {
        form.innerHTML = `<div class="text-center py-4"><div class="fs-1">✅</div><h4 class="fw-bold mt-2">Message Sent!</h4><p class="text-muted">We'll get back to you within 24 hours.</p></div>`;
      } else {
        alert("Error: " + (data.error || "Submission failed"));
        btn.disabled = false;
        btn.innerHTML = "Send Message ✉️";
      }
    } catch (err) {
      alert("Network error. Please try again.");
      btn.disabled = false;
      btn.innerHTML = "Send Message ✉️";
    }
  });
}

/* ── Init ── */
document.addEventListener("DOMContentLoaded", () => {
  loadFeaturedJobs();
  loadJobs(
    new URLSearchParams(location.search).get("country") || "",
    new URLSearchParams(location.search).get("type") || ""
  );
  initApplyForm();
  initSalaryCalc();
  updateJobOptions();
  initQuiz();
  initContactForm();
});
