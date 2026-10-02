from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.core.exceptions import (
    ResourceNotFoundError,
)
from app.schemas import (
    StockMovementCreate,
    StockMovementResponse,
    StockMovementUpdate,
)
from app.services import StockMovementService


router = APIRouter(
    prefix="/stock-movements",
    tags=["Stock Movements"],
)

service = StockMovementService()


@router.post(
    "",
    response_model=StockMovementResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_stock_movement(
    stock_movement_data: StockMovementCreate,
    db: Session = Depends(get_db),
):
    try:
        return service.create_stock_movement(
            db,
            stock_movement_data,
        )
    except ResourceNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.get(
    "",
    response_model=list[StockMovementResponse],
)
def list_stock_movements(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return service.list_stock_movements(
        db,
        offset=offset,
        limit=limit,
    )


@router.get(
    "/inventory/{inventory_id}",
    response_model=list[StockMovementResponse],
)
def list_stock_movements_by_inventory(
    inventory_id: int,
    db: Session = Depends(get_db),
):
    try:
        return service.list_by_inventory(
            db,
            inventory_id,
        )
    except ResourceNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.get(
    "/employee/{employee_id}",
    response_model=list[StockMovementResponse],
)
def list_stock_movements_by_employee(
    employee_id: int,
    db: Session = Depends(get_db),
):
    try:
        return service.list_by_employee(
            db,
            employee_id,
        )
    except ResourceNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.get(
    "/{stock_movement_id}",
    response_model=StockMovementResponse,
)
def get_stock_movement(
    stock_movement_id: int,
    db: Session = Depends(get_db),
):
    try:
        return service.get_stock_movement(
            db,
            stock_movement_id,
        )
    except ResourceNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.patch(
    "/{stock_movement_id}",
    response_model=StockMovementResponse,
)
def update_stock_movement(
    stock_movement_id: int,
    stock_movement_data: StockMovementUpdate,
    db: Session = Depends(get_db),
):
    try:
        return service.update_stock_movement(
            db,
            stock_movement_id,
            stock_movement_data,
        )
    except ResourceNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.delete(
    "/{stock_movement_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_stock_movement(
    stock_movement_id: int,
    db: Session = Depends(get_db),
):
    try:
        service.delete_stock_movement(
            db,
            stock_movement_id,
        )
    except ResourceNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc