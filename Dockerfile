# Use the official Python slim image as base
FROM python:3.9-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

# Default: run the Streamlit dashboard.
# Override in CI/CD: docker run ... python3 newsletter_collector.py
CMD ["streamlit", "run", "newsletter_dashboard.py", "--server.port=8501", "--server.address=0.0.0.0"]
