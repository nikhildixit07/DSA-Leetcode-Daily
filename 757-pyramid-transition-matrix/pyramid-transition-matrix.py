class Solution:
    def pyramidTransition(self, bottom, allowed):
        adj = {}
        for a,b,c in allowed:
            adj.setdefault(a+b, []).append(c)

        def dfs(row):
            if len(row) == 1:
                return True

            options = [[]]
            for i in range(len(row)-1):
                pair = row[i] + row[i+1]
                if pair not in adj:
                    return False
                possible = adj[pair]
                new_options = []
                for prefix in options:
                    for ch in possible:
                        new_options.append(prefix + [ch])
                options = new_options

            for nxt in options:
                if dfs("".join(nxt)):
                    return True
            return False

        return dfs(bottom)
