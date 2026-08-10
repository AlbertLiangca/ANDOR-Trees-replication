class OR:
    def __init__(
            self,
            car_id
    ):
        self._display = car_id
        self._car = car_id
        self._prob = None
        self._gamma = None
        self._stop_prob = None
        self._children = []
    
    def set_prob(self,prob):
        self._prob = prob
    
    def set_gamma(self,gamma):
        self._gamma = gamma

    def set_stop_prob(self,stop_prob):
        self._stop_prob = stop_prob
    
    def set_child(self,child):
        self._children.append(child)

    def del_child(self,child):
        self._children.remove(child)    

    def propagate_prob(self):
        stop_prob = self._prob * self._gamma
        self.set_stop_prob(stop_prob)
        
        cont = (self._prob - stop_prob) / len(self._children)
        for i in self._children:
            i.set_prob(cont)
            i.set_gamma(self._gamma)
            i.propagate_prob()

class AND:
    def __init__(
            self,
            move
    ):
        self._display = move.display()
        self._move = move
        self._prob = None
        self._gamma = None
        self._children = []
        self._is_leaf = False
    
    def set_prob(self,prob):
        self._prob = prob
    
    def set_child(self,child):
        self._children.append(child)
    
    def set_gamma(self,gamma):
        self._gamma = gamma

    def set_stop_prob(self,stop_prob):
        self._stop_prob = stop_prob

    def del_child(self,child):
        self._children.remove(child)

    def set_leaf(self):
        self._is_leaf = True    
    
    def propagate_prob(self):
        denom = len(self._children) if self._children else 1
        cont = self._prob / denom
        if self._children:
            for i in self._children:
                i.set_prob(cont)
                i.set_gamma(self._gamma)
                i.propagate_prob()