class Solution:
    def countPartitions(self, nums):
        return len(nums) - 1 if sum(nums) % 2 == 0 else 0