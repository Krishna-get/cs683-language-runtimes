public class MatrixMultWarmupOnly {
    static final int N = 512;
    static int[][] A = new int[N][N];
    static int[][] B = new int[N][N];
    static int[][] C = new int[N][N];

    public static void multiply() {
        for (int i = 0; i < N; i++) {
            for (int j = 0; j < N; j++) {
                int sum = 0;
                for (int k = 0; k < N; k++) {
                    sum += A[i][k] * B[k][j];
                }
                C[i][j] = sum;
            }
        }
    }

    public static void main(String[] args) {
        for (int i = 0; i < N; i++) {
            for (int j = 0; j < N; j++) {
                A[i][j] = 300 + (i + j) % 100;
                B[i][j] = 300 + (i * 2 + j) % 100;
            }
        }

        // Run 5 warmup iterations
        for (int w = 0; w < 5; w++) {
            multiply();
        }

        // Exit immediately before the final active run
        System.exit(0);
    }
}
