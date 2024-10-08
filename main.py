import uvicorn
from app import app

app = app

if __name__ == "__main__":
    uvicorn.run("app:app", host="localhost", port=5555)
