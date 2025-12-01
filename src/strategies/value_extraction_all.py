from parsel import Selector
from src.strategies.base_strategy import BaseStrategy

class ValueExtractionAllStrategy(BaseStrategy):
    """
    Strategy to extract a text value or an attribute from the page using XPath 
    and getting all occurance.

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
        results = page_selector.xpath(xpath).getall()
        all_result = '\n'.join(results)
        return all_result.strip() if all_result else ''
