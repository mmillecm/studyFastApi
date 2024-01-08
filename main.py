
import uvicorn
from fastapi import FastAPI,HTTPException

from schemas import load_db, save_db, CarInput, CarOutput

app = FastAPI(title="Car Sharing")
db = load_db()

@app.get("/api/cars")
def get_cars(size: str | None = None, doors: int | None = None) -> list:
    result = db
    if size:
        result = [car for car in result if car.size == size]
    if doors:
        result = [car for car in result if car.doors >= doors]
    return result


@app.get("/api/cars/{id}")
def get_car_by_size(id: int) -> dict:
    result = [car for car in db if car.id == id]
    if result:
        return result[0]
    else:
        raise HTTPException(status_code=404, detail="Not found")


@app.post("/api/cars/")
def create_car(car: CarInput) -> CarOutput:
    new_car = CarOutput(size=car.size, doors=car.doors,
                        fuel=car.fuel, transmission=car.transmission,
                        id=len(db)+1)
    db.append(new_car)
    save_db(db)
    return new_car


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
