from statsmodels.stats.proportion import proportion_confint
from math import sqrt
from scipy import stats

def confidence_interval(cls, L, y):
    return self_confidence_interval_joselu(cls, L, y)

def confidence_interval_cesar(cls, L, y):

    cte = stats.norm.isf(0.05 / 2.)
    y_pred = cls.predict(L)
    n_total = len(y)
    n_hits = (y_pred == y).sum()
    p_hat = n_hits / n_total
    margin = cte * sqrt(p_hat * (1 - p_hat) / n_total)

    return (p_hat - margin, p_hat + margin)


def confidence_interval_alvar(cls, L, y):

    y_pred = cls.predict(L)
    n_total = len(y)
    n_hits = (y_pred == y).sum()
    cte = stats.norm.isf(0.05 / 2.)

    zSq = cte ** 2
    f = n_hits / n_total

    left = f + (zSq / (2 * n_total))
    div = 1 + (zSq / n_total)
    sq = cte * sqrt((f / n_total) -
                     ((f * f) / n_total) + (zSq / (4 * n_total ** 2)))

    return ((left - sq) / div, (left + sq) / div)


def self_confidence_interval_joselu(cls, L, y):

    y_pred = cls.predict(L)
    n_total = len(y)
    n_hits = (y_pred == y).sum()

    li, hi = proportion_confint(
        n_hits, n_total, alpha=0.05, method="wilson")
    return li, hi
