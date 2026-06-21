from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import traceback
from contextlib import asynccontextmanager

from backend.routers import auth, workout_plan, planned_sets, actual_set, planned_exercise
from backend.databases.database import init_db
from backend.cache.redis import cache_backend

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    await cache_backend.connect()
    yield
    await cache_backend.close()

app = FastAPI(
    title="1.5 качка",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    print(f"Тип: {type(exc).__name__}")
    print(f"Сообщение: {str(exc)}")
    print("\n Полный Traceback:")
    traceback.print_exc()

    status_code = 500
    detail_message = "Internal Server Error"

    if isinstance(exc, ValueError):
        status_code = 404
        detail_message = str(exc)
    elif isinstance(exc, PermissionError):
        status_code = 400
        detail_message = str(exc)

    return JSONResponse(
        status_code=status_code,
        content={
            "detail": detail_message,
            "exception_type": type(exc).__name__,
            "exception_msg": str(exc),
            "traceback": traceback.format_exc()
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for err in exc.errors():
        msg = err.get('msg')
        if isinstance(msg, Exception):
            msg = str(msg)
        clean_err = {
            "loc": err.get('loc'),
            "msg": msg,
            "type": err.get('type')
        }
        errors.append(clean_err)
    return JSONResponse(
        status_code=422,
        content={"detail": errors}
    )


@app.get("/root")
async def print_hello():
    return "hello"

app.include_router(auth.router)
app.include_router(workout_plan.router)
app.include_router(planned_exercise.router)
app.include_router(planned_sets.router)
app.include_router(actual_set.router)

if __name__ == "__main__":
    uvicorn.run(
        "backend.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info",
    )