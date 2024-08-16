import uvicorn

from ..service.rest_service import router

def main():
    uvicorn.run(router, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()