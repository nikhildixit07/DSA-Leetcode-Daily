class Solution:
    def maximumHappinessSum(self, happiness, k):
        happiness.sort(reverse=True)
        ans = 0
        for i in range(k):
            val = happiness[i] - i
            if val > 0:
                ans += val
        return ans
