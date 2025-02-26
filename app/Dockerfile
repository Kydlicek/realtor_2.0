FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .

# Don't set a default command here since you override it in docker-compose
# CMD ["celery", "-A", "celery_app", "worker", "--loglevel=info"]