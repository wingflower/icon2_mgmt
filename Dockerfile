FROM python:3.10-slim

WORKDIR /app/was

COPY ./app/requirements.txt /app/was/requirements.txt
 
RUN apt-get update
RUN apt-get install -y python3-dev default-libmysqlclient-dev build-essential pkg-config
# RUN apt-get install -y libssl-dev mysql-server mysql-client libmysqlclient-dev
# RUN apt-get install -y libmysqlclient-dev libmariadb-dev
RUN pip install --upgrade pip
RUN pip install --no-cache-dir --upgrade -r /app/was/requirements.txt
 
# CMD ["python", "app/main.py"]
# CMD ["uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8080"]
