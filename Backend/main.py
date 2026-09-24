import uvicorn
from fastapi import FastAPI

app = FastAPI()

@app.get("/firstRoute")
def demo_route():
    return {"message": "Hello from the first route!"}

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "RAGX-Enterprise"
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
