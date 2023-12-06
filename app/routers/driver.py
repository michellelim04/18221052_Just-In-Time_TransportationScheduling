from fastapi import APIRouter, HTTPException, Depends
import json
from pydantic import BaseModel
from typing import Optional
from ..main import *
from ..auth import get_current_active_user, User
import re
from email_validator import validate_email, EmailNotValidError
from datetime import datetime

# model for adding driver
class Drivers(BaseModel): 
	driver_id : int
	name : str
	license_no : str
	date_of_birth : str
	contact_no : str
	email : str
	address : str

# model for updating driver
class DriverUpdate(BaseModel):
    name: Optional[str] = None
    license_no: Optional[str] = None
    date_of_birth: Optional[str] = None
    contact_no: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None


json_filename="./app/json/driver.json"

with open(json_filename,"r") as read_file:
	data = json.load(read_file)

app = APIRouter(
	prefix="/driver",
	tags=["driver"],
  responses={404: {"description": "Not found"}},
)

@app.get('/')
async def read_all_driver(current_user: User = Depends(get_current_active_user)):
	return data['driver']

@app.get('/search')
async def search_drivers(name: str = None, license_no: str = None, date_of_birth: str = None, contact_no: str = None, current_user: User = Depends(get_current_active_user)):
	"""
	Search for drivers based on one or more parameters.
	 
	Insert the parameter(s) as follows:
	- `name`: (Optional) The name of the driver.
	- `license_no`: (Optional) The driver's license number.
	- `date_of_birth`: (Optional) The driver's date of birth.
	- `contact_no`: (Optional) The driver's contact number.

	Returns a list of matching drivers.
	"""

	matching_drivers = []

	for driver in data.get('driver', []):
			if (
					(name is None or driver['name'] == name) and
					(license_no is None or driver['license_no'] == license_no) and
					(date_of_birth is None or driver['date_of_birth'] == date_of_birth) and
					(contact_no is None or driver['contact_no'] == contact_no)
			):
					matching_drivers.append(driver)

	if matching_drivers:
			return matching_drivers
	else:
			raise HTTPException(
					status_code=404,
					detail='No matching drivers found.',
			)

@app.get('/{drivers_id}')
async def read_driver(drivers_id: int, current_user: User = Depends(get_current_active_user)):
	"""
	Retrieve information about a driver based on their unique identifier. 
	
	Insert the parameter as follows:
	- `drivers_id`: (Required) The ID of the driver.
		
	Returns detailed information of a driver. 
    """
	for driver_drivers in data['driver']:
		print(driver_drivers)
		if driver_drivers['driver_id'] == drivers_id:
			return driver_drivers
	raise HTTPException(
		status_code=404, detail=f'Driver not found'
	)

@app.post('/')
async def add_driver(drivers: Drivers, current_user: User = Depends(get_current_active_user)):
	"""
	Add a driver's information in the dataset based on the driver's unique identifier.

	Checks whether a driver with the specified ID exists in the database.
	If the driver does not exist, the function will add the driver to the dataset. 
	
	Insert the parameter(s) in the request body as follows:
	- `driver_id`: (Required) The ID of the driver.
	- `name`: (Required) The name of the driver.
	- `license_no`: (Required) The driver's license number.
	- `date_of_birth`: (Required) The driver's date of birth.
	- `contact_no`: (Required) The driver's contact number.
	- `email`: (Required) The email of the driver.
	- `address`: (Required) The driver's address.
		
	Returns the driver's information if added.
	If the driver already exists, it returns a message indicating the driver exists.
	"""
	drivers_dict = drivers.dict()

	# Validate date_of_birth
	try:
		datetime.strptime(drivers_dict["date_of_birth"], '%Y-%m-%d')
	except ValueError:
		raise HTTPException(
		status_code=400, 
		detail="Incorrect date format. It should be 'YYYY-MM-DD'."
	)

	# Validate contact_no
	if not re.match(r'\d{2}-\d{4}-\d{3}-\d{3}', drivers_dict["contact_no"]):
		raise HTTPException(
			status_code=400, 
			detail="Incorrect contact number format. It should be 'CC-XXXX-XXX-XXX'."
		)

	# Validate email
	try:
		v = validate_email(drivers_dict["email"])
	except EmailNotValidError as e:
		raise HTTPException(
			status_code=400, 
			detail=f"Invalid email address: {str(e)}"
		)
	
	# Validate license number
	if not re.match(r'\d{14}', drivers_dict["license_no"]):
		raise HTTPException(
			status_code=400, 
			detail="Incorrect license number format. It should consists exactly 14 digits."
		)
	
	# Validate unique license no
	drivers_unique = True
	for driver_drivers in data['driver']:
		if driver_drivers['license_no'] == drivers_dict['license_no']:
			drivers_unique = False
			raise HTTPException(
				status_code=400, 
				detail="License Number "+str(drivers_dict['license_no'])+" exists."
			)

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
		status_code=404, detail=f'Driver not found'
	)

@app.put('/{drivers_id}')
async def update_driver(drivers_id: int, drivers: DriverUpdate, current_user: User = Depends(get_current_active_user)):
	"""
	Update a driver's information based on the driver's unique ID.

	In the request body, specify the driver's unique driver ID and put updates of the parameters you want to update:
	- `driver_id`: (Required) The ID of the driver.
	- `name`: (Optional) The name of the driver.
	- `license_no`: (Optional) The driver's license number.
	- `date_of_birth`: (Optional) The driver's date of birth.
	- `contact_no`: (Optional) The driver's contact number.
	- `email`: (Optional) The email address of the driver.
	- `address`: (Optional) The driver's address.

	For the parameters that are not to be updated, please delete them before executing the function.

	If the driver with the specified ID exists, returns "updated" to indicate a successful update.
	Else, returns "Driver ID not found." to indicate the specified driver to be updated does not exist.
	"""
	drivers_dict = drivers.dict(exclude_unset=True)

	print (drivers_dict)

	# Validate date_of_birth
	if 'date_of_birth' in drivers_dict:
		try:
			datetime.strptime(drivers_dict["date_of_birth"], '%Y-%m-%d')
		except ValueError:
			raise HTTPException(
				status_code=400, 
				detail="Incorrect date format. It should be 'YYYY-MM-DD'."
			)

	# Validate contact_no
	if 'contact_no' in drivers_dict:
		if not re.match(r'\d{2}-\d{4}-\d{3}-\d{3}', drivers_dict["contact_no"]):
			raise HTTPException(
				status_code=400, 
				detail="Incorrect contact number format. It should be 'CC-XXXX-XXX-XXX'."
			)

	# Validate email
	if 'email' in drivers_dict:
		try:
			v = validate_email(drivers_dict["email"])
		except EmailNotValidError as e:
			raise HTTPException(
				status_code=400, 
				detail=f"Invalid email address: {str(e)}"
			)
		
	# Validate license number
	if 'license_no' in drivers_dict:
		if not re.match(r'\d{14}', drivers_dict["license_no"]):
			raise HTTPException(
				status_code=400, 
				detail="Incorrect license number format. It should consists exactly 14 digits."
			)
		
	# Validate unique license_no
	if 'license_no' in drivers_dict:
		drivers_unique = True
		for driver_drivers in data['driver']:
			if driver_drivers['license_no'] == drivers_dict['license_no']:
				drivers_unique = False
				raise HTTPException(
					status_code=400, 
					detail="License Number "+str(drivers_dict['license_no'])+" exists."
				)

	drivers_found = False
	for driver_idx, driver_drivers in enumerate(data['driver']):
		if driver_drivers['driver_id'] == drivers_id:
			drivers_found = True
			# Update only the fields that are provided in the request
			for field, value in drivers_dict.items():
				data['driver'][driver_idx][field] = value
			with open(json_filename,"w") as write_file:
				json.dump(data, write_file)
			return "updated"
    
	if not drivers_found:
		return "Driver ID not found."
	raise HTTPException(
		status_code=404, detail=f'Driver not found'
    )

@app.delete('/{drivers_id}')
async def delete_driver(drivers_id: int, current_user: User = Depends(get_current_active_user)):
	"""
	Delete a driver's information by specifying their unique identifier. 
	
	Insert the parameter as follows:
	- `drivers_id`: (Required) The ID of the driver.
		
	Returns "deleted" to indicate a successful deletion of a driver's data
	with the specified ID. 
	"""

	drivers_found = False
	for driver_idx, driver_drivers in enumerate(data['driver']):
		if driver_drivers['driver_id'] == drivers_id:
			drivers_found = True
			data['driver'].pop(driver_idx)
			
			with open(json_filename,"w") as write_file:
				json.dump(data, write_file)
			return "deleted"
	
	if not drivers_found:
		return "Driver ID not found."
	raise HTTPException(
		status_code=404, detail=f'Driver not found'
	)
