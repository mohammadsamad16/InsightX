# InsightX Analytics API

FastAPI backend for the InsightX analytics prototype.

## Included endpoints

| Method | Endpoint | Purpose |
| --- | --- | --- |
| GET | `/` | API information |
| GET | `/health` | Health check |
| POST | `/api/v1/profile` | CSV data quality profile and numeric summary |
| POST | `/api/v1/churn` | Train/evaluate a Random Forest classification baseline |
| POST | `/api/v1/forecast` | Linear-trend forecast for a dated numeric series |
| POST | `/api/v1/segment` | K-Means segmentation using numeric features |

Interactive API documentation is available at `/docs` while the service is running.

## Run locally

Requires Python 3.11 or newer.

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

The API is available at http://127.0.0.1:8000.

## Request examples

All analysis endpoints accept a CSV as multipart form field named `file`.

Profile:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/profile \
  -F "file=@sample.csv"
```

Churn classification (change the target column to match your CSV):

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/churn?target=Churn" \
  -F "file=@customers.csv"
```

Forecast (the date and numeric value columns must exist):

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/forecast?date_column=Date&value_column=Sales&periods=6" \
  -F "file=@sales.csv"
```

Segmentation:

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/segment?clusters=4" \
  -F "file=@customers.csv"
```

To select segmentation columns, pass a comma-separated `features` query parameter, for example `features=Age,AnnualIncome,SpendingScore`.

## Limits and behavior

- CSV uploads are limited to 20 MB.
- Datasets are limited to 250,000 rows and 200 columns.
- `/api/v1/churn` trains a Random Forest baseline using a random holdout split. It does not automatically identify leakage or optimize business thresholds.
- `/api/v1/forecast` uses a linear trend baseline. It is not a seasonal forecasting model and should not be used as a production forecast without further validation.
- `/api/v1/segment` uses K-Means on selected numeric columns after imputation and standardization. Cluster labels are exploratory, not validated personas.
- Models are trained per request; this version does not persist uploaded data or trained models.
- SHAP explanations, authentication, database persistence, background jobs and model registry are not included in this initial backend.

## Deploy on Render (free plan)

1. Sign in to Render and choose **New → Blueprint**.
2. Connect GitHub and select `mohammadsamad16/InsightX`.
3. Render should detect the repository-root render.yaml.
4. Before creating the service, confirm the plan displayed is **Free** and the estimated recurring cost is **$0**.
5. Deploy the blueprint. The health check path is `/health`.
6. After deployment, the frontend is configured to call https://insightx-analytics-api.onrender.com. If Render assigns a different service URL, update the API base URL in the website.

Do not proceed if Render displays a paid plan or a charge. Free instances may sleep when inactive and can have cold starts or resource limits. Verify the current terms in Render before deploying.
