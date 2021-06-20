# syntax=docker/dockerfile:1

FROM python:3.9-slim

WORKDIR /app

# copy pip requirements then run pip install
COPY requirements.txt .
RUN pip3 install -r requirements.txt

# copy remaining files
COPY . .

CMD ["python3", "app.py"]
