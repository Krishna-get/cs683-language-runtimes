#include <stdio.h>

#define N 512

static int A[N][N], B[N][N], C[N][N];

__attribute__((noinline)) void champsim_roi_begin(void) { __asm__ volatile(""); }
__attribute__((noinline)) void champsim_roi_end(void)   { __asm__ volatile(""); }

int main(void)
{
    for (int i = 0; i < N; i++)
        for (int k = 0; k < N; k++) {
            A[i][k] = 300 + (i + k) % 100;
            B[i][k] = 300 + (2 * i + k) % 100;   /* B[k][j] = 300 + (2k+j)%100 */
            C[i][k] = 0;
        }

    champsim_roi_begin();
    for (int i = 0; i < N; i++)
        for (int j = 0; j < N; j++)
            for (int k = 0; k < N; k++)
                C[i][j] += A[i][k] * B[k][j];
    champsim_roi_end();

    long long sum = 0;
    for (int i = 0; i < N; i++)
        for (int j = 0; j < N; j++)
            sum += C[i][j];
    printf("Checksum: %lld\n", sum);
    return 0;
}
