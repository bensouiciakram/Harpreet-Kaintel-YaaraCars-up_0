from parsel import Selector
from strategies.base_strategy import BaseStrategy

class ValueExtractionStrategy(BaseStrategy):
    """
    Strategy to extract a text value or an attribute from the page using XPath.

    This is used for normal columns like Brand, Model, Year, EngineSize, etc.
    """

    def extract(self, page_selector: Selector,xpath:str,feature:str=None) -> str:
        """
        Extract a value from the page using the given XPath.

        Args:
            page_selector (Selector):
                The HTML page wrapped in a `parsel.Selector`.

            xpath (str):
                XPath expression used to extract a single text value or attribute.

        Returns:
            str:
                The extracted value, or `default` if nothing was found.
        """
        result = page_selector.xpath(xpath).get()
        return result.strip()
