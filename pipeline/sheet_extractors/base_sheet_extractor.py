# base_sheet_extractor.py
import json 
from pathlib import Path 
from columns import Column
from strategies.strategy_factory import StrategyFactory

class BaseSheetExtractor:
    """
    Base class for all sheet extractors.
    Each concrete sheet extractor should inherit from this.
    """

    def __init__(self, sheet_name:str):
        """
        Args:
            sheet_config (dict): Configuration dict for the sheet
                - 'sheet_name': str, name of the sheet
                - 'columns': list of column configs
        """
        self._sheet_name = sheet_name 
        self._sheet_config = self.get_sheet_config()
        self._columns = self._build_columns(self._sheet_config)

    def _build_columns(self, columns_config):
        """
        Build Column objects from the configuration.
        """
        columns = []
        for col_cfg in columns_config:
            columns.append(
                Column(
                    column_name=col_cfg['name'],
                    xpath=col_cfg["xpath"],
                    feature=col_cfg["name"] if col_cfg["type"] == "exists" else None,
                    strategy=StrategyFactory.create(
                        col_cfg
                    )
                )
            )
        return columns

    def extract(self, page):
        """
        Extract all column values for this sheet.

        Args:
            page: parsel Selector or similar object containing the HTML content.

        Returns:
            dict: {column_name: extracted_value, ...}
        """
        data = {}
        for col in self._columns:
            data[col.name] = col.extract(page)
        return data

    def get_sheet_config(self) -> list[dict]:
        return json.load(
            open(Path(__file__).parents[2].joinpath('config/config.json'),'r',encoding='utf-8')
        )[self._sheet_name]