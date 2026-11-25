from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from routers.api import api_router
from auth import auth_middleware

app = FastAPI()

app.include_router(api_router)


@app.get("/")
def read_root():
    return {"Hello": "World"}


app.middleware("http")(auth_middleware)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    # Drop "input" and "ctx": they can echo the client's payload back.
    errors = [
        {key: value for key, value in error.items() if key not in ("input", "ctx")}
        for error in exc.errors()
    ]
    messages = [error["msg"] for error in errors]

    return JSONResponse(
        status_code=422,
        content={
            "error": "; ".join(messages),
            "detail": jsonable_encoder(errors),
        },
    )


def main() -> None:
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=3000)

if __name__ == "__main__":
    main()