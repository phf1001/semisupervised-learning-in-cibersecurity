#!/usr/bin/env python
# -*-coding:utf-8 -*-
"""
@File    :   TriTrainingClassifier.py
@Time    :   2023/03/30 20:51:39
@Author  :   Patricia Hernando Fernández 
@Version :   3.0 Inheritance from SSLEnsemble
@Contact :   phf1001@alu.ubu.es
"""

import numpy as np
from math import floor, ceil
import os
import sys

src_path = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
sys.path.append(src_path)
from models.classifiers.SSLEnsembleClassifier import SSLEnsemble


class TriTraining(SSLEnsemble):
    """
    SSL Tri-Training Classifier.

    Zhi-Hua Zhou and Ming Li, "Tri-training: exploiting
    unlabeled data using three classifiers"
    """

    def __init__(self, h_0, h_1, h_2, random_state=None):
        """
        Constructor. Creates the tri-training instance.

        Parameters
        ----------
        h_0, h_1, h_2:
            Classifiers
        random_state:
            Random object or seed
        """
        super().__init__(classes=[], random_state=random_state)
        self.n = 3
        self.classifiers = {0: h_0, 1: h_1, 2: h_2}

    def fit(self, L, y, U):
        """
        Trains the tri-training ensemble using Zhi-Hua Zhou
        Algorithm.

        Parameters
        ----------
        L: np.array
            Labeled data used for training
        y: np.array
            Labeled data tags used for training
        U: np.array
            Unlabeled data used for training
        """
        self.initialize_classifiers(L, y)
        self.classes = np.unique(y)  # skipcq: PYL-W0201

        previous_e = [0.5] * self.n
        previous_l = [0.0] * self.n
        e = [0.0] * self.n

        new_data = True

        while new_data:
            cls_changes = np.array([False] * self.n)
            cls_pseudo_updates = [() for i in range(self.n)]

            for i in range(self.n):
                e[i] = self.measure_error(i, L, y)

                if e[i] < previous_e[i]:
                    cls_pseudo_updates[i] = self.create_pseudolabeled_set(i, U)

                    if previous_l[i] == 0:
                        previous_l[i] = floor(
                            (e[i] / (previous_e[i] - e[i])) + 1
                        )

                    L_i_size = cls_pseudo_updates[i][0].shape[0]

                    if previous_l[i] < L_i_size:
                        if e[i] * L_i_size < previous_e[i] * previous_l[i]:
                            cls_changes[i] = True

                        elif previous_l[i] > (e[i] / (previous_e[i] - e[i])):
                            L_index = self.random_state.choice(
                                L_i_size,
                                ceil(
                                    (previous_e[i] * previous_l[i] / e[i]) - 1
                                ),
                            )
                            cls_pseudo_updates[i] = (
                                cls_pseudo_updates[i][0][L_index, :],
                                cls_pseudo_updates[i][1][L_index],
                            )
                            cls_changes[i] = True

            if cls_changes.sum() == 0:
                new_data = False

            else:
                for i in np.fromiter(self.classifiers.keys(), dtype=int)[
                    cls_changes
                ]:
                    X_train = np.concatenate((L, cls_pseudo_updates[i][0]))
                    y_train = np.concatenate((y, cls_pseudo_updates[i][1]))
                    self.classifiers[i] = self.classifiers[i].fit(
                        X_train, y_train
                    )

                    previous_e[i] = e[i]
                    previous_l[i] = cls_pseudo_updates[i][0].shape[0]

    def initialize_classifiers(self, L, y, percentage=0.8):
        """
        Initializes each base classifier bootstrapping
        from L.

        Parameters
        ----------
        L: np.array
            Labeled data used for training
        """
        for i in range(self.n):
            rand_rows = self.random_state.choice(
                L.shape[0], replace=True, size=(int(percentage * L.shape[0]))
            )
            self.classifiers[i] = self.classifiers[i].fit(
                L[rand_rows, :], y[rand_rows]
            )

    def measure_error(self, i, L, y):
        """
        The classification error is approximated through
        dividing the number of labeled examples on which
        both hj and hk make incorrect classification by
        the number of labeled examples on which the
        classification made by hj is the same as that made
        by hk.

        Parameters
        ----------
        i: int
            Excluded classifier index
        L: np.array
            Labeled data used for training
        y: np.array
            Labeled data tags used for training
        """
        prediction_j = self.classifiers[(i + 1) % self.n].predict(L)
        prediction_k = self.classifiers[(i + 2) % self.n].predict(L)

        incorrect_classification = np.logical_and(
            prediction_j != y, prediction_k == prediction_j
        )
        concordance = prediction_j == prediction_k

        return sum(incorrect_classification) / sum(concordance)

    def create_pseudolabeled_set(self, i, U):
        """
        Li is created by saving those samples in which
        the other two classifiers agree on the tag.

        Parameters
        ----------
        i: int
            Excluded classifier index
        U: np.array
            Unlabeled data used for training
        """
        U_y_j = self.classifiers[(i + 1) % self.n].predict(U)
        U_y_k = self.classifiers[(i + 2) % self.n].predict(U)

        concordances = U_y_j == U_y_k

        return (U[concordances], U_y_k[concordances])

    def single_predict(self, sample):
        """
        Returns the class predicted by tri-training.

        Parameters
        ----------
        sample: np_array
            sample to predict

        Returns
        -------
        np.array:
            label predicted by tri-training.
        """
        count = {i: 0 for i in self.classes}

        for i in (
            cls.predict([sample])[0] for cls in self.classifiers.values()
        ):
            count[i] += 1

        return max(count, key=count.get)

    def single_predict_proba(self, sample):
        """
        Returns the probability for each class
        predicted by tri-training for a given sample.

        Parameters
        ----------
        sample: np_array
            sample to predict

        Returns
        -------
        np.array:
            array containing probability for each class.
        """
        count = {i: 0 for i in self.classes}

        for i in (
            cls.predict([sample])[0] for cls in self.classifiers.values()
        ):
            count[i] += 1

        votes = np.array(list(count.values()))
        return votes / self.n
