import uvicorn

from ..service.rest_service import router

def main():
    print("Service started")
    uvicorn.run(router, host="0.0.0.0", port=80)

if __name__ == "__main__":
    main()