# transformer.py
from re import findall,sub,split
from nested_lookup import nested_lookup
import chompjs

class Transformer:
    """
    Applies cleaning, normalization, splitting, and type conversions
    to the raw extracted data.

    raw_data structure:
    {
        "Engine & Power": {"Horse Power": "200 HP", "Fuel Type": "Petrol"},
        "Measurements": {"Dimensions": "4900 x 1800 x 1600 mm"}
    }
    """

    # Values to strip from all cells (treated as empty)
    STRIP_VALUES = ['N/A', 'N A']

    def __init__(self):
        # Mapping: sheet_name → { column_name → function }
        self._rules = {}
        self.add_rule('Make Model','Year',lambda v:self.clean_with_regex(v,'\d{4}'))
        self.add_rule('Make Model','Variant',lambda v:self.extract_jsonld_field(v,'variant'))
        self.add_rule('Make Model','Slug',lambda v:self.create_slug(v))
        self.add_rule('Make Model','Price',lambda v:self.clean_with_regex(v,'\d+,\d+'))
        self.add_rule('Make Model','Model',lambda v:self.clean_with_regex(v,'"model"\s*:\s*"([\s\S]+?)"'))
        # Extract Make from JSON-LD manufacturer field
        self.add_rule('Make Model','Make',lambda v:self.extract_jsonld_field(v,'manufacturer'))
        # Extract PNG URL from logo script using regex
        self.add_rule('Make Model','Logo Url',lambda v:self.clean_with_regex(v,'http\S+?\.png'))
        # Extract Brand from JSON-LD manufacturer field for other sheets
        self.add_rule('Engine & Power','Brand',lambda v:self.extract_jsonld_field(v,'manufacturer'))
        self.add_rule('Measurements','Brand',lambda v:self.extract_jsonld_field(v,'manufacturer'))
        self.add_rule('Safety Features','Brand',lambda v:self.extract_jsonld_field(v,'manufacturer'))
        self.add_rule('Interior Features','Brand',lambda v:self.extract_jsonld_field(v,'manufacturer'))
        self.add_rule('Exterior Features','Brand',lambda v:self.extract_jsonld_field(v,'manufacturer'))
        self.add_rule('Comfort Features','Brand',lambda v:self.extract_jsonld_field(v,'manufacturer'))
        # Description sheet Make and Model from JSON-LD
        self.add_rule('Description','Make',lambda v:self.extract_jsonld_field(v,'manufacturer'))
        self.add_rule('Description','Model',lambda v:self.extract_jsonld_field(v,'model'))
        self.add_rule('Engine & Power','Modal',lambda v:self.clean_with_regex(v,'"model"\s*:\s*"([\s\S]+?)"'))
        self.add_rule('Measurements','Modal',lambda v:self.clean_with_regex(v,'"model"\s*:\s*"([\s\S]+?)"'))
        self.add_rule('Safety Features','Modal',lambda v:self.clean_with_regex(v,'"model"\s*:\s*"([\s\S]+?)"'))
        self.add_rule('Interior Features','Modal',lambda v:self.clean_with_regex(v,'"model"\s*:\s*"([\s\S]+?)"'))
        self.add_rule('Exterior Features','Modal',lambda v:self.clean_with_regex(v,'"model"\s*:\s*"([\s\S]+?)"'))
        self.add_rule('Comfort Features','Modal',lambda v:self.clean_with_regex(v,'"model"\s*:\s*"([\s\S]+?)"'))
        self.add_rule('Engine & Power','Var',lambda v:self.extract_jsonld_field(v,'variant'))
        self.add_rule('Engine & Power','Battery Size (kWh)',lambda v:self.clean_with_regex(v,r'battery\\":\\"(\d+)\\"'))
        self.add_rule('Engine & Power','Battery Range km',lambda v:self.clean_with_regex(v,r'battery_range\\":\\"(\d+)\\"'))
        self.add_rule('Engine & Power','Motor',lambda v:self.clean_with_regex(v,r'motor\\":\\"([^"]+)\\"'))
        self.add_rule('Measurements','Var',lambda v:self.extract_jsonld_field(v,'variant'))
        self.add_rule('Safety Features','Var',lambda v:self.extract_jsonld_field(v,'variant'))
        self.add_rule('Interior Features','Var',lambda v:self.extract_jsonld_field(v,'variant'))
        self.add_rule('Exterior Features','Var',lambda v:self.extract_jsonld_field(v,'variant'))
        self.add_rule('Comfort Features','Var',lambda v:self.extract_jsonld_field(v,'variant'))
        self.add_rule('Description','ID',lambda v:self.clean_with_regex(v,'model/(\d+)'))
        self.add_rule('Description','Model Year',lambda v:self.clean_with_regex(v,'\d{4}'))
        self.add_rule(
            'Description',
            'Price',
            lambda v:sub('SAR|AED','',v).replace('to','-').strip()
            if findall('\d+',v) else ''
        )

    def add_rule(self, sheet_name: str, column_name: str, func):
        """
        Register a transformation function for a specific column.

        func receives ? value → output
        """
        if sheet_name not in self._rules:
            self._rules[sheet_name] = {}

        self._rules[sheet_name][column_name] = func

    def clean_universal(self, value: str) -> str:
        """
        Universal cleaner that strips unwanted values from all cells.
        Removes all occurrences of STRIP_VALUES from the value.
        """
        if not value:
            return value
        
        cleaned = value
        for strip_val in self.STRIP_VALUES:
            cleaned = cleaned.replace(strip_val, '')
        return cleaned.strip()

    def transform(self, raw_data: dict) -> dict:
        """
        Loops sheets and columns, applying transformations 
        only where rules exist.
        """
        cleaned = {}

        for sheet_name, sheet_dict in raw_data.items():
            cleaned[sheet_name] = {}

            for column_name, value in sheet_dict.items():
                # STEP 1: Check if a specific rule exists and apply it
                rule = (
                    self._rules
                    .get(sheet_name, {})
                    .get(column_name)
                )

                if rule:
                    value = rule(value)

                # STEP 2: Apply universal cleaner to ALL values
                cleaned_value = self.clean_universal(value)

                cleaned[sheet_name][column_name] = cleaned_value

        return cleaned

    def clean_with_regex(self,source:str,regex:str) -> str:
        return findall(regex,source)[0] if findall(regex,source) else ''

    def extract_variant(self,source:str) -> str:
        return split('\d{4}',source)[1].strip() if len(split('\d{4}',source)) > 1 else ''
    
    def create_slug(self,title:str) -> str:
        cleaning_list = [
            '\s+',
            '/',
            '\(',
            '\)',
            '"'
        ]
        title = sub('|'.join(cleaning_list),'-',title.lower())
        title = sub('-+','-',title)
        return title.strip('-')
    
    def extract_jsonld_field(self, source: str, field: str) -> str:
        """
        Extract a field from JSON-LD script content.
        
        Args:
            source: The JSON-LD script content string
            field: The field to extract ('manufacturer', 'brand', 'model', etc.)
            
        Returns:
            The extracted value or empty string if not found
        """
        try:
            # Parse the JSON-LD object
            obj = chompjs.parse_js_object(source)
            if not obj:
                return ''
            
            # Handle manufacturer field - returns manufacturer.name
            if field == 'manufacturer':
                manufacturer_data = nested_lookup('manufacturer', obj)
                if manufacturer_data and len(manufacturer_data) > 0:
                    manufacturer = manufacturer_data[0]
                    if isinstance(manufacturer, dict) and 'name' in manufacturer:
                        return manufacturer['name'].strip()
                    elif isinstance(manufacturer, str):
                        return manufacturer.strip()
                        
            # Handle brand field - returns brand.name
            elif field == 'brand':
                brand_data = nested_lookup('brand', obj)
                if brand_data and len(brand_data) > 0:
                    brand = brand_data[0]
                    if isinstance(brand, dict) and 'name' in brand:
                        return brand['name'].strip()
                    elif isinstance(brand, str):
                        return brand.strip()
                        
            # Handle model field
            elif field == 'model':
                model_data = nested_lookup('model', obj)
                if model_data and len(model_data) > 0:
                    model = model_data[0]
                    if isinstance(model, str):
                        return model.strip()
                    elif isinstance(model, dict) and 'name' in model:
                        return model['name'].strip()
                        
            # Handle variant (name field in JSON-LD)
            elif field == 'variant':
                if isinstance(obj, dict) and 'name' in obj:
                    return obj['name'].strip()
                    
            return ''
            
        except Exception:
            return ''
