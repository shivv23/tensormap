"""Unit tests for layer registry schema and loader."""

import json
import tempfile
from pathlib import Path

import pytest
from pydantic import ValidationError

from app.registry.loader import RegistryError, RegistryLoader
from app.registry.models import (
    LayerParam,
    LayerParamConstraints,
    LayerRegistry,
    LayerType,
    ParamType,
    load_registry_from_file,
)


# Minimal valid registry for testing
VALID_REGISTRY = {
    "schema_version": 1,
    "layers": [
        {
            "type_id": "test_layer",
            "display_name": "Test Layer",
            "category": "Test",
            "description": "A test layer",
            "keras_key": "test",
            "params": [
                {
                    "key": "units",
                    "label": "Units",
                    "type": "int",
                    "required": True,
                    "default": 128,
                }
            ],
        }
    ]
}


class TestLayerRegistrySchema:
    """Tests for the layer registry schema models."""

    def test_valid_registry(self):
        """Test that a valid registry passes validation."""
        registry = LayerRegistry.model_validate(VALID_REGISTRY)
        assert registry.schema_version == 1
        assert len(registry.layers) == 1
        assert registry.layers[0].type_id == "test_layer"

    def test_duplicate_type_id_fails(self):
        """Test that duplicate type_ids fail validation."""
        data = {
            "schema_version": 1,
            "layers": [
                {
                    "type_id": "duplicate",
                    "display_name": "Layer 1",
                    "category": "Test",
                    "keras_key": "key1",
                    "params": [],
                },
                {
                    "type_id": "duplicate",
                    "display_name": "Layer 2",
                    "category": "Test",
                    "keras_key": "key2",
                    "params": [],
                },
            ]
        }
        with pytest.raises(ValidationError) as exc_info:
            LayerRegistry.model_validate(data)
        assert "Duplicate type_id" in str(exc_info.value)

    def test_duplicate_param_key_fails(self):
        """Test that duplicate param keys within a layer fail."""
        data = {
            "schema_version": 1,
            "layers": [
                {
                    "type_id": "test_layer",
                    "display_name": "Test Layer",
                    "category": "Test",
                    "keras_key": "test",
                    "params": [
                        {"key": "units", "type": "int", "required": True},
                        {"key": "units", "type": "int", "required": True},
                    ],
                }
            ]
        }
        with pytest.raises(ValidationError) as exc_info:
            LayerRegistry.model_validate(data)
        assert "Duplicate param keys" in str(exc_info.value)

    def test_enum_missing_options_fails(self):
        """Test that enum param without options fails."""
        data = {
            "schema_version": 1,
            "layers": [
                {
                    "type_id": "test_layer",
                    "display_name": "Test Layer",
                    "category": "Test",
                    "keras_key": "test",
                    "params": [
                        {"key": "activation", "type": "enum", "required": False, "options": None}
                    ],
                }
            ]
        }
        with pytest.raises(ValidationError) as exc_info:
            LayerRegistry.model_validate(data)
        assert "Enum parameter must have options defined" in str(exc_info.value)

    def test_default_not_in_options_fails(self):
        """Test that default value not in options fails."""
        data = {
            "schema_version": 1,
            "layers": [
                {
                    "type_id": "test_layer",
                    "display_name": "Test Layer",
                    "category": "Test",
                    "keras_key": "test",
                    "params": [
                        {
                            "key": "activation",
                            "type": "enum",
                            "required": False,
                            "default": "invalid_option",
                            "options": ["relu", "sigmoid"],
                        }
                    ],
                }
            ]
        }
        with pytest.raises(ValidationError) as exc_info:
            LayerRegistry.model_validate(data)
        assert "must be one of the options" in str(exc_info.value)

    def test_min_max_constraint_violation_fails(self):
        """Test that min/max constraint violation fails."""
        data = {
            "schema_version": 1,
            "layers": [
                {
                    "type_id": "test_layer",
                    "display_name": "Test Layer",
                    "category": "Test",
                    "keras_key": "test",
                    "params": [
                        {
                            "key": "units",
                            "type": "int",
                            "required": True,
                            "default": 500,
                            "constraints": {"min": 1, "max": 100},
                        }
                    ],
                }
            ]
        }
        with pytest.raises(ValidationError) as exc_info:
            LayerRegistry.model_validate(data)
        assert "greater than maximum" in str(exc_info.value)

    def test_unknown_field_fails(self):
        """Test that unknown extra fields fail."""
        data = {
            "schema_version": 1,
            "layers": [
                {
                    "type_id": "test_layer",
                    "display_name": "Test Layer",
                    "category": "Test",
                    "keras_key": "test",
                    "unknown_field": "should fail",
                    "params": [],
                }
            ]
        }
        with pytest.raises(ValidationError) as exc_info:
            LayerRegistry.model_validate(data)
        # Pydantic v2 extra='forbid' error message contains the field name
        error_msg = str(exc_info.value)
        assert "extra" in error_msg or "unknown_field" in error_msg


class TestRegistryLoader:
    """Tests for the registry loader."""

    def test_load_valid_registry(self, tmp_path):
        """Test loading a valid registry file."""
        registry_file = tmp_path / "layers.json"
        registry_file.write_text(json.dumps(VALID_REGISTRY))

        registry = load_registry_from_file(registry_file)
        assert registry.schema_version == 1
        assert len(registry.layers) == 1

    def test_load_missing_file_fails(self, tmp_path):
        """Test that missing file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            load_registry_from_file(tmp_path / "nonexistent.json")

    def test_load_invalid_json_fails(self, tmp_path):
        """Test that invalid JSON raises ValueError."""
        registry_file = tmp_path / "invalid.json"
        registry_file.write_text("not valid json")

        with pytest.raises(ValueError) as exc_info:
            load_registry_from_file(registry_file)
        assert "Invalid JSON" in str(exc_info.value)

    def test_load_invalid_schema_fails(self, tmp_path):
        """Test that invalid schema raises ValueError."""
        registry_file = tmp_path / "invalid.json"
        registry_file.write_text(json.dumps({"invalid": "structure"}))

        with pytest.raises(ValueError) as exc_info:
            load_registry_from_file(registry_file)
        assert "validation failed" in str(exc_info.value).lower()


class TestRegistryLoaderClass:
    """Tests for the RegistryLoader class."""

    def test_get_registry_path_default(self, monkeypatch, tmp_path):
        """Test default registry path."""
        # Create a temporary registry file
        registry_file = tmp_path / "layers.json"
        registry_file.write_text(json.dumps(VALID_REGISTRY))

        # Mock the get_settings to return our test path
        monkeypatch.setattr("app.registry.loader.get_settings", lambda: type('Settings', (), {
            'upload_folder': str(tmp_path)
        })())

        # Should find the file
        path = RegistryLoader.get_registry_path()
        assert path.name == "layers.json"

    def test_env_override(self, monkeypatch, tmp_path):
        """Test environment variable override."""
        registry_file = tmp_path / "custom.json"
        registry_file.write_text(json.dumps(VALID_REGISTRY))

        monkeypatch.setenv("TENSORMAP_LAYER_REGISTRY_PATH", str(registry_file))

        path = RegistryLoader.get_registry_path()
        assert path == registry_file

    def test_load_and_get(self, monkeypatch, tmp_path):
        """Test loading and retrieving registry."""
        registry_file = tmp_path / "layers.json"
        registry_file.write_text(json.dumps(VALID_REGISTRY))

        monkeypatch.setenv("TENSORMAP_LAYER_REGISTRY_PATH", str(registry_file))

        # Reset the loader state
        RegistryLoader._registry = None
        RegistryLoader._loaded = False

        registry = RegistryLoader.load()
        assert registry is not None
        assert len(registry.layers) == 1

        # Test get_layer
        layer = RegistryLoader.get_layer("test_layer")
        assert layer is not None
        assert layer["type_id"] == "test_layer"

    def test_get_layer_not_found(self, monkeypatch, tmp_path):
        """Test get_layer returns None for unknown type."""
        registry_file = tmp_path / "layers.json"
        registry_file.write_text(json.dumps(VALID_REGISTRY))

        monkeypatch.setenv("TENSORMAP_LAYER_REGISTRY_PATH", str(registry_file))
        RegistryLoader._registry = None
        RegistryLoader._loaded = False
        RegistryLoader.load()

        result = RegistryLoader.get_layer("nonexistent")
        assert result is None

    def test_get_layers_by_category(self, monkeypatch, tmp_path):
        """Test filtering layers by category."""
        data = {
            "schema_version": 1,
            "layers": [
                {
                    "type_id": "layer1",
                    "display_name": "Layer 1",
                    "category": "CNN",
                    "keras_key": "key1",
                    "params": [],
                },
                {
                    "type_id": "layer2",
                    "display_name": "Layer 2",
                    "category": "CNN",
                    "keras_key": "key2",
                    "params": [],
                },
                {
                    "type_id": "layer3",
                    "display_name": "Layer 3",
                    "category": "Core",
                    "keras_key": "key3",
                    "params": [],
                },
            ]
        }
        registry_file = tmp_path / "layers.json"
        registry_file.write_text(json.dumps(data))

        monkeypatch.setenv("TENSORMAP_LAYER_REGISTRY_PATH", str(registry_file))
        RegistryLoader._registry = None
        RegistryLoader._loaded = False
        RegistryLoader.load()

        cnn_layers = RegistryLoader.get_layers_by_category("CNN")
        assert len(cnn_layers) == 2

        core_layers = RegistryLoader.get_layers_by_category("Core")
        assert len(core_layers) == 1


# Cleanup fixture
@pytest.fixture(autouse=True)
def cleanup_loader():
    """Cleanup loader state after each test."""
    yield
    RegistryLoader._registry = None
    RegistryLoader._loaded = False
