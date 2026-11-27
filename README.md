# InsightX — Explainable Analytics Platform

**Turning data into intelligence.**

InsightX is an educational analytics prototype with an independent React frontend and a FastAPI analytics service. The site and API are designed to be hosted outside the original website builder.

## Project

- **Repository:** https://github.com/mohammadsamad16/InsightX
- **Frontend:** Vite + React 19
- **Backend:** FastAPI + Pandas + scikit-learn
- **Hosting configuration:** Render Blueprint at the repository root (render.yaml)

## Frontend

The frontend source is in frontend/. It contains the InsightX landing page, responsive design, scroll-controlled hero, local CSV preview and optional API integration.

Local run:

~~~bash
cd frontend
npm install
npm run dev
~~~

The Render build obtains the media bundle, extracts it into frontend/public, then runs npm ci and npm run build.

## Backend API

| Capability | Endpoint | Method |
| --- | --- | --- |
| Dataset profile and data-quality checks | /api/v1/profile | POST |
| Churn classification baseline | /api/v1/churn | POST |
| Linear-trend forecasting baseline | /api/v1/forecast | POST |
| K-Means numeric segmentation | /api/v1/segment | POST |
| Health check | /health | GET |

Local API run (Python 3.11+):

~~~bash
cd backend
python -m venv .venv
# Windows:
.venv\\Scripts\\activate
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
~~~

Open http://127.0.0.1:8000/docs for interactive API documentation.

## Deploy the frontend and API together on Render

1. Sign in to Render and choose **New → Blueprint**.
2. Connect GitHub and select mohammadsamad16/InsightX.
3. Render should detect the root render.yaml. It defines:
   - insightx-analytics-web: static Vite site (no compute plan; static sites are free)
   - insightx-analytics-api: Docker web service on the Free compute plan
4. Before deploying, check that the API plan is **Free** and the estimated recurring compute cost is **$0**. Do not upgrade either service.
5. Deploy the Blueprint. The frontend is configured to call https://insightx-analytics-api.onrender.com.

Render Free web services can sleep after inactivity and have monthly usage limits. Bandwidth overages may incur charges, so monitor usage and configure spending controls in your Render account before enabling any billable usage.

## Important limitations

This is an early prototype, not a production decision system. Churn scoring is a baseline random-holdout evaluation, forecasting uses a linear trend (not seasonal modeling), and K-Means clusters require business interpretation. Models and uploaded data are not persisted. Authentication, SHAP explanations, a model registry, monitoring and a production test suite remain future work.

Do not upload sensitive personal or customer data to a public demo.
