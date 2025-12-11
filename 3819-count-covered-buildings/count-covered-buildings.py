class Solution:
    def countCoveredBuildings(self, n, buildings):
        from collections import defaultdict
        if not buildings:
            return 0
        min_y = defaultdict(lambda: 10**9)
        max_y = defaultdict(lambda: -10**9)
        min_x = defaultdict(lambda: 10**9)
        max_x = defaultdict(lambda: -10**9)
        pts = set()
        for x, y in buildings:
            pts.add((x, y))
            if y < min_y[x]: min_y[x] = y
            if y > max_y[x]: max_y[x] = y
            if x < min_x[y]: min_x[y] = x
            if x > max_x[y]: max_x[y] = x
        ans = 0
        for x, y in pts:
            if min_y[x] < y < max_y[x] and min_x[y] < x < max_x[y]:
                ans += 1
        return ans