from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.core.exceptions import (
    ResourceConflictError,
    ResourceNotFoundError,
)
from app.schemas import (
    StoreCreate,
    StoreResponse,
    StoreUpdate,
)
from app.services import StoreService

router = APIRouter(
    prefix="/stores",
    tags=["Stores"],
)

service = StoreService()


@router.post(
    "",
    response_model=StoreResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_store(
    store_data: StoreCreate,
    db: Session = Depends(get_db),
):
    try:
        return service.create_store(
            db,
            store_data,
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
    response_model=list[StoreResponse],
)
def list_stores(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return service.list_stores(
        db,
        offset=offset,
        limit=limit,
    )


@router.get(
    "/{store_id}",
    response_model=StoreResponse,
)
def get_store(
    store_id: int,
    db: Session = Depends(get_db),
):
    try:
        return service.get_store(
            db,
            store_id,
        )
    except ResourceNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.patch(
    "/{store_id}",
    response_model=StoreResponse,
)
def update_store(
    store_id: int,
    store_data: StoreUpdate,
    db: Session = Depends(get_db),
):
    try:
        return service.update_store(
            db,
            store_id,
            store_data,
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
    "/{store_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_store(
    store_id: int,
    db: Session = Depends(get_db),
):
    try:
        service.delete_store(
            db,
            store_id,
        )
    except ResourceNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc