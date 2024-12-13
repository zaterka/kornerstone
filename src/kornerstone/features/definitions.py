"""Feature definitions for the ML platform."""

from feast import Entity, Feature, FeatureView, ValueType

# Example feature definition
customer = Entity(
    name="customer",
    value_type=ValueType.INT64,
    description="Customer identifier",
)
