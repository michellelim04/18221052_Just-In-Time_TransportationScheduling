from typing import Union
from fastapi  import FastAPI

from .routers import driver, schedule, vehicle


app = FastAPI()

app.include_router(driver.router)
app.include_router(schedule.router)
app.include_router(vehicle.router)


@app.get("/")
def read_root():
	return {"message": "Hello World"}
