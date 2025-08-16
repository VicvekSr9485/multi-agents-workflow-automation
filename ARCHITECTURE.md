# **Multi-Agent Workflow Automation — Architecture**

## **Overview**

This project is a multi-agent orchestration platform that automates business workflows such as **Product Research & Report Generation**. It uses **LangChain** to manage agents, **Google Gemini API** for AI reasoning, and **Pandas** for data analysis.
The system is composed of a **FastAPI backend** for orchestrating agents and data processing, and a **React (Vite + TypeScript + TailwindCSS)** frontend for user interaction.

---

## **System Architecture**

**Core components:**

* **Frontend (React + TypeScript)** — Provides an interface for starting workflows, displaying progress, and showing final reports.
* **Backend (FastAPI)** — Hosts the multi-agent orchestration, integrates external APIs, and returns processed results.
* **LangChain Agents** — Each agent is responsible for a specific workflow step.
* **Gemini API** — LLM powering reasoning, summarization, and drafting.
* **SerpAPI/Serper.dev Api** — Web search and scraping for relevant business/product data.
* **Pandas** — Data wrangling and insights generation.
* **Post-processing** — Final formatting and report generation.

---

## **Agent Workflow**

1. **Research Agent**

   * Uses **SerpAPI** to search for relevant product/business data.
   * Cleans and structures search results.

2. **Analysis Agent**

   * Uses **Pandas** to process data.
   * Generates metrics, charts, and actionable insights.

3. **Writer Agent**

   * Uses **Gemini API** to draft the business report.
   * Ensures report follows required tone/style.

4. **Reviewer Agent**

   * Uses **Gemini API** to critique and improve the draft.
   * Returns final polished version.

---

## **Backend Architecture**

**Framework:** FastAPI
**Folder Structure:**

```
backend/
│── main.py              # FastAPI entry point
│── agents/              # Agent logic & LangChain workflows
│   ├── research_agent.py
│   ├── analysis_agent.py
│   ├── writer_agent.py
│   ├── reviewer_agent.py
│── services/            # API integrations (Gemini, SerpAPI, etc.)
│   ├── gemini_service.py
│   ├── serpapi_service.py
│── routes/              # API route definitions
│   ├── research_routes.py
│── schemas/             # Pydantic models for request/response validation
│   ├── request.py
│   ├── response.py
│── tests/               # Pytest unit/integration tests
│── requirements.txt     # Python dependencies
```

**Backend Responsibilities:**

* Orchestrate agents via LangChain.
* Expose REST endpoints for frontend.
* Handle external API communication.
* Validate and sanitize input/output.
* Serve structured JSON for frontend consumption.

---

## **Frontend Architecture**

**Framework:** React + Vite + TypeScript + TailwindCSS
**Folder Structure:**

```
frontend/
│── src/
│   ├── components/       # Reusable UI components
│   ├── pages/            # Page-level components
│   ├── App.tsx
│   ├── main.tsx
│   ├── api.ts
│   ├── index.css
│── tailwind.config.js    # TailwindCSS configuration
│── package.json
```

**Frontend Responsibilities:**

* Provide clean UI to trigger workflows.
* Show progress updates via WebSockets or polling.
* Display final generated report and insights.
* Handle error states and retries gracefully.

---

## **Communication Flow**

```
Frontend → Backend API → Agents Workflow → External APIs → Analysis → Writer → Reviewer → Backend → Frontend
```

---

## **Key Advantages**

* Clear modularity (each agent in its own module).
* Scalable — new agents can be added without breaking others.
* Frontend and backend are loosely coupled via REST API.
* Easily extensible to other workflows (e.g., market analysis, competitor benchmarking).

---