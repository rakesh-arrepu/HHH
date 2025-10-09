# simple backend Dockerfile placeholder
FROM python:3.11-slim
WORKDIR /app
COPY . /app
RUN pip install -r requirements/base.txt
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
