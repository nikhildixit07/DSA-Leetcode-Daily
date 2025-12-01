class Solution:
    def maxRunTime(self, n, batteries):
        s = sum(batteries)
        l, r = 0, s // n
        def ok(t):
            return sum(min(b, t) for b in batteries) >= n * t
        while l <= r:
            m = (l + r) // 2
            if ok(m):
                l = m + 1
            else:
                r = m - 1
        return r