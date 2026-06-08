FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the server configuration files
COPY orchestrated_agent.py .
COPY .env . 
COPY logistics_agent_app/ ./logistics_agent_app/

EXPOSE 8080

CMD ["uvicorn", "orchestrated_agent:app", "--host", "0.0.0.0", "--port", "8080"]

