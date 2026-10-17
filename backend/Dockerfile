FROM python:3.11-slim
WORKDIR /app
COPY backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt
COPY backend /app/backend
COPY ml /app/ml
RUN python /app/ml/train.py --quick
WORKDIR /app/backend
ENV MODEL_ARTIFACT_PATH=/app/ml/artifacts/zsentinel_pipeline_v1.joblib
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
