AppetIte – Smart AI-Powered Recipe & Pantry Management System

1. Project Title and Overview

AppetIte is an AI-driven recipe generation and pantry-inventory management system.
Its objective is to help users efficiently manage ingredients, reduce food waste, and instantly generate categorized recipes such as quick meals, healthy dishes, and high-protein options.

The system integrates:
	•	A recipe generation model
	•	A pantry inventory tracker per user
	•	A category-based recommendation engine
	•	A full deployment + monitoring pipeline (Docker + Prometheus + Grafana)

2. Repository Contents

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
│
└── videos/                # Demo screencast (user-recorded)

3. System Entry Point

Backend (FastAPI)

Main script:

src/backend/main.py

Run Locally:

uvicorn src.backend.main:app --reload

Run Full System in Docker:

cd deployment
docker-compose up --build

This launches:
	•	Backend (FastAPI)
	•	Frontend (Streamlit)
	•	Prometheus
	•	Grafana dashboard

4. Video Demonstration

 demo should show:
	•	Running the backend & frontend
	•	Logging into a user account
	•	Adding pantry ingredients
	•	Generating recipes (quick, healthy, protein-packed, etc.)
	•	Calling the API endpoints
	•	Metrics scraping via /metrics
	•	Live dashboard updates in Grafana

5. Deployment Strategy

The project uses a Docker-based deployment:
	•	Dockerfile for backend + frontend
	•	docker-compose.yml orchestrates:
	•	Backend (FastAPI)
	•	Frontend (Streamlit)
	•	Prometheus metrics collector
	•	Grafana dashboard visualization
See:
    deployment/Dockerfile
    deployment/docker-compose.yml

The backend exposes:
	•	/health → health checks
	•	/metrics → Prometheus scrape endpoint

6. Monitoring and Metrics

Monitoring tools used:
	•	Prometheus → scrapes backend metrics every 2 seconds
	•	Grafana → visualizes metrics using a custom dashboard

Metrics tracked:
	•	API response time (generation endpoint)
	•	Recommendation latency
	•	User-level recipe request counts
	•	System availability via /health

Setup instructions:
    cd deployment
    docker-compose up


Grafana Dashboard:
http://localhost:3000

Prometheus:
http://localhost:9090

7. Project Documentation

Key files inside the documentation/ folder:
	•	AI System Project Proposal
documentation/AI System project proposal template
	•	Final Project Report
documentation/Project report
	•	Jupyter Notebooks (Model Analysis, Category Classifier, etc.)
Located in:
documentation/notebooks/

8. Version Control and Team Collaboration

Version control practices used:
	•	GitHub repository with frequent commits
	•	Branching strategy:
	•	main → stable release
	•	feature branches → feature/pantry, feature-monitoring, etc.
	•	Clear commit messages documenting:
	•	Bug fixes
	•	Model updates
	•	Monitoring dashboard changes
	•	Front-end improvements

All contributions were coordinated using:
	•	GitHub commits and diffs
	•	Manual code reviews
	•	Issue-based tracking (local notes)

9. If Not Applicable

Components not used:
	•	Kubernetes (not required because Docker Compose was sufficient for this project)
	•	Serverless platforms (local and Docker deployment met all requirements)

Reasons:
The project requirement mandated local deployment with monitoring, and scaling was not needed for a single-user academic project environment.


