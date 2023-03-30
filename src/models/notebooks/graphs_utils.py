#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
@File    :   graphs_utils.py
@Time    :   2023/03/30 20:54:37
@Author  :   Patricia Hernando Fernández 
@Version :   1.0
@Contact :   phf1001@alu.ubu.es
'''

import numpy as np
import csv
import pandas as pd


def append_to_csv(file, array):
    """Appends an array to a csv file"""
    if '.csv' in file:
        with open(file, 'a') as f:
            np.savetxt(f, array, fmt='%1.3f', newline=",")
            f.write("\n")
            f.close()

    else:
        raise Exception("File must be a csv file")


def read_irregular_csv(file):
    """
    Reads an irregular csv file and
    returns a list of lists
    """
    if '.csv' in file:
        data = []

        with open(file) as csv_file:
            for row in csv.reader(csv_file):
                data.append([float(x) for x in row if x != ""])
            csv_file.close()

        return data

    raise Exception("File must be a csv file")


def create_graph_matrix(file):
    """
    Creates a matrix from an
    irregular csv file
    """
    m = []
    l = read_irregular_csv(file)
    max_iters = max([[len(x)] for x in l])[0]

    for individual_list in l:
        individual_list = np.array(individual_list)
        new = np.ones(shape=(max_iters)) * individual_list[-1]
        i = np.arange(0, individual_list.shape[0])
        new[i] = individual_list[i]
        m.append(new)

    return np.array(m)


def extract_training_data(csv_file):
    """
    Extracts the training data from
    a csv file
    """
    df = pd.read_csv(csv_file)

    caract_cols = df.columns
    X_y_all = df[caract_cols].values 

    L = X_y_all[X_y_all[:, -1] != -1]
    U = X_y_all[X_y_all[:, -1] == -1]

    L_tags = L[:, -1]
    L = L[:, :-1]
    U = U[:, :-1]

    return L, L_tags, U


def extract_test_data(csv_file):
    """Extracts the test data from a csv file"""
    df = pd.read_csv(csv_file)

    caract_cols = df.columns
    X_y_all = df[caract_cols].values 

    y = X_y_all[:, -1]
    X = X_y_all[:, :-1]

    return X, y
