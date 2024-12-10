FROM ghcr.io/mlflow/mlflow:latest

# Use Python 3.12
RUN apt-get update && apt-get install -y python3.12 python3.12-dev python3-pip
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.12 1

RUN pip3 install --upgrade pip
RUN pip3 install psycopg2-binary boto3 