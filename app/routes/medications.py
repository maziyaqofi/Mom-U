from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.ir_service import (
    resolve_medication_query,
    create_verification_session,
    confirm_verification_session,
)

router = APIRouter(
    prefix="/api/medications",
    tags=["Medication Retrieval"],
)


class MedicationQuery(BaseModel):
    query: str = Field(min_length=1)


class MedicationConfirmation(BaseModel):
    verification_token: str = Field(min_length=1)
    selected_document_ids: list[str] = Field(min_length=1)


@router.post("/resolve")
def resolve_medication(request: MedicationQuery):
    try:
        return resolve_medication_query(request.query)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))


@router.post("/verify")
def verify_medication(request: MedicationQuery):
    try:
        return create_verification_session(request.query)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))


@router.post("/confirm")
def confirm_medication(request: MedicationConfirmation):
    try:
        return confirm_verification_session(
            request.verification_token,
            request.selected_document_ids,
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
