# Use Python 3.11 slim image
FROM python:3.14.3-trixie

# Set working directory
WORKDIR /app
COPY sitezinho/ sitezinho/

# Install system dependencies for MySQL and other packages
RUN apt-get update && apt-get install -y \
    pkg-config \
    default-libmysqlclient-dev \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
COPY pyproject.toml .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install -e .

# Copy Node.js package files
COPY package*.json ./

# Install Node.js 18
RUN apt-get update && \
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    rm -rf /var/lib/apt/lists/*

# Install Node dependencies

# Copy application code
COPY . .

# Create logs file
RUN touch logs.txt

# Expose port 5000
EXPOSE 5000

# Set environment variables
ENV FLASK_APP=sitezinho
ENV FLASK_ENV=production

# Command to run the application
#CMD ["flask", "--app", "sitezinho", "run", "--host=0.0.0.0"]
