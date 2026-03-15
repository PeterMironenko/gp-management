FROM python:3.10
EXPOSE 5000
WORKDIR /app
COPY ./requirements.txt requirements.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt
# Application code is mounted in via volume in docker-compose / docker_run.sh
CMD ["flask", "--app", "app", "run", "--port", "5000", "--host", "0.0.0.0", "--debug"]
