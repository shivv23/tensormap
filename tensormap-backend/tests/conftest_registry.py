"""Registry-specific test configuration.

This conftest provides isolated test fixtures for registry tests
without requiring full app initialization.
"""

import pytest


@pytest.fixture
def valid_registry_data():
    """Return a valid minimal registry data structure."""
    return {
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


@pytest.fixture
def sample_layers_data():
    """Return sample registry with multiple layers."""
    return {
        "schema_version": 1,
        "layers": [
            {
                "type_id": "custominput",
                "display_name": "Input",
                "category": "Core",
                "description": "Input layer",
                "keras_key": "input",
                "params": [
                    {"key": "dim-1", "type": "int", "required": False},
                    {"key": "dim-2", "type": "int", "required": False},
                    {"key": "dim-3", "type": "int", "required": False},
                ],
            },
            {
                "type_id": "customdense",
                "display_name": "Dense",
                "category": "Core",
                "description": "Fully connected layer",
                "keras_key": "dense",
                "params": [
                    {"key": "units", "type": "int", "required": True, "default": 128},
                    {"key": "activation", "type": "enum", "options": ["relu", "sigmoid"], "default": "relu"},
                ],
            },
        ]
    }
