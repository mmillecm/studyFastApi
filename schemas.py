import json

from pydantic import BaseModel


class CarInput(BaseModel):
    size: str
    fuel: str | None = "electric"
    doors: int
    transmission: str | None = "auto"


class CarOutput(CarInput):
    id: int


def load_db() -> list[CarOutput]:
    with open("cars.json") as file:
        return [CarOutput.parse_obj(obj) for obj in json.load(file)]


def save_db(cars: list[CarInput]):
    with open("cars.json", "w") as file:
        json.dump([car.dict() for car in cars], file, indent=4)
