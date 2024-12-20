import uvicorn
from fastapi import FastAPI

from .database.database import client, client_article
from .routers import endpoints

app = FastAPI()
app.include_router(endpoints.router)

if __name__ == "__main__":

    client.connect()
    client_article()

    uvicorn.run(app, host="0.0.0.0", port=8000)
