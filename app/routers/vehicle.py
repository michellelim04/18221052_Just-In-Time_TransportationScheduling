from fastapi import APIRouter, HTTPException
import json
from pydantic import BaseModel


class Vehicles(BaseModel): 
	vehicle_id : int
	make : str
	model : str
	year : int
	registration_no : str

json_filename="./app/json/vehicle.json"

with open(json_filename,"r") as read_file:
	data = json.load(read_file)

app = APIRouter(
	prefix="/vehicle",
	tags=["vehicle"],
  responses={404: {"description": "Not found"}}
)

@app.get('/')
async def read_all_vehicle():
	return data['vehicle']

@app.get('/search')
async def search_vehicle(vehicles_id: int = None, make: str = None, model: str = None, year: int = None, registration_no: str = None):
	matching_vehicles = []

	for vehicle in data['vehicle']:
		if (
			(vehicles_id is None or vehicle['vehicle_id'] == vehicles_id) and
			(make is None or vehicle['make'] == make) and
			(model is None or vehicle['model'] == model) and
			(year is None or vehicle['year'] == year) and
			(registration_no is None or vehicle['registration_no'] == registration_no)
		):
			matching_vehicles.append(vehicle)

	if matching_vehicles:
		return matching_vehicles
	else:
		raise HTTPException(
			status_code=404, detail=f'vehicle not found'
		)

@app.get('/{vehicles_id}')
async def read_vehicle(vehicles_id: int):
	for vehicle_vehicles in data['vehicle']:
		print(vehicle_vehicles)
		if vehicle_vehicles['vehicle_id'] == vehicles_id:
			return vehicle_vehicles
	raise HTTPException(
		status_code=404, detail=f'vehicle not found'
	)

@app.post('/')
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

@app.put('/')
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

@app.delete('/{vehicles_id}')
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
