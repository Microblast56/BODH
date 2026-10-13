from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.core.exceptions import ResourceNotFoundError
from app.schemas import StockMovementResponse
from app.services import StockMovementService


router = APIRouter(
    prefix="/stock-movements",
    tags=["Stock Movements"],
)

service = StockMovementService()


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