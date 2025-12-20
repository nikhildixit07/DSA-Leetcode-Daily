class Solution:
    def minDeletionSize(self, strs: List[str]) -> int:
        m = len(strs)
        n = len(strs[0])
        res = 0
        
        for c in range(n):
            for r in range(1, m):
                if strs[r][c] < strs[r-1][c]:
                    res += 1
                    break
        return res
