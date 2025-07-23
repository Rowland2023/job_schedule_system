# Base image with Python
FROM python:3.11-slim

# Set work directory
WORKDIR /app

# Copy requirements file first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application files
COPY . .

# Set environment variables
ENV FLASK_APP=run.py
ENV FLASK_ENV=production

# Expose port Flask will run on
EXPOSE 5000

# Run the application
CMD ["flask", "run", "--host=0.0.0.0"]
