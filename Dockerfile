FROM python:3.12-alpine

# Set working directory
WORKDIR /app

# Install build dependencies for pip packages (if needed)
RUN apk add --no-cache gcc musl-dev libffi-dev

# Copy and install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set Flask app
ENV FLASK_APP=app.py

# Expose default port
EXPOSE 5000

# Start Flask
CMD ["flask", "run", "--host=0.0.0.0"]
