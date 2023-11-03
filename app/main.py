from typing import Union
from fastapi  import FastAPI

from .routers import driver, schedule, vehicle


app = FastAPI()

app.include_router(driver.app)
app.include_router(schedule.app)
app.include_router(vehicle.app)


@app.get("/")
def read_root():
	return {"message": "Hello World"}

@app.get("/ping")
def ping():
	return {"status": 200, "valid": 1, "message": "pong"}
