from sklearn.tree import DecisionTreeClassifier
import numpy as np
import numbers
from copy import deepcopy
from sklearn.metrics import recall_score, precision_score

class CoForest:

    def __init__(self, L, y, U, n, theta, random_state=None, max_features='log2'):
        """
        Constructor. Creates and trains the Co-Forest.
        
        Parameters
        ----------
        L: np.array
            Labeled data used for training
        y: np.array
            Tags of the labeled data used for training
        U: np.array
            Unlabeled data used for training
        n: int
            Number of trees in the ensemble
        theta: float
            Tolerance
        random_state:
            Random object to create deterministic experiments
        max_features: string
            log2, sqrt, None
        """

        self.random_state = self.check_random_state(random_state)
        self.n = n
        self.theta = theta
        self.classes = np.unique(y)

        self.U = U
        self.L = L
        self.y = y
        self.mask_L = np.zeros(shape=((self.L.shape[0]), self.n), dtype=int, order='C')

        self.ensemble = self.create_trees(max_features)
        

    def create_trees(self, max_features) -> dict:
        """
        Generates a dict containing co-forest's trees.

        Parameters
        ----------
        max_features: number of features to consider 
                      when looking for the best split
                      'sqrt', 'log2', None

        Returns
        -------
        dict: {key: int, value: Tree}
        """

        ensemble = {}

        for i in range(self.n):

            rand_rows = self.random_state.choice(self.L.shape[0], replace = True, size=(int(0.7*self.L.shape[0])) )
            self.mask_L[rand_rows, i] = 1
            h = DecisionTreeClassifier(max_features=max_features, random_state=self.random_state)
            ensemble[i] = h.fit(self.L[rand_rows, :], self.y[rand_rows])

        return ensemble

    def fit(self):
        """
        Fits the ensemble using both labeled and
        pseudo-labeled data.
        """

        e = [0 for i in range(self.n)]
        W = [0 for i in range(self.n)]
        previous_e = [0.5 for i in range(self.n)]
        previous_W = [min(0.1*len(self.L), 100) for i in range(self.n)]

        new_data = True
        t = 0

        while new_data:

            t += 1
            tree_changes = np.array([False for i in range(self.n)])
            tree_pseudo_updates = [() for i in range(self.n)]

            for i, hi in self.ensemble.items():

                e[i] = self.concomitant_oob_error(hi)
                W[i] = previous_W[i]
                pseudo_labeled_data = []
                pseudo_labeled_tags = []

                if e[i] < previous_e[i]:

                    if e[i] == 0:
                        Wmax = self.theta * self.U.shape[0]
                    else:
                        Wmax = min(self.theta * self.U.shape[0], ((previous_e[i]*previous_W[i])/e[i]) )

                    U_subsampled = self.subsample(hi, Wmax) 
                    W[i] = 0

                    for u in U_subsampled:
                        concomitant_confidence, selected_class = self.concomitant_confidence(hi, self.U[u, :])

                        if concomitant_confidence > self.theta:
                            tree_changes[i] = True
                            pseudo_labeled_data.append(self.U[u, :])
                            pseudo_labeled_tags.append(selected_class)
                            W[i] += concomitant_confidence

                tree_pseudo_updates[i] = ( (np.array(pseudo_labeled_data), np.array(pseudo_labeled_tags) ) )

            for i in np.fromiter(self.ensemble.keys(), dtype=int)[tree_changes]:
                if e[i] * W[i] < previous_e[i] * previous_W[i]:
                    self.retrain_tree(i, tree_pseudo_updates[i][0], tree_pseudo_updates[i][1])

            previous_e = deepcopy(e)
            previous_W = deepcopy(W)

            if tree_changes.sum() == 0:
                new_data = False
        
        
    def retrain_tree(self, i, pseudo_labeled_data, pseudo_labeled_tags):
        """
        Retrains a tree given new pseudo-labeled data.

        Parameters
        ----------
        i: int
            index of the three
        pseudo_labeled_data: np.array
            unlabeled samples
        pseudo_labeled_tags: np.array
            pseudo-labels for the unlabeled samples
        """

        pseudo_labeled_data = (lambda x: np.expand_dims(x, axis=0) if x.ndim == 1 else x)(pseudo_labeled_data)
        X_train = np.concatenate( (self.L[self.mask_L[:, i] == 1], pseudo_labeled_data) )
        y_train = np.concatenate( (self.y[self.mask_L[:, i] == 1], pseudo_labeled_tags) )
        self.ensemble[i] = self.ensemble[i].fit(X_train, y_train)

        
    def subsample(self, hi, Wmax):
        """
        Samples from U uniformly at random until 
        the sum of the sample weights reaches Wmax.
        Bootstraping is applied.

        Parameters
        ----------
        hi : DecisionTreeClassifier excluded
        Wmax: float

        Returns
        -------
        np.array
            Array containing the index of the chosen
            samples from U
        """

        W = 0
        U_subsampled = []

        while (W < Wmax):

            rand_row = self.random_state.choice(self.U.shape[0])
            W += self.concomitant_confidence(hi, self.U[rand_row, :])[0]
            U_subsampled.append(rand_row)

        return np.array(U_subsampled)

        
    def concomitant_oob_error(self, hi):
        """
        Calculates the Out of Bag Error of the concomitant 
        ensemble of hi for the whole labeled data.

        Parameters
        ----------
        hi : DecisionTreeClassifier excluded

        Returns
        -------
        float
            OOBE if trees voted, nan if not
        """

        errors = []

        for sample, tag in zip(self.L, self.y):
            n_votes = 0
            n_hits = 0 

            for i, tree in self.ensemble.items():

                rows_training = self.L[self.mask_L[:, i] == 1]
                used_training = np.any(np.all(sample == rows_training, axis=1))

                if tree is not hi and not used_training:
                    if tree.predict([sample])[0] == tag:
                        n_hits += 1
                    n_votes +=1

            if (n_votes > 0):
                errors.append(1 - (n_hits/n_votes))

        return np.mean(a=errors)

    def concomitant_confidence(self, hi, sample):
        """
        Calculates the number of coincidences during
        prediction of the hi concomitant ensemble for a
        data sample.

        Parameters
        ----------
        hi : DecisionTreeClassifier
        sample: sample's features array

        Returns
        -------
        tuple (float, int)
            float: confidence for the sample
            int: most agreed class
        """

        count = {i: 0  for i in self.classes}

        for tree in self.ensemble.values():
            if tree is not hi:
                count[tree.predict([sample])[0]] += 1

        max_agreement = max(count.values())
        most_agreed_class = list(count.keys())[list(count.values()).index(max_agreement)]

        return max_agreement/(len(self.ensemble) -1), most_agreed_class


    def single_predict(self, sample): 
        """
        Returns the class predicted by coforest
        for a given sample. Majority voting is used.

        Parameters
        ----------
        sample: np_array
            sample to predict

        Returns
        -------
        np.array:
            label predicted by coforest.
        """

        count = {i: 0  for i in self.classes}
        for i in (tree.predict([sample])[0] for tree in self.ensemble.values()):
            count[i]+= 1

        max_agreement = max(count.values())
        return list(count.keys())[list(count.values()).index(max_agreement)]


    def predict(self, samples):
        """
        Returns the labels predicted by the coforest
        for a given data.

        Parameters
        ----------
        samples: np_array
            samples to predict

        Returns
        -------
        np.array:
            labels predicted by the coforest.
        """
        
        samples = (lambda x: np.expand_dims(x, axis=0) if x.ndim == 1 else x)(samples)
        return np.array([self.single_predict(sample) for sample in samples])


    def single_predict_proba(self, sample):
        """
        Returns the probability for each class 
        predicted by coforest for a given sample.

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

        for i in (tree.predict([sample])[0] for tree in self.ensemble.values()):
                count[i]+= 1

        votes = np.array(list(count.values()))
        return votes / self.n


    def predict_proba(self, samples):
        """
        Returns the probabilities predicted by 
        coforest for a given data.

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


    def score(self, X_test, y_test):
        """
        Calculates the number of hits by coforest
        given a training set.

        Parameters
        ----------
        X_test: np_array
            Samples used during testing
        y_test: np_array
            Samples' tags

        Returns
        -------
        float:
            percentage of hits.
        """
        y_predictions = self.predict(X_test)
        return np.count_nonzero(y_predictions==y_test)/len(y_test)


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


    def recall(self, y_true, y_pred):
        """
        Returns recall.
        
        Parameters
        ----------
        y_true: np.array with true labels
        y_pred: np.array with labels predicted by co-forest

        Returns
        -------
        Recall score
        """
        return recall_score(y_true, y_pred)
        

    def precision(self, y_true, y_pred):
        """
        Returns precision.
        
        Parameters
        ----------
        y_true: np.array with true labels
        y_pred: np.array with labels predicted by co-forest

        Returns
        -------
        Precision score
        """

        return precision_score(y_true, y_pred)