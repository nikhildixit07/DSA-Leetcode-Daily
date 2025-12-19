class Solution:
    def findAllPeople(self, n, meetings, firstPerson):
        meetings.sort(key=lambda x: x[2])

        know = set([0, firstPerson])
        i = 0
        m = len(meetings)

        while i < m:
            time = meetings[i][2]
            graph = defaultdict(list)
            people = set()

            while i < m and meetings[i][2] == time:
                x, y, _ = meetings[i]
                graph[x].append(y)
                graph[y].append(x)
                people.add(x)
                people.add(y)
                i += 1

            q = deque()
            visited = set()

            for p in people:
                if p in know:
                    q.append(p)
                    visited.add(p)

            while q:
                u = q.popleft()
                for v in graph[u]:
                    if v not in visited:
                        visited.add(v)
                        q.append(v)

            know |= visited

        return list(know)
