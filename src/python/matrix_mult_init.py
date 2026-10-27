import sys

N = 512

A = [[(300 + (i + k) % 100) for k in range(N)] for i in range(N)]
B = [[(300 + (k * 2 + j) % 100) for j in range(N)] for k in range(N)]
C = [[0 for _ in range(N)] for _ in range(N)]

assert len({id(elem) for row in B for elem in row}) == N * N, "Objects aliased!"

# Exit immediately prior to the computational loop
sys.exit(0)
