#Python
from email import message
from email.policy import default
from operator import gt
from turtle import title
from typing import Optional
from enum import Enum


#Pydantic
from pydantic import BaseModel, EmailStr, Field


#FastAPI
from fastapi import Body, Cookie, FastAPI, File, Form, Header, Path, Query, UploadFile, status
from fastapi import HTTPException

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

class LoginOut(BaseModel):
    username: str = Field(..., max_length=20, example="Juan")
    message: str = Field(default="login sucess!")

@app.get(
    "/",
    status_code=status.HTTP_200_OK
    )
async def root():
    return {"message":"Hola mundo"}


#Request and Response Body

@app.post(
    '/person/new',
    response_model=PersonOut,
    status_code=status.HTTP_201_CREATED,
    tags=["Persons"]
    )
def create_person(person: Person = Body(...)):
    """
    Create Person
    
    This path Operation creates a person in the app and save the information in the database.

    Parameters:
    - Request body parameter:
        - **person: Person** -> A person model with first name, last name, age, hair color and marital status
    
    Returns a person model with first name, last name, age, hair color and marital status
    """
    return person

#Validar Query Parameters
@app.get(
    "/person/detail",
    status_code=status.HTTP_200_OK,
    tags=["Persons"]
    )
async def show_person(
    name: Optional[str] = Query(
        None,
        min_length=1,
        max_length=50,
        title="Person name",
        description="This is person name, it's between 1 and 50 characters",
        example="Alejandra",
        deprecated=True
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
persons = [1, 2, 3, 4, 5]

@app.get("/person/detail{person_id}",tags=["Persons"])
async def show_person(
    person_id: int = Path(
        ...,
        gt=0,
        example=123
        )
):
    if person_id not in persons:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="This person doesn't exist!"
        )
    return {person_id: "It exists!"}


#Validar Request body:
@app.put("/person/{person_id}",tags=["Persons"])
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

@app.post(
    path="/login",
    response_model=LoginOut,
    status_code=status.HTTP_200_OK
)
async def login(username: str = Form(...), password: str = Form(...)):
    return LoginOut(username=username)

#Cookies and headers parameters

@app.post(
    path="/contact",
    status_code=status.HTTP_200_OK
)
async def contact(
    first_name: str = Form(
        ...,
        max_length=20,
        min_length=1
    ),
    email: EmailStr = Form(...),
    message: str = Form(
        ...,
        min_length=20
    ),
    user_agent: Optional[str] = Header(default=None),
    ads: Optional[str] = Cookie(default=None)
):
    return user_agent


@app.post(
    path='/post-image',
    status_code=status.HTTP_200_OK,
    tags=['Upload'], 
    summary='Upload image',
)
async def post_image(
    image: UploadFile = File(...)
): 
    """
    #Upload Image

    Args:
        image -> Image to upload

    Returns:
        Type of the image and it´s weight
    """
    return {
    #getting the name of the file
    'filename': image.filename,
    #show the type of image
    'format': image.content_type,
    #convert bytes to kb
    'size(kb)': round(len(image.file.read()) / 1024, 2)
}