# -*- coding: utf-8 -*-
"""
Created on Fri Jun  7 11:11:55 2024

@author: Denny Krempin
"""
import json
import pandas as pd


gazepathlist = []
pos1 = []
pos2 = []
pos3 = []
pos4 = []
pos5 = []
dur1 = []
dur2 = []
dur3 = []
dur4 = []
dur5 = []
pathtype = []
pos1tupel= []
pos2tupel= []
pos3tupel= []
pos4tupel= []
pos5tupel= []
fix1 = []
fix2 = []
fix3 = []
fix4 = []
fix5 = []




pathtype = pd.read_csv("type.csv", dtype=str)
pathtype = pathtype.values.tolist()

pos1 = pd.read_csv("pos1.csv", dtype=float)
pos1 = pos1.values.tolist()
for i in range(len(pos1)):
    pos1tupel.append((pos1[i][0],pos1[i][1]))
    
pos2 = pd.read_csv("pos2.csv", dtype=float)
pos2 = pos2.values.tolist()
for i in range(len(pos1)):
    pos2tupel.append((pos2[i][0],pos2[i][1]))
    
pos3 = pd.read_csv("pos3.csv", dtype=float)
pos3 = pos3.values.tolist()
for i in range(len(pos1)):
    pos3tupel.append((pos3[i][0],pos3[i][1]))
    
pos4 = pd.read_csv("pos4.csv", dtype=float)
pos4 = pos4.values.tolist()
for i in range(len(pos1)):
    pos4tupel.append((pos4[i][0],pos4[i][1]))
    
pos5 = pd.read_csv("pos5.csv", dtype=float)
pos5 = pos5.values.tolist()
for i in range(len(pos1)):
    pos5tupel.append((pos5[i][0],pos5[i][1]))
    
    
    
dur1 = pd.read_csv("dur1.csv", dtype=float)
dur1 = dur1.values.tolist()

dur2 = pd.read_csv("dur2.csv", dtype=float)
dur2 = dur2.values.tolist()

dur3 = pd.read_csv("dur3.csv", dtype=float)
dur3 = dur3.values.tolist()

dur4 = pd.read_csv("dur4.csv", dtype=float)
dur4 = dur4.values.tolist()

dur5 = pd.read_csv("dur5.csv", dtype=float)
dur5 = dur5.values.tolist()



temp = []

for i in range(len(pos1)):
    temp = []
    temp.append(pos1tupel[i])
    fix1.append(temp + dur1[i])
for i in range(len(pos1)):
    temp = []
    temp.append(pos2tupel[i])
    fix2.append(temp + dur2[i])
for i in range(len(pos1)):
    temp = []
    temp.append(pos3tupel[i])
    fix3.append(temp + dur3[i])
for i in range(len(pos1)):
    temp = []
    temp.append(pos4tupel[i])
    fix4.append(temp + dur4[i])
for i in range(len(pos1)):
    temp = []
    temp.append(pos5tupel[i])
    fix5.append(temp + dur5[i])
    

for i in range(len(pos1)):
    temp = []
    temp.append(pathtype[i])
    temp.append(fix1[i])
    temp.append(fix2[i])
    temp.append(fix3[i])
    temp.append(fix4[i])
    temp.append(fix5[i])
    gazepathlist.append(temp)

with open("gazepathlist.json", "w") as fp:
        json.dump(gazepathlist, fp)
        
    

