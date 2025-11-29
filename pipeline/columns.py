from parsel import Selector
from strategies.base_strategy import BaseStrategy

class Column:
    """
    Represents a single column in a sheet and handles extracting its value
    from an HTML page using a given strategy.

    A Column defines *what* to extract and *how* to extract it.
    """

    def __init__(self, column_name: str,xpath:str, strategy: BaseStrategy):
        """
        Initialize a Column.

        Args:
            column_name (str):
                The name of the column as it should appear in the final sheet
                (e.g., "ModelName", "HasABS", "Brand", etc.).

            strategy (BaseStrategy):
                The extraction strategy instance responsible for computing
                the column value. This strategy determines *how* the data
                is extracted (e.g., using an XPath selector, or checking if
                something exists on the page).
        """
        self.__name = column_name
        self.__xpath = xpath 
        self.__strategy = strategy

    def extract(self, page_selector: Selector,**kwargs):
        """
        Extract the column value from the HTML page using the assigned strategy.

        Args:
            page_selector (Selector):
                A `parsel.Selector` containing the HTML content for extraction.
                The strategy will use this to locate the value.

        Returns:
            Any:
                The extracted value (usually a string, but can be bool, int,
                or None depending on the strategy).
        """
        return self.__strategy.extract(page_selector,xpath=self.__xpath,**kwargs)

    @property
    def name(self) -> str:
        """Return the column name."""
        return self.__name
    
    @property
    def xpath(self) -> str:
        return self.__xpath 
