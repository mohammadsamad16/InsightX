from __future__ import annotations

from io import BytesIO
from typing import Any

import numpy as np
import pandas as pd
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from sklearn.cluster import KMeans
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression
from sklearn.metrics import accuracy_score, f1_score, mean_absolute_error, mean_squared_error
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

APP_VERSION = "0.1.0"
MAX_UPLOAD_BYTES = 20 * 1024 * 1024
MAX_ROWS = 250_000
MAX_COLUMNS = 200

app = FastAPI(
    title="InsightX Analytics API",
    description="CSV profiling, churn classification, sales trend forecasting and customer segmentation.",
    version=APP_VERSION,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://insightx-analytics.higgsfield.app",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


async def read_csv(file: UploadFile) -> pd.DataFrame:
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Upload a .csv file.")
    raw = await file.read(MAX_UPLOAD_BYTES + 1)
    if len(raw) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="File exceeds the 20 MB upload limit.")
    if not raw:
        raise HTTPException(status_code=400, detail="The uploaded file is empty.")
    try:
        frame = pd.read_csv(BytesIO(raw))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Could not parse CSV: {exc}") from exc
    if frame.empty:
        raise HTTPException(status_code=400, detail="The CSV contains no data rows.")
    if len(frame) > MAX_ROWS or len(frame.columns) > MAX_COLUMNS:
        raise HTTPException(
            status_code=413,
            detail=f"Dataset limit is {MAX_ROWS:,} rows and {MAX_COLUMNS} columns.",
        )
    frame.columns = [str(column).strip() for column in frame.columns]
    if frame.columns.duplicated().any():
        raise HTTPException(status_code=400, detail="Column names must be unique.")
    return frame


def json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): json_safe(val) for key, val in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_safe(item) for item in value]
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return None if not np.isfinite(value) else float(value)
    if isinstance(value, (np.bool_,)):
        return bool(value)
    if isinstance(value, (pd.Timestamp,)):
        return value.isoformat()
    if value is None:
        return None
    try:
        missing = pd.isna(value)
        if isinstance(missing, (bool, np.bool_)) and missing:
            return None
    except (TypeError, ValueError):
        pass
    return value


def numeric_columns(frame: pd.DataFrame) -> list[str]:
    return frame.select_dtypes(include=np.number).columns.tolist()


@app.get("/")
def root() -> dict[str, str]:
    return {"name": "InsightX Analytics API", "version": APP_VERSION, "docs": "/docs"}


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "version": APP_VERSION}


@app.post("/api/v1/profile")
async def profile(file: UploadFile = File(...)) -> dict[str, Any]:
    frame = await read_csv(file)
    missing = frame.isna().sum()
    columns = []
    for name in frame.columns:
        series = frame[name]
        columns.append({
            "name": name,
            "dtype": str(series.dtype),
            "missing": int(missing[name]),
            "missing_pct": round(float(missing[name] / len(frame) * 100), 2),
            "unique": int(series.nunique(dropna=True)),
            "sample": json_safe(series.dropna().head(5).tolist()),
        })
    return json_safe({
        "row_count": len(frame),
        "column_count": len(frame.columns),
        "missing_cells": int(frame.isna().sum().sum()),
        "duplicate_rows": int(frame.duplicated().sum()),
        "memory_usage_bytes": int(frame.memory_usage(deep=True).sum()),
        "columns": columns,
        "numeric_summary": frame[numeric_columns(frame)].describe().round(3).to_dict(),
    })


@app.post("/api/v1/churn")
async def churn(
    file: UploadFile = File(...),
    target: str = "Churn",
) -> dict[str, Any]:
    frame = await read_csv(file)
    if target not in frame.columns:
        raise HTTPException(status_code=400, detail=f"Target column '{target}' was not found.")
    frame = frame.dropna(subset=[target]).copy()
    if len(frame) < 20:
        raise HTTPException(status_code=400, detail="At least 20 labelled rows are required.")
    y = frame.pop(target).astype(str)
    if y.nunique() < 2 or y.nunique() > 20:
        raise HTTPException(status_code=400, detail="Target must contain 2 to 20 classes.")
    X = frame
    if X.shape[1] == 0:
        raise HTTPException(status_code=400, detail="No feature columns were found.")

    numeric = X.select_dtypes(include=np.number).columns.tolist()
    categorical = [column for column in X.columns if column not in numeric]
    transformers = []
    if numeric:
        transformers.append(("numeric", Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]), numeric))
    if categorical:
        transformers.append(("categorical", Pipeline([
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore")),
        ]), categorical))

    model = Pipeline([
        ("preprocessor", ColumnTransformer(transformers)),
        ("classifier", RandomForestClassifier(
            n_estimators=150, random_state=42, class_weight="balanced",
            n_jobs=-1, min_samples_leaf=2,
        )),
    ])
    stratify = y if y.value_counts().min() >= 2 else None
    try:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=stratify
        )
        model.fit(X_train, y_train)
        predictions = model.predict(X_test)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Model training failed: {exc}") from exc

    return json_safe({
        "target": target,
        "rows_used": len(frame),
        "train_rows": len(X_train),
        "test_rows": len(X_test),
        "classes": sorted(y.unique().tolist()),
        "accuracy": round(float(accuracy_score(y_test, predictions)), 4),
        "weighted_f1": round(float(f1_score(y_test, predictions, average="weighted", zero_division=0)), 4),
        "baseline": "RandomForestClassifier",
        "note": "Random holdout baseline. Check leakage, class balance and business costs before operational use.",
    })


@app.post("/api/v1/forecast")
async def forecast(
    file: UploadFile = File(...),
    date_column: str = "Date",
    value_column: str = "Sales",
    periods: int = 12,
) -> dict[str, Any]:
    if not 1 <= periods <= 120:
        raise HTTPException(status_code=400, detail="periods must be between 1 and 120.")
    frame = await read_csv(file)
    if date_column not in frame.columns or value_column not in frame.columns:
        raise HTTPException(status_code=400, detail="date_column or value_column was not found.")
    data = frame[[date_column, value_column]].copy()
    data[date_column] = pd.to_datetime(data[date_column], errors="coerce")
    data[value_column] = pd.to_numeric(data[value_column], errors="coerce")
    data = data.dropna().groupby(date_column, as_index=False)[value_column].sum()
    data = data.sort_values(date_column)
    if len(data) < 8:
        raise HTTPException(status_code=400, detail="At least 8 distinct valid dates are required.")

    y = data[value_column].to_numpy(dtype=float)
    split = min(max(5, int(len(y) * 0.8)), len(y) - 2)
    train_y, test_y = y[:split], y[split:]
    train_x = np.arange(len(train_y), dtype=float).reshape(-1, 1)
    test_x = np.arange(len(train_y), len(y), dtype=float).reshape(-1, 1)
    model = LinearRegression().fit(train_x, train_y)
    validation_predictions = model.predict(test_x)
    future_x = np.arange(len(y), len(y) + periods, dtype=float).reshape(-1, 1)
    predictions = model.predict(future_x)

    gaps = data[date_column].diff().dropna().dt.total_seconds()
    median_gap = float(gaps.median()) if len(gaps) else 30 * 86400
    step = pd.to_timedelta(median_gap, unit="s")
    last_date = data[date_column].iloc[-1]
    future_dates = [last_date + step * (index + 1) for index in range(periods)]

    return json_safe({
        "baseline": "LinearRegression trend",
        "observations": len(data),
        "validation_observations": len(test_y),
        "validation_mae": float(mean_absolute_error(test_y, validation_predictions)),
        "validation_rmse": float(np.sqrt(mean_squared_error(test_y, validation_predictions))),
        "forecast": [
            {"date": date, "predicted_value": max(0.0, float(value))}
            for date, value in zip(future_dates, predictions)
        ],
        "note": "Simple linear trend baseline; this is not a seasonal forecasting model.",
    })


@app.post("/api/v1/segment")
async def segment(
    file: UploadFile = File(...),
    features: str | None = None,
    clusters: int = 4,
) -> dict[str, Any]:
    if not 2 <= clusters <= 10:
        raise HTTPException(status_code=400, detail="clusters must be between 2 and 10.")
    frame = await read_csv(file)
    candidates = [item.strip() for item in features.split(",")] if features else numeric_columns(frame)
    missing = [name for name in candidates if name not in frame.columns]
    if missing:
        raise HTTPException(status_code=400, detail=f"Unknown feature columns: {missing}")
    selected = frame[candidates].apply(pd.to_numeric, errors="coerce")
    selected = selected.replace([np.inf, -np.inf], np.nan).dropna(axis=1, how="all")
    if selected.shape[1] == 0:
        raise HTTPException(status_code=400, detail="Select at least one usable numeric feature.")
    selected = selected.fillna(selected.median()).fillna(0)
    if len(selected) < clusters:
        raise HTTPException(status_code=400, detail=f"At least {clusters} rows are required.")

    scaled = StandardScaler().fit_transform(selected)
    labels = KMeans(n_clusters=clusters, random_state=42, n_init=10).fit_predict(scaled)
    result = frame.copy()
    result["segment"] = labels
    summary = result.groupby("segment")[selected.columns.tolist()].mean().round(3).reset_index()
    sizes = result["segment"].value_counts().sort_index()

    return json_safe({
        "algorithm": "KMeans",
        "rows_clustered": len(result),
        "features_used": selected.columns.tolist(),
        "cluster_count": clusters,
        "cluster_sizes": {str(key): int(value) for key, value in sizes.items()},
        "cluster_profiles": summary.to_dict(orient="records"),
        "note": "Exploratory clusters, not verified customer personas. Validate business meaning before action.",
    })
