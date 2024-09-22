# Use the smaller Alpine-based Python image
FROM python:3.12-alpine

# Set the working directory in the container
WORKDIR /app

# Copy your Python app to the working directory
COPY . .

# Install dependencies, build Python packages, and remove build tools in one layer
RUN apk add --no-cache --virtual .build-deps gcc musl-dev libffi-dev \
    && pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir uv \
    && uv sync \
    && apk del .build-deps

# Expose the port your app will run on (adjust if necessary)
EXPOSE 8000

# Command to run your Python app using uv to execute main.py
CMD ["uv", "run", "main.py"]
