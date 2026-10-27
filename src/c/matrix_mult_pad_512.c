#include <stdio.h>

#define N 512

/* 
 * Array padding: Second bracket changed to N + 4 (260 ints).
 * First bracket remains N (256).
 * This eliminates power-of-two cache conflict misses.
 */
static int A[N][N + 4];
static int B[N][N + 4];
static int C[N][N + 4];

/* 
 * ChampSim ROI marker functions.
 */
__attribute__((noinline))
void champsim_roi_begin(void) {
    asm volatile("");
}

__attribute__((noinline))
void champsim_roi_end(void) {
    asm volatile("");
}

int main(void) {
    /* Initialization: loops still run up to N */
    for (int i = 0; i < N; i++) {
        for (int j = 0; j < N; j++) {
            A[i][j] = (i * 3 + j) % 100;
            B[i][j] = (i + j * 5) % 100;
            C[i][j] = 0;
        }
    }

    /* ROI marker begin */
    champsim_roi_begin();

    /* Original i-j-k loop order */
    for (int i = 0; i < N; i++) {
        for (int j = 0; j < N; j++) {
            for (int k = 0; k < N; k++) {
                C[i][j] += A[i][k] * B[k][j];
            }
        }
    }

    /* ROI marker end */
    champsim_roi_end();

    /* 64-bit checksum calculation */
    long long checksum = 0;
    for (int i = 0; i < N; i++) {
        for (int j = 0; j < N; j++) {
            checksum += C[i][j];
        }
    }

    printf("Checksum: %lld\n", checksum);

    return 0;
}
