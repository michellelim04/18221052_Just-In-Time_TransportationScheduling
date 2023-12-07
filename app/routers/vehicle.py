from fastapi import APIRouter, HTTPException, Depends
import json
from pydantic import BaseModel
from typing import Optional
from ..main import *
from ..auth import get_current_active_user, User
import re

class Vehicles(BaseModel): 
	vehicle_id : int
	make : str
	model : str
	year : int
	registration_no : str

class VehiclesUpdate(BaseModel):
	make: Optional[str] = None
	model: Optional[str] = None
	year: Optional[int] = None
	registration_no: Optional[str] = None

json_filename="./app/json/vehicle.json"

with open(json_filename,"r") as read_file:
	data = json.load(read_file)

app = APIRouter(
	prefix="/vehicle",
	tags=["vehicle"],
  responses={404: {"description": "Not found"}}
)

@app.get('/')
async def read_all_vehicle(current_user: User = Depends(get_current_active_user)):
	return data['vehicle']

@app.get('/search')
async def search_vehicle(vehicles_id: int = None, make: str = None, model: str = None, year: int = None, registration_no: str = None, current_user: User = Depends(get_current_active_user)):
	"""
	Search for vehicles based on one or more parameters.
	
	Insert the parameter(s) as follows:
	- `vehicles_id`: (Optional) The ID of the vehicle.
	- `make`: (Optional) The make of the vehicle.
	- `model`: (Optional) The vehicle's model name.
	- `year`: (Optional) The vehicle's manufactured year.
	- `registration_no`: (Optional) The vehicle's registration plate.

	Returns a list of matching vehicles.
	"""
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
async def read_vehicle(vehicles_id: int, current_user: User = Depends(get_current_active_user)):
	"""
	Retrieve information about a vehicle based on their unique identifier. 
	
	Insert the parameter as follows:
	- `vehicles_id`: (Required) The ID of the vehicle.
		
	Returns detailed information of a vehicle. 
    """
	for vehicle_vehicles in data['vehicle']:
		print(vehicle_vehicles)
		if vehicle_vehicles['vehicle_id'] == vehicles_id:
			return vehicle_vehicles
	raise HTTPException(
		status_code=404, detail=f'vehicle not found'
	)

@app.post('/')
async def add_vehicle(vehicles: Vehicles, current_user: User = Depends(get_current_active_user)):
	"""
	Add a vehicle's information in the dataset based on the vehicle's unique identifier.

	Checks whether a vehicle with the specified ID exists in the database.
	If the vehicle does not exist, the function will add the vehicle to the dataset. 
	
	Insert the parameter(s) in the request body as follows:
	- `vehicle_id`: (Required) The ID of the vehicle.
	- `make`: (Optional) The make of the vehicle.
	- `model`: (Optional) The vehicle's model name.
	- `year`: (Optional) The vehicle's manufactured year.
	- `registration_no`: (Optional) The unique vehicle's registration plate.

	Returns the vehicle's information if added.
	If the vehicle already exists, it returns a message indicating the vehicle exists.
	"""
	vehicles_dict = vehicles.dict()

	# Validate registration_no
	if not re.match(r'^[A-Z]{1,2}\d{1,4}[A-Z]{1,3}$', vehicles_dict["registration_no"]):
		raise HTTPException(
			status_code=400, 
			detail="Incorrect registration plate format."
		)
	
	# Validate year
	if vehicles_dict["year"] > 2040 or vehicles_dict["year"] < 1900:
		raise HTTPException(
			status_code=400, 
			detail="Invalid manufacture year."
		)
	
	# Validate unique registration_no
	vehicles_unique = True
	for vehicle_vehicles in data['vehicle']:
		if vehicle_vehicles['registration_no'] == vehicles_dict['registration_no']:
			vehicles_unique = False
			raise HTTPException(
				status_code=400, 
				detail="Registration Plate "+str(vehicles_dict['registration_no'])+" exists."
			)
	
	vehicles_found = False
	for vehicle_vehicles in data['vehicle']:
		if vehicle_vehicles['vehicle_id'] == vehicles_dict['vehicle_id']:
			vehicles_found = True
			return "Vehicle ID "+str(vehicles_dict['vehicle_id'])+" exists."
	
	if not vehicles_found:
		data['vehicle'].append(vehicles_dict)
		with open(json_filename,"w") as write_file:
			json.dump(data, write_file)

		return vehicles_dict
	raise HTTPException(
		status_code=404, detail=f'vehicle not found'
	)

@app.put('/{vehicles_id}')
async def update_vehicle(vehicles_id: int, vehicles: VehiclesUpdate, current_user: User = Depends(get_current_active_user)):
	"""
	Update a vehicle's information based on the vehicle's unique ID.

	In the request body, specify the vehicle's unique vehicle ID and put updates of the  parameters you want to update:
	- `vehicle_id`: (Required) The ID of the vehicle.
	- `make`: (Optional) The make of the vehicle.
	- `model`: (Optional) The vehicle's model name.
	- `year`: (Optional) The vehicle's manufactured year.
	- `registration_no`: (Optional) The unique vehicle's registration plate.

	For the parameters that are not to be updated, please delete them before executing the function. 

	If the vehicle with the specified ID exists, returns "updated" to indicate a successful update.
	Else, returns "Vehicle ID not found." to indicate the specified vehicle to be updated does not exist.
	"""
	vehicles_dict = vehicles.dict(exclude_unset=True)

	# Validate registration_no
	if 'registration_no' in vehicles_dict:
		if not re.match(r'^[A-Z]{1,2}\d{1,4}[A-Z]{1,3}$', vehicles_dict["registration_no"]):
			raise HTTPException(
				status_code=400, 
				detail="Incorrect registration plate format."
			)
		
	# Validate year
	if 'year' in vehicles_dict:
		if vehicles_dict["year"] > 2040 or vehicles_dict["year"] < 1900:
			raise HTTPException(
				status_code=400, 
				detail="Invalid manufacture year."
			)
		
	# Validate unique registration_no
	if 'registration_no' in vehicles_dict:
		vehicles_unique = True
		for vehicle_vehicles in data['vehicle']:
			if vehicle_vehicles['registration_no'] == vehicles_dict['registration_no']:
				vehicles_unique = False
				raise HTTPException(
				status_code=400, 
				detail="Registration Plate "+str(vehicles_dict['registration_no'])+" exists."
			)

	vehicles_found = False
	for vehicle_idx, vehicle_vehicles in enumerate(data['vehicle']):
		if vehicle_vehicles['vehicle_id'] == vehicles_id:
			vehicles_found = True
			for field, value in vehicles_dict.items():
				data['vehicle'][vehicle_idx][field] = value
			with open(json_filename,"w") as write_file:
				json.dump(data, write_file)
			return "updated"
		
	if not vehicles_found:
		return "Vehicle ID not found."
	raise HTTPException(
		status_code=404, detail=f'Vehicle not found'
	)

@app.delete('/{vehicles_id}')
async def delete_vehicle(vehicles_id: int, current_user: User = Depends(get_current_active_user)):

	"""
	Delete a vehicle's information by specifying their unique identifier. 
	
	Insert the parameter as follows:
	- `vehicles_id`: (Required) The ID of the vehicle.
		
	Returns "deleted" to indicate a successful deletion of a vehicle's data
	with the specified ID. 
	"""

	vehicles_found = False
	for vehicle_idx, vehicle_vehicles in enumerate(data['vehicle']):
		if vehicle_vehicles['vehicle_id'] == vehicles_id:
			vehicles_found = True
			data['vehicle'].pop(vehicle_idx)
			
			with open(json_filename,"w") as write_file:
				json.dump(data, write_file)
			return "deleted"
	
	if not vehicles_found:
		return "Vehicle ID not found."
	raise HTTPException(
		status_code=404, detail=f'vehicle not found'
	)
