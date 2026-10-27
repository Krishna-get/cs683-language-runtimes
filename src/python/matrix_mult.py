import sys

N = 512

A = [[(300 + (i + k) % 100) for k in range(N)] for i in range(N)]
B = [[(300 + (k * 2 + j) % 100) for j in range(N)] for k in range(N)]
C = [[0 for _ in range(N)] for _ in range(N)]

assert len({id(elem) for row in B for elem in row}) == N * N, "Objects aliased!"

checksum = 0
for i in range(N):
    for j in range(N):
        total = 0
        for k in range(N):
            total += A[i][k] * B[k][j]
        C[i][j] = total
        checksum += total

print(f"Checksum: {checksum}")
