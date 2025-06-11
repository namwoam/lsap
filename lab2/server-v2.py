from fastapi import FastAPI
import socket

hostname = socket.gethostname()
ip_addr = socket.gethostbyname(hostname)

app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "Hello NTUIM!", "hostname": hostname, "ip_address": ip_addr}
