# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# ARG will be passed in from the docker build command
# This tells the Dockerfile which app's files to copy
ARG APP_DIR

# Copy the specific application's requirements file
COPY ${APP_DIR}/requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the specific application's source code
COPY ${APP_DIR}/ .

# Make port 8501 available to the world outside this container
EXPOSE 8501

# Define environment variable
ENV NAME World

# Run app.py when the container launches
# The entryPoint from manifest.yaml will eventually be used here
CMD ["streamlit", "run", "app.py"]

