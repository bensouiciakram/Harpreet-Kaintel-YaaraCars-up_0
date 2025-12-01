from typing import Dict, Any

from src.strategies.value_extraction import ValueExtractionStrategy
from src.strategies.exists_check import ExistsCheckStrategy
from src.strategies.value_extraction_all import ValueExtractionAllStrategy
from src.strategies.base_strategy import BaseStrategy


class StrategyFactory:
    """
    Factory responsible for creating strategy instances based on a
    configuration dictionary.

    This prevents direct imports in the sheet extractors and allows
    dynamic strategy creation from JSON/YAML config.
    """

    # Maps a strategy "type" (defined in config file) to a Python class
    _registry = {
        "value": ValueExtractionStrategy,
        "value_all":ValueExtractionAllStrategy,
        "exists": ExistsCheckStrategy,
    }

    @classmethod
    def create(cls, config: Dict[str, Any]) -> BaseStrategy:
        """
        Create a strategy instance based on the given config.

        Expected config structure:
        {
            "type": "value" | "exists",
            "xpath": "...",
            ... other params ...
        }

        Args:
            config (dict): Strategy configuration.

        Returns:
            BaseStrategy: Instance of the selected strategy.

        Raises:
            ValueError: If the strategy type is not registered.
        """

        strategy_type = config.get("type")
        if strategy_type not in cls._registry:
            raise ValueError(f"Unknown strategy type: {strategy_type}")

        strategy_class = cls._registry[strategy_type]

        # Instantiate the strategy — keep clean and argument-free here
        # All runtime arguments (xpath, feature, etc.) will be passed
        # through Column.apply().
        return strategy_class()
