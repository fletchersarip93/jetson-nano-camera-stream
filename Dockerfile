# syntax=docker/dockerfile:1

FROM nvcr.io/nvidia/l4t-base:r32.5.0

RUN apt-get update
RUN apt-get install python3 -y
RUN apt-get install python3-pip -y


WORKDIR /app

# copy pip requirements then run pip install
COPY requirements.txt .
RUN pip3 install -r requirements.txt

# copy remaining files
COPY . .

CMD ["python3", "app.py"]
