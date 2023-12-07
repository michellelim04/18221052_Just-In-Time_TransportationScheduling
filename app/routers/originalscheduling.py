from fastapi import APIRouter, HTTPException, Depends
import json
from pydantic import BaseModel
from typing import Optional
from ..main import *
from ..auth import get_current_active_user, User
from datetime import datetime

class TransportSchedule(BaseModel): 
	schedule_id : int
	route_name : str
	departure_location : str
	arrival_location : str
	departure_time : str
	arrival_time : str
	vehicle_id : int
	driver_id : int
	status : str

class TransportScheduleUpdate(BaseModel):
	route_name: Optional[str] = None
	departure_location: Optional[str] = None
	arrival_location: Optional[str] = None
	departure_time: Optional[str] = None
	arrival_time: Optional[str] = None
	vehicle_id: Optional[int] = None
	driver_id: Optional[int] = None
	status: Optional[str] = None

json_filename="./app/json/schedule.json"
json_filename1="./app/json/driver.json"
json_filename2="./app/json/vehicle.json"

with open(json_filename,"r") as read_file:
	data = json.load(read_file)
with open(json_filename1,"r") as read_file1:
	data_driver = json.load(read_file1)
with open(json_filename2,"r") as read_file2:
	data_vehicle = json.load(read_file2)

app = APIRouter(
	prefix="/transportationoriginalsched",
	tags=["originalschedule"],
  responses={404: {"description": "Not found"}}
)

@app.get('/')
async def read_all_original_schedule(current_user: User = Depends(get_current_active_user)):
	data = None
	with open (json_filename,"r") as read_file:
		data = json.load(read_file)
	return data["schedule"]
	

@app.get('/search')
async def search_original_schedule(
	route_name: str = None,
	departure_location: str = None,
	arrival_location: str = None,
	departure_time : str = None,
	arrival_time : str = None,
	vehicle_id : int = None,
	driver_id : int = None,
	status : str = None,
	current_user: User = Depends(get_current_active_user)

):
	"""
	Search for schedules based on one or more parameters.
	
	Insert the parameter(s) as follows:
	- `route_name`: (Optional) The name of the route.
	- `departure_location`: (Optional) The name of the departure location.
	- `arrival_location`: (Optional) The name of the arrival location.
	- `departure_time`: (Optional) The time of departure in format 'YYYY-MM-DD HH:MM:SS'.
	- `arrival_time`: (Optional) The time of arrival in format 'YYYY-MM-DD HH:MM:SS'.
	- `vehicle_id`: (Optional) The ID of the vehicle.
	- `driver_id`: (Optional) The ID of the driver.
	- `status`: (Optional) The status of the transportation trip (SCHEDULED/DEPARTED/ONGOING/ARRIVED).

	Returns a list of matching schedules.
	"""
	data = None
	with open (json_filename,"r") as read_file:
		data = json.load(read_file)
		
	matching_schedules = []

	for schedule in data['schedule']:
		if (
			(route_name is None or schedule['route_name'] == route_name) and
			(departure_location is None or schedule['departure_location'] == departure_location) and
			(arrival_location is None or schedule['arrival_location'] == arrival_location) and
			(departure_time is None or schedule['departure_time'] == departure_time) and
			(arrival_time is None or schedule['arrival_time'] == arrival_time) and
			(vehicle_id is None or schedule['vehicle_id'] == vehicle_id) and
			(driver_id is None or schedule['driver_id'] == driver_id) and
			(status is None or schedule['status'] == status) 
		):
			matching_schedules.append(schedule)

	if matching_schedules:
		return matching_schedules
	else:
		raise HTTPException(
			status_code=404, detail=f'Schedule not found'
		)

@app.get('/{schedule_id}')
async def read_original_schedule(schedule_id: int, current_user: User = Depends(get_current_active_user)):
	"""
	Retrieve information about a transportation schedule based on their unique identifier. 
	
	Insert the parameter as follows:
	- `schedule_id`: (Required) The ID of the schedule.
		
	Returns detailed information of a transportation schedule. 
	"""
	data = None
	with open (json_filename,"r") as read_file:
		data = json.load(read_file)
		
	for schedule_schedules in data['schedule']:
		print(schedule_schedules)
		if schedule_schedules['schedule_id'] == schedule_id:
			return schedule_schedules
	raise HTTPException(
		status_code=404, detail=f'Schedule not found'
	)

@app.post('/')
async def add_original_schedule(schedules: TransportSchedule, current_user: User = Depends(get_current_active_user)):
	"""
	Add a schedule's information in the dataset based on the schedule's unique identifier.

	Checks whether a schedule with the specified ID exists in the database.
	If the schedule does not exist, the function will add the schedule to the dataset. 
	
	Insert the parameter(s) in the request body as follows:
	- `schedule_id`: (Required) The ID of the schedule.
	- `route_name`: (Required) The name of the route.
	- `departure_location`: (Required) The name of the departure location.
	- `arrival_location`: (Required) The name of the arrival location.
	- `departure_time`: (Required) The time of departure in format 'YYYY-MM-DD HH:MM:SS'.
	- `arrival_time`: (Required) The time of arrival in format 'YYYY-MM-DD HH:MM:SS'.
	- `vehicle_id`: (Required) The ID of the vehicle.
	- `driver_id`: (Required) The ID of the driver.
	- `status`: (Required) The status of the transportation trip (SCHEDULED/DEPARTED/ONGOING/ARRIVED).
		
	Returns the schedule's information if added.
	If the schedule already exists, it returns a message indicating the schedule exists.
	"""
	data = None
	with open (json_filename,"r") as read_file:
		data = json.load(read_file)
		
	schedules_dict = schedules.dict()
	
    # status validation
	if schedules_dict["status"] not in ["SCHEDULED", "DEPARTED", "ONGOING", "ARRIVED"]:
		raise HTTPException (
			status_code = 400, 
			detail = "Status value should be SCHEDULED/DEPARTED/ONGOING/ARRIVED."
		)
	
	# vehicle id validation
	vehicle_found = False
	for vehicle_vehicles in data_vehicle['vehicle']:
		if vehicle_vehicles['vehicle_id'] == schedules_dict['vehicle_id']:
			vehicle_found = True
	if not vehicle_found:
		raise HTTPException(
			status_code=404, detail=f'Vehicle not found'
		)
	
	# driver id validation
	driver_found = False
	for driver_drivers in data_driver['driver']:
		if driver_drivers['driver_id'] == schedules_dict['driver_id']:
			driver_found = True
	if not driver_found:
		raise HTTPException(
			status_code=404, detail=f'Driver not found'
		)

	# datetime format validation
	try:
		datetime.strptime(schedules_dict["departure_time"], '%Y-%m-%d %H:%M:%S')
	except ValueError:
		raise HTTPException(
		status_code=400, 
		detail="Incorrect time format. It should be 'YYYY-MM-DD HH:MM:SS'."
	)
	
    # datetime format validation
	try:
		datetime.strptime(schedules_dict["arrival_time"], '%Y-%m-%d %H:%M:%S')
	except ValueError:
		raise HTTPException(
		status_code=400, 
		detail="Incorrect time format. It should be 'YYYY-MM-DD HH:MM:SS'."
	)
    

	schedules_found = False
	for schedule_schedules in data['schedule']:
		if schedule_schedules['schedule_id'] == schedules_dict['schedule_id']:
			schedules_found = True
			return "Schedule ID "+str(schedules_dict['schedule_id'])+" exists."
	
	if not schedules_found:
		data['schedule'].append(schedules_dict)
		with open(json_filename,"w") as write_file:
			json.dump(data, write_file)

		return schedules_dict
	raise HTTPException(
		status_code=404, detail=f'Schedule not found'
	)

@app.put('/{schedule_id}')
async def update_original_schedule(schedule_id: int, schedules: TransportScheduleUpdate, current_user: User = Depends(get_current_active_user)):
	"""
	Update a schedule's information based on the schedule's unique ID.

	In the request body, specify the schedule's unique schedule ID and put updates of the parameters you want to update:
	- `schedule_id`: (Required) The ID of the schedule.
	- `route_name`: (Optional) The name of the route.
	- `departure_location`: (Optional) The name of the departure location.
	- `arrival_location`: (Optional) The name of the arrival location.
	- `departure_time`: (Optional) The time of departure in format 'YYYY-MM-DD HH:MM:SS'.
	- `arrival_time`: (Optional) The time of arrival in format 'YYYY-MM-DD HH:MM:SS'.
	- `vehicle_id`: (Optional) The ID of the vehicle.
	- `driver_id`: (Optional) The ID of the driver.
	- `status`: (Optional) The status of the transportation trip (SCHEDULED/DEPARTED/ONGOING/ARRIVED).

	For the parameters that are not to be updated, please delete them before executing the function.  

	If the schedule with the specified ID exists, returns "updated" to indicate a successful update.
	Else, returns "Schedule ID not found." to indicate the specified schedule to be updated does not exist.
	"""
	data = None
	with open (json_filename,"r") as read_file:
		data = json.load(read_file)
		
	schedules_dict = schedules.dict(exclude_unset=True)
	
    # status validation
	if 'status' in schedules_dict:
		if schedules_dict["status"] not in ["SCHEDULED", "DEPARTED", "ONGOING", "ARRIVED"]:
			raise HTTPException (
				status_code = 400, 
				detail = "Status value should be SCHEDULED/DEPARTED/ONGOING/ARRIVED."
			)
	
	# vehicle id validation
	if 'vehicle_id' in schedules_dict:
		vehicle_found = False
		for vehicle_vehicles in data_vehicle['vehicle']:
			if vehicle_vehicles['vehicle_id'] == schedules_dict['vehicle_id']:
				vehicle_found = True
		if not vehicle_found:
			raise HTTPException(
				status_code=404, detail=f'Vehicle not found'
			)
	
	# driver id validation
	if 'driver_id' in schedules_dict:
		driver_found = False
		for driver_drivers in data_driver['driver']:
			if driver_drivers['driver_id'] == schedules_dict['driver_id']:
				driver_found = True
		if not driver_found:
			raise HTTPException(
				status_code=404, detail=f'Driver not found'
			)

	# datetime format validation
	if 'departure_time' in schedules_dict:
		try:
			datetime.strptime(schedules_dict["departure_time"], '%Y-%m-%d %H:%M:%S')
		except ValueError:
			raise HTTPException(
			status_code=400, 
			detail="Incorrect time format. It should be 'YYYY-MM-DD HH:MM:SS'."
		)
		
    # datetime format validation
	if 'arrival_time' in schedules_dict:
		try:
			datetime.strptime(schedules_dict["arrival_time"], '%Y-%m-%d %H:%M:%S')
		except ValueError:
			raise HTTPException(
			status_code=400, 
			detail="Incorrect time format. It should be 'YYYY-MM-DD HH:MM:SS'."
		)

	schedules_found = False
	for schedule_idx, schedule_schedules in enumerate(data['schedule']):
		if schedule_schedules['schedule_id'] == schedule_id:
			schedules_found = True
			for field, value in schedules_dict.items():
				data['schedule'][schedule_idx][field] = value
			with open(json_filename,"w") as write_file:
				json.dump(data, write_file)
			return "updated"
		
	if not schedules_found:
		return "Schedule ID not found."
	raise HTTPException(
		status_code=404, detail=f'Schedule not found'
	)
		
@app.delete('/{schedule_id}')
async def delete_original_schedule(schedule_id: int, current_user: User = Depends(get_current_active_user)):

	"""
	Delete a schedule's information by specifying their unique identifier. 
	
	Insert the parameter as follows:
	- `schedule_id`: (Required) The ID of the schedule.
		
	Returns "deleted" to indicate a successful deletion of a schedule's data
	with the specified ID. 
	"""
	data = None
	with open (json_filename,"r") as read_file:
		data = json.load(read_file)

	schedules_found = False
	for schedule_idx, schedule_schedules in enumerate(data['schedule']):
		if schedule_schedules['schedule_id'] == schedule_id:
			schedules_found = True
			data['schedule'].pop(schedule_idx)
			
			with open(json_filename,"w") as write_file:
				json.dump(data, write_file)
			return "deleted"
	
	if not schedules_found:
		return "Schedule ID not found."
	raise HTTPException(
		status_code=404, detail=f'Schedule not found'
	)