"""
Data validation utilities for YaaraCars data pipeline.
"""
import pandas as pd
from typing import List, Dict, Any, Optional

class DataValidator:
    """Base class for data validation."""
    
    @staticmethod
    def validate_required_columns(df: pd.DataFrame, required_columns: List[str]) -> List[str]:
        """
        Check if all required columns exist in the DataFrame.
        
        Args:
            df: Input DataFrame
            required_columns: List of required column names
            
        Returns:
            List of missing columns, empty if all are present
        """
        return [col for col in required_columns if col not in df.columns]
    
    @staticmethod
    def validate_no_empty_values(df: pd.DataFrame, columns: List[str]) -> Dict[str, List[int]]:
        """
        Check for empty or null values in specified columns.
        
        Args:
            df: Input DataFrame
            columns: List of columns to check
            
        Returns:
            Dictionary mapping column names to list of row indices with empty values
        """
        issues = {}
        for col in columns:
            if col in df.columns:
                empty_rows = df[df[col].isna() | (df[col] == '')].index.tolist()
                if empty_rows:
                    issues[col] = empty_rows
        return issues
    
    @staticmethod
    def validate_numeric_range(
        df: pd.DataFrame, 
        column: str, 
        min_val: Optional[float] = None, 
        max_val: Optional[float] = None
    ) -> List[int]:
        """
        Validate that numeric values fall within specified range.
        
        Args:
            df: Input DataFrame
            column: Column name to validate
            min_val: Minimum allowed value (inclusive)
            max_val: Maximum allowed value (inclusive)
            
        Returns:
            List of row indices with out-of-range values
        """
        if column not in df.columns or df[column].isna().all():
            return []
            
        mask = pd.Series(True, index=df.index)
        
        if min_val is not None:
            mask &= (df[column] >= min_val)
        if max_val is not None:
            mask &= (df[column] <= max_val)
            
        return df[~mask].index.tolist()
    
    @staticmethod
    def validate_string_length(
        df: pd.DataFrame, 
        column: str, 
        min_length: int = 0, 
        max_length: Optional[int] = None
    ) -> List[int]:
        """
        Validate string length constraints.
        
        Args:
            df: Input DataFrame
            column: Column name to validate
            min_length: Minimum allowed length
            max_length: Maximum allowed length
            
        Returns:
            List of row indices with invalid string lengths
        """
        if column not in df.columns or df[column].isna().all():
            return []
            
        mask = df[column].astype(str).str.len() >= min_length
        
        if max_length is not None:
            mask &= (df[column].astype(str).str.len() <= max_length)
            
        return df[~mask].index.tolist()
    
    @staticmethod
    def validate_against_enum(
        df: pd.DataFrame, 
        column: str, 
        allowed_values: List[Any]
    ) -> List[int]:
        """
        Validate that column values are in a predefined list of allowed values.
        
        Args:
            df: Input DataFrame
            column: Column name to validate
            allowed_values: List of allowed values
            
        Returns:
            List of row indices with invalid values
        """
        if column not in df.columns or df[column].isna().all():
            return []
            
        return df[~df[column].isin(allowed_values)].index.tolist()


def validate_brands(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Validate brand data according to YaaraCars requirements.
    
    Args:
        df: Brands DataFrame
        
    Returns:
        Dictionary containing validation results
    """
    validator = DataValidator()
    issues = {}
    
    # Required columns check
    required_columns = ['name', 'slug', 'market']
    missing_columns = validator.validate_required_columns(df, required_columns)
    if missing_columns:
        issues['missing_columns'] = missing_columns
    
    # No empty values in required fields
    empty_values = validator.validate_no_empty_values(df, required_columns)
    if empty_values:
        issues['empty_values'] = empty_values
    
    # Validate market values
    if 'market' in df.columns:
        invalid_markets = validator.validate_against_enum(
            df, 'market', ['UAE', 'KSA']
        )
        if invalid_markets:
            issues['invalid_markets'] = invalid_markets
    
    # Validate slug format (alphanumeric, hyphens, underscores only)
    if 'slug' in df.columns:
        invalid_slugs = []
        for idx, slug in df['slug'].items():
            if not isinstance(slug, str) or not slug.replace('-', '').replace('_', '').isalnum():
                invalid_slugs.append(idx)
        if invalid_slugs:
            issues['invalid_slugs'] = invalid_slugs
    
    return {
        'is_valid': len(issues) == 0,
        'issues': issues,
        'validated_rows': len(df) - len(set(
            idx for issue in issues.values() 
            for idx in (issue if isinstance(issue, list) else issue.values())
        ))
    }
