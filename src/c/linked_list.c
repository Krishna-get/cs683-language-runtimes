#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

#define N 524288

typedef struct Node { int value; struct Node *next; } Node;

static Node nodes[N];
static int perm[N];

__attribute__((noinline)) void champsim_roi_begin(void) { __asm__ volatile(""); }
__attribute__((noinline)) void champsim_roi_end(void)   { __asm__ volatile(""); }

int main(int argc, char **argv)
{
    int passes = (argc > 1) ? atoi(argv[1]) : 2;

    for (int i = 0; i < N; i++) { nodes[i].value = 300 + (i * 7 + 3) % 1000; perm[i] = i; }

    uint64_t state = 12345;
    for (int i = N - 1; i > 0; i--) {
        state = state * 6364136223846793005ULL + 1442695040888963407ULL;
        int j = (int)((state >> 33) % (uint64_t)(i + 1));
        int t = perm[i]; perm[i] = perm[j]; perm[j] = t;
    }

    for (int k = 0; k < N; k++)
        nodes[perm[k]].next = &nodes[perm[(k + 1) % N]];

    Node *cur = &nodes[perm[0]];
    uint64_t s = 0;

    champsim_roi_begin();
    for (int p = 0; p < passes; p++)
        for (int i = 0; i < N; i++) {
            s = s * 31 + (uint64_t)cur->value;
            cur = cur->next;
        }
    champsim_roi_end();

    printf("Checksum: %llu\n", (unsigned long long)s);
    return 0;
}
