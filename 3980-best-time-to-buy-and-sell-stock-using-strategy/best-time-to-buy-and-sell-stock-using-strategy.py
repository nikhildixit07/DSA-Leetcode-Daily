class Solution:
    def maxProfit(self, prices, strategy, k):
        n = len(prices)

        base = 0
        for i in range(n):
            base += strategy[i] * prices[i]

        sp = [0] * (n + 1)
        pp = [0] * (n + 1)

        for i in range(n):
            sp[i + 1] = sp[i] + strategy[i] * prices[i]
            pp[i + 1] = pp[i] + prices[i]

        half = k // 2
        best = 0

        for l in range(n - k + 1):
            r = l + k
            m = l + half

            original = sp[r] - sp[l]
            forced_sell = pp[r] - pp[m]

            gain = forced_sell - original
            if gain > best:
                best = gain

        return base + best
