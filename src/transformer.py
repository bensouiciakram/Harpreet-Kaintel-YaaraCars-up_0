# transformer.py
from re import findall,sub,split

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

    def __init__(self):
        # Mapping: sheet_name → { column_name → function }
        self._rules = {}
        self.add_rule('Make Model','Year',lambda v:self.clean_with_regex(v,'\d{4}'))
        self.add_rule('Make Model','Variant',lambda v:self.extract_variant(v))
        self.add_rule('Make Model','Slug',lambda v:sub('[\s|\(|\)]+','-',v).strip('-'))
        self.add_rule('Make Model','Price',lambda v:self.clean_with_regex(v,'\d+,\d+'))
        self.add_rule('Engine & Power','Var',lambda v:self.extract_variant(v))
        self.add_rule('Measurements','Var',lambda v:self.extract_variant(v))
        self.add_rule('Safety Features','Var',lambda v:self.extract_variant(v))
        self.add_rule('Interior Features','Var',lambda v:self.extract_variant(v))
        self.add_rule('Exterior Features','Var',lambda v:self.extract_variant(v))
        self.add_rule('Comfort Features','Var',lambda v:self.extract_variant(v))
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

    def transform(self, raw_data: dict) -> dict:
        """
        Loops sheets and columns, applying transformations 
        only where rules exist.
        """
        cleaned = {}

        for sheet_name, sheet_dict in raw_data.items():
            cleaned[sheet_name] = {}

            for column_name, value in sheet_dict.items():

                # check if a rule exists
                rule = (
                    self._rules
                    .get(sheet_name, {})
                    .get(column_name)
                )

                if rule:
                    cleaned_value = rule(value)
                else:
                    cleaned_value = value  # no transform applied

                cleaned[sheet_name][column_name] = cleaned_value

        return cleaned

    def clean_with_regex(self,source:str,regex:str) -> str:
        return findall(regex,source)[0] if findall(regex,source) else ''

    def extract_variant(self,source:str) -> str:
        return split('\d{4}',source)[1].strip() if len(split('\d{4}',source)) > 1 else ''