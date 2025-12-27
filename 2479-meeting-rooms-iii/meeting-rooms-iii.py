class Solution:
    def mostBooked(self, n, meetings):
        meetings.sort()
        
        freeRooms = list(range(n))
        heapq.heapify(freeRooms)
        
        busyRooms = []
        count = [0] * n

        for start, end in meetings:
            while busyRooms and busyRooms[0][0] <= start:
                _, room = heapq.heappop(busyRooms)
                heapq.heappush(freeRooms, room)

            duration = end - start

            if freeRooms:
                room = heapq.heappop(freeRooms)
                heapq.heappush(busyRooms, (end, room))
            else:
                endTime, room = heapq.heappop(busyRooms)
                heapq.heappush(busyRooms, (endTime + duration, room))

            count[room] += 1

        maxMeetings = max(count)
        for i in range(n):
            if count[i] == maxMeetings:
                return i