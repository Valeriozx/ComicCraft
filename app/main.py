import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.routes import router

app = FastAPI(
    title="ComicCraft - AI Comic Story Creator",
    description="Full-stack AI Application for generating comic book panels, scripts, images, and PDFs",
    version="1.0.0"
)

# Static directory path
static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
os.makedirs(os.path.join(static_dir, "panels"), exist_ok=True)
os.makedirs(os.path.join(static_dir, "exports"), exist_ok=True)

app.mount("/static", StaticFiles(directory=static_dir), name="static")

app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
