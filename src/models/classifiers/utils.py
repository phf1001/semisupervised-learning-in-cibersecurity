#!/usr/bin/env python
# -*-coding:utf-8 -*-
"""
@File    :   utils.py
@Time    :   2023/03/30 20:52:13
@Author  :   Patricia Hernando Fernández 
@Version :   1.0
@Contact :   phf1001@alu.ubu.es
"""

from statsmodels.stats.proportion import proportion_confint
from math import sqrt
from scipy import stats


def confidence_interval(cls, L, y):
    """
    Returns the confidence interval
    for the classifier cls given a set
    of labeled data L and the labels y.
    """
    return self_confidence_interval_method_3(cls, L, y)


def confidence_interval_method_1(cls, L, y):
    """
    Returns the confidence interval
    for the classifier cls given a set
    of labeled data L and the labels y.
    Suggested by César Ignacio García.
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
    Returns the confidence interval
    for the classifier cls given a set
    of labeled data L and the labels y.
    Suggested by Álvar Arnaiz.
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


def self_confidence_interval_method_3(cls, L, y):
    """
    Returns the confidence interval
    for the classifier cls given a set
    of labeled data L and the labels y.
    Suggested by Jose Luis Garrido.
    """
    y_pred = cls.predict(L)
    n_total = len(y)
    n_hits = (y_pred == y).sum()

    li, hi = proportion_confint(n_hits, n_total, alpha=0.05, method="wilson")
    return li, hi
