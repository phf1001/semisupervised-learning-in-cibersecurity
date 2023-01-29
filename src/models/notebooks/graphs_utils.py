import numpy as np
import csv
import pandas as pd

def append_to_csv(file, array):
    f = open( file, 'a')
    np.savetxt(f, array, fmt='%1.3f', newline=",")
    f.write("\n")
    f.close()


def read_irregular_csv(file):

    data = []

    with open(file) as csv_file:
        
        for row in csv.reader(csv_file):
            data.append([float(x) for x in row if x != ""])
        csv_file.close()

    return data

def create_graph_matrix(file):

    m = []
    l = read_irregular_csv(file)
    max_iters = max([[len(x)] for x in l])[0]

    for list in l:
        list = np.array(list)
        new = np.ones(shape = (max_iters)) * list[-1]
        i = np.arange(0, list.shape[0])
        new[i] = list[i]
        m.append(new)

    return np.array(m)


def extract_training_data(csv):

    df = pd.read_csv(csv)

    caract_cols = df.columns
    X_y_all = df[caract_cols].values 

    L = X_y_all[X_y_all[:, -1] != -1]
    U = X_y_all[X_y_all[:, -1] == -1]

    L_tags = L[:, -1]
    L = L[:, :-1]
    U = U[:, :-1]

    return L, L_tags, U


def extract_test_data(csv):

    df = pd.read_csv(csv)

    caract_cols = df.columns
    X_y_all = df[caract_cols].values 

    y = X_y_all[:, -1]
    X = X_y_all[:, :-1]

    return X, y