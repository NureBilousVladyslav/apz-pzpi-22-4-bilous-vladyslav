import re
from datetime import datetime
from typing import Optional


class Validator:
    EMAIL_REGEX = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    NAME_REGEX = r'^[a-zA-Zа-яА-Я\s-]{2,100}$'

    @staticmethod
    def validate_required_fields(data: dict, required_fields: list) -> None:
        """Validate that all required fields are present and not empty."""
        missing_fields = [field for field in required_fields if not data.get(field)]
        if missing_fields:
            raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")

    @staticmethod
    def validate_email(email: str) -> None:
        """Validate email format using regex."""
        if not re.match(Validator.EMAIL_REGEX, email):
            raise ValueError("Invalid email format")

    @staticmethod
    def validate_name(name: str) -> None:
        """Validate name format using regex."""
        if not re.match(Validator.NAME_REGEX, name):
            raise ValueError("Invalid name format")

    @staticmethod
    def validate_password(password: str) -> None:
        """Validate password strength."""
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters")

    @staticmethod
    def validate_limit(limit: str) -> None:
        """Validate limit is a positive integer."""
        try:
            limit_int = int(limit)
            if limit_int <= 0:
                raise ValueError("Limit must be positive")
        except (ValueError, TypeError):
            raise ValueError("Limit must be a positive integer")

    @staticmethod
    def validate_birthday(birthday: Optional[str]) -> None:
        """Validate birthday format and logic."""
        if birthday is None:  # Поле необязательное
            return

        try:
            birth_date = datetime.strptime(birthday, '%Y-%m-%d').date()
            current_date = datetime.now().date()
            if birth_date >= current_date:
                raise ValueError("Birthday cannot be in the future")
            if (current_date.year - birth_date.year) > 150:  # Предполагаемый максимальный возраст
                raise ValueError("Invalid birthday: age exceeds reasonable limit")
        except ValueError as e:
            if str(e).startswith("Birthday") or str(e).startswith("Invalid"):
                raise
            raise ValueError("Invalid birthday format. Use YYYY-MM-DD")

    @staticmethod
    def validate_pressure(value: float | str, unit: str, desired_unit: str) -> float:
        """
        Convert pressure value to the desired unit.

        Args:
            value: Pressure value (float or string convertible to float)
            unit: Current unit ('bar', 'psi', 'kPa')
            desired_unit: Unit to convert to ('bar', 'psi', 'kPa')

        Returns:
            float: Pressure value converted to desired_unit

        Raises:
            ValueError: If value or unit is invalid
        """
        try:
            pressure = float(value)
        except (ValueError, TypeError):
            raise ValueError("Pressure must be a valid number")

        if unit is None or desired_unit is None:
            return pressure

        unit = unit.lower()
        desired_unit = desired_unit.lower()
        if unit not in ['bar', 'psi', 'kpa'] or desired_unit not in ['bar', 'psi', 'kpa']:
            raise ValueError("Pressure unit must be 'bar', 'psi', or 'kPa'")

        # Conversion factors to bar (intermediate step)
        to_bar = {
            'bar': 1.0,
            'psi': 0.0689476,
            'kpa': 0.01
        }
        # Conversion factors from bar
        from_bar = {
            'bar': 1.0,
            'psi': 14.5038,
            'kpa': 100.0
        }

        # Convert to bar first
        pressure_in_bar = pressure * to_bar[unit]
        if pressure_in_bar <= 0 or pressure_in_bar > 99.99:
            raise ValueError(f"Pressure in {unit} must be between 0 and 99.99 when converted to bar")

        # Convert from bar to desired unit
        converted_pressure = pressure_in_bar * from_bar[desired_unit]
        return converted_pressure
