from fastapi import FastAPI, HTTPException
import json
from pydantic import BaseModel


class Vehicles(BaseModel): 
	vehicle_id : int
	make : str
	model : str
	year : int
	registration_no : str

json_filename="vehicle.json"

with open(json_filename,"r") as read_file:
	data = json.load(read_file)

app = FastAPI()

@app.get('/vehicle')
async def read_all_vehicle():
	return data['vehicle']


@app.get('/vehicle/{vehicles_id}')
async def read_vehicle(vehicles_id: int):
	for vehicle_vehicles in data['vehicle']:
		print(vehicle_vehicles)
		if vehicle_vehicles['vehicle_id'] == vehicles_id:
			return vehicle_vehicles
	raise HTTPException(
		status_code=404, detail=f'vehicle not found'
	)

@app.post('/vehicle')
async def add_vehicle(vehicles: Vehicles):
	vehicles_dict = vehicles.dict()
	vehicles_found = False
	for vehicle_vehicles in data['vehicle']:
		if vehicle_vehicles['vehicle_id'] == vehicles_dict['vehicle_id']:
			vehicles_found = True
			return "Driver ID "+str(vehicles_dict['vehicle_id'])+" exists."
	
	if not vehicles_found:
		data['vehicle'].append(vehicles_dict)
		with open(json_filename,"w") as write_file:
			json.dump(data, write_file)

		return vehicles_dict
	raise HTTPException(
		status_code=404, detail=f'vehicle not found'
	)

@app.put('/vehicle')
async def update_vehicle(vehicles: Vehicles):
	vehicles_dict = vehicles.dict()
	vehicles_found = False
	for vehicle_idx, vehicle_vehicles in enumerate(data['vehicle']):
		if vehicle_vehicles['vehicle_id'] == vehicles_dict['vehicle_id']:
			vehicles_found = True
			data['vehicle'][vehicle_idx]=vehicles_dict
			
			with open(json_filename,"w") as write_file:
				json.dump(data, write_file)
			return "updated"
	
	if not vehicles_found:
		return "Driver ID not found."
	raise HTTPException(
		status_code=404, detail=f'vehicle not found'
	)

@app.delete('/vehicle/{vehicles_id}')
async def delete_vehicle(vehicles_id: int):

	vehicles_found = False
	for vehicle_idx, vehicle_vehicles in enumerate(data['vehicle']):
		if vehicle_vehicles['id'] == vehicles_id:
			vehicles_found = True
			data['vehicle'].pop(vehicle_idx)
			
			with open(json_filename,"w") as write_file:
				json.dump(data, write_file)
			return "updated"
	
	if not vehicles_found:
		return "Driver ID not found."
	raise HTTPException(
		status_code=404, detail=f'vehicle not found'
	)
