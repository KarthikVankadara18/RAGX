import uvicorn
from fastapi import FastAPI
from Backend.Routes.Health import router as health_router
from Backend.Routes.Chat import router as chat_router

app = FastAPI(
    title= "RAGX-Enterprise API",
    description= "This is the API for RAGX-Enterprise, a powerful tool for managing and analyzing data.",
)

app.include_router(health_router)
app.include_router(chat_router)

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