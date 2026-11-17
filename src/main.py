from fastapi import FastAPI
from src.routers.api import api_router

from auth import auth_middleware

app = FastAPI()
app.include_router(api_router)
app.middleware("http")(auth_middleware)


@app.get("/")
def read_root():
    return {"Hello": "World"}

def main() -> None:
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)