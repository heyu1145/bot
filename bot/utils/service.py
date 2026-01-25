"""
run a http service at localhost:4100/api for frontend localhost:3000
"""
from datetime import datetime, timezone
from random import randint
from time import sleep
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from pydantic import BaseModel
import psutil

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class MessageRequest(BaseModel):
    message: str


class MessageResponse(BaseModel):
    reply: str


@app.get("/ping")
async def response_ping():
    return {
        "reply": "pong!",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@app.post("/bot-control", response_model=MessageResponse)
async def handle_message(request: MessageRequest):
    # temp message, will edit after all complete
    reply = f"Received your message: {request.message}"
    return MessageResponse(reply=reply)

# post to /status for frontend data: disk, memory, cpu usage, thread count, bot latency


def get_cpu_usage(dec=2):
    """
    dec: duration to measure cpu usage, default 2 seconds
    """
    try:
        t1 = psutil.Process().cpu_times()
        sleep(dec)
        t2 = psutil.Process().cpu_times()
        cpu_usage = (t2.user - t1.user) + (t2.system - t1.system)
        return round(cpu_usage / dec * 100, 2)
    except PermissionError:
        # unsupported service, return -1.0
        return -1.0


@app.get("/status")
async def get_status():
    try:
        cpu_usage = psutil.cpu_percent(interval=1)
    except PermissionError:
        # unsupported service, use manual count instead
        cpu_usage = get_cpu_usage(1)

    status = {
        "bot_status": "running",  # placeholder, edit after full access
        "disk_usage": psutil.disk_usage('/')._asdict(),
        "memory_usage": psutil.virtual_memory()._asdict(),
        "cpu_usage": cpu_usage,
        "thread_count": psutil.Process().num_threads(),
        "bot_latency_ms": randint(100, 1000)   # Placeholder value
    }
    return status

# special method


@app.post("/")
async def teapot(request: Request):
    if not request.client:
        return RedirectResponse('/', 303)

    body = await request.body()

    agent = request.headers.get("user-agent", "unknown")

    content_type = request.headers.get("content-type", "unknown")

    resp: dict[str, object] = {
        "status": 418,
        "message": "I'm a teapot",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "client": {
            "host": request.client.host,
            "user_agent": agent
        },
        "body": {
            "content-type": content_type,
            "first_100_character": body.decode('utf-8', 'ignore')[:100]
            if len(body) < 1024*1024*3
            else 'so big body that i cant solve it'
        }
    }

    hints: dict[str, str] = {
        "python": "life is short, I'm using Python.",
        "javascript": "typeof null === 'object'",
        "typescript": "just javascript plus",
        "rust": "memory safety!",
        "lua": "everything is a table, even list or dict",
        "go": "did you err != nil today?",
        "html": '<div id="meme">hello world!</div>',
        "css": 'div#meme {\nbackground-color: rgb(255,136,0);\n}'
    }

    for patten, hint in hints.items():
        if patten in content_type.lower():
            resp["hint"] = hint
            break

    return JSONResponse(resp, 418)


@app.get('/')
async def root():
    return JSONResponse({
        "message": "Welcome to teapot"
    }, 203, {"Teapot": "hello world!"})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=4100)

# To run the service, execute this file directly.
