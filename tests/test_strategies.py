from parsel import Selector 
from src.strategies.value_extraction import ValueExtractionStrategy
from src.strategies.value_extraction_all import ValueExtractionAllStrategy
from src.strategies.exists_check import ExistsCheckStrategy


class TestValueExtract:

    def test_extract_exist(self):
        extractor = ValueExtractionStrategy()
        page_selector =Selector(
            text='<div class="data">value</div>'
        )
        result = extractor.extract(page_selector,'//div[@class="data"]/text()')
        assert result == 'value'

    def test_extract_not_exist(self):
        extractor = ValueExtractionStrategy()
        page_selector =Selector(
            text='<div>value</div>'
        )
        result = extractor.extract(page_selector,'//div[@class="data"]/text()')
        assert result == ''

    
class TestValueExtractAll:

    def test_extract_exist(self):
        extractor = ValueExtractionAllStrategy()
        page_selector =Selector(
            text="""
                    <div>
                        <div class="data">value1</div>
                        <div class="data">value2</div>
                    </div>
                """
        )
        result = extractor.extract(page_selector,'//div[@class="data"]/text()')
        assert result == 'value1\nvalue2'

    def test_extract_not_exist(self):
        extractor = ValueExtractionAllStrategy()
        page_selector =Selector(
            text='<div>value</div>'
        )
        result = extractor.extract(page_selector,'//div[@class="data"]/text()')
        assert result == ''


class TestCheckExistsExtract:

    def test_extract_yes(self):
        extractor = ExistsCheckStrategy()
        page_selector =Selector(
            text="""
                <ul>
                    <li>feature</li>
                </ul>
            """
        )
        result = extractor.extract(page_selector,'//ul/li/text()','feature')
        assert result == 'Yes'

    def test_extract_no(self):
        extractor = ExistsCheckStrategy()
        page_selector =Selector(
            text="""
                <ul>
                    <li></li>
                </ul>
            """
        )
        result = extractor.extract(page_selector,'//ul/li/text()','feature')
        assert result == 'No'

    def test_extract_no_selector_result(self):
        extractor = ExistsCheckStrategy()
        page_selector =Selector(
            text="""
                <ul>
                    <li></li>
                </ul>
            """
        )
        result = extractor.extract(page_selector,'//ul[@class="data"]/li/text()','feature')
        assert result == 'No'

