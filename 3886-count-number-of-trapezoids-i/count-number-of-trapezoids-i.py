from collections import defaultdict
class Solution:
    def countTrapezoids(self, points):
        MOD = 10**9+7
        g = defaultdict(int)
        for x,y in points:
            g[y] += 1
        cnts = [v*(v-1)//2 % MOD for v in g.values()]
        ans = 0
        s = 0
        for c in cnts:
            ans = (ans + c * s) % MOD
            s = (s + c) % MOD
        return ans
