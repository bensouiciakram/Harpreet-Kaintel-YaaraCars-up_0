"""
Slug generation utilities for YaaraCars.
Converts strings into URL-friendly slugs.
"""
import re
import unicodedata

def slugify(text):
    """
    Convert a string to a URL-friendly slug.
    
    Args:
        text (str): Input string to convert
        
    Returns:
        str: URL-friendly slug
    """
    if not text:
        return ""
    
    # Normalize unicode characters
    text = unicodedata.normalize('NFKD', str(text))
    
    # Convert to lowercase and remove special characters
    text = re.sub(r'[^\w\s-]', '', text.lower())
    
    # Replace spaces and dashes with single hyphen
    text = re.sub(r'[-\s]+', '-', text.strip())
    
    # Remove leading/trailing hyphens
    return text.strip('-')

def generate_variant_slug(brand, model, year, trim):
    """
    Generate a slug for a vehicle variant.
    
    Args:
        brand (str): Brand name
        model (str): Model name
        year (int/str): Model year
        trim (str): Trim level
        
    Returns:
        str: Generated slug
    """
    return f"{slugify(brand)}-{slugify(model)}-{year}-{slugify(trim)}"

if __name__ == "__main__":
    # Example usage
    print(slugify("Toyota Camry 2023 XSE"))  # toyota-camry-2023-xse
    print(generate_variant_slug("Toyota", "Camry", 2023, "XSE Hybrid"))  # toyota-camry-2023-xse-hybrid
