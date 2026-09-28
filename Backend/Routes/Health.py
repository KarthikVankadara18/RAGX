from fastapi import APIRouter

router= APIRouter(
    prefix= "/health",
    tags= ["Health Check"],
)

@router.get("/")
def check_test():
    return{
        "status": "healthy",
    }