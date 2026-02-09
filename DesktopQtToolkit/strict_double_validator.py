from typing import cast
from PySide6.QtGui import QDoubleValidator, QValidator


# pyright: reportIncompatibleMethodOverride=false
class StrictDoubleValidator(QDoubleValidator):
    """A custom QDoubleValidator that validates double values with strict bounds.
    
        This validator ensures that the input is a valid double and falls within the specified range.
    """

    def check_value_bounds(self, value:str) -> bool:
        """Check if the value is within the specified bounds."""
        try:
            value_float = float(value)
        except ValueError:
            return True# If the value is not a valid float, we consider it's intermediate state for example input is 1. and user is still typing
        
        return self.bottom() < value_float < self.top()


    def validate(self, input_str:str, pos:int) -> tuple[QValidator.State, str, int]:
        result = super().validate(input_str, pos)
        # Cast is needed because mypy doesn't know the return type of super().validate
        state, input_str, pos = cast(tuple[QValidator.State, str, int], result)

        try:
            if not input_str:
                return QValidator.State.Intermediate, input_str, pos
            
            if input_str.find(".") != -1:
                digit, decimal = input_str.split(".")
                if len(decimal) > self.decimals() or not decimal.isdigit() and len(decimal) > 0 or digit == "" or not digit.isdigit():
                    return QValidator.State.Invalid, input_str, pos
                
                if not self.check_value_bounds(input_str):
                    return QValidator.State.Invalid, input_str, pos
                
                return QValidator.State.Intermediate, input_str, pos
            
        except ValueError:
            return QValidator.State.Invalid, input_str, pos
        
        if not self.check_value_bounds(input_str):
            return QValidator.State.Invalid, input_str, pos
        
        return state, input_str, pos
