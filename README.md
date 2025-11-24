# AppetIte

## 1. Project Title and Overview

**AppetIte** is an AI-driven recipe generation and pantry inventory management system designed to help users efficiently manage ingredients, reduce food waste, and instantly generate categorized recipes such as quick meals, healthy dishes, and high-protein options.

The system integrates:
- A recipe generation model
- A pantry inventory tracker per user
- A category-based recommendation engine
- A full deployment and monitoring pipeline (Docker + Prometheus + Grafana)

---

## 2. Repository Contents

Appetite/
│
├── src/
│   ├── backend/           # FastAPI backend, recipe engine, pantry DB, models
│   ├── frontend/          # Streamlit UI pages, user interface logic
│   └── main.py            # Entry point for backend
│
├── deployment/            # Dockerfile, docker-compose, environment configs
│
├── monitoring/
│   ├── prometheus/        # Prometheus config (scraping backend metrics)
│   ├── grafana/           # Custom dashboard JSON
│   └── dashboards/        # Exported Grafana dashboards
│
├── documentation/         # Project report, proposal, notebook experiments

---

## 3. System Entry Point

### Backend (FastAPI)

**Main script:**
src/backend/main.py

**Run locally:**
uvicorn src.backend.main:app --reload

**Run full system in Docker:**
cd deployment
docker-compose up --build

This launches:
- Backend (FastAPI)
- Frontend (Streamlit)
- Prometheus
- Grafana dashboard

---

## 4. Video Demonstration

The demo video showcases:
- Running the backend and frontend
- Logging into a user account
- Adding pantry ingredients
- Generating recipes (quick, healthy, protein-packed, etc.)
- Calling the API endpoints
- Metrics scraping via `/metrics`
- Live dashboard updates in Grafana

---

## 5. Deployment Strategy

The project uses a **Docker-based deployment** with the following components:

- **Dockerfile** for backend and frontend
- **docker-compose.yml** orchestrates:
  - Backend (FastAPI)
  - Frontend (Streamlit)
  - Prometheus metrics collector
  - Grafana dashboard visualization

**Configuration files:**
deployment/Dockerfile
deployment/docker-compose.yml

### Backend Endpoints

The backend exposes:
- `/health` → Health checks
- `/metrics` → Prometheus scrape endpoint

---

## 6. Monitoring and Metrics

### Monitoring Stack

- **Prometheus** → Scrapes backend metrics every 2 seconds
- **Grafana** → Visualizes metrics using a custom dashboard

### Metrics Tracked

- API response time (generation endpoint)
- Recommendation latency
- User-level recipe request counts
- System availability via `/health`

### Setup Instructions

cd deployment
docker-compose up

**Access points:**
- **Grafana Dashboard:** http://localhost:3000
- **Prometheus:** http://localhost:9090

---

## 7. Project Documentation

Key files located in the `documentation/` folder:

- **AI System Project Proposal**
  documentation/AI System project proposal template

- **Final Project Report**
  documentation/Project report

- **Jupyter Notebooks** (Model Analysis, Category Classifier, etc.)
  documentation/notebooks/

---

## 8. Version Control and Team Collaboration

### Version Control Practices

The project utilizes GitHub for version control with the following practices:

**Branching Strategy:**
- `main` → Stable release branch
- Feature branches → `feature/pantry`, `feature-monitoring`, etc.

**Commit Practices:**
- Frequent commits with clear, descriptive messages
- Documentation of:
  - Bug fixes
  - Model updates
  - Monitoring dashboard changes
  - Front-end improvements

**Collaboration Tools:**
- GitHub commits and diffs
- Manual code reviews
- Issue-based tracking (local notes)

---

## 9. Technology Stack Decisions

### Components Used

- **Docker Compose** for local orchestration
- **FastAPI** for backend API
- **Streamlit** for frontend UI
- **Prometheus + Grafana** for monitoring

### Components Not Used

The following technologies were **not used** in this project:

- **Kubernetes** – Not required; Docker Compose was sufficient for single-user academic deployment
- **Serverless platforms** – Local and Docker deployment met all requirements

**Rationale:** The project requirement mandated local deployment with monitoring. Scaling infrastructure was not needed for a single-user academic environment, making Docker Compose the optimal choice for simplicity and effectiveness.

---

## Quick Start Guide

### Prerequisites
- Docker and Docker Compose installed
- Python 3.8+ (for local development)

### Launch the Application

1. Clone the repository
2. Navigate to deployment directory:
   cd deployment
3. Start all services:
   docker-compose up --build
4. Access the application:
   - **Frontend:** http://localhost:8501
   - **Backend API:** http://localhost:8000
   - **Grafana:** http://localhost:3000
   - **Prometheus:** http://localhost:9090

---

## Project Highlights

**AI-Powered Recipe Generation** – Personalized recipes based on available ingredients  
**Smart Pantry Management** – Track inventory and reduce food waste  
**Category-Based Recommendations** – Quick meals, healthy options, high-protein dishes  
**Production-Ready Deployment** – Fully containerized with Docker  
**Real-Time Monitoring** – Prometheus metrics with Grafana dashboards  
**Clean Architecture** – Separated backend, frontend, and monitoring concerns