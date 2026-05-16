class Marble:
    def __init__(self, color, pit, owner, location, size):
        self.color = color
        self.pit = pit
        self.owner = owner
        self.location = location
        self.size = size
        
    def update_owner(self):
        if type(self.pit) == int:
            self.owner = 1 if self.pit <= 6 else 2
    
    def move(self):
        p = self.pit
        match p:
            case 6:
                self.pit = 'b1' if self.owner == 1 else 7
            case 12:
                self.pit = 'b2' if self.owner == 2 else 1
            case 'b1' | 'b2':
                self.pit = 7 if p == 'b1' else 1
            case _:
                self.pit = int(p) + 1