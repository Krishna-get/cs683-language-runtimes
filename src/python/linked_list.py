import sys, os

N = 524288
MASK = (1 << 64) - 1


class Node:
    __slots__ = ("value", "next")

    def __init__(self, v):
        self.value = v
        self.next = None


def main():
    passes = int(sys.argv[1]) if len(sys.argv) > 1 else 2

    nodes = [Node(300 + (i * 7 + 3) % 1000) for i in range(N)]
    perm = list(range(N))

    state = 12345
    for i in range(N - 1, 0, -1):
        state = (state * 6364136223846793005 + 1442695040888963407) & MASK
        j = (state >> 33) % (i + 1)
        perm[i], perm[j] = perm[j], perm[i]

    for k in range(N):
        nodes[perm[k]].next = nodes[perm[(k + 1) % N]]

    cur = nodes[perm[0]]
    s = 0
    for p in range(passes):
        for i in range(N):
            s = (s * 31 + cur.value) & MASK
            cur = cur.next

    print("Checksum:", s)
    sys.stdout.flush()
    os._exit(0)


main()
