import itertools
import operator
import unittest

class TestMatrix(unittest.TestCase):

    def test_multiply1(self):
        # https://www.mathsisfun.com/algebra/matrix-multiplying.html
        A = [[1,2,3],
             [4,5,6]]
        B = [[ 7, 8],
             [ 9,10],
             [11,12]]
        C = [[ 58, 64],
             [139,154]]
        self.assertEqual(multiply(A,B), C)

    def test_multiply2(self):
        # pies sold
        A = [[3,4,2]]
        B = [[13,],
             [ 8,],
             [ 6,]]
        R = multiply(A,B)
        self.assertEqual(R[0][0], 83)


def multiply(A, B):
    """
    Multiply matrices A and B.
    """
    # TODO: n-dimensional matrices?
    # reduce line length in inner-most loop
    starmap = operator.starmap
    mul = operator.mul

    # a dictionary to hold values at a position
    S = {}

    # rotate the B matrix
    B_by_column = list(zip(*B))
    for A_ri, A_row in enumerate(A):
        for B_ci, B_col in enumerate(B_by_column):
            # pair-wise multiply the row in A and the column in B.
            # sum these values and save at position A row index and B column index.
            S[(A_ri, B_ci)] = sum(starmap(mul, zip(A_row, B_col)))

    # find maximum row and column indexes
    max_ci, max_ri = map(max, zip(*S))
    # construct nested list matrix of result
    C = [[S[(row,col)] for col in range(max_ci+1)] for row in range(max_ri+1)]
    return C

if __name__ == '__main__':
    unittest.main()
