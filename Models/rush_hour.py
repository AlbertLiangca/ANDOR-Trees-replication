from misc import move
import json
import numpy as np

class problem:
    def __init__(self,json_file):
        with open(json_file) as file:
            problem = json.load(file)
        self.id = problem['id']
        self._cars_tmp = problem['cars']
        self._board = np.zeros(36)
        self._board_2d = self._board.reshape(6,6)

        # Initialize a new cars value which takes the form of dict, so I can access car values easier
        self._cars = {}
        self.history = []
        for i in self._cars_tmp:
            id = i['id']
            if id != 'r':
                id = str(int(id)+1)
            else:
                id = '-1'
            i_orient = i['orientation']
            i_pos = i['position']
            i_len = i['length']
            if i_orient == 'horizontal':
                sq_occ = np.arange(i_pos,i_pos+i_len)
            elif i_orient == 'vertical':
                sq_occ = np.arange(i_pos,i_pos+6*i_len,6)
            self._board[sq_occ] = int(id)

            self._cars[id] = {
                'orientation': i_orient,
                'position': i_pos,
                'length': i_len,
                'sq_occ': sq_occ}
    
    # Print a board (this is just to improve QOL when I'm debugging)
    def display_board_2d(self):
        self._board_2d = self._board.reshape(6,6)
        print('-------------------------')
        for row in self._board_2d:
            print('|',end = '')
            print(*(' ' + str(int(i)) + ' ' if i > -1 else ' r ' for i in row),end = '')
            print('|',end = '\n')
        print('-------------------------')


    # Change the indices of a car based on a move object
    def hyp_move(self,move_obj):
        id,move = move_obj.unpack()
        car = self._cars[id]
        move_dir = car['orientation']
        sq_occ = car['sq_occ']
        sq_change = move*(move_dir=='horizontal') + move*(move_dir=='vertical')*6

        return sq_occ + sq_change
    
    def sqs_passed(self,move_obj):
        id,move = move_obj.unpack()
        car = self._cars[id]
        move_dir = car['orientation']
        sq_occ = car['sq_occ']
        new_occ = self.hyp_move(move_obj)
        temp = np.concatenate((sq_occ,new_occ))
        d1_dir = ((move_dir =='horizontal') + (move_dir == 'vertical')*6)
        sqs_passed = np.arange(np.min(temp),np.max(temp)+d1_dir,d1_dir)
        return sqs_passed
    
    # Check whether a move is legal, return one of three states
    def check_legal(self,move_obj):
        id,move = move_obj.unpack()
        car = self._cars[id]
        move_dir = car['orientation']
        sq_occ = car['sq_occ']
        legal = True
        sqs_passed = self.sqs_passed(move_obj)
        if move_dir != car['orientation']:
            #print('Illegal - car orientation and move direction conflict')
            legal = False
        if move_dir == 'horizontal' and np.any(sqs_passed // 6 != sq_occ[0] // 6):
            #print('Illegal - car went out of bounds')
            legal = False
        elif np.any(sqs_passed < 0) or np.any(sqs_passed > 35):
            #print('Illegal - car went out of bounds')
            legal = False
        elif np.any((self._board[sqs_passed] != 0) == (self._board[sqs_passed] != int(id))):
            legal = 'Blocked'
        return legal
        
    # Check what cars a car is blocked by
    def blocked_by(self,move_obj):
        id,move = move_obj.unpack()
        car = self._cars[id]
        move_dir = car['orientation']
        sq_occ = car['sq_occ']
        blocked = self.check_legal(move_obj)
        if blocked == 'Blocked':
            sqs_passed = self.sqs_passed(move_obj)
            if np.any((self._board[sqs_passed] != 0) == (self._board[sqs_passed] != int(id))):
                blocked_cars_id = np.unique(self._board[sqs_passed][(self._board[sqs_passed] != 0) == (self._board[sqs_passed] != int(id))])
                temp_board = self.get_board().copy()
                temp_board[sqs_passed] = int(id)
                blocked_spaces_list = []
                for blocked_car in blocked_cars_id:
                    goal_car_mask = (temp_board == int(id))
                    blocked_car_mask = (self.get_board() == int(float(blocked_car)))
                    mask = np.logical_and(goal_car_mask,blocked_car_mask)
                    overlapping_sqs = np.argwhere(mask).flatten()
                    blocked_spaces_list.append(overlapping_sqs)

                ids_as_str = [str(i) for i in blocked_cars_id]
                
                return list(zip(ids_as_str,blocked_spaces_list))
            else:
                return None
    
    # Make a move
    def make_move(self,move_obj):
        id,move = move_obj.unpack()
        car = self._cars[id]
        sq_occ = car['sq_occ']
        legal = self.check_legal(move_obj)
        if legal == True:
            new_occ = self.hyp_move(move_obj)
            car['position'] = new_occ[0]
            car['sq_occ'] = new_occ
            self._board[sq_occ] = 0
            self._board[new_occ] = int(id)
            self.history.append(move_obj)
        else:
            return None
            #print('Illegal move - blocked by: ',*(str(int(float(i))) + ' ' for i in self.blocked_by(move_obj)))
    
    # Undo the last move in the problem history
    def undo_move(self):
        if not self.history:
            print('No moves to undo')
        else:
            last_move = self.history[-1]
            id,move_qt = last_move.unpack()
            self.make_move(move(id,-move_qt))
            self.history.pop()
            self.history.pop()
    
    # Get the dict of cars
    def get_cars(self):
        return self._cars
    
    def all_legal_moves(self):
        legal_moves_list = []
        cars_list = list(self._cars.keys())
        for car in cars_list:
            pos = True
            neg = True
            i = 1
            while pos or neg:
                if pos:
                    potential_move = move(car,i)
                    legal = self.check_legal(potential_move)
                    if legal == True:
                        legal_moves_list.append(potential_move)
                    else:
                        pos = False
                if neg:
                    potential_move = move(car,-i)
                    legal = self.check_legal(potential_move)
                    if legal == True:
                        legal_moves_list.append(potential_move)
                    else:
                        neg = False
                i += 1
        return legal_moves_list
    
    def reset_board(self):
        while self.history:
            self.undo_move()

    def get_board(self):
        return self._board

    def unblocking_moves(self,id,squares):
        pos = True
        neg = True
        i = 1
        unblocking_moves_list = [] 
        while pos or neg:
            if pos:
                potential_move = move(id,i)
                legal = self.check_legal(potential_move)
                if (legal != False):
                    new_occ = self.hyp_move(potential_move)
                    if not np.any(np.isin(new_occ,squares)):
                        unblocking_moves_list.append(potential_move)
                else:
                    pos = False
            if neg:
                potential_move = move(id,-i)
                legal = self.check_legal(potential_move)
                if (legal != False):
                    new_occ = self.hyp_move(potential_move)
                    if not np.any(np.isin(new_occ,squares)):
                        unblocking_moves_list.append(potential_move)
                else:
                    neg = False
            i += 1

        return unblocking_moves_list

