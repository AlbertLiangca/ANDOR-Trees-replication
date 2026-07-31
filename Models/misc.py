import copy
import numpy as np

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

def make_lambda_func(a,d):
        return lambda y : a*((1-y)**d)
    
def make_adder(funcs):
# Copy the function list 
    funcs = funcs[:]
    def sigma(x):
        return sum(f(x) for f in funcs)
    return sigma

def make_reciprocal(func):
    funcy = copy.copy(func)
    def sigma(x):
        return 1 - funcy(x)
    return sigma

def apply_neg_log(func):
    funcy = copy.copy(func)
    def sigma(x):
        return -1*np.log(funcy(x))
    return sigma

def create_nll(ls):
    funcs = ls[:]
    return make_adder(list(apply_neg_log(l) for l in funcs))
