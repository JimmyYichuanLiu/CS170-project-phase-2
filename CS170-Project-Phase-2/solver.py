#!/user/bin/bash
#-*- coding:utf-8 -*-

import os
import sys
import numpy as np
import time
sys.path.append('..')
sys.path.append('../..')
import argparse
import utils
import GeneticAlgorithm
from student_utils import *

MAX_VALUE = int(1e8)

"""
  convert adjacency_matrix of list type with alphabet to numpy array 
  type,for the convenience of computation.
"""
def data_format_convert(adjacency_matrix_alpha_bet):
    n=len(adjacency_matrix_alpha_bet)
    adjacency_matrix_numpy_arr=np.zeros([n,n],dtype=np.float32)
    for i in range(n):
        for j in range(n):
            if i!=j:
                if adjacency_matrix_alpha_bet[i][j]=='x':
                    adjacency_matrix_numpy_arr[i,j]=MAX_VALUE           # take 1e8 as inf
                else:
                    adjacency_matrix_numpy_arr[i,j]=adjacency_matrix_alpha_bet[i][j]
    return adjacency_matrix_numpy_arr

"""
    get distance_matrix from adjacency_matrix with Floyd Algorithm
"""
def Floyd(adjacency_matrix):
    n=adjacency_matrix.shape[0]
    #distance_matrix=np.zeros_like(adjacency_matrix, dtype=np.float32)
    for k in range(n):
        for i in range(n):
            for j in range(n):
                select=MAX_VALUE if adjacency_matrix[i][k]==MAX_VALUE or adjacency_matrix[k][j]==MAX_VALUE  else (adjacency_matrix[i][k]+adjacency_matrix[k][j])
                if adjacency_matrix[i,j]>select:
                    adjacency_matrix[i,j]=select
    return adjacency_matrix


def DropOffs(distance_matrix,list_of_homes,locations_dict_inverse,path_best):
    """
        get drops_offs of TAs for best car_path 
    """
    drop_offs=[]
    for home in list_of_homes:
        home_idx=locations_dict_inverse[home]
        drop_off={'distance':MAX_VALUE,'drop_off':locations_dict_inverse[path_best[0]]}    # drop off at car_starting)location by default
        for point in path_best:
            if distance_matrix[home_idx,point]<drop_off['distance']:
                drop_off['distance']=distance_matrix[home_idx,point]
                drop_off['drop_off']=locations_dict_inverse[point]
        drop_offs.append(drop_off['drop_off'])
    return drop_offs

def NoDrivingEnergy(distance_matrix,list_of_homes,locations_dict_inverse,starting_car_location):
    start_idx=locations_dict_inverse[starting_car_location]
    energy=0
    for home in list_of_homes:
        home_idx=locations_dict_inverse[home]
        energy+=distance_matrix[start_idx,home_idx]
    return energy
        
   
def solve(list_of_locations, list_of_homes, starting_car_location, adjacency_matrix, params=[]):
    """
    Write your algorithm here.
    Input:
        list_of_locations: A list of locations such that node i of the graph corresponds to name at index i of the list
        list_of_homes: A list of homes
        starting_car_location: The name of the starting location for the car
        adjacency_matrix: The adjacency matrix from the input file
    Output:
        A list of locations representing the car path
        A dictionary mapping drop-off location to a list of homes of TAs that got off at that particular location
        NOTE: both outputs should be in terms of indices not the names of the locations themselves
    """
    n=len(list_of_locations)
    adjacency_matrix_numpy_arr= data_format_convert(adjacency_matrix)
    distance_matrix=Floyd(adjacency_matrix_numpy_arr)
    
    locations_dict={}          # key: index(int), value: location name(other types)
    for i in range(n):
        locations_dict[i]=list_of_locations[i]
    locations_dict_inverse={v:k for k,v in locations_dict.items()}      # k:v = location:index
     
    
    # no driving
    car_path=[], 
    drop_offs=[starting_car_location]
    energy=NoDrivingEnergy(distance_matrix,list_of_homes,locations_dict_inverse,starting_car_location)
    print('    energy cost when no driving is ', energy)
 
    for i in range(1,n):
        print('    processing for middle point = ',i,end=" ")
        start_t=time.time()
        path_best,energy_best=GeneticAlgorithm.GA(distance_matrix, locations_dict_inverse,
                                    list_of_homes, starting_car_location, i)
        if energy_best<energy:
            car_path=path_best
            energy=energy_best
        
        print(', current minimum energy cost is ',energy,", time elapsed with ", time.time()-start_t,"s")
     
    drop_offs=DropOffs(distance_matrix, list_of_homes, locations_dict_inverse, car_path)  
    car_path=[locations_dict_inverse[loc] for loc in car_path]  
     
    print('    Eventually: car_path  ',car_path)
    print('                drop_offs ',drop_offs)
    print('                energy    ',energy)
    return car_path,drop_offs

"""
Convert solution with path and dropoff_mapping in terms of indices
and write solution output in terms of names to path_to_file + file_number + '.out'
"""
def convertToFile(path, dropoff_mapping, path_to_file, list_locs):
    string = ''
    for node in path:
        string += list_locs[node] + ' '
    string = string.strip()
    string += '\n'

    dropoffNumber = len(dropoff_mapping.keys())
    string += str(dropoffNumber) + '\n'
    for dropoff in dropoff_mapping.keys():
        strDrop = list_locs[dropoff] + ' '
        for node in dropoff_mapping[dropoff]:
            strDrop += list_locs[node] + ' '
        strDrop = strDrop.strip()
        strDrop += '\n'
        string += strDrop
    utils.write_to_file(path_to_file, string)

def solve_from_file(input_file, output_directory, params=[]):
    print('Processing', input_file)

    input_data = utils.read_file(input_file)
    num_of_locations, num_houses, list_locations, list_houses, starting_car_location, adjacency_matrix = data_parser(input_data)
    #print(list_locations)

    car_path, drop_offs = solve(list_locations, list_houses, starting_car_location, adjacency_matrix, params=params)
 
    basename, filename = os.path.split(input_file)
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    output_file = utils.input_to_output(input_file, output_directory)
 
    convertToFile(car_path, drop_offs, output_file, list_locations)


def solve_all(input_directory, output_directory, params=[]):
    input_files = utils.get_files_with_extension(input_directory, 'in')

    for input_file in input_files:
        solve_from_file(input_file, output_directory, params=params)
        
 
if __name__=="__main__":
    parser = argparse.ArgumentParser(description='Parsing arguments')
    parser.add_argument('--all', action='store_true', help='If specified, the solver is run on all files in the input directory. Else, it is run on just the given input file')
    parser.add_argument('input', type=str, help='The path to the input file or directory')
    parser.add_argument('output_directory', type=str, nargs='?', default='.', help='The path to the directory where the output should be written')
    parser.add_argument('params', nargs=argparse.REMAINDER, help='Extra arguments passed in')
    args = parser.parse_args()
    output_directory = args.output_directory
    if args.all:
        input_directory = args.input
        solve_all(input_directory, output_directory, params=args.params)
    else:
        input_file = args.input
        solve_from_file(input_file, output_directory, params=args.params)