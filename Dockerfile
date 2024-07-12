FROM python:3.10

EXPOSE 5000/tcp

WORKDIR /app


COPY packages.txt ./
RUN apt update -y  &&  apt upgrade -y
RUN xargs apt install -y < packages.txt

COPY requirements-docker.txt ./requirements.txt
RUN pip install --upgrade pip
RUN pip install --no-deps --no-cache-dir -r requirements.txt

COPY pdfs/* ./pdfs/
COPY .env main.py main.css ./

CMD ["python3", "main.py", "--host", "0.0.0.0", "--port", "5000"]
