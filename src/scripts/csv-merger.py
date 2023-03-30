#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
@File    :   csv-merger.py
@Time    :   2023/03/30 20:58:40
@Author  :   Patricia Hernando Fernández 
@Version :   1.0
@Contact :   phf1001@alu.ubu.es
'''

import os
import glob
import pandas as pd

actual_directory = os.getcwd()
os.chdir(os.path.join(actual_directory, 'training-sets'))

file_out = 'train-merged.csv'

extension = 'csv'
all_files = list(glob.glob(f'*.{extension}'))
merged = pd.concat([pd.read_csv(f) for f in all_files])
merged.to_csv(file_out, index=False, encoding='utf-8-sig')
