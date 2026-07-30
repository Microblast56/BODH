from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.core.exceptions import (
    ResourceConflictError,
    ResourceNotFoundError,
)
from app.schemas import (
    RetailerCreate,
    RetailerResponse,
    RetailerUpdate,
)
from app.services import RetailerService


router = APIRouter(
    prefix="/retailers",
    tags=["Retailers"],
)

service = RetailerService()


@router.post(
    "",
    response_model=RetailerResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_retailer(
    retailer_data: RetailerCreate,
    db: Session = Depends(get_db),
):
    try:
        return service.create_retailer(
            db,
            retailer_data,
        )
    except ResourceConflictError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@router.get(
    "",
    response_model=list[RetailerResponse],
)
def list_retailers(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return service.list_retailers(
        db,
        offset=offset,
        limit=limit,
    )


@router.get(
    "/{retailer_id}",
    response_model=RetailerResponse,
)
def get_retailer(
    retailer_id: int,
    db: Session = Depends(get_db),
):
    try:
        return service.get_retailer(
            db,
            retailer_id,
        )
    except ResourceNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.patch(
    "/{retailer_id}",
    response_model=RetailerResponse,
)
def update_retailer(
    retailer_id: int,
    retailer_data: RetailerUpdate,
    db: Session = Depends(get_db),
):
    try:
        return service.update_retailer(
            db,
            retailer_id,
            retailer_data,
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
    "/{retailer_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_retailer(
    retailer_id: int,
    db: Session = Depends(get_db),
):
    try:
        service.delete_retailer(
            db,
            retailer_id,
        )
    except ResourceNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc