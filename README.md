# InsightX — Explainable Analytics Platform

**Turning data into intelligence.**

InsightX is an educational analytics prototype that brings together dataset profiling, predictive modeling, time-series trend estimation and customer segmentation behind a simple API.

## Project

- **Website:** https://insightx-analytics.higgsfield.app
- **Repository:** https://github.com/mohammadsamad16/InsightX
- **Backend:** FastAPI + Pandas + scikit-learn
- **API docs:** Available at `/docs` when the API is running

## Current capabilities

| Capability | Endpoint | Method |
| --- | --- | --- |
| Dataset profile and data-quality checks | `/api/v1/profile` | POST |
| Churn classification baseline | `/api/v1/churn` | POST |
| Linear-trend forecasting baseline | `/api/v1/forecast` | POST |
| K-Means numeric segmentation | `/api/v1/segment` | POST |
| Health check | `/health` | GET |

## Repository structure

```text
InsightX/
├── backend/
│   ├── app/
│   │   └── main.py
│   ├── Dockerfile
│   ├── README.md
│   ├── render.yaml
│   └── requirements.txt
├── .gitignore
└── README.md
```

## Run the API locally

Python 3.11+ is recommended.

```bash
cd backend
python -m venv .venv
# Windows:
.venv\\Scripts\\activate
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000/docs for interactive API documentation.

## Deployment

A Render Blueprint is included at `backend/render.yaml`. It is configured for the Free plan. Review the plan and displayed cost in Render before confirming deployment; do not continue if a paid plan or charge is shown.

See [backend/README.md](backend/README.md) for endpoint examples, limits and deployment instructions.

## Important limitations

This is an early prototype, not a production decision system. Churn scoring is a baseline random-holdout evaluation, forecasting uses a linear trend (not seasonal modeling), and K-Means clusters require business interpretation. Models and uploaded data are not persisted. Authentication, SHAP explanations, a model registry, monitoring and a production test suite remain future work.

Do not upload sensitive personal or customer data to a public demo.
