"""FastAPI application entrypoint for DeployLens."""

from fastapi import FastAPI

app = FastAPI(title="DeployLens API", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    """Return the service liveness status."""

    return {"status": "ok", "service": "deploylens-api"}
