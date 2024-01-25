from typing import Sequence, Type

import uvicorn
from fastapi import FastAPI, HTTPException, Depends
from sqlmodel import create_engine, SQLModel, Session, select

from schemas import CarInput, CarOutput, TripOutput, TripInput, Car, Trip

app = FastAPI(title="Car Sharing")


engine = create_engine(
    "sqlite:///carsharing.db",
    connect_args={"check_same_thread": False},
    echo=True
)


@app.on_event("startup")
def on_startup() -> None:
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


@app.get("/api/cars")
def get_cars(size: str | None = None, doors: int | None = None,
             session: Session = Depends(get_session)) -> Sequence[Car]:
    query = select(Car)
    if size:
        query = query.where(Car.size == size)
    if doors:
        query = query.where(Car.doors == doors)
    return session.exec(query).all()


@app.get("/api/cars/{id}", response_model=Car)
def get_car_by_size(id: int, session: Session = Depends(get_session)) -> Type[Car]:
    car = session.get(Car, id)
    if car:
        return car
    else:
        raise HTTPException(status_code=404, detail="Car not found")


@app.post("/api/cars/", response_model=Car)
def create_car(car_input: CarInput, session: Session = Depends(get_session)) -> Car:
    new_car = Car.from_orm(car_input)
    session.add(new_car)
    session.commit()
    session.refresh(new_car)
    return new_car


@app.delete("api/cars/{id}", status_code=204)
def delete_car(id: int, session: Session = Depends(get_session)) -> None:
    car = session.get(Car, id)
    if car:
        session.delete(car)
        session.commit()
    else:
        raise HTTPException(status_code=404, detail="Car not found")


@app.put("/api/cars/{id}", response_model=CarOutput)
def update_car(id: int, new_car: CarInput, session: Session = Depends(get_session)) -> Type[Car]:
    car = session.get(Car, id)
    if car:
        car.doors = new_car.doors
        car.fuel = new_car.fuel
        car.transmission = new_car.transmission
        car.size = new_car.size
        session.commit()
        return car
    else:
        raise HTTPException(status_code=404, detail="Cat not found")

@app.post("/api/cars/{car_id}/trips", response_model=Trip)
def create_trip(car_id: int, trip: TripInput, session: Session = Depends(get_session)) -> Trip:
    car = session.get(Car, car_id)
    if car:
        new_trip = Trip.from_dict(trip, update={'car_id': car_id})
        car.trips.append(new_trip)
        session.commit()
        session.refresh(new_trip)
        return new_trip
    else:
        raise HTTPException(status_code=404, detail="No cars found")


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
