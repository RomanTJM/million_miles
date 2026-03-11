from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from app.core.database import get_db
from app.core.security import get_current_user
from app.models import Car
from app.schemas import CarResponse, CarsListResponse, CarCreate, CarUpdate

router = APIRouter(prefix="/api/cars", tags=["cars"])


@router.get("", response_model=CarsListResponse)
async def get_cars(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    brand: str = Query(None),
    model: str = Query(None),
    year_from: int = Query(None),
    year_to: int = Query(None),
    price_from: float = Query(None),
    price_to: float = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):

    filters = [Car.is_active == True]
    
    if brand:
        filters.append(Car.brand.ilike(f"%{brand}%"))
    if model:
        filters.append(Car.model.ilike(f"%{model}%"))
    if year_from:
        filters.append(Car.year >= year_from)
    if year_to:
        filters.append(Car.year <= year_to)
    if price_from:
        filters.append(Car.price >= price_from)
    if price_to:
        filters.append(Car.price <= price_to)
    
    count_result = await db.execute(
        select(func.count()).select_from(Car).where(and_(*filters))
    )
    total = count_result.scalar()
    
    offset = (page - 1) * page_size
    result = await db.execute(
        select(Car)
        .where(and_(*filters))
        .order_by(Car.updated_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    cars = result.scalars().all()
    
    return CarsListResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=[CarResponse.model_validate(car) for car in cars],
    )


@router.get("/{car_id}", response_model=CarResponse)
async def get_car(
    car_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    result = await db.execute(select(Car).where(Car.id == car_id))
    car = result.scalar_one_or_none()
    
    if not car:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Car not found",
        )
    
    return CarResponse.model_validate(car)


@router.post("", response_model=CarResponse)
async def create_car(
    car_data: CarCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    if car_data.external_id:
        result = await db.execute(
            select(Car).where(Car.external_id == car_data.external_id)
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Car with this external_id already exists",
            )
    
    result = await db.execute(select(Car).where(Car.url == car_data.url))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Car with this URL already exists",
        )
    
    new_car = Car(**car_data.model_dump())
    db.add(new_car)
    await db.commit()
    await db.refresh(new_car)
    
    return CarResponse.model_validate(new_car)


@router.put("/{car_id}", response_model=CarResponse)
async def update_car(
    car_id: int,
    car_data: CarUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    result = await db.execute(select(Car).where(Car.id == car_id))
    car = result.scalar_one_or_none()
    
    if not car:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Car not found",
        )
    
    update_data = car_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(car, field, value)
    
    await db.commit()
    await db.refresh(car)
    
    return CarResponse.model_validate(car)


@router.delete("/{car_id}")
async def delete_car(
    car_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    result = await db.execute(select(Car).where(Car.id == car_id))
    car = result.scalar_one_or_none()
    
    if not car:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Car not found",
        )
    
    car.is_active = False
    await db.commit()
    
    return {"message": "Car deleted successfully"}
