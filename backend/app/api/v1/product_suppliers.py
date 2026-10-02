from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.core.exceptions import (
    ResourceConflictError,
    ResourceNotFoundError,
)
from app.schemas import (
    ProductSupplierCreate,
    ProductSupplierResponse,
    ProductSupplierUpdate,
)
from app.services import ProductSupplierService


router = APIRouter(
    prefix="/product-suppliers",
    tags=["Product Suppliers"],
)

service = ProductSupplierService()


@router.post(
    "",
    response_model=ProductSupplierResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_product_supplier(
    product_supplier_data: ProductSupplierCreate,
    db: Session = Depends(get_db),
):
    try:
        return service.create_product_supplier(
            db,
            product_supplier_data,
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
    response_model=list[ProductSupplierResponse],
)
def list_product_suppliers(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return service.list_product_suppliers(
        db,
        offset=offset,
        limit=limit,
    )


@router.get(
    "/product/{product_id}",
    response_model=list[ProductSupplierResponse],
)
def list_product_suppliers_by_product(
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
    "/supplier/{supplier_id}",
    response_model=list[ProductSupplierResponse],
)
def list_product_suppliers_by_supplier(
    supplier_id: int,
    db: Session = Depends(get_db),
):
    try:
        return service.list_by_supplier(
            db,
            supplier_id,
        )
    except ResourceNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.get(
    "/{product_supplier_id}",
    response_model=ProductSupplierResponse,
)
def get_product_supplier(
    product_supplier_id: int,
    db: Session = Depends(get_db),
):
    try:
        return service.get_product_supplier(
            db,
            product_supplier_id,
        )
    except ResourceNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.patch(
    "/{product_supplier_id}",
    response_model=ProductSupplierResponse,
)
def update_product_supplier(
    product_supplier_id: int,
    product_supplier_data: ProductSupplierUpdate,
    db: Session = Depends(get_db),
):
    try:
        return service.update_product_supplier(
            db,
            product_supplier_id,
            product_supplier_data,
        )
    except ResourceNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.delete(
    "/{product_supplier_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_product_supplier(
    product_supplier_id: int,
    db: Session = Depends(get_db),
):
    try:
        service.delete_product_supplier(
            db,
            product_supplier_id,
        )
    except ResourceNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
