from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


def main() -> None:
    import uvicorn

    uvicorn.run("main:app")
