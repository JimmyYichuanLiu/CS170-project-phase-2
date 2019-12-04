#!/user/bin/bash
#-*- coding:utf-8 -*-

import numpy as np
import math
import random
from goto import goto


MAX_VALUE = int(1e8)

P=0.7     # Probability of variation
PR=0.7    # Probability of reproduction

def CalculateEnergy(distance_matrix,list_of_homes,locations_dict_inverse,drving_path):
    """
    Func: compute the minimum total distance under the drving path "path_best"
    """
    list_of_homes_idx=[]
    for home in list_of_homes:
        list_of_homes_idx.append(locations_dict_inverse[home])
    total_energy=0
    
    # energy of the car cost
    for i in range(len(drving_path)-1):
        total_energy+=2/3*distance_matrix[i,i+1]
        
    # energy of TAs cost for going home
    for home_idx in list_of_homes_idx:
        min_energy=MAX_VALUE;
        for j in range(len(drving_path)-1):
            if distance_matrix[home_idx,j]<min_energy:
                min_energy=distance_matrix[home_idx,j]
        total_energy+=min_energy
    return total_energy


@goto        
def Variation(r1,r2,inmid_points):
    label .begin
    a=np.random.randint(1,inmid_points+1,2)
    l=np.min(a)
    m=np.max(a)
    
    if l==m:
        goto .begin
    
    # Fragment exchange
    for k in range(l,m+1):
        temp=r1[k]
        r1[k]=r2[k]
        r2[k]=temp
    if(not IsValidGroup(r1) or not IsValidGroup(r2)):
        goto .begin
    
    # Self variation
    if np.random.rand()>P:
        a=random.sample(range(1,inmid_points+1),2)
        s=r1[a[0]]
        r1[a[0]]=r1[a[1]]
        r1[a[1]]=s
        
    if np.random.rand()>P:
        a=random.sample(range(1,inmid_points+1),2)
        s=r2[a[0]]
        r2[a[0]]=r2[a[1]]
        r2[a[1]]=s
    
    if(not IsValidGroup(r1) or not IsValidGroup(r2)):
        goto .begin
    
    return r1,r2

def InheritanceImpl(res,list_of_homes,locations_dict_inverse,distance_matrix,M,inmid_points,NUM):
    groups=res[0:M,0:inmid_points+1]
    energy=res[0:M,inmid_points+1]
    llist=np.random.permutation(np.arange(M))
    for i in range(0,M-1,2):
        groups[llist[i]],groups[llist[i+1]]=Variation(groups[llist[i]], groups[llist[i+1]], inmid_points)
        energy[i]=CalculateEnergy(distance_matrix, list_of_homes, locations_dict_inverse, groups[i])
        energy[i+1]=CalculateEnergy(distance_matrix, list_of_homes, locations_dict_inverse, groups[i+1])
    R=np.append(groups, energy, axis=1)    
    R=np.append(res,R,axis=0)
    R=R[np.argsort(R[:,inmid_points+1])]
    return R[0:M]


def IsValidGroup(group):
    for i in range(len(group)-1):
        if group[i]==group[i+1]:
            return False
    return True

def GA(adjacency_matrix,distance_matrix,locations_dict,list_of_locations,locations_dict_inverse,list_of_homes,starting_car_location,inmid_points):
    """
    Input:
        adjacency_matrix          The adjacency matrix 
        distance_matrix           The shortest of the adjacency matrix  by Floyd algorithm
        locations_dict            The dictionay of number and location name
        list_of_locations         A list of locations such that node i of the graph corresponds to name at index i of the list
        locations_dict_inverse    k,v inverse for list_of_locations
        list_of_homes             A list of homes
        starting_car_location     The name of the starting location for the car
        inmid_points              Number of intermediate points, possible values 0:(n-1)
    Output:
        
    """
    n=distance_matrix.shape[0]
    NUM=20*inmid_points                                      # Number of population
    GEN=20*inmid_points                                      # Number of reproduction
    groups=np.zeros([NUM,inmid_points+2],dtype=np.float32)   # +2 means take the starting_car_location as the fisrt and the end 
    energy=np.zeros([NUM,1],dtype=np.float32)
    
    
    # generating the initial group
    for i in range(NUM):
        group=np.random.randint(0,n,inmid_points+2)
        group[0]=group[-1]=locations_dict_inverse[starting_car_location]
        while(IsValidGroup(group==False)):
            group=np.random.randint(0,n,inmid_points+2)
            group[0]=group[-1]=locations_dict_inverse[starting_car_location]
        groups[i]=group
        energy[i]=CalculateEnergy(distance_matrix, list_of_homes, locations_dict_inverse, group)    
    res=np.append(groups, energy, axis=1)
    res=res[np.argsort(res[:,inmid_points+1])]
    path_best=res[0,0:inmid_points+1]
    energy_best=res[0,inmid_points+1]
    M=math.floor(NUM*PR)
    
    # Perform hybrid operation
    for i in range(GEN):
        res=InheritanceImpl(res, list_of_homes,locations_dict_inverse,distance_matrix, M, inmid_points, NUM)
        path_best=res[0,0:inmid_points+1]
        energy_best=res[0,inmid_points+1]
    
    # output result
    return path_best,energy_best
    
    
    
    
    
    

    
    
    
    
