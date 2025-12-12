class Solution:
    def countMentions(self, numberOfUsers, events):
        ev = []
        for typ, t, s in events:
            ev.append((int(t), 0 if typ == "OFFLINE" else 1, typ, s))
        ev.sort()
        mentions = [0] * numberOfUsers
        offline_until = [0] * numberOfUsers
        for time, _, typ, s in ev:
            if typ == "OFFLINE":
                uid = int(s)
                offline_until[uid] = time + 60
            else:
                tokens = s.split()
                for tok in tokens:
                    if tok == "ALL":
                        for i in range(numberOfUsers):
                            mentions[i] += 1
                    elif tok == "HERE":
                        for i in range(numberOfUsers):
                            if offline_until[i] <= time:
                                mentions[i] += 1
                    else:
                        idx = int(tok[2:])
                        mentions[idx] += 1
        return mentions
