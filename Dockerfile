FROM python:3.9-slim
WORKDIR /app
ARG APP_DIR

# This Dockerfile now expects a standard 'requirements.txt' and 'app.py'
COPY ${APP_DIR}/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY ${APP_DIR}/ .
EXPOSE 8501
CMD ["streamlit", "run", "app.py"]

