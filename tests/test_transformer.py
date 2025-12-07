import pytest 
from src.transformer import Transformer

class TestTransformer:
    
    def test_clean_with_regex_exists(self):
        transformer = Transformer()
        cleaned_source = transformer.clean_with_regex('BYD Shark 6 2025 Premium','\d{4}')
        assert cleaned_source == '2025'

    def test_clean_with_regex_not_exist(self):
        transformer = Transformer()
        cleaned_source = transformer.clean_with_regex('BYD Shark Premium','\d{4}')
        assert cleaned_source == ''

    def test_clean_with_regex_value_absence(self):
        transformer = Transformer()
        with pytest.raises(TypeError):
            transformer.clean_with_regex(None,'')

    def test_extract_variant_exist(self):
        transformer = Transformer()
        extracted_source = transformer.extract_variant('Toyota Sequoia 2025 3.5L V6 Hybrid (AWD)')
        assert extracted_source == '3.5L V6 Hybrid (AWD)'

    def test_extract_variant_not_exist(self):
        transformer = Transformer()
        extracted_source = transformer.extract_variant('Toyota Sequoia 3.5L V6 Hybrid (AWD)')
        assert extracted_source == ''

    def test_extract_variant_value_absence(self):
        transformer = Transformer()
        with pytest.raises(TypeError):
            transformer.extract_variant(None)

    