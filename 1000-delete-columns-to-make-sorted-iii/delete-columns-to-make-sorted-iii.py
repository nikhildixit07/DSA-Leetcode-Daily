class Solution:
    def minDeletionSize(self, strs: List[str]) -> int:
        m = len(strs[0])
        dp = [1] * m
        ans = 1

        for j in range(m):
            for i in range(j):
                good = True
                for s in strs:
                    if s[i] > s[j]:
                        good = False
                        break
                if good:
                    dp[j] = max(dp[j], dp[i] + 1)
            ans = max(ans, dp[j])

        return m - ans
