import numpy as np
import matplotlib.pyplot as plt

from objectives import cross_entropy
from metrics import accuracy
from utils import *


def sigmoid(H):
	return 1/(1 + np.exp(-H))


def softmax(H):
	eH = np.exp(H)
	return eH/eH.sum(axis = 1, keepdims = True)


def ReLU(H):
	return H*(H > 0)


def derivative(Z, a):
	if a is sigmoid:
		return Z*(1 - Z)
	elif a is np.tanh:
		return 1 - Z*Z
	elif a is ReLU:
		return Z > 0
	else:
		raise exception("No known activation provided.")


class ClassificationANN():
    def __init__(self, hidden_layer_sizes, hidden_activations = None):
        self.hidden_layer_sizes = hidden_layer_sizes
        self.hidden_activations = hidden_activations
        self.L = len(hidden_layer_sizes) + 1

    def forward(self, X):
        self.Z = {0: X}

        for l in sorted(self.a.keys()):
            self.Z[l] = self.a[l](np.matmul(self.Z[l - 1],self.W[l]) + self.b[l])

    def fit(self, X, y, eta = 1e-3, lambda2 = 0, mu = 0.9, epochs = 1000, batch_sz = None, show_curve = False):
        N, D = X.shape
        K = len(set(y))

        Y = one_hot_encode(y)
                
        self.layer_sizes = [D] + self.hidden_layer_sizes + [K]

        self.W = {l + 1: np.random.randn(M[0],M[1]) for l, M in enumerate(zip(self.layer_sizes, self.layer_sizes[1:]))}
        self.b = {l + 1: np.random.randn(M) for l, M in enumerate(self.layer_sizes[1:])}
        self.vW = {l + 1: np.zeros((M[0],M[1])) for l, M in enumerate(zip(self.layer_sizes, self.layer_sizes[1:]))}
        self.vb = {l + 1: np.zeros(M) for l, M in enumerate(self.layer_sizes[1:])}
        
        if self.hidden_activations is None:
            self.a = {l+1: ReLU for l in range(self.L - 1)}
        else:
            self.a = {l+1: act for l, act in enumerate(self.hidden_activations)}

        self.a[self.L] = softmax
        
        J = []

        if batch_sz is None:
            batch_sz = N
        else:
            batch_sz = batch_sz
                
        for epoch in range(int(epochs)):
            X, Y, y = shuffle(X, Y, y)

            for i in range(int(N/batch_sz)):
                x_i = X[i*batch_sz:(i+1)*batch_sz,:]
                y_i = Y[i*batch_sz:(i+1)*batch_sz,:]
            
                self.forward(x_i)
                J.append(cross_entropy(y_i,self.Z[self.L]) + (lambda2/2)*sum(np.sum(W*W) for W in self.W.values()))

                dH = self.Z[self.L] - y_i

                for l in sorted(self.W.keys(), reverse = True):
                    dW = np.matmul(self.Z[l - 1].T,dH) + lambda2*self.W[l]
                    self.vW[l] = mu*self.vW[l] - eta*dW
                    self.vb[l] = mu*self.vb[l] - eta*dH.sum(axis = 0)
                    self.W[l] += self.vW[l]
                    self.b[l] += self.vb[l]

                    if l > 1:
                        dZ = np.matmul(dH, self.W[l].T)
                        dH = dZ*derivative(self.Z[l - 1], self.a[l - 1])
                        
        self.forward(X)

        
        if show_curve:
            plt.plot(J)
            plt.title("Training Curve")
            plt.xlabel("epochs")
            plt.ylabel("J")
            plt.show()

    def predict(self, X):
        self.forward(X)
        return self.Z[self.L].argmax(axis = 1)
