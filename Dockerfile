# 1. Use a lightweight Python image
FROM python:3.12-slim

# 2. Prevent __pycache__ and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# 3. Set working directory
WORKDIR /code

# 4. Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 5. Copy & install Python dependencies
COPY requirements.txt /code/requirements.txt
RUN pip install --upgrade pip \
    && pip install -r /code/requirements.txt

# 6. Copy the entire project
COPY . /code/

# 7. Default command
CMD ["python", "ONLINE_SHOPPING/manage.py", "runserver", "0.0.0.0:8000"]