from fastapi import FastAPI, HTTPException
import json
from pydantic import BaseModel


class Drivers(BaseModel): 
	driver_id : int
	name : str
	license_no : str
	date_of_birth : str
	contact_no : str
	email : str
	address : str



json_filename="driver.json"

with open(json_filename,"r") as read_file:
	data = json.load(read_file)

app = FastAPI()

@app.get('/driver')
async def read_all_driver():
	return data['driver']


@app.get('/driver/{drivers_id}')
async def read_driver(drivers_id: int):
	for driver_drivers in data['driver']:
		print(driver_drivers)
		if driver_drivers['driver_id'] == drivers_id:
			return driver_drivers
	raise HTTPException(
		status_code=404, detail=f'driver not found'
	)

@app.post('/driver')
async def add_driver(drivers: Drivers):
	drivers_dict = drivers.dict()
	drivers_found = False
	for driver_drivers in data['driver']:
		if driver_drivers['driver_id'] == drivers_dict['driver_id']:
			drivers_found = True
			return "Driver ID "+str(drivers_dict['driver_id'])+" exists."
	
	if not drivers_found:
		data['driver'].append(drivers_dict)
		with open(json_filename,"w") as write_file:
			json.dump(data, write_file)

		return drivers_dict
	raise HTTPException(
		status_code=404, detail=f'driver not found'
	)

@app.put('/driver')
async def update_driver(drivers: Drivers):
	drivers_dict = drivers.dict()
	drivers_found = False
	for driver_idx, driver_drivers in enumerate(data['driver']):
		if driver_drivers['driver_id'] == drivers_dict['driver_id']:
			drivers_found = True
			data['driver'][driver_idx]=drivers_dict
			
			with open(json_filename,"w") as write_file:
				json.dump(data, write_file)
			return "updated"
	
	if not drivers_found:
		return "Driver ID not found."
	raise HTTPException(
		status_code=404, detail=f'driver not found'
	)

@app.delete('/driver/{drivers_id}')
async def delete_driver(drivers_id: int):

	drivers_found = False
	for driver_idx, driver_drivers in enumerate(data['driver']):
		if driver_drivers['id'] == drivers_id:
			drivers_found = True
			data['driver'].pop(driver_idx)
			
			with open(json_filename,"w") as write_file:
				json.dump(data, write_file)
			return "updated"
	
	if not drivers_found:
		return "Driver ID not found."
	raise HTTPException(
		status_code=404, detail=f'driver not found'
	)
