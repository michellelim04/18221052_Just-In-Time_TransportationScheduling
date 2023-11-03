from fastapi import APIRouter, HTTPException
import json
from pydantic import BaseModel


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

json_filename="./app/json/schedule.json"

with open(json_filename,"r") as read_file:
	data = json.load(read_file)

app = APIRouter(
	prefix="/schedule",
	tags=["schedule"],
  responses={404: {"description": "Not found"}}
)

@app.get('/')
async def read_all_schedule():
	return data['schedule']

@app.get('/search')
async def search_schedule(
	route_name: str = None,
	departure_location: str = None,
	arrival_location: str = None,
	departure_time : str = None,
	arrival_time : str = None,
	vehicle_id : int = None,
	driver_id : int = None,
	status : str = None

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

@app.get('/{schedules_id}')
async def read_schedule(schedules_id: int):
	"""
	Retrieve information about a transportation schedule based on their unique identifier. 
	
	Insert the parameter as follows:
	- `schedules_id`: (Required) The ID of the schedule.
		
	Returns detailed information of a transportation schedule. 
	"""
	for schedule_schedules in data['schedule']:
		print(schedule_schedules)
		if schedule_schedules['schedule_id'] == schedules_id:
			return schedule_schedules
	raise HTTPException(
		status_code=404, detail=f'Schedule not found'
	)

@app.post('/')
async def add_schedule(schedules: TransportSchedule):
	"""
	Add a schedule's information in the dataset based on the schedule's unique identifier.

	Checks whether a schedule with the specified ID exists in the database.
	If the schedule does not exist, the function will add the schedule to the dataset. 
	
	Insert the parameter(s) in the request body as follows:
	- `schedule_id`: (Required) The ID of the schedule.
	- `route_name`: (Optional) The name of the route.
	- `departure_location`: (Optional) The name of the departure location.
	- `arrival_location`: (Optional) The name of the arrival location.
	- `departure_time`: (Optional) The time of departure in format 'YYYY-MM-DD HH:MM:SS'.
	- `arrival_time`: (Optional) The time of arrival in format 'YYYY-MM-DD HH:MM:SS'.
	- `vehicle_id`: (Optional) The ID of the vehicle.
	- `driver_id`: (Optional) The ID of the driver.
	- `status`: (Optional) The status of the transportation trip (SCHEDULED/DEPARTED/ONGOING/ARRIVED).
		
	Returns the schedule's information if added.
	If the schedule already exists, it returns a message indicating the schedule exists.
	"""
	schedules_dict = schedules.dict()
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

@app.put('/')

async def update_schedule(schedules: TransportSchedule):
	"""
	Update a schedule's information based on the schedule's unique ID.

	In the request body, specify the schedule's unique schedule ID and put updates of the following parameter:
	- `schedule_id`: (Required) The ID of the schedule.
	- `route_name`: (Optional) The name of the route.
	- `departure_location`: (Optional) The name of the departure location.
	- `arrival_location`: (Optional) The name of the arrival location.
	- `departure_time`: (Optional) The time of departure in format 'YYYY-MM-DD HH:MM:SS'.
	- `arrival_time`: (Optional) The time of arrival in format 'YYYY-MM-DD HH:MM:SS'.
	- `vehicle_id`: (Optional) The ID of the vehicle.
	- `driver_id`: (Optional) The ID of the driver.
	- `status`: (Optional) The status of the transportation trip (SCHEDULED/DEPARTED/ONGOING/ARRIVED).

	If the schedule with the specified ID exists, returns "updated" to indicate a successful update.
	Else, returns "Schedule ID not found." to indicate the specified schedule to be updated does not exist.
	"""
	schedules_dict = schedules.dict()
	schedules_found = False
	for schedule_idx, schedule_schedules in enumerate(data['schedule']):
		if schedule_schedules['schedule_id'] == schedules_dict['schedule_id']:
			schedules_found = True
			data['schedule'][schedule_idx]=schedules_dict
			
			with open(json_filename,"w") as write_file:
				json.dump(data, write_file)
			return "updated"
	
	if not schedules_found:
		return "Schedule ID not found."
	raise HTTPException(
		status_code=404, detail=f'Schedule not found'
	)

@app.delete('/{schedules_id}')
async def delete_schedule(schedules_id: int):

	"""
	Delete a schedule's information by specifying their unique identifier. 
	
	Insert the parameter as follows:
	- `schedules_id`: (Required) The ID of the schedule.
		
	Returns "deleted" to indicate a successful deletion of a schedule's data
	with the specified ID. 
	"""

	schedules_found = False
	for schedule_idx, schedule_schedules in enumerate(data['schedule']):
		if schedule_schedules['id'] == schedules_id:
			schedules_found = True
			data['schedule'].pop(schedule_idx)
			
			with open(json_filename,"w") as write_file:
				json.dump(data, write_file)
			return "updated"
	
	if not schedules_found:
		return "Schedule ID not found."
	raise HTTPException(
		status_code=404, detail=f'Schedule not found'
	)
