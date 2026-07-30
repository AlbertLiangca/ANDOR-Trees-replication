# I made a move class just to make my life easier when it comes to playing out a problem
class move:
    def __init__(self,
                 id, # Which car
                 move, # Forward or backward
                 ):
        self.id = id
        self.move = move

    def __eq__(self, value):
        if not isinstance(value,move):
            return NotImplemented
        return self.id == value.id and self.move == value.move
    
    def unpack(self):
        return self.id,self.move # take the move and return a list of the items
    
    def display(self):
        return (self.id*(self.id != '-1')) + ('r'*int(self.id == '-1')) + str(self.move)
