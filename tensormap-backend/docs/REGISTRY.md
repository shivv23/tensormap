# Layer Registry

The TensorMap Layer Registry is a data-driven system that defines available neural network layer types and their configurable parameters.

## Overview

The registry provides a centralized, versioned schema for all supported Keras layer types. This enables:
- Centralized layer type definitions
- Parameter validation at startup
- Future extensibility for adding new layers without code changes

## Registry File

The registry is stored in `app/registry/layers.json`.

### Structure

```json
{
  "schema_version": 1,
  "layers": [
    {
      "type_id": "customdense",
      "display_name": "Dense",
      "category": "Core",
      "description": "Fully connected dense layer",
      "keras_key": "dense",
      "params": [
        {
          "key": "units",
          "label": "Units",
          "type": "int",
          "required": true,
          "default": 128,
          "constraints": { "min": 1, "max": 4096 },
          "help_text": "Number of neurons in the layer"
        }
      ]
    }
  ]
}
```

## Validation

The registry is validated using Pydantic v2 at backend startup. If validation fails, the application will not start and will display actionable error messages.

### Validation Rules

- Each `type_id` must be unique across all layers
- Each `param.key` must be unique within a layer
- Enum parameters must have `options` defined
- Default values must be within min/max constraints
- Default values for enum must be in the options list
- Unknown fields are forbidden

## Development Override

To use a custom registry file during development, set the environment variable:

```bash
export TENSORMAP_LAYER_REGISTRY_PATH=/path/to/custom/layers.json
```

## Accessing the Registry

```python
from app.registry.loader import RegistryLoader

# Get a specific layer
layer = RegistryLoader.get_layer("customdense")

# Get all layers in a category
cnn_layers = RegistryLoader.get_layers_by_category("CNN")
```

## Adding New Layers

1. Add the layer definition to `app/registry/layers.json`
2. Ensure all validation rules are met
3. The backend will validate on next startup
4. (Future PRs will wire this into code generation)
