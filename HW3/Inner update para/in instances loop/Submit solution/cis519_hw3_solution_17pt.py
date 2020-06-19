import pandas as pd
import numpy as np

"""### Logistic Regression"""


class LogisticRegression:

    def __init__(self, alpha=0.01, regLambda=0.01, regNorm=2, epsilon=0.0001, maxNumIters=10000, initTheta=None):
        '''
        Constructor
        Arguments:
        	alpha is the learning rate
        	regLambda is the regularization parameter
        	regNorm is the type of regularization (either L1 or L2, denoted by a 1 or a 2)
        	epsilon is the convergence parameter
        	maxNumIters is the maximum number of iterations to run
          initTheta is the initial theta value. This is an optional argument
        '''
        self.alpha = alpha
        self.regLambda = regLambda
        self.regNorm = regNorm
        self.epsilon = epsilon
        self.maxNumIters = maxNumIters
        self.theta = initTheta  # give the initial theta to the theta
        self.X_train_mean = None  # mean value of standardization
        self.X_train_std = None  # standard deviation

    def computeCost(self, theta, X, y, regLambda):
        '''
        Computes the objective function
        Arguments:
            X is a n-by-d numpy matrix
            y is an n-by-1 numpy matrix
            regLambda is the scalar regularization constant
        Returns:
            a scalar value of the cost  ** make certain you're not returning a 1 x 1 matrix! **
        '''
        z = np.dot(X, theta)
        yhat = self.sigmoid(z)  # n-by-1 vector h_theta
        # the theta zero is not regularized, using L2 norm
        if self.regNorm == 1:  # 1st Norm for regularization
            Lreg = -1 * (np.dot(y.T, np.log(yhat)) + np.dot((1 - y).T, np.log(1 - yhat))) + regLambda * (
                np.linalg.norm(theta[1:], ord=1))
        elif self.regNorm == 2:  # 2nd Norm for regularization
            Lreg = -1 * (np.dot(y.T, np.log(yhat)) + np.dot((1 - y).T, np.log(1 - yhat))) + regLambda * (
                        (np.linalg.norm(theta[1:])) ** 2)
        else:
            print("regNorm is not defined")
        cost_value = Lreg.tolist()[0][0]  # convert the matrix to scalar
        return cost_value

    def computeGradient(self, theta, X, y, regLambda):
        '''
        Computes the gradient of the objective function
        Arguments:
            X is a n-by-d numpy matrix
            y is an n-by-1 numpy matrix
            regLambda is the scalar regularization constant
        Returns:
            the gradient, an d-dimensional vector
        '''
        n, d = X.shape  # theta is d shape
        z = np.dot(X, theta)
        yhat = self.sigmoid(z)  # n-by-1 vector h_theta
        gradient = np.zeros((d, 1))
        # extract the alpha outside of the gradient, and use different formula for gradient
        if self.regNorm == 1:  # L1
            gradient = np.dot(np.transpose(X), (yhat - y))  # the first row of X is 1
            gradient[1:] = gradient[1:] + regLambda * theta[1:] / np.absolute(theta[1:])  # regularization term
        elif self.regNorm == 2:  # L2
            gradient = np.dot(np.transpose(X), (yhat - y))  # the first row of X is 1
            gradient[1:] = gradient[1:] + regLambda * theta[1:]  # regularization term
        return gradient  # include the negative into the gradient

    def hasConverged(self, theta_new, theta_old):
        '''
        Check if the gradient has converged/ L2 norm less than self.epsilon
        :param theta_new: new theta
        :param theta_old: old theta
        :return: True or False
        '''
        if np.linalg.norm(theta_old - theta_new) <= self.epsilon:
            print('Has converged!')
            return True
        else:
            return False

    def gradientDescent(self, X, y, theta):  # the X should be preprocessed
        '''
        This function is for implementing the gradient descent to update the theta
        X: proprocessed n by d
        y: labels
        theta
        '''
        n, d = X.shape
        for iter in range(self.maxNumIters):
            theta_old = theta.copy()
            theta = theta - self.alpha * self.computeGradient(theta, X, y, self.regLambda)  # gradient is negative, +
            print('Cost is: ' + str(self.computeCost(theta, X, y, self.regLambda)))  # indicator of Cost value
            if iter > 0 and self.hasConverged(theta, theta_old) is True:
                break  # the gradient descent has converged
        return theta

    def fit(self, X, y):
        '''
        Trains the model
        Arguments:
            X is a n-by-d Pandas data frame
            y is an n-by-1 Pandas data frame
        Note:
            Don't assume that X contains the x_i0 = 1 constant feature.
            Standardization should be optionally done before fit() is called.
        '''
        # process the X set and standardization
        X_copy = X.copy().to_numpy()  # in case the new operation affects the original X, and convert df to np
        y_copy = y.copy().to_numpy()

        n = len(y)
        # self.X_train_mean = X_copy.mean(0)
        # self.X_train_std = X_copy.std(0)
        # X_scaled = (X_copy - X_copy.mean(0))/X_copy.std(0)
        X_fit = np.c_[np.ones((n, 1)), X_copy]  # add the first column

        n, d = X_fit.shape  # now the X has been added the first column
        y_fit = y_copy.reshape(n, 1)

        if self.theta is None:  # initialize the theta
            self.theta = np.matrix(np.random.rand(d, 1) - 0.5)  # why initial with random integer rather than zeros????

        # theta_copy = self.theta.copy()    # copy the theta (not sure if necessary)
        self.theta = self.gradientDescent(X_fit, y_fit, self.theta)

    def predict(self, X):
        '''
        Used the model to predict values for each instance in X
        Arguments:
            X is a n-by-d Pandas data frame
        Returns:
            an n-by-1 dimensional Pandas data frame of the predictions
        Note:
            Don't assume that X contains the x_i0 = 1 constant feature.
            Standardization should be optionally done before predict() is called.
        '''
        y_raw = self.predict_proba(X)
        y_pre = y_raw.iloc[:, 0].apply(lambda x: 1 if x >= 0.5 else 0)
        return y_pre

    def predict_proba(self, X):
        '''
        Used the model to predict the class probability for each instance in X
        Arguments:
            X is a n-by-d Pandas data frame
        Returns:
            an n-by-1 Pandas data frame of the class probabilities
        Note:
            Don't assume that X contains the x_i0 = 1 constant feature.
            Standardization should be optionally done before predict_proba() is called.
        '''
        X_copy = X.copy().to_numpy()
        print(X_copy.shape)
        print('=======')
        n, d = X_copy.shape
        X_scaled = np.c_[np.ones((n, 1)), X_copy]
        return pd.DataFrame(self.sigmoid(X_scaled * self.theta))

    def sigmoid(self, Z):
        sigmoid = 1 / (1 + np.exp(-Z))
        return sigmoid


"""# Test Logistic Regression 1"""

# Test script for training a logistic regressiom model
#
# This code should run successfully without changes if your implementation is correct
#
from numpy import loadtxt, ones, zeros, where
import numpy as np
from pylab import plot, legend, show, where, scatter, xlabel, ylabel, linspace, contour, title
import matplotlib.pyplot as plt


def test_logreg1():
    # load the data
    filepath = "http://www.seas.upenn.edu/~cis519/spring2020/data/hw3-data1.csv"
    df = pd.read_csv(filepath, header=None)

    X = df[df.columns[0:2]]
    y = df[df.columns[2]]

    n, d = X.shape

    # # Standardize features
    from sklearn.preprocessing import StandardScaler
    standardizer = StandardScaler()
    Xstandardized = pd.DataFrame(
        standardizer.fit_transform(X))  # compute mean and stdev on training set for standardization

    # train logistic regression
    logregModel = LogisticRegression(regLambda=0.00000001)
    logregModel.fit(Xstandardized, y)

    # Plot the decision boundary
    h = .02  # step size in the mesh
    x_min = X[X.columns[0]].min() - .5
    x_max = X[X.columns[0]].max() + .5
    y_min = X[X.columns[1]].min() - .5
    y_max = X[X.columns[1]].max() + .5
    xx, yy = np.meshgrid(np.arange(x_min, x_max, h), np.arange(y_min, y_max, h))
    allPoints = pd.DataFrame(np.c_[xx.ravel(), yy.ravel()])
    allPoints = pd.DataFrame(standardizer.transform(allPoints))
    Z = logregModel.predict(allPoints)
    Z = np.asmatrix(Z.to_numpy())

    # Put the result into a color plot
    Z = Z.reshape(xx.shape)
    plt.figure(1, figsize=(8, 6))
    plt.contourf(xx, yy, Z, cmap=plt.cm.Paired)

    # Plot the training points
    plt.scatter(X[X.columns[0]], X[X.columns[1]], c=y.ravel(), edgecolors='k', cmap=plt.cm.Paired)

    # Configure the plot display
    plt.xlabel('Exam 1 Score')
    plt.ylabel('Exam 2 Score')

    plt.xlim(xx.min(), xx.max())
    plt.ylim(yy.min(), yy.max())
    plt.xticks(())
    plt.yticks(())

    plt.show()


# test_logreg1()

"""# Map Feature"""


def mapFeature(X, column1, column2, maxPower=6):
    '''
    Maps the two specified input features to quadratic features. Does not standardize any features.

    Returns a new feature array with d features, comprising of
        X1, X2, X1 ** 2, X2 ** 2, X1*X2, X1*X2 ** 2, ... up to the maxPower polynomial

    Arguments:
        X is an n-by-d Pandas data frame, where d > 2
        column1 is the string specifying the column name corresponding to feature X1
        column2 is the string specifying the column name corresponding to feature X2
    Returns:
        an n-by-d2 Pandas data frame, where each row represents the original features augmented with the new features of the corresponding instance
        the first bias row is not added here
    '''
    X_1 = X[column1]  # the first column of the X, X1
    X_2 = X[column2]  # the second column of X, X2
    X_map = pd.concat([X_1, X_2], axis=1)  # define the new X
    for d in range(1, maxPower):
        for i in range(d + 2):  # 0, 1, 2, ..., d+1
            x_2_new = X_2.pow(i)  # axis
            x_1_new = X_1.pow(d + 1 - i)
            new_col = x_1_new.multiply(x_2_new)
            X_map = pd.concat([X_map, new_col], axis=1)
    print(X_map)
    return X_map


"""# Test Logistic Regression 2"""

from numpy import loadtxt, ones, zeros, where
import numpy as np
from pylab import plot, legend, show, where, scatter, xlabel, ylabel, linspace, contour, title
import matplotlib.pyplot as plt
from sklearn.utils import shuffle


def test_logreg2():
    polyPower = 6

    # load the data
    filepath = "http://www.seas.upenn.edu/~cis519/spring2020/data/hw3-data2.csv"
    df = pd.read_csv(filepath, header=None)

    X = df[df.columns[0:2]]
    y = df[df.columns[2]]

    n, d = X.shape

    # map features into a higher dimensional feature space
    Xaug = mapFeature(X.copy(), X.columns[0], X.columns[1], polyPower)

    # # Standardize features
    from sklearn.preprocessing import StandardScaler
    standardizer = StandardScaler()
    Xaug = pd.DataFrame(standardizer.fit_transform(Xaug))  # compute mean and stdev on training set for standardization

    # train logistic regression
    logregModel = LogisticRegressionAdagrad(regLambda=0.00000001, regNorm=2)  # this line is changed for testing
    logregModel.fit(Xaug, y)

    # Plot the decision boundary
    h = .02  # step size in the mesh
    x_min = X[X.columns[0]].min() - .5
    x_max = X[X.columns[0]].max() + .5
    y_min = X[X.columns[1]].min() - .5
    y_max = X[X.columns[1]].max() + .5
    xx, yy = np.meshgrid(np.arange(x_min, x_max, h), np.arange(y_min, y_max, h))

    allPoints = pd.DataFrame(np.c_[xx.ravel(), yy.ravel()])
    allPoints = mapFeature(allPoints, allPoints.columns[0], allPoints.columns[1], polyPower)
    allPoints = pd.DataFrame(standardizer.transform(allPoints))
    Xaug = pd.DataFrame(standardizer.fit_transform(Xaug))  # standardize data

    Z = logregModel.predict(allPoints)
    Z = np.asmatrix(Z.to_numpy())

    # Put the result into a color plot
    Z = Z.reshape(xx.shape)
    plt.figure(1, figsize=(8, 6))
    plt.contourf(xx, yy, Z, cmap=plt.cm.Paired)

    # Plot the training points
    plt.scatter(X[X.columns[0]], X[X.columns[1]], c=y.ravel(), edgecolors='k', cmap=plt.cm.Paired)

    # Configure the plot display
    plt.xlabel('Microchip Test 1')
    plt.ylabel('Microchip Test 2')

    plt.xlim(xx.min(), xx.max())
    plt.ylim(yy.min(), yy.max())
    plt.xticks(())
    plt.yticks(())

    plt.show()

    print(str(Z.min()) + " " + str(Z.max()))


# test_logreg2()

"""# Logistic Regression with Adagrad"""


class LogisticRegressionAdagrad:

    def __init__(self, alpha=0.01, regLambda=0.01, regNorm=2, epsilon=0.0001, maxNumIters=10000, initTheta=None):
        '''
        Constructor
        Arguments:
        	alpha is the learning rate
        	regLambda is the regularization parameter
        	regNorm is the type of regularization (either L1 or L2, denoted by a 1 or a 2)
        	epsilon is the convergence parameter
        	maxNumIters is the maximum number of iterations to run
          initTheta is the initial theta value. This is an optional argument
        '''
        self.alpha = alpha
        self.regLambda = regLambda
        self.regNorm = regNorm
        self.epsilon = epsilon
        self.maxNumIters = maxNumIters
        self.theta = initTheta  # give the initial theta to the theta
        self.X_train_mean = None  # mean value of standardization
        self.X_train_std = None  # standard deviation

    def computeCost(self, theta, X, y, regLambda):
        '''
        Computes the objective function
        Arguments:
            X is a n-by-d numpy matrix
            y is an n-by-1 numpy matrix
            regLambda is the scalar regularization constant
        Returns:
            a scalar value of the cost  ** make certain you're not returning a 1 x 1 matrix! **
        '''
        z = np.dot(X, theta)
        yhat = self.sigmoid(z)  # n-by-1 vector h_theta
        # the theta zero is not regularized, using L2 norm
        if self.regNorm == 1:  # 1st Norm for regularization
            Lreg = -1 * (np.dot(y.T, np.log(yhat)) + np.dot((1 - y).T, np.log(1 - yhat))) + regLambda * (
                np.linalg.norm(theta[1:], ord=1))
        elif self.regNorm == 2:  # 2nd Norm for regularization
            Lreg = -1 * (np.dot(y.T, np.log(yhat)) + np.dot((1 - y).T, np.log(1 - yhat))) + regLambda * (
                        (np.linalg.norm(theta[1:])) ** 2)
        else:
            print("regNorm is not defined")
        cost_value = Lreg.tolist()[0][0]  # convert the matrix to scalar
        return cost_value

    def computeGradient(self, theta, X, y, regLambda):
        '''
        Computes the gradient of the objective function
        Arguments:
            X is a n-by-d numpy matrix
            y is an n-by-1 numpy matrix
            regLambda is the scalar regularization constant
        Returns:
            the gradient, an d-dimensional vector
        '''
        X_copy = X.copy()
        d = len(X_copy)  # theta is d shape d=1 now
        X_copy = X_copy.reshape((1, d))  # (n,) to (n,1)
        z = np.dot(X_copy, theta)
        print('=====' + str(z))
        yhat = self.sigmoid(z)  # one value
        gradient = np.zeros((d, 1))
        # extract the alpha outside of the gradient, and use different formula for gradient
        if self.regNorm == 1:  # L1
            gradient = np.dot(X_copy.T, (yhat - y))  # the first row of X is 1
            gradient[1:] = gradient[1:] + regLambda * theta[1:] / np.absolute(theta[1:])  # regularization term
        elif self.regNorm == 2:  # L2
            gradient = np.dot(X_copy.T, (yhat - y))  # the first row of X is 1
            gradient[1:] = gradient[1:] + regLambda * theta[1:]  # regularization term
        return gradient  # include the negative into the gradient

    def hasConverged(self, theta_new, theta_old):
        '''
        Check if the gradient has converged/ L2 norm less than self.epsilon
        :param theta_new: new theta
        :param theta_old: old theta
        :return: True or False
        '''
        if np.linalg.norm(theta_old - theta_new) <= self.epsilon:
            print('Has converged!')
            return True
        else:
            return False

    def gradientDescent(self, X, y, theta):  # the X should be preprocessed
        '''
        This function is for implementing the gradient descent to update the theta
        X: proprocessed n by d
        y: labels
        theta
        '''
        n, d = X.shape
        X_copy = X.copy()
        y_copy = y.copy()
        dataset = np.concatenate((X_copy, y_copy), axis=1)  # combine the X and y for shuffling
        G = 0
        g = 0
        min_const = 1E-5

        break_iter = 0  # flag for iteration loop
        for iter in range(self.maxNumIters):
            # dataset = np.concatenate((X_copy, y_copy), axis=1)   # combine the X and y for shuffling
            np.random.shuffle(dataset)  # shuffle the dataset for every outter iteration  # shuffle function
            y_shuffled = dataset[:, -1]  # separate the last column as y numpy.array
            X_shuffled = dataset[:, 0:-1]  # drop the y column
            theta_old = theta.copy()  # store the old theta of last outter iteration
            # G += g          # put this in the end
            g = np.zeros((d, 1))  # store the gradient
            for ins_num in range(n):  # instance n is number of instances
                x_temp = X_shuffled[ins_num, :]
                y_temp = y_shuffled[ins_num]
                curr_grad = self.computeGradient(theta, x_temp, y_temp, self.regLambda)  # a vector
                g = g + curr_grad
                G += g
                # g += np.linalg.norm(curr_grad) ** 2
                # curr_alpha = self.alpha / (np.sqrt(G) + min_const)

                curr_alpha = self.alpha / (np.linalg.norm(G, 2) + min_const)
                theta = theta - curr_alpha * self.computeGradient(theta, x_temp, y_temp, self.regLambda)

                if iter > 0 and self.hasConverged(theta, theta_old) is True:
                    break_iter = 1  # flag for stop iterations
                    break
            print('==============\nCurrent Iter is:' + str(iter + 1))  # print the iter number

            if break_iter == 1:
                break  # stop iterations

            # G += g
            # curr_alpha = self.alpha / (np.linalg.norm(G, 2) + min_const)
            # theta = theta - curr_alpha * self.computeGradient(theta, x_temp, y_temp, self.regLambda)

            # if iter > 0 and self.hasConverged(theta, theta_old) is True:    # iteration loop judgement/ for plot
            #     break

        return theta

    def fit(self, X, y):
        '''
        Trains the model
        Arguments:
            X is a n-by-d Pandas data frame
            y is an n-by-1 Pandas data frame
        Note:
            Don't assume that X contains the x_i0 = 1 constant feature.
            Standardization should be optionally done before fit() is called.
        '''
        # process the X set and standardization
        X_copy = X.copy().to_numpy()  # in case the new operation affects the original X, and convert df to np
        y_copy = y.copy().to_numpy()

        n = len(y)
        # self.X_train_mean = X_copy.mean(0)
        # self.X_train_std = X_copy.std(0)
        # X_scaled = (X_copy - X_copy.mean(0))/X_copy.std(0)
        X_fit = np.c_[np.ones((n, 1)), X_copy]  # add the first column

        n, d = X_fit.shape  # now the X has been added the first column
        y_fit = y_copy.reshape(n, 1)

        if self.theta is None:  # initialize the theta
            self.theta = np.matrix(np.random.rand(d, 1) - 0.5)  # why initial with random integer rather than zeros????

        # theta_copy = self.theta.copy()    # copy the theta (not sure if necessary)
        self.theta = self.gradientDescent(X_fit, y_fit, self.theta)

    def predict(self, X):
        '''
        Used the model to predict values for each instance in X
        Arguments:
            X is a n-by-d Pandas data frame
        Returns:
            an n-by-1 dimensional Pandas data frame of the predictions
        Note:
            Don't assume that X contains the x_i0 = 1 constant feature.
            Standardization should be optionally done before predict() is called.
        '''
        y_raw = self.predict_proba(X)
        y_pre = y_raw.iloc[:, 0].apply(lambda x: 1 if x >= 0.5 else 0)
        return y_pre

    def predict_proba(self, X):
        '''
        Used the model to predict the class probability for each instance in X
        Arguments:
            X is a n-by-d Pandas data frame
        Returns:
            an n-by-1 Pandas data frame of the class probabilities
        Note:
            Don't assume that X contains the x_i0 = 1 constant feature.
            Standardization should be optionally done before predict_proba() is called.
        '''
        X_copy = X.copy().to_numpy()
        print(X_copy.shape)
        print('=======')
        n, d = X_copy.shape
        X_scaled = np.c_[np.ones((n, 1)), X_copy]
        return pd.DataFrame(self.sigmoid(X_scaled * self.theta))

    def sigmoid(self, Z):
        sigmoid = 1 / (1 + np.exp(-Z))
        return sigmoid