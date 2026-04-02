"""Layer Registry schema models.

Defines the structure for the layer registry using Pydantic v2.
"""

import json
from enum import Enum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, field_validator, model_validator


class ParamType(str, Enum):
    """Parameter type enumeration."""

    INT = "int"
    FLOAT = "float"
    BOOL = "bool"
    ENUM = "enum"
    INT_TUPLE = "int_tuple"
    FLOAT_TUPLE = "float_tuple"
    STRING = "string"


class LayerParamConstraints(BaseModel):
    """Constraints for numeric parameters."""

    min: float | None = None
    max: float | None = None
    step: float | None = None

    model_config = {"extra": "forbid"}


class LayerParam(BaseModel):
    """Definition of a single layer parameter."""

    key: str = Field(..., description="Unique identifier for the parameter")
    label: str | None = Field(None, description="Human-readable label for UI")
    type: ParamType = Field(..., description="Type of the parameter")
    required: bool = Field(False, description="Whether this parameter is required")
    default: Any | None = Field(None, description="Default value for the parameter")
    constraints: LayerParamConstraints | None = Field(None, description="Constraints for numeric types")
    options: list[str] | None = Field(None, description="Options for enum parameters")
    help_text: str | None = Field(None, description="Help text for UI tooltip")

    model_config = {"extra": "forbid"}

    @model_validator(mode="after")
    def validate_constraints(self) -> "LayerParam":
        """Validate parameter constraints."""
        if self.type in (ParamType.INT, ParamType.FLOAT):
            if self.constraints is not None:
                if self.default is not None:
                    if self.constraints.min is not None and self.default < self.constraints.min:
                        raise ValueError(
                            f"Default value {self.default} is less than minimum {self.constraints.min}"
                        )
                    if self.constraints.max is not None and self.default > self.constraints.max:
                        raise ValueError(
                            f"Default value {self.default} is greater than maximum {self.constraints.max}"
                        )
        if self.type == ParamType.ENUM:
            if not self.options:
                raise ValueError("Enum parameter must have options defined")
            if self.default is not None and self.default not in self.options:
                raise ValueError(f"Default '{self.default}' must be one of the options: {self.options}")
        return self


class LayerType(BaseModel):
    """Definition of a layer type in the registry."""

    type_id: str = Field(..., description="Unique stable identifier for the layer type")
    display_name: str = Field(..., description="Human-readable display name")
    category: str = Field(..., description="Category (e.g., Core/CNN/RNN/Regularization/Utility)")
    description: str | None = Field(None, description="Description of what the layer does")
    keras_key: str = Field(..., description="Key to map to Keras builder functions")
    params: list[LayerParam] = Field(default_factory=list, description="List of configurable parameters")

    model_config = {"extra": "forbid"}

    @field_validator("params")
    @classmethod
    def unique_param_keys(cls, v: list[LayerParam]) -> list[LayerParam]:
        """Ensure param keys are unique within a layer."""
        keys = [p.key for p in v]
        if len(keys) != len(set(keys)):
            raise ValueError("Duplicate param keys found in layer definition")
        return v


class LayerRegistry(BaseModel):
    """Top-level container for the layer registry."""

    schema_version: int = Field(..., description="Registry schema version")
    layers: list[LayerType] = Field(..., description="List of registered layer types")

    model_config = {"extra": "forbid"}

    @field_validator("layers")
    @classmethod
    def unique_type_ids(cls, v: list[LayerType]) -> list[LayerType]:
        """Ensure type_ids are unique across all layers."""
        type_ids = [layer.type_id for layer in v]
        if len(type_ids) != len(set(type_ids)):
            raise ValueError("Duplicate type_id found in registry")
        return v


def load_registry_from_file(file_path: str | Path) -> LayerRegistry:
    """Load and validate a layer registry from a JSON file.

    Args:
        file_path: Path to the registry JSON file.

    Returns:
        Validated LayerRegistry instance.

    Raises:
        FileNotFoundError: If the registry file doesn't exist.
        ValueError: If the registry fails validation.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Registry file not found: {path.absolute()}")

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in registry file: {e}") from e

    try:
        return LayerRegistry.model_validate(data)
    except Exception as e:
        raise ValueError(f"Registry validation failed: {e}") from e
