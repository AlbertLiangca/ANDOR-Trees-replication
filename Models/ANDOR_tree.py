import numpy as np
from misc import move, make_lambda_func, make_adder, make_reciprocal
import copy
from numpy import random as random

rng = random.default_rng()

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

class ANDOR:
    def __init__(self,
                 problem):
        self._problem = problem
        self._tree = None
    
    def recursive_child_maker(self,in_OR_Child, move, history = []):
        history.append(move)
        AND_Child = AND(move)
        in_OR_Child.set_child(AND_Child)
        blocked_by = self._problem.blocked_by(move)
        for blocked_car in blocked_by:
            bl_id, bl_sq = blocked_car
            bl_id = str(int(float(bl_id)))
            unblocking_moves = self._problem.unblocking_moves(bl_id,bl_sq)
            #print(bl_id,bl_sq)
            #print(*(unblocking_move.display() for unblocking_move in unblocking_moves))
            OR_Child = OR(bl_id)
            AND_Child.set_child(OR_Child)
            for unblocking_move in unblocking_moves:
                if self._problem.check_legal(unblocking_move) != True and (unblocking_move not in history):
                    self.recursive_child_maker(OR_Child,unblocking_move,history)
                if self._problem.check_legal(unblocking_move) == True:
                    leaf_node = AND(unblocking_move)
                    leaf_node.set_leaf()
                    OR_Child.set_child(leaf_node)

    def maketree(self):
        goal_car = self._problem._cars['-1']
        goal_car_pos = goal_car['position']
        winning_move = move('-1',4 - (goal_car_pos % 6))
        self._tree = OR('-1')
        self._tree.set_prob(1)
        if self._problem.check_legal(winning_move) == True:
            AND_node = AND(winning_move)
            AND_node.set_leaf()
            self._tree.set_child(AND_node)
        else:
            self.recursive_child_maker(self._tree,winning_move,history = [])

        self.prune_tree()

        return self._tree
    
    def display_tree(self,node = None,lvl = 0):
        if lvl == 0:
            node = self._tree
        print(' '*lvl + node._display)
        for child in node._children:
            self.display_tree(child,lvl+1)

    def display_probs(self,node = None,lvl = 0):
        if lvl == 0:
            node = self._tree
        
        norm_print_stm = ' '*lvl + str(node._prob)
        if type(node) == OR and node._stop_prob != None:
            norm_print_stm = norm_print_stm + '  (' + str(node._stop_prob) + ')'
        print(norm_print_stm)
        for child in node._children:
            self.display_probs(child,lvl+1)
    
    def display_problem(self):
        self._problem.display_board_2d()

    def reset_board(self):
        self._problem.reset_board()
    
    def prune_tree_in(self, node):
            if node == None:
                pass
            else:
                if type(node) == OR:
                    if not node._children:
                        return False
                    else:
                        child_list_copy = copy.copy(node._children)
                        for child in child_list_copy:
                            if self.prune_tree_in(child) == False:
                                node._children.remove(child)
                        if not node._children:
                            return False
                
                elif type(node) == AND:
                    if not node._children and not node._is_leaf:
                        return False
                    else:
                        child_list_copy = copy.copy(node._children)
                        for child in child_list_copy:
                            if self.prune_tree_in(child) == False:
                                node._children.remove(child)
                        if not node._children and not node._is_leaf:
                            return False

    def prune_tree(self):  
        self.prune_tree_in(self._tree)
                

    def propagate_prob(self,gamma):
        if self._tree == None:
            pass
        else:
            self._tree.set_gamma(gamma)
            self._tree.propagate_prob()
    
    def all_leaves_in(self,node = None, depth = 0):
        if node == None:
            node = self._tree
        if type(node) == AND:
            depth += 1

        if type(node) == AND and node._is_leaf:
            leaf_tuple = [(node,depth)]
            return leaf_tuple
        else:
            curr_set = []
            for child in node._children:
                curr_set = curr_set + self.all_leaves_in(child,depth)
            return curr_set
    
    def all_leaves(self):
        if self._tree == None:
            pass
        else:
            return self.all_leaves_in()
        

    def select_move(self):
        if self._tree == None:
            pass
        if self._tree._stop_prob == None:
            pass
        else:
            all_leaves = self.all_leaves()
            all_leaf_probs = np.array(list(leaf._prob for (leaf,depth) in all_leaves))
            all_leaf_moves = np.array(list(leaf._move for (leaf,depth) in all_leaves))
            tot_stop_prob = (1 - sum(all_leaf_probs))
            tot_stop_prob = np.where(tot_stop_prob < 1e-12, 0,tot_stop_prob)
            legal_moves = np.array(self._problem.all_legal_moves())
            out_tree_moves = np.array(list(move for move in legal_moves if move not in all_leaf_moves))
            num_out_tree = len(out_tree_moves)
            ind_stop_prob = tot_stop_prob / len(legal_moves)
            probs = np.append(all_leaf_probs,np.repeat(0,num_out_tree))
            probs = probs + ind_stop_prob
            probs = probs / probs.sum()
            moves = np.append(all_leaf_moves,out_tree_moves)
            idx = np.where(rng.multinomial(1,probs))
            pick = moves[idx][0]
            return pick


    def simulate_solve(self,gamma):
        self._problem.reset_board()
        goal_car = self._problem._cars['-1']
        goal_car_pos = goal_car['position']
        while (goal_car_pos % 6) != 4:
            self.maketree()
            self.propagate_prob(gamma)
            move = self.select_move()
            self._problem.make_move(move)
            goal_car_pos = goal_car['position']
        history_copy = copy.copy(self._problem.history)
        #self._problem.reset_board()
        return history_copy

    def base_probs(self,solve_instance):
        self._problem.reset_board()
        func_list = np.array([])
        for index, row in solve_instance.iterrows():
            if row['event'] in ['start','restart']:
                self._problem.reset_board()
            elif row['event'] == 'move':
                self.maketree()
                self.propagate_prob(gamma=0)
                all_leaf_tuples = self.all_leaves()
                all_leaves, all_depths = list(zip(*all_leaf_tuples))
                all_depths = np.array(all_depths)
                all_leaf_probs = np.array(list(leaf._prob for leaf in all_leaves))
                all_leaf_moves = np.array(list(leaf._move for leaf in all_leaves))
                played_move = move(row['p_as_str'],row['dist'])
                if self._problem.check_legal(played_move) != True:
                    return ValueError
                all_funcs = list(make_lambda_func(prob,depth) for prob,depth in zip(all_leaf_probs,all_depths))
                if played_move in all_leaf_moves:
                    assoc_probs = all_leaf_probs[all_leaf_moves == played_move]
                    assoc_depths = all_depths[all_leaf_moves == played_move].astype(np.float64)
                    funcs = list(make_lambda_func(a,d) for a,d in zip(assoc_probs,assoc_depths))
                    summed_funcs = make_adder(funcs)
                    func_list = np.append(func_list,summed_funcs)
                else:
                    sum_of_funcs = make_adder(all_funcs)
                    reciprocal = make_reciprocal(sum_of_funcs)
                    func_list = np.append(func_list,reciprocal)
                self._problem.make_move(played_move)
        return func_list

    def dist_to_goal(self):
        if self._tree == None:
            self.maketree()