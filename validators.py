"""
Input validation utilities for the application.
"""
from typing import Any, Optional, List, Callable
import re


class Validator:
    """Input validation utility class."""
    
    @staticmethod
    def validate_string(value: str, min_length: int = 1, max_length: int = 255) -> str:
        """
        Validate string input.
        
        Args:
            value: String to validate
            min_length: Minimum allowed length
            max_length: Maximum allowed length
        
        Returns:
            Stripped string value
        
        Raises:
            ValueError: If validation fails
        """
        if not isinstance(value, str):
            raise ValueError("Value must be a string")
        
        value = value.strip()
        
        if len(value) < min_length:
            raise ValueError(f"String must be at least {min_length} character(s)")
        
        if len(value) > max_length:
            raise ValueError(f"String must not exceed {max_length} character(s)")
        
        return value
    
    @staticmethod
    def validate_name(name: str, min_length: int = 1, max_length: int = 50) -> str:
        """
        Validate player name.
        
        Args:
            name: Player name
            min_length: Minimum length
            max_length: Maximum length
        
        Returns:
            Validated name
        
        Raises:
            ValueError: If validation fails
        """
        name = Validator.validate_string(name, min_length, max_length)
        
        # Allow letters, numbers, spaces, hyphens, and apostrophes only
        if not re.match(r"^[a-zA-Z0-9\s'-]+$", name):
            raise ValueError("Name contains invalid characters")
        
        return name
    
    @staticmethod
    def validate_email(email: str) -> str:
        """
        Validate email address.
        
        Args:
            email: Email to validate
        
        Returns:
            Validated email
        
        Raises:
            ValueError: If validation fails
        """
        email = Validator.validate_string(email, max_length=255)
        
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            raise ValueError("Invalid email format")
        
        return email.lower()
    
    @staticmethod
    def validate_integer(value: Any, min_val: Optional[int] = None, max_val: Optional[int] = None) -> int:
        """
        Validate integer input.
        
        Args:
            value: Value to validate
            min_val: Minimum allowed value
            max_val: Maximum allowed value
        
        Returns:
            Integer value
        
        Raises:
            ValueError: If validation fails
        """
        try:
            num = int(value)
        except (TypeError, ValueError):
            raise ValueError("Value must be an integer")
        
        if min_val is not None and num < min_val:
            raise ValueError(f"Value must be at least {min_val}")
        
        if max_val is not None and num > max_val:
            raise ValueError(f"Value must not exceed {max_val}")
        
        return num
    
    @staticmethod
    def validate_list(value: Any, item_validator: Optional[Callable] = None, min_items: int = 0) -> List:
        """
        Validate list input.
        
        Args:
            value: List to validate
            item_validator: Optional function to validate each item
            min_items: Minimum number of items
        
        Returns:
            Validated list
        
        Raises:
            ValueError: If validation fails
        """
        if not isinstance(value, list):
            raise ValueError("Value must be a list")
        
        if len(value) < min_items:
            raise ValueError(f"List must contain at least {min_items} item(s)")
        
        if item_validator:
            return [item_validator(item) for item in value]
        
        return value
    
    @staticmethod
    def validate_choice(value: str, choices: List[str]) -> str:
        """
        Validate choice from predefined list.
        
        Args:
            value: Value to validate
            choices: List of allowed values
        
        Returns:
            Validated value
        
        Raises:
            ValueError: If validation fails
        """
        if value not in choices:
            raise ValueError(f"Value must be one of: {', '.join(choices)}")
        
        return value


class MatchValidator:
    """Validator for match-related data."""
    
    @staticmethod
    def validate_match_type(match_type: str) -> str:
        """Validate match type is 'singles' or 'doubles'."""
        return Validator.validate_choice(match_type, ['singles', 'doubles'])
    
    @staticmethod
    def validate_match_data(winners: List[str], losers: List[str], match_type: str) -> tuple:
        """
        Validate complete match data.
        
        Args:
            winners: List of winner names
            losers: List of loser names
            match_type: 'singles' or 'doubles'
        
        Returns:
            Tuple of (validated_winners, validated_losers, validated_type)
        
        Raises:
            ValueError: If validation fails
        """
        # Validate type
        match_type = MatchValidator.validate_match_type(match_type)
        
        # Validate winners
        winners = Validator.validate_list(
            winners,
            item_validator=lambda x: Validator.validate_name(x),
            min_items=1
        )
        
        # Validate losers
        losers = Validator.validate_list(
            losers,
            item_validator=lambda x: Validator.validate_name(x),
            min_items=1
        )
        
        # Ensure match type matches player count
        if match_type == 'doubles' and (len(winners) != 2 or len(losers) != 2):
            raise ValueError("Doubles match must have exactly 2 winners and 2 losers")
        
        if match_type == 'singles' and (len(winners) != 1 or len(losers) != 1):
            raise ValueError("Singles match must have exactly 1 winner and 1 loser")
        
        return winners, losers, match_type
