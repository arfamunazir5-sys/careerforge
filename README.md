# CareerForge

### AI-Powered Career Resource Allocation & Weekly Planning

CareerForge is an AI-driven career planning web application that treats **career growth as a resource-allocation problem**.

Instead of giving every career activity equal attention, CareerForge uses four specialized domain agents — **Skill Building, Networking, Portfolio, and Interview Prep** — that compete for a user's limited weekly time budget. A coordinator evaluates their bids and allocates time according to the user's career goals and current progress.

> **Built as a final-year BCA project — 2026**

---

## Live Application

| Component             | Link                                               |
| --------------------- | -------------------------------------------------- |
| **Frontend**          | https://careerforge-five-tau.vercel.app/           |
| **Backend API**       | https://careerforge-backend-lo7f.onrender.com      |
| **API Documentation** | https://careerforge-backend-lo7f.onrender.com/docs |

---

## What CareerForge Does

CareerForge helps users turn their career goals into a practical weekly action plan.

The system:

* Analyzes the user's career profile and current progress
* Considers the user's target role
* Calculates competing priorities across career domains
* Uses domain agents to submit time-allocation bids
* Coordinates those bids within a fixed weekly time budget
* Generates concrete weekly tasks
* Tracks task completion and ignored tasks
* Applies rewards and maintains a career streak
* Calculates a **Career Health Score**
* Explains why time was allocated to each domain
* Exports the weekly plan to a calendar-compatible `.ics` file

---

## Core Architecture

```text
                    ┌─────────────────────┐
                    │      User Profile   │
                    │  Target Role + Data │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   Profile Analysis  │
                    │ Resume + Portfolio  │
                    └──────────┬──────────┘
                               │
                               ▼
              ┌──────────────────────────────────┐
              │         Domain Agents            │
              │                                  │
              │  Skill Building   Networking     │
              │  Portfolio        Interview Prep │
              └────────────────┬─────────────────┘
                               │
                            Bids ▼
                    ┌─────────────────────┐
                    │ Bidding Coordinator │
                    │ Role-Weighted       │
                    │ Allocation          │
                    └──────────┬──────────┘
                               │
                         Allocated Hours
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Weekly Plan         │
                    │ Generator           │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Progress + Rewards  │
                    │ + Career Health     │
                    │ + Explainability    │
                    └─────────────────────┘
```

---

## Modules

### 1. Onboarding & Career Goal

* Target role selection
* Career goal configuration
* Role-specific weighting profiles

### 2. Profile Analysis

* Resume analysis
* Resume score
* GitHub portfolio scanning
* Portfolio score

### 3. Skill Dependency Graph

* Prerequisite-aware skill recommendations
* Identifies the next relevant skill to develop

### 4. Domain Agents

Four specialized agents independently evaluate the user's needs:

* **Skill Building**
* **Networking**
* **Portfolio**
* **Interview Prep**

Each agent produces a bid based on the user's current career state.

### 5. Bidding Coordinator

The coordinator evaluates the agents' bids and distributes the available weekly hours while considering the user's target role.

### 6. Weekly Plan Generator

Converts the final allocation into concrete, actionable weekly tasks.

### 7. Progress Tracking & Reward Loop

Tracks:

* Completed tasks
* Ignored tasks
* Weekly progress
* Career streak
* Reward signals

### 8. Dashboard & Explainability

Provides:

* **Career Health Score**
* Module-level scores
* Visual progress bars
* Plain-language explanations for the weekly allocation

### 9. Calendar Export

Exports the generated weekly plan as a standard **`.ics` calendar file** that can be imported into calendar applications.

---

## Career Health Score

CareerForge provides a high-level view of the user's career readiness through four module scores:

| Module         | Description                           |
| -------------- | ------------------------------------- |
| **Resume**     | Resume/profile strength               |
| **Portfolio**  | Project and portfolio strength        |
| **Networking** | Networking activity and readiness     |
| **Interview**  | Interview preparation and performance |

The dashboard combines these module scores into an overall **Career Health Score** and provides explanations for the current weekly allocation.

---

## Tech Stack

### Backend

* Python
* FastAPI
* Pydantic
* JSON-based state storage
* GitHub REST API
* Pytest

### Frontend

* React
* Vite
* JavaScript
* CSS

### Deployment

* **Backend:** Render
* **Frontend:** Vercel

---

## Project Structure

```text
careerforge/
│
├── backend/
│   ├── app/
│   │   ├── agents/
│   │   ├── analysis/
│   │   ├── export/
│   │   ├── insights/
│   │   ├── plan/
│   │   ├── state/
│   │   ├── tracker/
│   │   └── main.py
│   │
│   ├── tests/
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   ├── components/
│   │   └── pages/
│   └── package.json
│
├── docs/
└── README.md
```

---

## API Highlights

The FastAPI backend currently provides endpoints for:

```text
GET  /
GET  /state
GET  /bids
GET  /allocate
POST /generate-plan
GET  /plan
GET  /export-calendar
POST /tasks/{task_id}/complete
POST /tasks/{task_id}/ignore
GET  /rewards
GET  /dashboard
POST /reset
```

Interactive API documentation is available through the deployed Swagger UI:

https://careerforge-backend-lo7f.onrender.com/docs

---

## Running Locally

### Backend

From the project root:

```bash
cd backend
python -m venv venv
```

Activate the virtual environment.

**Windows:**

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the FastAPI server:

```bash
uvicorn app.main:app --reload
```

The backend will be available at:

```text
http://127.0.0.1:8000
```

Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

### Frontend

Open another terminal:

```bash
cd frontend
npm install
npm run dev
```

The frontend runs at:

```text
http://localhost:5173
```

> **Important:** For local frontend testing, use `http://localhost:5173` rather than `http://127.0.0.1:5173`.

---

## Testing

Backend tests can be run with:

```bash
cd backend
python -m pytest
```

The project includes tests covering the Career Health and explainability functionality.

---

## Demo / Reset

CareerForge includes a baseline reset endpoint for demonstrations and testing.

```text
POST /reset
```

This restores the application state to the clean baseline without requiring manual modification of the state file.

---

## Deployment

CareerForge is deployed using:

**Frontend**

* Vercel
* React + Vite

**Backend**

* Render
* FastAPI

The production frontend communicates with the deployed backend through the configured API base URL.

---

## Team

**Person A · Person B · Person C**

Final-Year BCA Project · 2026

---

## Project Goal

CareerForge explores how **AI agents, resource allocation, and explainable decision-making** can be combined to create a practical career-planning system.

The goal is not simply to recommend what a user should learn, but to determine **where the user's limited weekly time should be invested for maximum career growth**.
