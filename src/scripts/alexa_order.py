#!/usr/bin/env python
# -*-coding:utf-8 -*-
"""
@File    :   alexa_order.py
@Time    :   2023/03/30 20:58:27
@Author  :   Patricia Hernando Fernández 
@Version :   2.0
@Contact :   phf1001@alu.ubu.es
"""

from difflib import SequenceMatcher
import os
import sys
import csv
import pandas as pd

src_path = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
sys.path.append(src_path)

from phishing_fvg.phishing_utils import (
    get_alexa_sites,
    get_data_path,
    get_csv_data,
)

ordered_list = get_csv_data(get_data_path() + os.sep + "alexa_top_10k.csv")
# Change the flag to True if you want to use the genuine_pd.csv file
from_file = False


if from_file:
    set_alexa = pd.read_csv("genuine_pd.csv", delimiter=";")
else:
    set_alexa = get_alexa_sites()

ordered_working = []

for element in ordered_list:
    max_similarity = 0
    item = None

    for index, row in set_alexa.iterrows():
        element_2 = row["url"]
        new_similarity = SequenceMatcher(None, element, element_2).ratio()

        if new_similarity > max_similarity:
            item = row
            max_similarity = new_similarity

    ordered_working.append([item["url"], item["fv"], item["tag"]])

    if len(ordered_working) == len(set_alexa):
        break


output_file = get_data_path() + os.path.sep + "alexa_ordered_working_urls.csv"
with open(output_file, mode="w") as f:
    writer = csv.writer(
        f, delimiter=";", quotechar='"', quoting=csv.QUOTE_MINIMAL
    )

    for url in ordered_working:
        writer.writerow(url)

f.close()
