from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.core.exceptions import (
    ResourceConflictError,
    ResourceNotFoundError,
)
from app.schemas import (
    InventoryCreate,
    InventoryResponse,
    InventoryUpdate,
    StockInCreate,
    StockOutCreate,
)
from app.services import InventoryService


router = APIRouter(
    prefix="/inventories",
    tags=["Inventories"],
)

service = InventoryService()


@router.post(
    "",
    response_model=InventoryResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_inventory(
    inventory_data: InventoryCreate,
    db: Session = Depends(get_db),
):
    try:
        return service.create_inventory(
            db,
            inventory_data,
        )
    except ResourceNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except ResourceConflictError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@router.get(
    "",
    response_model=list[InventoryResponse],
)
def list_inventories(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return service.list_inventories(
        db,
        offset=offset,
        limit=limit,
    )


@router.get(
    "/store/{store_id}",
    response_model=list[InventoryResponse],
)
def list_inventories_by_store(
    store_id: int,
    db: Session = Depends(get_db),
):
    try:
        return service.list_by_store(
            db,
            store_id,
        )
    except ResourceNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.get(
    "/product/{product_id}",
    response_model=list[InventoryResponse],
)
def list_inventories_by_product(
    product_id: int,
    db: Session = Depends(get_db),
):
    try:
        return service.list_by_product(
            db,
            product_id,
        )
    except ResourceNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.get(
    "/{inventory_id}",
    response_model=InventoryResponse,
)
def get_inventory(
    inventory_id: int,
    db: Session = Depends(get_db),
):
    try:
        return service.get_inventory(
            db,
            inventory_id,
        )
    except ResourceNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.patch(
    "/{inventory_id}",
    response_model=InventoryResponse,
)
def update_inventory(
    inventory_id: int,
    inventory_data: InventoryUpdate,
    db: Session = Depends(get_db),
):
    try:
        return service.update_inventory(
            db,
            inventory_id,
            inventory_data,
        )
    except ResourceNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.delete(
    "/{inventory_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_inventory(
    inventory_id: int,
    db: Session = Depends(get_db),
):
    try:
        service.delete_inventory(
            db,
            inventory_id,
        )
    except ResourceNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

@router.post(
    "/{inventory_id}/stock-in",
    response_model=InventoryResponse,
    status_code=status.HTTP_200_OK,
)
def stock_in(
    inventory_id: int,
    stock_data: StockInCreate,
    db: Session = Depends(get_db),
):
    try:
        return service.stock_in(
            db,
            inventory_id,
            stock_data,
        )

    except ResourceNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )


@router.post(
    "/{inventory_id}/stock-out",
    response_model=InventoryResponse,
    status_code=status.HTTP_200_OK,
)
def stock_out(
    inventory_id: int,
    stock_data: StockOutCreate,
    db: Session = Depends(get_db),
):
    
    try:
        return service.stock_out(
            db,
            inventory_id,
            stock_data,
        )

    except ResourceNotFoundError as exc:
        raise HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail=str(exc),
) from exc

    except ResourceConflictError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )