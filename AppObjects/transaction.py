

class Transaction:

    def __init__(self, id:int, year:int, month:int, day:int, value:int|float, name:str):
        self.id = id
        self.year = year
        self.month = month
        self.day = day
        self.value = value
        self.name = name
