from fastapi import FastAPI

app = FastAPI(
    title="BODH API",
    description="AI Decision Intelligence Platform",
    version="0.1.0"
)


@app.get("/")
async def root():
    return {
        "project": "BODH",
        "version": "0.1.0",
        "status": "running"
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy"
    }