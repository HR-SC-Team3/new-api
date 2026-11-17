from fastapi import FastAPI

from auth import auth_middleware

app = FastAPI()
app.middleware("http")(auth_middleware)


@app.get("/")
def read_root():
    return {"Hello": "World"}


def main() -> None:
    import uvicorn

    uvicorn.run("main:app")
