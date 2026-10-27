public class LinkedList {
    static final int N = 524288;

    static class Node {
        int value;
        Node next;
        Node(int v) { value = v; }
    }

    public static void main(String[] args) {
        int passes = (args.length > 0) ? Integer.parseInt(args[0]) : 2;

        Node[] nodes = new Node[N];
        int[] perm = new int[N];
        for (int i = 0; i < N; i++) {
            nodes[i] = new Node(300 + (i * 7 + 3) % 1000);
            perm[i] = i;
        }

        long state = 12345L;
        for (int i = N - 1; i > 0; i--) {
            state = state * 6364136223846793005L + 1442695040888963407L;
            int j = (int) ((state >>> 33) % (long) (i + 1));
            int t = perm[i]; perm[i] = perm[j]; perm[j] = t;
        }

        for (int k = 0; k < N; k++)
            nodes[perm[k]].next = nodes[perm[(k + 1) % N]];

        Node cur = nodes[perm[0]];
        long s = 0;
        for (int p = 0; p < passes; p++)
            for (int i = 0; i < N; i++) {
                s = s * 31 + cur.value;
                cur = cur.next;
            }

        System.out.println("Checksum: " + Long.toUnsignedString(s));
    }
}
