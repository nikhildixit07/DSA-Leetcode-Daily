class Solution:
    def specialTriplets(self, nums: List[int]) -> int:
        MOD = 10**9 + 7
        right = Counter(nums)
        left = Counter()
        ans = 0
        for x in nums:
            right[x] -= 1
            d = x * 2
            ans = (ans + left[d] * right[d]) % MOD
            left[x] += 1
        return ans
