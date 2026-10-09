import uvicorn

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from Backend.Routes.Auth import route as auth_router
from Backend.Routes.Health import router as health_router
from Backend.Routes.Chat import router as chat_router
from Backend.Exceptions.Exceptions import AppException

app = FastAPI(
    title="RAGX-Enterprise API",
    description=(
        "API for RAGX-Enterprise, "
        "an enterprise RAG and agent system."
    ),
    version="1.0.0",
)

app.include_router(
    health_router
)

app.include_router(
    chat_router
)

app.include_router(
    auth_router
)

@app.exception_handler(AppException)
async def app_exception_handler(
    request: Request,
    exc: AppException
):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": exc.error_code,
                "message": exc.message
            }
        }
    )

@app.exception_handler(Exception)
async def unexpected_exception_handler(
    request: Request,
    exc: Exception
):
    print("UNEXPECTED ERROR:", repr(exc))

    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred."
            }
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
):
    details = []

    for error in exc.errors():
        location = error.get("loc", ())

        field = ".".join(
            str(part)
            for part in location
            if part not in ("body", "query", "path", "header")
        )

        details.append({
            "field": field or "request",
            "reason": error.get("msg", "Invalid value.")
        })

    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Invalid request.",
                "details": details
            }
        }
    )

@app.get("/")
def root():

    return {
        "message": "RAGX-Enterprise API is running"
    }

if __name__ == "__main__":

    uvicorn.run(
        "Backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )