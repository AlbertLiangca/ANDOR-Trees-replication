import numpy as np
import cProfile
import pandas as pd
import json
import os
from rush_hour import problem
import copy
import itertools

import multiprocessing
from multiprocessing import Pool, cpu_count,Queue

import time

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

make_move_obj_scalar = lambda a,b : move(a,b)
make_move_obj = np.frompyfunc(make_move_obj_scalar,2,1)

# Check for verticality
def isvert(sq_occ):
    return sq_occ[1] - sq_occ[0] == 6

# Return the square change given vertical or horizontal
def hyp_move_arr(vert,move):
    sq_change = move*(not vert) + move*(vert)*6
    return sq_change


# Push car some number of blocks based on the move_object given
def make_legal_move(board_arr,move_obj):
    amended_board = board_arr.copy()
    id,move = move_obj.unpack()
    id = int(id)
    sq_occ = np.flatnonzero(board_arr == id)
    vert = isvert(sq_occ)
    sq_change = hyp_move_arr(vert,move)
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

def bfs(board_arr):
    
    def propose(next_board_str,prev_board_str):
        if next_board_str not in pred_map:
            pred_map[next_board_str] = prev_board_str
            Q.append(next_board_str)

    def isGoal(board_arr):
        return (np.flatnonzero(board_arr == -1)[0] % 6) == 4

    def explore(board_arr):
        legal_moves = all_legal_moves_list(board_arr)
        curr_board_as_str = ' '.join(board_arr.astype(str))
        for legal_move in legal_moves:
            new_board_state = make_legal_move(board_arr,legal_move)
            new_board_state_as_str = ' '.join(new_board_state.astype(str))
            propose(new_board_state_as_str,curr_board_as_str)

    def get_dist_to_root(board_key):
        prev = pred_map[board_key]
        step = 0 if prev == None else get_dist_to_root(prev) + 1
        return step

    Q = []
    pred_map = {}

    board_arr = ' '.join(board_arr.astype(int).astype(str))
    propose(board_arr,None)
    while Q:
        current = np.array(Q.pop(0).split(),dtype = int)
        if isGoal(current):
            curr_as_key = ' '.join(current.astype(str))
            break
        explore(current)
    return get_dist_to_root(curr_as_key), curr_as_key,pred_map


#-----Get distances for a solve instance, a particular participant, or a whole CSV-----#
def get_dists(problem_in,solve_inst):
    problem_in.reset_board()
    dist_list = np.array([])
    for index, row in solve_inst.iterrows():
        board = problem_in.get_board()
        if row['event'] in ['start','restart']:
            problem_in.reset_board()
            dist,key,pred_map = bfs(board)
            dist_list = np.append(dist_list,dist)
        elif row['event'] == 'move':
            played_move = move(row['p_as_str'],row['dist'])
            assert problem_in.check_legal(played_move) == True
            problem_in.make_move(played_move)
            dist,key,pred_map = bfs(board)
            dist_list = np.append(dist_list,dist)
        else:
            dist_list = np.append(dist_list,-1)
    return dist_list

def batch_get_dists(participant_csv):
    prbs = pd.unique(participant_csv['instance'])
    all_dists = np.array([])
    for prb in prbs:
        curr_inst = participant_csv[participant_csv['instance'] == prb]
        curr_prb = copy.deepcopy(problem_list[prb])
        dists = get_dists(curr_prb,curr_inst)
        all_dists = np.append(all_dists,dists)
    return all_dists

def get_all_dists(processed_data):
    all_dists = np.array([])
    all_subs = pd.unique(processed_data['subject'])
    for sub in all_subs:
        sub_df = processed_data[processed_data['subject'] == sub]
        dists = batch_get_dists(sub_df)
        all_dists = np.append(all_dists,dists)
    return all_dists

if __name__ == '__main__':
    dir_str = '../Data/raw_data/problems'
    directory = os.fsencode(dir_str)
    problem_list = {}
    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        key,extra = filename.split('.')
        unpacked_problem = problem(dir_str + '/' + str(filename))
        problem_list[key] = unpacked_problem

    #-----Importing processed data-----#
    processed_data = pd.read_csv('../Data/my_processed_data/processed_data.csv',dtype={'p_as_str':str,'dist':int})
    processed_data = processed_data.drop(columns = ['Unnamed: 0'])
    all_subs = pd.unique(processed_data['subject'])
    all_prbs = pd.unique(processed_data['instance'])
    s1_sub_df = processed_data[processed_data['subject']==all_subs[0]]
    s1_prb_1 = s1_sub_df[s1_sub_df['instance'] == all_prbs[0]]
    s1_prb_2 = s1_sub_df[s1_sub_df['instance'] == all_prbs[1]]
    mini_ex = pd.concat([s1_prb_1,s1_prb_2])

    s1_dfs = list(s1_sub_df[s1_sub_df['instance'] == prb] for prb in pd.unique(s1_sub_df['instance']))
    s1_prbs = list(problem_list[prb] for prb in pd.unique(s1_sub_df['instance']))

    t0 = time.time()

    with Pool(cpu_count() - 1) as pool:
        s1_dists = pool.starmap(get_dists,zip(s1_prbs,s1_dfs))
    s1_dists = list(itertools.chain(*s1_dists))
    s1_sub_df['dists'] = s1_dists

    t1 = time.time()

    print(t1-t0)