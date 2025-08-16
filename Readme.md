# Multi-Agent Workflow Automation (Business Process Orchestrator)

## Overview

This project demonstrates an **AI-powered multi-agent system** that automates a real-world business workflow — in this case, **Product Research & Report Generation**.
It uses **LangChain**, **Google Gemini API**, and a coordinated set of AI agents to research, analyze, write, and review reports automatically.
The application is powered by **FastAPI** for the backend and **React + TailwindCSS** for the frontend.

## Features

* **Research Agent** – Searches the web for relevant information.
* **Analysis Agent** – Processes and summarizes collected data.
* **Writer Agent** – Drafts business reports in a specific style.
* **Reviewer Agent** – Critiques and improves the final report.
* **Multi-Agent Orchestration** – Agents communicate and coordinate via LangChain workflows.
* **Web Interface** – Allows users to initiate workflows and download reports.

## Tech Stack

* **Backend:** FastAPI, LangChain, Google Gemini API, Pandas, BeautifulSoup4, SerpAPI
* **Frontend:** React (Vite + TypeScript), TailwindCSS
* **Orchestration:** LangChain Agents, Tools, Chains
* **Deployment:** Vercel (Frontend), Render / Railway / Docker (Backend)

## Installation

### 1️⃣ Backend Setup

```bash
# Clone the repository
git clone https://github.com/VicvekSr9485/Multi-Agent-Workflow-Automation.git
cd Multi-Agent-Workflow-Automation/backend

# Create a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

**Run the backend**

```bash
uvicorn main:app --reload
```

---

### 2️⃣ Frontend Setup

```bash
cd ../frontend/multi-agent-frontend



# Install dependencies (stable TailwindCSS)
npm install

```

**Run the frontend**

```bash
npm run dev
```

---

## Environment Variables

Create a `.env` file in the **backend** directory:

```env
GEMINI_API_KEY=your_google_gemini_key
SERPAPI_API_KEY=your_serpapi_key
```

---

## Usage

1. Open the frontend in your browser.
2. Enter a **product name** or topic to research.
3. Agents will collaborate to:

   * Search online for data.
   * Summarize insights.
   * Draft and review a business report.
4. Download the generated report.

---