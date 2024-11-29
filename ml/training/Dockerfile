FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN pip install feast

# Copy training code
COPY train.py .

ENTRYPOINT ["python", "train.py"] 