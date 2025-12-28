class Solution:
    def countNegatives(self, grid: List[List[int]]) -> int:
        def firstNeg(row):
            lo, hi = 0, len(row)
            while lo < hi:
                mid = (lo + hi) // 2
                if row[mid] < 0:
                    hi = mid
                else:
                    lo = mid + 1
            return lo

        cnt = 0
        for row in grid:
            idx = firstNeg(row)
            cnt += len(row) - idx
        return cnt
