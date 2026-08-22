import numpy as np
from matplotlib import pyplot as pyplot
from numpy import random as random

from misc import move, isvert, hyp_move
from rush_hour import problem

import pickle

def make_legal_move(board_arr,move_obj):
    amended_board = board_arr.copy()
    id,move = move_obj.unpack()
    id = int(id)
    sq_occ = np.flatnonzero(board_arr == id)
    vert = isvert(sq_occ)
    sq_change = hyp_move(vert,move)
    new_occ = sq_occ + sq_change
    amended_board[sq_occ] = 0
    amended_board[new_occ] = int(id)
    return amended_board

def all_legal_moves_list(board_arr):
    legal_moves_list = []
    cars_list = np.unique(board_arr)
    cars_list = cars_list[cars_list!=0]
    board_as_list = list(board_arr)
    for car in cars_list:
        id = str(int(car))
        sq_occ = list(i for i,x in enumerate(board_as_list) if x == car)
        vert = isvert(sq_occ)
        if vert:
            row_mask = range(sq_occ[0] % 6,36,6)
        else:
            row_mask = range(6*(sq_occ[0] // 6),6*(sq_occ[0] // 6) + 6)
        row_slice = list(board_arr[i] for i in row_mask)
        car_mask = list(True if i == car else False for i in row_slice)
        car_loc = row_slice.index(car)
        other_mask = list(False if (i==car) or (i==0) else True for i in row_slice)
        car_len = sum(car_mask)
        left_manipulated_row = (other_mask[:car_loc])[::-1]
        left_manipulated_row.append(True)
        right_manipulated_row = other_mask[car_loc+car_len:]
        right_manipulated_row.append(True)
        num_left = left_manipulated_row.index(max(left_manipulated_row))
        num_right = right_manipulated_row.index(max(right_manipulated_row))
        dists_left = list(-a for a in range(0,num_left+1))
        dists_right = list(a for a in range(0,num_right+1))
        dists = dists_left+dists_right
        legal_moves_list = legal_moves_list + list(move(id,dist) for dist in dists)

    return legal_moves_list


def bfs(board_arr,get_goal_states = False):
    
    def propose(next_board_str,prev_board_str):
        if next_board_str not in pred_map:
            pred_map[next_board_str] = prev_board_str
            Q.append(next_board_str)

    def isGoal(board_arr):
        return (np.flatnonzero(board_arr == -1)[0] % 6) == 4

    def explore(board_arr):
        legal_moves = all_legal_moves_list(board_arr)
        for legal_move in legal_moves:
            new_board_state = make_legal_move(board_arr,legal_move)
            new_board_state_as_key = tuple(new_board_state)
            propose(new_board_state_as_key,board_arr)

    def get_dist_to_root(board_key):
        prev = pred_map[board_key]
        if type(prev) == np.ndarray:
            prev = tuple(prev)
        step = 0 if prev == None else get_dist_to_root(prev) + 1
        return step

    Q = []
    pred_map = {}
    goal_states_list = []

    board_arr = tuple(board_arr)
    propose(board_arr,None)
    while Q:
        current = np.array(list(Q.pop(0)),dtype = int)
        if isGoal(current):
            curr_as_key = tuple(current)
            if get_goal_states:
                goal_states_list.append(curr_as_key)
            else:
                break
        explore(current)
    if get_goal_states:
        return goal_states_list
    else:
        return get_dist_to_root(curr_as_key),curr_as_key,pred_map

def alm_no_goal_car(board_arr):
    legal_moves_list = []
    cars_list = np.unique(board_arr)
    cars_list = cars_list[cars_list!= 0]
    cars_list = cars_list[cars_list!= -1]
    board_as_list = list(board_arr)
    for car in cars_list:
        id = str(int(car))
        sq_occ = list(i for i,x in enumerate(board_as_list) if x == car)
        vert = isvert(sq_occ)
        if vert:
            row_mask = range(sq_occ[0] % 6,36,6)
        else:
            row_mask = range(6*(sq_occ[0] // 6),6*(sq_occ[0] // 6) + 6)
        row_slice = list(board_arr[i] for i in row_mask)
        car_mask = list(True if i == car else False for i in row_slice)
        car_loc = row_slice.index(car)
        other_mask = list(False if (i==car) or (i==0) else True for i in row_slice)
        car_len = sum(car_mask)
        left_manipulated_row = (other_mask[:car_loc])[::-1]
        left_manipulated_row.append(True)
        right_manipulated_row = other_mask[car_loc+car_len:]
        right_manipulated_row.append(True)
        num_left = left_manipulated_row.index(max(left_manipulated_row))
        num_right = right_manipulated_row.index(max(right_manipulated_row))
        dists_left = list(-a for a in range(0,num_left+1))
        dists_right = list(a for a in range(0,num_right+1))
        dists = dists_left+dists_right
        legal_moves_list = legal_moves_list + list(move(id,dist) for dist in dists)

    return legal_moves_list

def d_goal(board_arr):
    def propose(next_board_str,prev_board_str):
        if next_board_str not in pred_map:
            pred_map[next_board_str] = prev_board_str
            Q.append(next_board_str)

    def explore(board_arr):
        legal_moves = all_legal_moves_list(board_arr)
        curr_board_as_val = tuple(board_arr)
        for legal_move in legal_moves:
            new_board_state = make_legal_move(board_arr,legal_move)
            new_board_state_as_key = tuple(new_board_state)
            propose(new_board_state_as_key,curr_board_as_val)

    '''def get_dist_to_root(board_key):
        prev = pred_map[board_key]
        step = 0 if prev == None else get_dist_to_root(prev) + 1
        return step'''

    Q = []
    pred_map = {}

    goal_states_list = bfs(board_arr,get_goal_states=True)
    for goal_state in goal_states_list:
        propose(goal_state,None)
    
    while Q:
        current = np.array(list(Q.pop(0)),dtype = int)
        explore(current)
    return pred_map

def get_dist_to_root(map,board_key):
    prev = map[board_key]
    if type(prev) == np.ndarray:
        prev = tuple(prev)
    step = 0 if prev == None else get_dist_to_root(map,prev) + 1
    return step

if __name__ == '__main__':
    with open('../Data/my_processed_data/problem_list.pkl', 'rb') as g:
        problem_list = pickle.load(g)
    d_goals_dict = {}
    for problem_name in problem_list.keys():
        curr_problem = problem_list[problem_name]
        curr_board = curr_problem.get_board()
        curr_map = d_goal(curr_board)
        d_goals_dict[problem_name] = curr_map
    with open('../Data/my_processed_data/all_board_states_dict.pkl', 'wb') as f:
        pickle.dump(d_goals_dict,f)
