from classifiers.utils import confidence_interval
import numpy as np
import numbers


class DemocraticCo:

    def __init__(self, base_cls, random_state=None):
        """
        Constructor. Creates the democratic-co instance.

        Parameters
        ----------
        base_cls:
            Classifiers
        random_state:
            Random object or seed
        """
        self.n = len(base_cls)
        self.classes = []
        self.rd = self.check_random_state(random_state)
        self.classifiers = {i: base_cls[i] for i in range(self.n)}
        self.w = []
        self.alpha = 0.95

    def fit(self, L, y, U):
        """
        Trains the democratic-Co.

        Parameters
        ----------
        L: np.array
            Labeled data used for training
        y: np.array
            Labeled data tags used for training
        U: np.array
            Unlabeled data used for training
        """
        classes = np.unique(y)
        self.classes = classes
        changes = True

        e = [0] * self.n
        L_ = [(list(L), list(y)) for i in range(self.n)]
        U_in_L_ = [dict() for i in range(self.n)]
        cls_changes = np.ones(self.n, dtype=bool)

        while changes:

            for i in np.arange(self.n)[cls_changes]:
                self.classifiers[i] = self.classifiers[i].fit(*L_[i])
            cls_changes = np.zeros(self.n, dtype=bool)

            U_tag_votes = [{i: set() for i in self.classes} for x in U]
            U_y = []

            for x_id, x in enumerate(U):
                for id_cls, cls in self.classifiers.items():
                    prediction = cls.predict([x])[0]
                    U_tag_votes[x_id][prediction].add(id_cls)

                U_y.append(
                    max(U_tag_votes[x_id], key=lambda k: len(U_tag_votes[x_id].get(k))))

            # Choose which exs to propose for labeling
            w = [self.get_w(cls, L, y) for cls in self.classifiers.values()]
            L_prime = [([], []) for i in range(self.n)]
            Li_prime_ids = [[] for i in range(self.n)]

            for x_id, x in enumerate(U):

                most_voted_tag = U_y[x_id]
                cls_agree_tag = U_tag_votes[x_id][most_voted_tag]

                exp_1 = 0
                for cls in cls_agree_tag:
                    exp_1 += w[cls]

                exp_2 = 0
                for tag in classes:
                    if tag != most_voted_tag:
                        weight_tag = 0
                        for cls in U_tag_votes[x_id][tag]:
                            weight_tag += w[cls]
                        exp_2 = max(exp_2, weight_tag)

                if exp_1 > exp_2:
                    for id_cls in (set(self.classifiers.keys()) - cls_agree_tag):
                        Li_prime, y_Li_prime = L_prime[id_cls]
                        Li_prime.append(x)
                        y_Li_prime.append(U_y[x_id])
                        Li_prime_ids[id_cls].append(x_id)

            # Estimate if adding this is better
            l_mean = 0
            for id_cls, cls in self.classifiers.items():
                l_mean += confidence_interval(cls,
                                              L_[id_cls][0], L_[id_cls][1])[0]
            l_mean /= self.n

            for i in range(self.n):

                Li, y_Li = L_[i]
                Li_prime, y_Li_prime = L_prime[i]
                Li_union_Li_prime = Li + Li_prime

                q_i = len(Li) * (1 - 2 * (e[i] / len(Li))) ** 2
                e_i_prime = (1 - l_mean) * len(Li_prime)
                q_i_prime = len(
                    Li_union_Li_prime) * (1 - (2*(e[i] + e_i_prime) / len(Li_union_Li_prime))) ** 2

                if q_i_prime > q_i:
                    cls_changes[i] = True
                    e[i] = e[i] + e_i_prime

                    for x_id, x, y_x in zip(Li_prime_ids[i], Li_prime, y_Li_prime):
                        if x_id in U_in_L_[i]:
                            index = U_in_L_[i][x_id]
                            y_Li[index] = y_x

                        else:
                            U_in_L_[i][x_id] = len(Li)
                            Li.append(x)
                            y_Li.append(y_x)

            if cls_changes.sum() == 0:
                changes = False
                self.w = [self.get_w(cls, L, y)
                          for cls in self.classifiers.values()]

    @staticmethod
    def get_w(classifier, L, y):
        """
        Returns the weight of a given classifier.

        Parameters
        ----------
        cls:
            classifier
        L: np.array
            Labeled data
        y: np.array
            Labeled data tags

        Returns
        -------
        float
            weight of the classifier
        """
        li, hi = confidence_interval(classifier, L, y)
        return (li + hi) / 2

    @staticmethod
    def check_random_state(seed=None):
        """
        Turn seed into a np.random.RandomState instance.
        Source: SkLearn

        Parameters
        ----------
        seed : None, int or instance of RandomState
            If None, return the RandomState singleton.
            If int, return a new RandomState seeded with seed.
            If RandomState instance, return it.

        Returns
        -------
        numpy.random.RandomState
            The random state object based on seed parameter.
        """
        if seed is None or seed is np.random:
            return np.random.mtrand._rand

        if isinstance(seed, numbers.Integral):
            return np.random.RandomState(seed)

        if isinstance(seed, np.random.RandomState):
            return seed

    def predict(self, samples):
        """
        Returns the labels predicted by the democratic-co
        for a given data.

        Parameters
        ----------
        samples: np_array
            samples to predict

        Returns
        -------
        np.array:
            labels predicted by democratic-co
        """
        samples = (lambda x: np.expand_dims(x, axis=0)
                   if x.ndim == 1 else x)(samples)
        return np.array([self.single_predict(sample) for sample in samples])

    def single_predict(self, sample):
        """
        Returns the class predicted by democratic-co.

        Parameters
        ----------
        sample: np_array
            sample to predict

        Returns
        -------
        np.array:
            label predicted by democratic-co
        """
        groups = {i: set() for i in self.classes}

        for id_cls, cls in self.classifiers.items():
            if self.w[id_cls] > 0.5:
                prediction = cls.predict([sample])[0]
                groups[prediction].add(id_cls)

        max_confidence = -1
        chosen_tag = None

        for j, group in groups.items():

            n_cls = len(group)
            if n_cls > 0:
                group_weight = 0
                for id_cls in group:
                    group_weight += self.w[id_cls]

                average_confidence = (
                    (n_cls + 0.5) / (n_cls + 1)) * (group_weight / n_cls)

                if average_confidence > max_confidence:
                    max_confidence = average_confidence
                    chosen_tag = j

        return chosen_tag

    def single_predict_proba(self, sample):
        """
        Returns the probability for each class 
        predicted by democratic-co for a given sample.

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

        for id_cls, cls in self.classifiers.items():
            if self.w[id_cls] > 0.5:
                prediction = cls.predict([sample])[0]
                count[prediction] += 1

        votes = np.array(list(count.values()))
        return votes / self.n

    def predict_proba(self, samples: np.array):
        """
        Returns the probabilities predicted by 
        democratic-co for a given data.

        Parameters
        ----------
        samples: np_array
            samples to predict

        Returns
        -------
        np.array:
            array containing one array for each
            sample with probabilities for each 
            class.
        """
        samples = (lambda x: np.expand_dims(x, axis=0)
                   if x.ndim == 1 else x)(samples)
        return np.array([self.single_predict_proba(sample) for sample in samples])

    def score(self, X, y_true):
        """
        Calculates the number of hits by democratic-co.

        Parameters
        ----------
        X: np_array
            Samples to predict
        y: np_array
            True tags

        Returns
        -------
        float:
            percentage of hits.
        """
        y_predictions = self.predict(X)
        return np.count_nonzero(y_predictions == y_true)/len(y_true)