#Python
from email.policy import default
from operator import gt
from turtle import title
from typing import Optional
from enum import Enum


#Pydantic
from pydantic import BaseModel, Field


#FastAPI
from fastapi import Body, FastAPI, Path, Query

app = FastAPI()

#Models
class HairColor(Enum):
    white = "white"
    brown = "brown"
    black = "black"
    blonde = "blonde"
    red = "red"

class Location(BaseModel):
    city: str
    state: str
    country: str

class PersonBase(BaseModel):

    first_name: str = Field(
        ...,
        min_length=1,
        max_length=50
    )
    last_name: str = Field(
        ...,
        min_length=1,
        max_length=50
    )
    age: int = Field(
        ...,
        gt=0,
        lt=115
    )
    hair_color: Optional[HairColor] = Field(default=None)
    is_married: Optional[bool] = Field(default=None)


    class Config:
        schema_extra = {
            "example" : {
                "first_name": "Juan Sebastian",
                "last_name": "Pastrana",
                "age": 21,
                "hair_color": "black",
                "is_married": False,
                "password": "contrasenia_segura"

            }
        }

class Person(PersonBase):
    password: str = Field(
        ...,
        min_length=8
    )


class PersonOut(PersonBase): 
    pass

@app.get("/")
async def root():
    return {"message":"Hola mundo"}


#Request and Response Body

@app.post('/person/new', response_model=PersonOut)
def create_person(person: Person = Body(...)):
    return person

#Validar Query Parameters
@app.get("/person/detail")
async def show_person(
    name: Optional[str] = Query(
        None,
        min_length=1,
        max_length=50,
        title="Person name",
        description="This is person name, it's between 1 and 50 characters",
        example="Alejandra"
        ),
    age: Optional[str] = Query(
        ...,
        title="Person age",
        description="This is the person age. It's required",
        example=25
        )
):
    return {name: age}


#Validar Path parameters

@app.get("/person/detail{person_id}")
async def show_person(
    person_id: int = Path(
        ...,
        gt=0,
        example=123
        )
):
    return {person_id: "It exists!"}


#Validar Request body:
@app.put("/person/{person_id}")
async def update_person(
    person_id: int = Path(
        ...,
        title="Person ID",
        description="this is person ID",
        gt=0,
        example=123
    ),
    person: Person = Body(...),
    location: Location = Body(...)
):
    results = person.dict()
    results.update(location.dict())
    return results