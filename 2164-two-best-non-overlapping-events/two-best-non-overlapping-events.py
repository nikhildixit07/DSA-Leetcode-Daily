class Solution:
    def maxTwoEvents(self, events):
        events.sort()
        n = len(events)

        suffixMax = [0] * (n + 1)
        for i in range(n - 1, -1, -1):
            suffixMax[i] = max(suffixMax[i + 1], events[i][2])

        starts = [e[0] for e in events]
        ans = 0

        for i in range(n):
            val = events[i][2]
            j = bisect_right(starts, events[i][1])
            ans = max(ans, val + suffixMax[j])

        return ans
