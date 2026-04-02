"""Layer Registry loader module.

Loads and validates the layer registry at startup.
"""

import os
from pathlib import Path
from typing import Any

from app.config import get_settings
from app.registry.models import LayerRegistry, load_registry_from_file


class RegistryError(Exception):
    """Exception raised when registry loading fails."""

    pass


class RegistryLoader:
    """Handles loading and caching of the layer registry."""

    _registry: LayerRegistry | None = None
    _loaded: bool = False

    @classmethod
    def get_registry_path(cls) -> Path:
        """Get the registry file path from settings or environment.

        Returns:
            Path to the registry file.
        """
        settings = get_settings()
        # Check for environment variable override first
        env_path = os.environ.get("TENSORMAP_LAYER_REGISTRY_PATH")
        if env_path:
            return Path(env_path)

        # Default to layers.json in the app directory
        return Path(__file__).parent / "layers.json"

    @classmethod
    def load(cls) -> LayerRegistry:
        """Load and validate the registry from file.

        Returns:
            Validated LayerRegistry instance.

        Raises:
            RegistryError: If loading or validation fails.
        """
        if cls._loaded and cls._registry is not None:
            return cls._registry

        try:
            registry_path = cls.get_registry_path()
            cls._registry = load_registry_from_file(registry_path)
            cls._loaded = True
            return cls._registry
        except FileNotFoundError as e:
            raise RegistryError(
                f"Layer registry file not found. Expected at: {cls.get_registry_path()}"
            ) from e
        except ValueError as e:
            raise RegistryError(
                f"Layer registry validation failed: {e}"
            ) from e
        except Exception as e:
            raise RegistryError(
                f"Unexpected error loading layer registry: {e}"
            ) from e

    @classmethod
    def get(cls) -> LayerRegistry:
        """Get the loaded registry instance.

        Returns:
            The validated LayerRegistry instance.

        Raises:
            RegistryError: If the registry hasn't been loaded yet.
        """
        if cls._registry is None:
            raise RegistryError("Registry not loaded. Call load() first.")
        return cls._registry

    @classmethod
    def reload(cls) -> LayerRegistry:
        """Force reload the registry from disk.

        Returns:
            Validated LayerRegistry instance.
        """
        cls._registry = None
        cls._loaded = False
        return cls.load()

    @classmethod
    def get_layer(cls, type_id: str) -> dict[str, Any] | None:
        """Get a layer definition by type_id.

        Args:
            type_id: The unique identifier for the layer type.

        Returns:
            Dictionary representation of the layer, or None if not found.
        """
        registry = cls.get()
        for layer in registry.layers:
            if layer.type_id == type_id:
                return layer.model_dump()
        return None

    @classmethod
    def get_layers_by_category(cls, category: str) -> list[dict[str, Any]]:
        """Get all layers in a specific category.

        Args:
            category: The category to filter by.

        Returns:
            List of layer dictionaries.
        """
        registry = cls.get()
        return [
            layer.model_dump()
            for layer in registry.layers
            if layer.category == category
        ]
