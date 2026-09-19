from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.core.exceptions import (
    ResourceConflictError,
    ResourceNotFoundError,
)
from app.schemas import (
    OutletCreate,
    OutletResponse,
    OutletUpdate,
)
from app.services import OutletService


router = APIRouter(
    prefix="/outlets",
    tags=["Outlets"],
)

service = OutletService()


@router.post(
    "",
    response_model=OutletResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_outlet(
    outlet_data: OutletCreate,
    db: Session = Depends(get_db),
):
    try:
        return service.create_outlet(
            db,
            outlet_data,
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
    response_model=list[OutletResponse],
)
def list_outlets(
    restaurant_id: int | None = Query(
        default=None,
        ge=1,
    ),
    offset: int = Query(
        default=0,
        ge=0,
    ),
    limit: int = Query(
        default=100,
        ge=1,
        le=100,
    ),
    db: Session = Depends(get_db),
):
    return service.list_outlets(
        db,
        restaurant_id=restaurant_id,
        offset=offset,
        limit=limit,
    )


@router.get(
    "/{outlet_id}",
    response_model=OutletResponse,
)
def get_outlet(
    outlet_id: int,
    db: Session = Depends(get_db),
):
    try:
        return service.get_outlet(
            db,
            outlet_id,
        )
    except ResourceNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.patch(
    "/{outlet_id}",
    response_model=OutletResponse,
)
def update_outlet(
    outlet_id: int,
    outlet_data: OutletUpdate,
    db: Session = Depends(get_db),
):
    try:
        return service.update_outlet(
            db,
            outlet_id,
            outlet_data,
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


@router.delete(
    "/{outlet_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_outlet(
    outlet_id: int,
    db: Session = Depends(get_db),
):
    try:
        service.delete_outlet(
            db,
            outlet_id,
        )
    except ResourceNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc