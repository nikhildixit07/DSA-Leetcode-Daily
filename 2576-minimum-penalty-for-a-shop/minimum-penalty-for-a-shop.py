class Solution:
    def bestClosingTime(self, customers: str) -> int:
        n = len(customers)
        suffixY = [0] * (n + 1)

        for i in range(n - 1, -1, -1):
            suffixY[i] = suffixY[i + 1] + (customers[i] == 'Y')

        best = float('inf')
        ans = 0
        openN = 0

        for j in range(n + 1):
            penalty = openN + suffixY[j]
            if penalty < best:
                best = penalty
                ans = j
            if j < n and customers[j] == 'N':
                openN += 1

        return ans
