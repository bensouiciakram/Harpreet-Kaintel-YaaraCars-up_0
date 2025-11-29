from parsel import Selector
from strategies.base_strategy import BaseStrategy

class ExistsCheckStrategy(BaseStrategy):
    """
    Strategy that checks whether a specific feature or value exists within
    elements extracted from the page.

    Typically used for feature sheets where each column represents a
    "Does the car have X?" question.

    Returns:
        'Yes' if the feature exists,
        'No' otherwise.
    """

    def extract(self, page_selector: Selector,xpath:str,feature:str=None) -> str:
        """
        Check whether a given feature exists on the page.

        Args:
            page_selector (Selector):
                The HTML page wrapped in a `parsel.Selector`.

            xpath (str):
                The XPath expression used to extract all feature texts
                from the page.

            feature (str):
                The feature name you want to check for existence.
                (e.g., "ABS", "Airbags", "Bluetooth")


        Returns:
            str:
                'Yes' if the feature exists on the page,
                'No' otherwise.
        """
        extracted_values = page_selector.xpath(xpath).getall()

        feature_lower = feature.lower()
        exists = any(feature_lower == value.strip().lower() for value in extracted_values)

        return "Yes" if exists else "No"
