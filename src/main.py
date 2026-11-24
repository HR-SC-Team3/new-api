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


@app.middleware("http")
async def check_item_content_type(request, call_next):
    if (
        request.url.path == "/api/v1/items"
        or request.url.path.startswith("/api/v1/items/")
    ) and request.method in ("POST", "PUT"):

        content_type = request.headers.get("content-type", "")
        content_type = content_type.split(";")[0].strip().lower()

        if content_type != "application/json":
            return JSONResponse(
                status_code=415,
                content={"detail": "Content-Type must be application/json"},
            )

    return await call_next(request)

app.middleware("http")(auth_middleware)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    messages = [
        error["msg"]
        for error in exc.errors()
    ]

    return JSONResponse(
        status_code=422,
        content={
            "error": "; ".join(messages),
            "detail": jsonable_encoder(exc.errors()),
        },
    )


def main() -> None:
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=3000)

if __name__ == "__main__":
    main()