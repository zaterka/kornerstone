FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy training code
COPY train.py .

ENTRYPOINT ["python", "train.py"] 