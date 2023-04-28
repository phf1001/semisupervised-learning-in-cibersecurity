#!/usr/bin/env python
# -*-coding:utf-8 -*-
"""
@File    :   utils.py
@Time    :   2023/03/30 20:52:13
@Author  :   Patricia Hernando Fernández 
@Version :   1.0
@Contact :   phf1001@alu.ubu.es
"""
# Statmodels commented since it's giving problems with Heroku
# from statsmodels.stats.proportion import proportion_confint
from math import sqrt
from scipy import stats


def confidence_interval(cls, L, y):
    """
    Returns the confidence interval  for the classifier cls given a set
    of labeled data L and the labels y.

    Args:
        cls (object): classifier
        L (np.array): labeled data
        y (np.array): labels

    Returns:
        tuple: confidence interval
    """
    return confidence_interval_method_1(cls, L, y)


def confidence_interval_method_1(cls, L, y):
    """
    Returns the confidence interval  for the classifier cls given a set
    of labeled data L and the labels y.

    Suggested by César Ignacio García Osorio.

    Args:
        cls (object): classifier
        L (np.array): labeled data
        y (np.array): labels

    Returns:
        tuple: confidence interval
    """
    cte = stats.norm.isf(0.05 / 2.0)
    y_pred = cls.predict(L)
    n_total = len(y)
    n_hits = (y_pred == y).sum()
    p_hat = n_hits / n_total
    margin = cte * sqrt(p_hat * (1 - p_hat) / n_total)

    return (p_hat - margin, p_hat + margin)


def confidence_interval_method_2(cls, L, y):
    """
    Returns the confidence interval  for the classifier cls given a set
    of labeled data L and the labels y.

    Suggested by Álvar Arnaiz González.

    Args:
        cls (object): classifier
        L (np.array): labeled data
        y (np.array): labels

    Returns:
        tuple: confidence interval
    """
    y_pred = cls.predict(L)
    n_total = len(y)
    n_hits = (y_pred == y).sum()
    cte = stats.norm.isf(0.05 / 2.0)

    zSq = cte**2
    f = n_hits / n_total

    left = f + (zSq / (2 * n_total))
    div = 1 + (zSq / n_total)
    sq = cte * sqrt(
        (f / n_total) - ((f * f) / n_total) + (zSq / (4 * n_total**2))
    )

    return ((left - sq) / div, (left + sq) / div)


# def confidence_interval_method_3(cls, L, y):
#     """
#     Returns the confidence interval  for the classifier cls given a set
#     of labeled data L and the labels y.

#     Commented because it's giving problems with Heroku.

#     Suggested by José Luis Garrido Labrador.

#     Args:
#         cls (object): classifier
#         L (np.array): labeled data
#         y (np.array): labels

#     Returns:
#         tuple: confidence interval
#     """
#     y_pred = cls.predict(L)
#     n_total = len(y)
#     n_hits = (y_pred == y).sum()

#     li, hi = proportion_confint(n_hits, n_total, alpha=0.05, method="wilson")
#     return li, hi
#     return 0, 0
