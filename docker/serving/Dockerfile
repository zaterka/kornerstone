FROM python:3.12-slim

WORKDIR /app

# Install the kornerstone package
COPY src/ /app/src/
RUN pip install -e /app/src/

# Copy configurations
COPY configs/ /app/configs/

ENTRYPOINT ["python", "-m", "kornerstone.serving.predict"] 