import fileparser as f
import algorithms as alg
import dateutil.parser
import datetime as d

students = f.parse_students()
adv_prog = "582103"
intro_prog = "581325"


def process_students(students):
    processed_students = []
    for student in students:
        record = [{'grade': int(attempt.grade),
                   'id': str(attempt.course.id_num),
                   'date': dateutil.parser.parse(attempt.date)}
                  for attempt
                  in student.attempts]
        record.sort(key=lambda a: a['date'])
        processed_students.append(record)
    return processed_students

def next_semester_date(date, springmonth, fallmonth):
    month = date.month
    if month < fallmonth:
        return d.datetime(date.year, fallmonth, 1, 0, 0, 0, 0)
    else:
        return d.datetime(date.year + 1, springmonth, 1, 0, 0, 0, 0)

#partitions the student data by semester
#assumes that the data is sorted chronologically
def partition_by_semester(student, springmonth=1, fallmonth=9):
    partition = []
    deadline = next_semester_date(student[0]['date'], springmonth, fallmonth)
    cur_partition = []
    for course in student:
        if course['date'] < deadline:
            cur_partition.append(course)
        else:
            deadline = next_semester_date(course['date'],
                                          springmonth,
                                          fallmonth)
            partition.append(cur_partition)
            cur_partition = [course]
    return partition

def replace_id(original, new, transactions):
    for transcript in transactions:
        for a in transcript:
            if a['id'] == original:
                a['id'] = new

def strip_all_but_codes(lists):
    result = []
    for courselist in lists:
        result.append([int(course['id']) for course in courselist])
    return result

def tuplify(students):
    result = []
    for student in students:
        courseaccum = []
        for course in student:
            courseaccum.append((int(course['id']), course['grade']))
        result.append(courseaccum)
    return result

#goes through student data and truncates course list
#after if finds course with any of the specified grades
#filters out a student if such course is not found
#assumes attempts are chronologically sorted
def get_until_course_grade(students, course_id, grades):
    accum = []
    for student in students:
        for i in xrange(len(student)):
            if student[i]['id'] == course_id and student[i]['grade'] in grades:
                accum.append(student[:i])
    return accum

def flatten_a_level(lists):
    result = []
    for courselistlist in lists:
        for courselist in courselistlist:
            result.append(courselist)
    return result

def unique_courses_from_codes(students):
    result_st = set([])
    for student in students:
        for course in student:
            result_st.add(course)
    result_list = list(result_st)
    result_list.sort()
    return result_list

def setify(lists):
    result = []
    for listt in lists:
        result.append(set(listt))
    return result

simple_data = process_students(students)
simpler_semester_data = strip_all_but_codes(flatten_a_level(
    [partition_by_semester(student) for student in simple_data]))
simpler_data = setify(strip_all_but_codes(simple_data))
almost_as_simple_data = setify(tuplify(simple_data))
unique_simpler_courses = unique_courses_from_codes(simpler_semester_data)
unique_grade_courses = unique_courses_from_codes(almost_as_simple_data)


# returns true if the student has course codes listed on their
# student record with grades that are in the argument 'grades'
# (yes I know the method is pretty hacky, but whatever)
def in_sets_test(simple_student, course_codes, grades):
    satisfied = True
    for code in course_codes:
        for record in simple_student:
            if str(record['id']) == str(code) and record['grade'] in grades:
                satisfied = True
                break
            satisfied = False
        if not satisfied:
            break
    return satisfied

def in_only_codes_set(transaction_as_codes, course_codes):
    satisfied = True
    for code in course_codes:
        for course_id in transaction_as_codes:
            if int(course_id) == int(code):
                satisfied = True
                break
        satisfied = False
        if not satisfied:
            break
    return satisfied


def support_for_adv_prog_grade(simple_students, grade):
    has_done_with_grade = lambda student: in_sets_test(student,
                                                       [adv_prog],
                                                       [grade])
    return alg.relative_frequency(simple_students, has_done_with_grade)

# support_for_adv_prog_grade(simple_data, 4)
# 0.22662889518413598

# support_for_adv_prog_grade(simple_data, 2)
# 0.10835694050991501

# support_for_adv_prog_grade(simple_data, 0)
# 0.051699716713881017


def confidence_for_intro_to_adv(simple_students, intro_grade, adv_grade):
    intro_with_grade = lambda student: in_sets_test(student,
                                                    [intro_prog],
                                                    [intro_grade])
    adv_with_grade = lambda student: in_sets_test(student,
                                                  [adv_prog],
                                                  [adv_grade])
    return alg.confidence(simple_students, intro_with_grade, adv_with_grade)


# assumes transcript is sorted by date
# returns a copy of transcript with all courses started later than the first course which matches course_id removed
def truncate_after_match(transcript, course_id):
    found = False
    for i, a in enumerate(transcript):
        if found and a['date'] > transcript[i - 1]['date']:
            return transcript[:i]
        if a['id'] == course_id:
            found = True
    if not found:
        transcript.append({'grade': -1, 'id': course_id, 'date': dateutil.parser.parse("1-1-2100")})
    return transcript


def take_best_attempt_only(transcript):
    d = {}
    for a in transcript:
        id = a['id']
        if id not in d.keys() or a['grade'] > d[id]['grade']:
            d[id] = a
    if intro_prog not in d.keys():
        d[intro_prog] = {'grade': -1, 'id': intro_prog, 'date': dateutil.parser.parse("1-1-1900")}
    return sorted(d.values(), key=lambda a: a['date'])

decimals = 3

def print_confidence_for_intro_to_adv_all_grade_combinations(simple_students):
    x = [-1, 0, 2, 4]
    print("a\\b -1 0 2 4 row_sup")
    for a in x:
        ans = []
        for b in x:
            ans.append(
                  confidence_for_intro_to_adv(simple_students, a, b),
            )
        support_count = 0
        print(a, " ")
        for i in range(len(x)):
            support_count += alg.absolute_frequency(
                simple_students,
                lambda t: in_sets_test(t, [intro_prog], [a]) and in_sets_test(t, [adv_prog], [x[i]])
              )
            print(round(ans[i], decimals), " ")
        print(support_count)
    print()




# print_confidence_for_intro_to_adv_all_grade_combinations(simple_data)
# 0 0 0.4107142857142857 23
# 0 2 0.35714285714285715 20
# 0 4 0.17857142857142858 10
#
# 2 0 0.24183006535947713 37
# 2 2 0.477124183006536 73
# 2 4 0.2875816993464052 44
#
# 4 0 0.08060453400503778 32
# 4 2 0.19395465994962216 77
# 4 4 0.6498740554156172 258

# print_confidence_for_intro_to_adv_all_grade_combinations([truncate_after_match(t, adv_prog) for t in simple_data])
# 0 0 0.39215686274509803 20
# 0 2 0.1568627450980392 8
# 0 4 0.09803921568627451 5

# 2 0 0.24161073825503357 36
# 2 2 0.3825503355704698 57
# 2 4 0.24161073825503357 36

# 4 0 0.0625 24
# 4 2 0.171875 66
# 4 4 0.6354166666666666 244
replace_id(55056, 55521, simple_data)
replace_id(55063, 55522, simple_data)

#pairs = [(581325, 582103), (55521, 55522), (581325, 582103), (57016, 57017)]
#for x in pairs:
#    intro_prog = str(x[0])
#    adv_prog = str(x[1])
#    print(x[0], x[1])
#    print_confidence_for_intro_to_adv_all_grade_combinations(
#        [take_best_attempt_only(truncate_after_match(t, adv_prog)) for t in simple_data]
#    )


# 0 0 0.2916666666666667 7
# 0 2 0.0 0
# 0 4 0.08333333333333333 2

# 2 0 0.22794117647058823 31
# 2 2 0.375 51
# 2 4 0.23529411764705882 32

# 4 0 0.0625 24
# 4 2 0.16666666666666666 64
# 4 4 0.6354166666666666 244

#print(alg.absolute_frequency(
#[take_best_attempt_only(truncate_after_match(t, adv_prog)) for t in simple_data],
#lambda t: in_sets_test(t, [adv_prog], [4])
#) /
#alg.absolute_frequency(
#[take_best_attempt_only(truncate_after_match(t, adv_prog)) for t in simple_data],
#lambda t: in_sets_test(t, [adv_prog], [0, 2, 4])
#)
#)

# count how many times a student has the intro on record
# for datum in simple_data:
#    if (in_sets_test(datum, ["581325"], [0, 2, 4])):
#        count = 0
#        for courses in datum:
#            if (str(courses['id']) == "581325"):
#                count += 1
#        print(count)

adv_g4_truncated = setify(tuplify(get_until_course_grade
                                  (simple_data, adv_prog, [4])))

adv_any_strip_grades = setify(
    strip_all_but_codes(
        get_until_course_grade(simple_data, adv_prog, [0, 2, 4])))

#alg.apriori(0.1, unique_grade_courses, adv_g4_truncated)[-10:]
#[({(581324, 4), (581325, 4), (582514, 4)}, 0.2225609756097561),
# ({(581325, 4), (582104, 4), (582514, 4)}, 0.11585365853658537),
# ({(57039, 4), (581324, 4), (581325, 4)}, 0.14939024390243902),
# ({(57039, 4), (581324, 4), (582104, 4)}, 0.10060975609756098),
# ({(57039, 4), (581324, 4), (582514, 4)}, 0.14939024390243902),
# ({(57039, 4), (581325, 4), (582514, 4)}, 0.12804878048780488),
# ({(581324, 4), (582104, 4), (582514, 4)}, 0.11890243902439024),
# ({(57016, 4), (57043, 4), (57598, 4)}, 0.10060975609756098),
# ({(581324, 4), (581325, 4), (582104, 4), (582514, 4)}, 0.10060975609756098),
# ({(57039, 4), (581324, 4), (581325, 4), (582514, 4)}, 0.11585365853658537)]
#
#alg.apriori(0.3, unique_simpler_courses, adv_any_strip_grades)[-10:]
#[({582104, 582514}, 0.358974358974359),
# ({57039, 581324, 582514}, 0.3230769230769231),
# ({57039, 581325, 582514}, 0.3247863247863248),
# ({581324, 581325, 582514}, 0.4717948717948718),
# ({581324, 581325, 582104}, 0.37094017094017095),
# ({581324, 582104, 582514}, 0.35213675213675216),
# ({581325, 582104, 582514}, 0.35213675213675216),
# ({57039, 581324, 581325}, 0.3435897435897436),
# ({581324, 581325, 582104, 582514}, 0.3452991452991453),
# ({57039, 581324, 581325, 582514}, 0.3162393162393162)]
#alg.apriori(0.1, unique_simpler_courses, adv_any_strip_grades)[-10:]
#[({57039, 57049, 581324, 581325, 582102, 582513, 582514}, 0.11282051282051282),
# ({57039, 57049, 581324, 582102, 582104, 582513, 582514}, 0.10427350427350428),
# ({57039, 57049, 581325, 582102, 582104, 582513, 582514}, 0.10427350427350428),
# ({57049, 581324, 581325, 582102, 582104, 582513, 582514},
#  0.11452991452991453),
# ({57039, 57049, 581324, 581325, 582102, 582104, 582513}, 0.1094017094017094),
# ({57039, 57049, 581324, 581325, 582104, 582513, 582514}, 0.1111111111111111),
# ({57039, 57049, 581324, 581325, 582102, 582104, 582514}, 0.11452991452991453),
# ({57016, 57017, 57043, 57047, 57594, 57598, 581325}, 0.10085470085470086),
# ({57039, 581324, 581325, 582102, 582104, 582513, 582514},
#  0.13675213675213677),
# ({57039, 57049, 581324, 581325, 582102, 582104, 582513, 582514},
#  0.10427350427350428)]
#
def count_transcript_lenghts(students):
    lengths = {}
    for student in students:
        length = len(student)
        if length not in lengths:
            lengths[length] = 1
        else:
            lengths[length] += 1
    return lengths


adv_g4_stripped = get_until_course_grade(simple_data, adv_prog, [4])
adv_g4_stripped = setify(strip_all_but_codes(adv_g4_stripped))

def take_out_course_not_grade(course_id, accepted_grades,
                              students = simple_data):
    result = []
    for student in students:
        accum_course = []
        for course in student:
            if course['id'] != course_id:
                accum_course.append(course)
            elif course['grade'] in accepted_grades:
                accum_course.append(course)
        result.append(accum_course)
    return result

def data_asked():
    results = []
    threshold_for_rule = 0.1
    last_n = 30
    the_courses = unique_courses_from_codes(adv_g4_stripped)
    large_freq_itemsets = alg.apriori(threshold_for_rule,
                                      the_courses,
                                      adv_g4_stripped)[-last_n:]
    premises = []
    for itemsetsup in large_freq_itemsets:
        premises.append(itemsetsup[0])
    the_base_set = setify(strip_all_but_codes
                          (take_out_course_not_grade(adv_prog, [4])))
    for fr_itemset in premises:
        premise = lambda(tr): fr_itemset <= tr
        consequent = lambda(tr): adv_prog in tr
        conf = alg.confidence(the_base_set, premise, consequent)
        results.append({'premise': fr_itemset, 'conf': conf})
    return results
