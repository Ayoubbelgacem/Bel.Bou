class BouBelError(Exception):
    def __init__(self, message, line=None, column=None):
        self.message = message
        self.line = line
        self.column = column
        super().__init__(self.format())
    
    def format(self):
        if self.line and self.column:
            return f"❌ {self.message} (line {self.line}, col {self.column})"
        elif self.line:
            return f"❌ {self.message} (line {self.line})"
        return f"❌ {self.message}"
    
    def __str__(self):
        return self.format()