FROM python:3.12-slim

COPY ./requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /app

COPY ./server.py ./

ENTRYPOINT ["fastapi", "run" ,  "server.py"]