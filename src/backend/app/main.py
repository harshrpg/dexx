import os
import multiprocessing
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes.process import router as process_router
from app.api.routes.auth import router as auth_router
from app.api.routes.threads import router as thread_router
import logging
from app.lib.config.logging_config import setup_logging
from app.middleware import auth_middleware


def print_startup_banner():
    banner = """
\033[36m╔════════════════════════════════════════════════════════════════════
║                                                                            ║
║     $$$$$$\                      $$\                                      ║
║    $$  __$$\                     $$ |                                     ║
║    $$ /  $$ | $$$$$$\   $$$$$$\  $$ |  $$\  $$\   $$\  $$$$$$$\        ║
║    $$$$$$$$ | \____$$\ $$  __$$\ $$ | $$  | $$ |  $$ |$$  _____|       ║
║    $$  __$$ | $$$$$$$ |$$ |  \__|$$$$$$  /  $$ |  $$ |\$$$$$$\         ║
║    $$ |  $$ |$$  __$$ |$$ |      $$  _$$<   $$ |  $$ | \____$$\        ║
║    $$ |  $$ |\$$$$$$$ |$$ |      $$ | \$$\  \$$$$$$  |$$$$$$$  |       ║
║    \__|  \__| \_______|\__|      \__|  \__|  \______/ \_______/         ║
║                                                                          ║
║        Aarkus Intelligence Token Insights Server v1.0.0                  ║
╚════════════════════════════════════════════════════════════════════════════╝\033[0m
"""
    logger = logging.getLogger(__name__)
    logger.info(banner)
    logger.info(
        "\033[32m✨ Welcome to Aarkus Intelligence Token Insights Server ✨\033[0m"
    )
    logger.info("\033[34m🚀 Server initialization in progress...\033[0m")


app = FastAPI()
setup_logging()
print_startup_banner()
logger = logging.getLogger(__name__)
app.include_router(router=process_router)
app.include_router(router=auth_router)
app.include_router(router=thread_router)

allowed_origins = [
    "http://localhost:3000",
    "https://agent-iz88b0umx-harshrpgs-projects.vercel.app",
    "https://agent-ui-alpha.vercel.app",
    "https://agent-ui-harshrpgs-projects.vercel.app",
    "https://agent-ui-git-main-harshrpgs-projects.vercel.app",
    "https://www.agentdexx.ai",
    "https://staging.agentdexx.ai",
    "http://192.168.0.5:3000",
    "http://172.18.70.254:3000",
    "http://192.168.0.2:3000",
]

allowed_methods = ["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH"]

allowed_headers = [
    "Content-Type",
    "Authorization",
    "X-Session-ID",
    "Accept",
    "Origin",
    "X-Requested-With",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=allowed_methods,
    allow_headers=allowed_headers,
    expose_headers=["X-Session-ID"],
    max_age=3600,
)


@app.get("/")
def read_root():
    return {"message": "Welcome to Token Insights Server!"}


def worker_count():
    return (multiprocessing.cpu_count() * 2) + 1


if __name__ == "__main__":
    import uvicorn

    logger.info(
        "\033[35m💫 Starting server on port %s\033[0m", os.environ.get("PORT", 8000)
    )
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        workers=worker_count(),
        loop="auto",
        limit_concurrency=100,
        limit_max_requests=10000,
        timeout_keep_alive=30,
        log_config=None,
        access_log=False,
    )
