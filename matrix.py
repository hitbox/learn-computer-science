import operator
import unittest

from itertools import starmap
from itertools import tee
from operator import mul

class TestMatrix(unittest.TestCase):
    """
    Test matrix operations.
    """
    # data taken from:
    # https://www.mathsisfun.com/algebra/matrix-multiplying.html

    def test_add(self):
        A = [[3,8],
             [4,6]]
        B = [[4, 0],
             [1,-9]]
        C = [[7, 8],
             [5,-3]]
        self.assertEqual(add(A, B), C)

    def test_dotproduct_1(self):
        A = [[1,2,3],
             [4,5,6]]
        B = [[ 7, 8],
             [ 9,10],
             [11,12]]
        C = [[ 58, 64],
             [139,154]]
        self.assertEqual(dotproduct(A,B), C)

    def test_dotproduct_2(self):
        # pies sold - example only show first row/col result
        A = [[3,4,2]]
        B = [[13],
             [ 8],
             [ 6]]
        C = dotproduct(A,B)
        self.assertEqual(C[0][0], 83)


def iterproduct(A, B):
    """
    Generate position, row-column tuples. Intended for the row-by-column
    operations to build a mapping of positions to values.
    """
    # TODO: Quickly tried to make B_by_column an itertools.repeat but it didn't
    #       work and is maybe trying to be too clever. Was thinking this would
    #       avoid enumerate-ing the list many times.
    B_by_column = list(zip(*B))
    for A_ri, A_row in enumerate(A):
        for B_ci, B_col in enumerate(B_by_column):
            yield ((A_ri, B_ci), (A_row, B_col))

def make_matrix_from_space(S):
    """
    Convert dict of position/values to nested lists.
    """
    # max row and column indices
    max_ci, max_ri = map(max, zip(*S))
    # construct nested list matrix of result
    C = [[S[(row,col)] for col in range(max_ci+1)] for row in range(max_ri+1)]
    return C

def add(A, B):
    """
    Add matrices A and B.
    """
    return [[sum(vals) for vals in zip(*rows)] for rows in zip(A, B)]

def dotproduct(A, B):
    """
    The dot product of matrices A and B.
    """
    # NOTE: This idea of saving positions as we go and figuring out the
    #       dimensions late was my first idea for resizing after the operation.
    #       Could have taken the minimum row/column size of the matrices.
    # TODO: performance test of this vs. that.
    S = {pos: sum(starmap(mul, zip(*rowcol))) for pos, rowcol in iterproduct(A, B)}
    return make_matrix_from_space(S)

if __name__ == '__main__':
    unittest.main()
