from fastapi  import FastAPI

from .routers import driver, schedule, vehicle


tags_metadata = [
	  {
		  "name" : "driver",
		  "description" : "This route of Driver's Directory allows you to Search, Get, Add, Update, and Delete Drivers' Data."},
	  {
		  "name" : "schedule",
		  "description" : "This route of Transportation Scheduling allows you to Search, Get, Add, Update, and Delete Schedules' Data. The Update feature ensures Just-In-Time Delivery by allowing Transportation Status Updates"},

	  {
		  "name" : "vehicle",
		  "description" : "This route of Vehicle's Directory allows you to Search, Get, Add, Update, and Delete Vehicles' Data."}

  ]

app = FastAPI(openapi_tags=tags_metadata)


app.include_router(driver.app)
app.include_router(schedule.app)
app.include_router(vehicle.app)


@app.get("/")
def read_root():
	return {"message": "Hello World"}

@app.get("/ping")
def ping():
	return {"status": 200, "valid": 1, "message": "pong"}
