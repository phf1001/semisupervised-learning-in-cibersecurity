
import numpy as np
import numbers

class TriTraining:  

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
        
        self.n = 3
        self.classes = []
        self.rd = self.check_random_state(random_state)
        self.classifiers = {0 : h_0, 1: h_1, 2: h_2}


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
        self.classes = np.unique(y)

        previous_e = [0.5 for i in range(self.n)]
        previous_l = [0.0 for i in range(self.n)]

        e = [0.0 for i in range(self.n)]
        l = [0.0 for i in range(self.n)]

        new_data = True

        while new_data:

            cls_changes = np.array([False for i in range(self.n)])
            cls_pseudo_updates = [() for i in range(self.n)]

            for i in range(self.n):

                e[i] = self.measure_error(i, L, y)

                if e[i] < previous_e[i]:
                    cls_pseudo_updates[i] = self.create_pseudolabeled_set(i, U)

                    if previous_l[i] == 0:
                        previous_l[i] = ((e[i] / (previous_e[i]-e[i])) + 1)

                    L_i_size = cls_pseudo_updates[i][0].shape[0]

                    if previous_l[i] < L_i_size:

                        if e[i] * L_i_size < previous_e[i] * previous_l[i]:
                            cls_changes[i] = True
                        
                        elif previous_l[i] > (e[i] / (previous_e[i] - e[i])):

                            L_index = self.rd.choice(L_i_size, int((previous_e[i] * previous_l[i] / e[i]) - 1))
                            cls_pseudo_updates[i] = (cls_pseudo_updates[i][0][L_index, :], cls_pseudo_updates[i][1][L_index])
                            cls_changes[i] = True

            if cls_changes.sum() == 0:
                new_data = False

            else:

                for i in np.fromiter(self.classifiers.keys(), dtype=int)[cls_changes]:

                    X_train = np.concatenate((L, cls_pseudo_updates[i][0]))
                    y_train = np.concatenate((y, cls_pseudo_updates[i][1]))
                    self.classifiers[i] = self.classifiers[i].fit(X_train, y_train)

                    previous_e[i] = e[i]
                    previous_l[i] = cls_pseudo_updates[i][0].shape[0] #Tamaño de Li anterior


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
            rand_rows = self.rd.choice(L.shape[0], replace = True, size = (int(percentage * L.shape[0])) )
            self.classifiers[i] = self.classifiers[i].fit(L[rand_rows, :], y[rand_rows])


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
        
        prediction_j = self.classifiers[(i+1) % self.n].predict(L)
        prediction_k = self.classifiers[(i+2) % self.n].predict(L)

        incorrect_classification = np.logical_and(prediction_j != y, prediction_k == prediction_j)
        concordance = (prediction_j == prediction_k)

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

        U_y_j = self.classifiers[(i+1) % self.n].predict(U)
        U_y_k = self.classifiers[(i+2) % self.n].predict(U)

        concordances = (U_y_j == U_y_k)

        return (U[concordances], U_y_k[concordances])


    def check_random_state(self, seed=None):
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

        count = {i: 0  for i in self.classes}

        for i in (cls.predict([sample])[0] for cls in self.classifiers.values()):
            count[i]+= 1

        max_agreement = max(count.values())
        return list(count.keys())[list(count.values()).index(max_agreement)]


    def predict(self, samples):
        """
        Returns the labels predicted by the tri-training
        for a given data.

        Parameters
        ----------
        samples: np_array
            samples to predict

        Returns
        -------
        np.array:
            labels predicted by tri-training.
        """
        
        samples = (lambda x: np.expand_dims(x, axis=0) if x.ndim == 1 else x)(samples)
        return np.array([self.single_predict(sample) for sample in samples])


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

        count = {i: 0  for i in self.classes}

        for i in (cls.predict([sample])[0] for cls in self.classifiers.values()):
                count[i]+= 1

        votes = np.array(list(count.values()))
        return votes / self.n


    def predict_proba(self, samples: np.array):
        """
        Returns the probabilities predicted by 
        tri-training for a given data.

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

        samples = (lambda x: np.expand_dims(x, axis=0) if x.ndim == 1 else x)(samples)
        return np.array([self.single_predict_proba(sample) for sample in samples])


    def score(self, X, y_true):
        """
        Calculates the number of hits by tri-training.

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
        return np.count_nonzero(y_predictions==y_true)/len(y_true)