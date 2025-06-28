# AI Resume Tailor & Interview Prep

## ✨ What does it do?

This application uses a team of specialised AI agents to:

1. Analyse a job description and identify the skills and experience employers are actually looking for.
2. Scan your existing resume and GitHub profile to understand your background.
3. Rewrite your resume so the most relevant accomplishments are front-and-centre.
4. Produce a custom list of interview questions and talking points that showcase your strengths.

All you need to provide is:

- the public URL of the job post
- a link to your GitHub profile
- a short personal write-up (optional)
- your current resume in Markdown

The finished documents are delivered as downloadable `.md` files you can tweak before sending.

## 🏃‍♂️ Quick start

### 1. Clone the repository

```bash
git clone <YOUR_REPO_URL_HERE>
cd <PROJECT_FOLDER_NAME>
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set environment variables

Create a `.env` file in the project root with:

```env
GOOGLE_API_KEY=<YOUR_GEMINI_KEY>
SERPER_API_KEY=<YOUR_SERPER_KEY>
```

### 4. Launch

```bash
streamlit run app.py
```

Visit the address shown in your terminal (usually http://localhost:8501).

## 🕹 How it works (under the hood)

The app is built on **CrewAI**, an orchestration framework that lets multiple agents collaborate on a single objective.

Agent lineup:
| Agent | Purpose |
|-------|---------|
| Job Researcher | Scrapes the job posting and extracts hard/soft requirements |
| Personal Profiler | Builds a structured profile from your GitHub + write-up |
| Resume Strategist | Re-writes your resume focusing on employer priorities |
| Interview Coach | Generates questions & key points to practice |

They communicate using shared context so each step feeds the next.

Key libraries & services:

- Streamlit – lightweight UI layer
- Google Gemini – language model used by the agents
- Serper API – Google-like web search API
- BeautifulSoup & Requests via CrewAI tools for website scraping

## 📂 Repository layout

- `app.py` – Streamlit front-end & agent orchestration
- `db/` – chroma vectorstore (created at runtime)
- `requirements.txt` – python package list
- `example_resume.md` – sample input resume
- `tailored_resume.md` – generated output (only after a run)
- `interview_materials.md` – generated output (only after a run)

---

### 🔧 Placeholders to replace

- `<YOUR_REPO_URL_HERE>` – repository url
- `<PROJECT_FOLDER_NAME>` – folder name of your clone
- `<YOUR_GEMINI_KEY>` – Google Generative AI key
- `<YOUR_SERPER_KEY>` – Serper key
