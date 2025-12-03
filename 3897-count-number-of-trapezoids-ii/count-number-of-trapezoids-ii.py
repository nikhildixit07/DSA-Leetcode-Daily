class Solution:
    def countTrapezoids(self, points):
        n = len(points)
        lp = defaultdict(set)
        for i in range(n):
            x1, y1 = points[i]
            for j in range(i+1, n):
                x2, y2 = points[j]
                A = y2 - y1
                B = x1 - x2
                C = A * x1 + B * y1
                g = gcd(gcd(abs(A), abs(B)), abs(C))
                if g == 0:
                    g = 1
                A //= g; B //= g; C //= g
                if A < 0 or (A == 0 and B < 0):
                    A = -A; B = -B; C = -C
                lp[(A, B, C)].add(i); lp[(A, B, C)].add(j)

        sg = defaultdict(list)
        for (A, B, C), s in lp.items():
            k = len(s)
            if k < 2:
                continue
            g = gcd(A, B)
            if g == 0:
                g = 1
            sa = A // g; sb = B // g
            if sa < 0 or (sa == 0 and sb < 0):
                sa = -sa; sb = -sb
            sg[(sa, sb)].append(k * (k - 1) // 2)

        total_pairs = 0
        for v in sg.values():
            s = sum(v)
            s2 = sum(x * x for x in v)
            total_pairs += (s * s - s2) // 2

        mid = defaultdict(list)
        for i in range(n):
            x1, y1 = points[i]
            for j in range(i+1, n):
                x2, y2 = points[j]
                mid[(x1 + x2, y1 + y2)].append((i, j))

        parallelograms = 0
        for pairs in mid.values():
            m = len(pairs)
            if m < 2:
                continue
            for a in range(m):
                i, j = pairs[a]
                xi, yi = points[i]; xj, yj = points[j]
                for b in range(a+1, m):
                    k, l = pairs[b]
                    if i == k or i == l or j == k or j == l:
                        continue
                    xk, yk = points[k]; xl, yl = points[l]
                    if (xk - xi) * (yj - yi) != (yk - yi) * (xj - xi):
                        parallelograms += 1

        return total_pairs - parallelograms