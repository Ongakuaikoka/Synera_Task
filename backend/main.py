from fastapi import FastAPI

from routers import chat

app = FastAPI()

app.include_router(chat.router)


if __name__ == "__main__":
    for r in app.routes:
        print("ROUTE", getattr(r, "methods", None), r.path)