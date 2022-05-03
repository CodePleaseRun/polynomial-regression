import numpy as np


def get_matrix(x, degree):
    x = x.reshape((len(x), 1))
    a_mat = np.ones((len(x), 1), dtype=np.float64)
    for i in range(1, degree+1):
        a_mat = np.concatenate((a_mat, np.power(x, i)), axis=1)
    return a_mat


def calc_coef(matrix_a, y):
    lhs = np.dot(matrix_a.T, matrix_a)
    rhs = np.dot(matrix_a.T, y)
    coef = np.linalg.solve(lhs, rhs)
    return coef


def interpolate(data, degree):
    """
    data = (2,N) numpy array with x & y points
    degree = degree of fitting equation. Non-negative integere
    Returns (N+1,1) numpy array of coefficients with dtype=np.float64 
    """
    matrix_a = get_matrix(data[0], degree)
    coef = calc_coef(matrix_a, data[1])
    return coef
