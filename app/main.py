from fastapi  import FastAPI, Depends

from .routers import driver, schedule, vehicle

from .auth import *

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
app.include_router(router)


    
# Register a new user
@app.post('/register')
async def register_user(new_user: User, current_user: User = Depends(get_current_active_user)):
    user_dict = new_user.dict()
    user_found = False

    for user in users_data:
        if new_user.username == user or new_user.user_id == user[0]:
            user_found = True
    
    if not user_found:
        createdUser = UserCreate()
        createdUser.user_id = new_user.user_id
        createdUser.username = new_user.username
        createdUser.password_preprocessed = ""
        createdUser.hashed_password = get_password_hash(new_user.password_preprocessed)
        createdUser.isOwner = 0
        createdUser.isAdmin = 1
        createdUser.disabled = 0

        finalNewUser = vars(createdUser)

        users_data[new_user.username]= finalNewUser
        

        with open("./app/json/users.json", "w") as write_file:
            json.dump(users_data, write_file, indent=2)

        return finalNewUser

    else:
        return "Username or ID taken"


@app.get("/")
def read_root():
	return {"message": "Hello World"}

@app.get("/ping")
def ping():
	return {"status": 200, "valid": 1, "message": "pong"}
