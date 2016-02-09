def support_count(x, transactions):
    count = 0
    for set in transactions:
        count += (x <= set)
    return count

# returns the number of transactions that satisfy
# the given predicate
def absolute_frequency(transactions, pred):
    count = 0
    for transaction in transactions:
        if(pred(transaction)):
            count += 1
    return count


def support(x, transactions):
    return support_count(x, transactions) / len(transactions)

# returns the relative amount of transactions that
# satisfy the given predicate
def relative_frequency(transactions, pred):
    set_support_count = absolute_frequency(transactions, pred) + 0.0
    return set_support_count / len(transactions)

# calculates the relative amount of transactions
# that satisfy the association rule premise -> conclusion
# premise and conclusion are both predicates
def confidence(transactions, premise, conclusion):
    union = lambda trnsc: premise(trnsc) and conclusion(trnsc)
    rule_support_count = absolute_frequency(transactions, union) + 0.0
    premise_support_count = absolute_frequency(transactions, premise)
    if premise_support_count == 0:
        return 0
    return rule_support_count / premise_support_count

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
