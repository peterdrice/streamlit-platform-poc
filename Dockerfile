FROM python:3.9-slim
WORKDIR /app

# Argument for the app's directory
ARG APP_DIR

# Argument for the requirements file, with a default
ARG REQUIREMENTS_FILE=requirements.txt

# Argument for the startup script, with a default value
ARG ENTRYPOINT_SCRIPT=app.py

# Copy only the requirements file first to leverage Docker's build cache
COPY ${APP_DIR}/${REQUIREMENTS_FILE} ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app's code
COPY ${APP_DIR}/ .
EXPOSE 8501

# Use the dynamic entrypoint script in the CMD instruction
CMD ["streamlit", "run", "${ENTRYPOINT_SCRIPT}"]

