"""India-specific context service — re-exports from utils.india_context for backwards compat."""

from utils.india_context import (
    compute_india_boost,
    get_city_demand_label,
    INDIA_SECTORS,
    INDIA_CITIES,
)

__all__ = ["compute_india_boost", "get_city_demand_label", "INDIA_SECTORS", "INDIA_CITIES"]
