from fastapi import FastAPI

app = FastAPI(title="ClipOps API")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
