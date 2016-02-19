def support_count(x, transactions):
    count = 0.0
    for set in transactions:
        count += (x <= set)
    return count

# returns the number of transactions that satisfy
# the given predicate
def absolute_frequency(transactions, pred):
    count = 0.0
    for transaction in transactions:
        if pred(transaction):
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


def apriori_new(min_support, lists, transactions):
    response = []
    accum = []
    for listt in lists:
        supp = support(listt, transactions)
        if supp >= min_support:
            accum.append(listt)
            response.append((listt, supp))
    lists = accum
    accum = []

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

def apriori(min_support, items, transactions):
    return apriori_new(min_support, [set([item]) for item in items], transactions)


import copy

def generate_sequence(lists):
    response = []
    if len(lists) <= 1:
        return response

    dA = {}
    dB = {}
    for x in lists:
        k = list(x)
        k[0] = k[0][1:]
        if len(k[0]) == 0:
            k = k[1:]
        k = tuple(k)
        if k not in dA.keys():
            dA[k] = []
        dA[k].append(x)

    for x in lists:
        x = list(x)
        v = x[-1][-1]
        x[-1] = x[-1][0:-1]
        loner = False
        if len(x[-1]) == 0:
            x = x[0:-1]
            loner = True
        k = tuple(x)
        if k not in dB.keys():
            dB[k] = []
        dB[k].append((v, loner))

    for k in dA.keys():
        for s1 in dA[k]:
            if k in dB.keys():
                for e in dB[k]:
                    loner = e[1]
                    e = e[0]
                    if not loner or (len(s1) == 1 and len(s1[0]) == 1 and e > s1[0][0]):
                        s1_list = list(s1)
                        if e not in s1_list[-1]: # no duplicate events in element
                            s1_list[-1] = s1_list[-1] + (e,)
                            response.append(tuple(s1_list))
                    if loner:
                        response.append(s1 + ((e,),))

    print("Prepruning {} generated candidates".format(len(response)))
    prunedResponse = []
    previous_sequences = [[set(element) for element in prev_sequence] for prev_sequence in lists]
    for sequence in response:
        #print(sequence)
        #continue
        #p = [(set(element) for element in prev_sequence) for prev_sequence in lists]
        c = [set(element) for element in sequence]
        ok = True
        i = 0
        for i_element in range(len(c)):
            for event in c[i_element]:
                #subsequence = sequence
                c[i_element].remove(event)
                subsequence = [e for e in c if e != set()]
                #print(subsequence, list([list(x) for x in previous_sequences]))
                if subsequence not in previous_sequences:
                    ok = False
                c[i_element].add(event)
            if not ok:
                break
        if ok:
            prunedResponse.append(sequence)
    return prunedResponse


def support_count_sequence(x, transactions):
    count = 0
    for sequence in transactions:
        i = 0
        for element in sequence:
            if i == len(x):
                break
            if set(x[i]) <= element:
                i += 1
        count += (i == len(x))
    return count


def support_sequence(x, transactions):
    return support_count_sequence(x, transactions) / len(transactions)


def apriori_sequence(min_support, items, transactions, target_sequence_length):
    lists = list(((item,),) for item in items)
    response = []
    first_go = True
    sequence_length = 1
    while len(lists) > 0 and sequence_length <= target_sequence_length:
        print("generating candidates from {} sequences".format(len(lists)))
        if first_go:
            candidates = lists
            first_go = False
        else:
            candidates = generate_sequence(lists)

        lists = []
        print("calculating support for {} candidates".format(len(candidates)))
        i = 0
        for candidate in candidates:
            if i % 1000 == 0:
                print(i)
            i += 1
            supp = support_sequence(candidate, transactions)
            if supp >= min_support:
                lists.append(candidate)
                if sequence_length == target_sequence_length:
                    response.append((candidate, supp))
        sequence_length += 1

    return response
