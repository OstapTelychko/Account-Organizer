from typing import cast
from PySide6.QtGui import QDoubleValidator, QValidator



class StrictDoubleValidator(QDoubleValidator):
    """A custom QDoubleValidator that validates double values with strict bounds.
    
        This validator ensures that the input is a valid double and falls within the specified range.
    """

    def validate(self, input_str:str, pos:int) -> tuple[QValidator.State, str, int]:
        result = super().validate(input_str, pos)
        # Cast is needed because mypy doesn't know the return type of super().validate
        state, input_str, pos = cast(tuple[QValidator.State, str, int], result)

        try:
            if not input_str:
                return QValidator.State.Intermediate, input_str, pos
            
            if input_str.find(".") != -1:
                if len(input_str.split(".")[1]) > self.decimals():
                    return QValidator.State.Invalid, input_str, pos
                
                return QValidator.State.Intermediate, input_str, pos
            
            value = float(input_str)
            
        except ValueError:
            return QValidator.State.Invalid, input_str, pos
        
        # Instead of a potential Intermediate state, we return Invalid
        if not self.bottom() < value < self.top():
            return QValidator.State.Invalid, input_str, pos
        
        return state, input_str, pos
