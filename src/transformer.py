# transformer.py

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
