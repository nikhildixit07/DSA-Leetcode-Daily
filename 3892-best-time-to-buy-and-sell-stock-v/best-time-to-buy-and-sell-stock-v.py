class Solution:
    def maximumProfit(self, prices, k):
        NEG = -10**30
        dp0 = [0] + [NEG] * k
        dp1 = [NEG] * (k + 1)
        dp2 = [NEG] * (k + 1)

        for p in prices:
            ndp0 = dp0[:]
            ndp1 = dp1[:]
            ndp2 = dp2[:]

            for t in range(k + 1):
                ndp1[t] = max(ndp1[t], dp0[t] - p)
                ndp2[t] = max(ndp2[t], dp0[t] + p)

                if t + 1 <= k:
                    ndp0[t + 1] = max(
                        ndp0[t + 1],
                        dp1[t] + p,
                        dp2[t] - p
                    )

            dp0, dp1, dp2 = ndp0, ndp1, ndp2

        return max(dp0)