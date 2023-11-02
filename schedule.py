from fastapi import FastAPI, HTTPException
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

json_filename="schedule.json"

with open(json_filename,"r") as read_file:
	data = json.load(read_file)

app = FastAPI()

@app.get('/schedule')
async def read_all_schedule():
	return data['schedule']


@app.get('/schedule/{schedules_id}')
async def read_schedule(schedules_id: int):
	for schedule_schedules in data['schedule']:
		print(schedule_schedules)
		if schedule_schedules['schedule_id'] == schedules_id:
			return schedule_schedules
	raise HTTPException(
		status_code=404, detail=f'schedule not found'
	)

@app.get('/schedule/search')
async def search_schedules(
	name: str = None,
	route_name: str = None,
	departure_location: str = None,
	arrival_location: str = None,
	departure_time : str = None,
	arrival_time : str = None,
	vehicle_id : int = None,
	driver_id : int = None,
	status : str = None

):
	matching_schedules = []

	for schedule in data['schedule']:
		if (
			(name is None or schedule['name'] == name) and
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
			status_code=404, detail=f'schedule not found'
		)

@app.post('/schedule')
async def add_schedule(schedules: TransportSchedule):
	schedules_dict = schedules.dict()
	schedules_found = False
	for schedule_schedules in data['schedule']:
		if schedule_schedules['schedule_id'] == schedules_dict['schedule_id']:
			schedules_found = True
			return "Driver ID "+str(schedules_dict['schedule_id'])+" exists."
	
	if not schedules_found:
		data['schedule'].append(schedules_dict)
		with open(json_filename,"w") as write_file:
			json.dump(data, write_file)

		return schedules_dict
	raise HTTPException(
		status_code=404, detail=f'schedule not found'
	)

@app.put('/schedule')
async def update_schedule(schedules: TransportSchedule):
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
		return "Driver ID not found."
	raise HTTPException(
		status_code=404, detail=f'schedule not found'
	)

@app.delete('/schedule/{schedules_id}')
async def delete_schedule(schedules_id: int):

	schedules_found = False
	for schedule_idx, schedule_schedules in enumerate(data['schedule']):
		if schedule_schedules['id'] == schedules_id:
			schedules_found = True
			data['schedule'].pop(schedule_idx)
			
			with open(json_filename,"w") as write_file:
				json.dump(data, write_file)
			return "updated"
	
	if not schedules_found:
		return "Driver ID not found."
	raise HTTPException(
		status_code=404, detail=f'schedule not found'
	)
