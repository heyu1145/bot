"""
run a http service at localhost:4100/api for frontend localhost:3000
"""

from datetime import datetime, timezone
from random import randint
from time import sleep
from secrets import token_urlsafe
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from pydantic import BaseModel
import psutil

# Programming language easter eggs for content-type matching
LANGUAGE_HINTS: dict[str, str] = {
    "python": "life is short, I'm using Python.",
    "javascript": "typeof null === 'object'",
    "typescript": "just javascript plus",
    "rust": "memory safety!",
    "lua": "everything is a table, even list or dict",
    "go": "did you err != nil?",
    "html": '<div id="meme">hello world!</div>',
    "css": "div#meme {\nbackground-color: rgb(255,136,0);\n}",
    "java": "Write once, run anywhere... if you're lucky",
    "kotlin": "Null safety is a feature, not a bug",
    "swift": "Objective-C, but modern and safer",
    "php": "It just works... most of the time",
    "ruby": "Beautiful code, or at least it tries to be",
    "perl": "There's more than one way to do it",
    "haskell": "Pure functional programming is a lifestyle",
    "dart": "Flutter's favorite child",
    "sql": "SELECT * FROM files WHERE todo > 0 OR bug > 0",
    "scala": "Java, but with more parentheses",
}

# Drink easter eggs for Accept/Expect header matching
DRINK_HINTS: dict[str, str] = {
    "drinks/coffee": "I'm a teapot, not a coffee machine! ☕",
    "drinks/tea": "Ah, tea! My favorite! 🍵",
    "drinks/water": "Refreshing! 💧",
    "drinks/juice": "Sweet and fruity! 🧃",
    "drinks/soda": "Bubbly! 🥤",
    "drinks/milk": "Calcium for strong bones! 🥛",
}

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*/*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class MessageRequest(BaseModel):
    message: str


class MessageResponse(BaseModel):
    reply: str


@app.get("/ping")
async def response_ping(request: Request):
    now = datetime.now(timezone.utc).timestamp()
    return {
        "reply": "pong!",
        "timestamp": now,
        "client_host": request.client.host if request.client else "unknown",
        "random_bytes": token_urlsafe(16),
    }


@app.post("/bot-control", response_model=MessageResponse)
async def handle_message(request: MessageRequest) -> MessageResponse:
    # temp message, will edit after all complete
    reply = f"Received your message: {request.message}"
    return MessageResponse(reply=reply)


# post to /status for frontend data: disk, memory, cpu usage, thread count, bot latency


def get_cpu_usage(dec: float = 2.0, /) -> float:
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
        "disk_usage": psutil.disk_usage("/")._asdict(),
        "memory_usage": psutil.virtual_memory()._asdict(),
        "cpu_usage": cpu_usage,
        "thread_count": psutil.Process().num_threads(),
        "bot_latency_ms": randint(100, 1000),  # Placeholder value
    }
    return status


# special method


@app.post("/")
async def teapot(request: Request):
    """
    HTTP 418 I'm a teapot endpoint with easter eggs.

    This endpoint returns a 418 status code and includes easter eggs based on:
    - Content-Type header: Programming language hints
    - Accept/Expect headers: Drink preferences

    Returns:
        JSONResponse: A 418 response with request information and easter eggs
    """
    if not request.client:
        return RedirectResponse("/", 303)

    try:
        body = await request.body()
    except Exception:
        body = b""

    # Collect request headers
    user_agent = request.headers.get("user-agent", "unknown")
    content_type = request.headers.get("content-type", "unknown")
    accept_header = request.headers.get("accept", "")
    accept_language = request.headers.get("accept-language", "")
    expect_header = request.headers.get("expect", "")

    # Generate unique request ID
    request_id = token_urlsafe(16)

    # Build response structure
    resp: dict[str, object] = {
        "status": 418,
        "message": "I'm a teapot",
        "request_id": request_id,
        "server_time": datetime.now(timezone.utc).isoformat(),
        "http_method": request.method,
        "path": request.url.path,
        "query_params": dict(request.query_params),
        "client": {
            "host": request.client.host,
            "user_agent": user_agent,
        },
        "headers": {
            "accept": accept_header,
            "accept_language": accept_language,
            "content_type": content_type,
            "expect": expect_header,
        },
        "body": {
            "content_type": content_type,
            "first_100_characters": _safe_decode_body(body)[:100]
            if body
            else "empty body",
        },
    }

    # Check for programming language hints in content-type
    for pattern, hint in LANGUAGE_HINTS.items():
        if pattern in content_type.lower():
            resp["language_hint"] = hint
            break

    # Check for drink preferences in Accept/Expect headers
    drink_preference = None
    for header in [accept_header, expect_header]:
        if not header:
            continue
        for drink_pattern, drink_hint in DRINK_HINTS.items():
            if drink_pattern in header.lower():
                resp["drink_preference"] = drink_hint
                drink_preference = drink_pattern
                break
        if drink_preference:
            break

    return JSONResponse(resp, 418)


def _safe_decode_body(body: bytes, max_size: int = 3 * 1024 * 1024) -> str:
    """
    Safely decode request body to string.

    Args:
        body: Raw bytes to decode
        max_size: Maximum body size to attempt decoding

    Returns:
        str: Decoded string or error message
    """
    if len(body) > max_size:
        return "body too large to decode"
    try:
        return body.decode("utf-8", "ignore")
    except Exception:
        return "failed to decode body"


@app.get("/")
async def root():
    return JSONResponse(
        {"message": "Welcome to teapot"}, 203, {"Teapot": "hello world!"}
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="localhost", port=4100)

# To run the service, execute this file directly.
