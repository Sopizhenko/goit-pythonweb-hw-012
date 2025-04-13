from fastapi import FastAPI

from src.api import contacts, utils

app = FastAPI()

app.include_router(contacts.router)
app.include_router(utils.router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
