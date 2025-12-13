class Solution:
    def validateCoupons(self, code, businessLine, isActive):
        order = {"electronics": 0, "grocery": 1, "pharmacy": 2, "restaurant": 3}
        res = []
        for c, b, a in zip(code, businessLine, isActive):
            if not a or b not in order or not c:
                continue
            ok = True
            for ch in c:
                if not (ch.isalnum() or ch == "_"):
                    ok = False
                    break
            if ok:
                res.append((order[b], c))
        res.sort(key=lambda x: (x[0], x[1]))
        return [c for _, c in res]
