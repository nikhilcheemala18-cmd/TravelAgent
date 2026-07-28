"""Schemas for validation results produced after tool execution."""

from pydantic import BaseModel

from app.schemas.common import ValidationSeverity


class ValidationIssue(BaseModel):
    field: str | None = None
    message: str
    severity: ValidationSeverity = ValidationSeverity.ERROR


class ValidationResult(BaseModel):
    is_valid: bool
    issues: list[ValidationIssue] = []
