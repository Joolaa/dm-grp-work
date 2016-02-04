def support_count(x, data):
    count = 0
    for set in data:
        count += (x <= set)
    return count


def support(x, data):
    return support_count(x, data) / len(data)


def generate(lists):
    response = []
    if len(lists) <= 1:
        return response

    d = {}
    for x in lists:
        x = list(x)
        b = tuple(x[0:-1])
        if b not in d.keys():
            d[b] = []
        d[b].append(x[-1])

    for k in d.keys():
        arr = d[k]
        for r in range(len(arr)):
            for l in range(r):
                response.append(set(k) | {arr[l]} | {arr[r]})

    return response


def apriori(min_support, items, transactions):
    lists = list(set([item]) for item in items)
    response = []

    while len(lists) > 0:
        print("generating candidates")
        candidates = generate(lists)
        lists = []
        print("calculating support for {} candidates".format(len(candidates)))
        for candidate in candidates:
            supp = support(candidate, transactions)
            if supp >= min_support:
                lists.append(candidate)
                response.append((candidate, supp))

    return response
