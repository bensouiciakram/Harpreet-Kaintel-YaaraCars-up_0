from parsel import Selector 

class BaseStrategy:
    """
    Base Strategy interface for column extraction behaviors.
    Every strategy must implement the `apply()` method.
    """

    def extract(self,page_selector:Selector,xpath:str)->str:
        """
        Args:
            page_selector (Selector): Selector object that represent the dom of page
            xpath: xpath selector to extract data necessary 
        Returns:
            str: Extracted value of the column.
        """
        raise NotImplementedError("Strategy classes must implement the extract() method.")