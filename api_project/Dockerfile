FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY ./api_project.py .
CMD ["uvicorn", "api_project:awsHandler", "--host", "0.0.0.0", "--port", "80"]
