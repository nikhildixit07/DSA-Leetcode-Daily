class Solution:
    def minDeletionSize(self, strs):
        n = len(strs)
        m = len(strs[0])
        deleted = 0
        sorted_row = [False] * (n - 1)

        for c in range(m):
            bad = False
            for i in range(n - 1):
                if not sorted_row[i] and strs[i][c] > strs[i + 1][c]:
                    bad = True
                    break

            if bad:
                deleted += 1
                continue

            for i in range(n - 1):
                if not sorted_row[i] and strs[i][c] < strs[i + 1][c]:
                    sorted_row[i] = True

        return deleted
