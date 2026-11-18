from fastapi import FastAPI
from routers.api import api_router

from auth import auth_middleware

app = FastAPI()
app.include_router(api_router)
app.middleware("http")(auth_middleware)


@app.get("/")
def read_root():
    return {"Hello": "World"}

def main() -> None:
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=3000)