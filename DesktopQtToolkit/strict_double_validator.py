from PySide6.QtGui import QDoubleValidator, QValidator



class StrictDoubleValidator(QDoubleValidator):
    def validate(self, input_str:str, pos:int) -> tuple[QValidator.State, str, int]:
        state, input_str, pos = super().validate(input_str, pos)

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
            print(self.bottom()< value < self.top())
            return QValidator.State.Invalid, input_str, pos
        
        return state, input_str, pos
