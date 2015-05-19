import numpy as np
import matplotlib.pyplot as plt
import sys
import warnings

#warnings.simplefilter("error", RuntimeWarning)

na = np.newaxis


def sigmoid(x):
    return 1 / (1 + np.exp(-x))


def softmax(x):
    return np.exp(x) / np.sum(np.exp(x))


class MultilayerPerceptron:
    def __init__(self,
                 num_hidden_units=5,
                 max_itr=100000,
                 eta_0=1,
                 threshold=1e-10,
                 activation_func='sigmoid',
                 output_func='sigmoid'):
        self.H = num_hidden_units
        self.w_o = None  # H*O
        self.w_h = None  # D*H
        self.max_itr = max_itr
        self.eta_0 = eta_0
        self.std = None
        self.mean = None
        self.old_err = float('Inf')
        self.threshold = threshold

        self.activate = sigmoid

        if(output_func == 'sigmoid'):
            self.activate_out = sigmoid
        elif(output_func == 'softmax'):
            self.activate_out = softmax
        else:
            raise

    def _forward(self, x):
        h = self.activate(np.sum(x[:, na] * self.w_h[:, :], axis=0))
        y = self.activate_out(np.sum(h[:, na] * self.w_o[:, :], axis=0))
        return y, h

    def predict(self, _X):
        X = (_X[:, :] - self.mean[na, :]) / self.std[na, :]
        Y = np.array([self._forward(x)[0] for x in X])
        return Y

    def backward(self, x, t, y, h):
        delta_o = (y - t) * y * (1 - y)  # O
        Ew_o = h[:, na] * delta_o[na, :]  # H * O
        delta_h = np.sum(delta_o[na, :] * self.w_o[:, :] *
                         h[:, na] * (1 - h[:, na]), axis=1)  # H
        Ew_h = x[:, na] * delta_h[na, :]  # D * H
        return Ew_o, Ew_h

    def fit(self, _X, _T):
        self.std = np.std(_X, axis=0)
        self.mean = np.mean(_X, axis=0)
        self.std[self.std == 0] = 1

        X = (_X[:, :] - self.mean[na, :]) / self.std[na, :]
        T = _T

        N = X.shape[0]
        D = X.shape[1]
        O = T.shape[1]

        self.w_h = np.random.rand(D, self.H) * 2 - 1
        self.w_o = np.random.rand(self.H, O) * 2 - 1

        for i in range(self.max_itr):
            err = 0
            Ew_o = 0
            Ew_h = 0
            for x, t in zip(X, T):
                y, h = self._forward(x)
                _Ew_o, _Ew_h = self.backward(x, t, y, h)
                eta = self.eta_0
                Ew_o += _Ew_o
                Ew_h += _Ew_h
                err += 1 / 2 * (y - t) * (y - t)

            err = err / N
            delta_err = self.old_err - err
            self.old_err = err
            self.w_o -= eta * (Ew_o / N)
            self.w_h -= eta * (Ew_h / N)
            if(delta_err < threashold):
                break


    def fit_online(self, _X, _T):
        self.std = np.std(_X, axis=0)
        self.mean = np.mean(_X, axis=0)
        self.std[self.std == 0] = 1

        X = (_X[:, :] - self.mean[na, :]) / self.std[na, :]
        T = _T

        N = X.shape[0]
        D = X.shape[1]
        O = T.shape[1]

        self.w_h = np.random.rand(D, self.H) * 2 - 1
        self.w_o = np.random.rand(self.H, O) * 2 - 1

        for i in range(self.max_itr):
            index = np.random.random_integers(N) - 1
            x = X[index, :]
            t = T[index]
            y, h = self._forward(x)
            Ew_o, Ew_h = self.backward(x, t, y, h)
            eta = self.eta_0
            self.w_o -= eta * Ew_o
            self.w_h -= eta * Ew_h

    def discr(self, X):
        Y = self.predict(X)
        discr = np.zeros(Y.shape)
        discr[Y > 0.5] = 1
        return discr

    def score(self, X, T):
        Y = self.predict(X)
        Discr = np.zeros(Y.shape)
        Discr[Y > 0.5] = 1
        Score = np.zeros(Y.shape)
        Score[Discr == T] = 1
        return Score


def main():
    train_data = np.loadtxt("../dataset/vowel/train.txt", delimiter=" ")
    test_data = np.loadtxt("../dataset/vowel/test.txt", delimiter=" ")

    _train_set = [train_data[train_data[:-1, 2] == i+1, :-1]
                 for i in range(5)]
    train_set = [np.c_[ts, np.ones(ts.shape[0])] for ts in _train_set]

    _test_set = [test_data[test_data[:-1, 2] == i+1, :-1]
                for i in range(5)]
    test_set = [np.c_[ts, np.ones(ts.shape[0])] for ts in _test_set]

    for i in range(5):
        for j in range(5):
            if(j <= i):
                continue
            cls_1 = i
            cls_2 = j
            mlp = MultilayerPerceptron(max_itr=100)
            X = np.r_[test_set[cls_1], test_set[cls_2]]
            num_zeros = test_set[cls_1].shape[0]
            num_ones = test_set[cls_2].shape[0]
            _T = np.r_[np.zeros(num_zeros), np.ones(num_ones)]
            T = _T[:, na]
            mlp.fit_online(X, T)
            Y = mlp.predict(X)
            E = np.absolute(Y - T)
            print('------------------')
            print(np.average(mlp.score(X, T)))
            print(np.average(E))
            plt.plot(train_set[cls_1][:, 0], train_set[cls_1][:,1], 'bo')
            plt.plot(train_set[cls_2][:, 0], train_set[cls_2][:,1], 'ro')
            plt.savefig('fig.png')

if __name__ == '__main__':
    main()
