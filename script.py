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
def get_until_course_grade(students, course_id, grades, includeLast = False):
    accum = []
    for student in students:
        for i in range(len(student)):
            if student[i]['id'] == course_id and student[i]['grade'] in grades:
                accum.append(student[:i + includeLast])
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

replace_id(55056, 55521, simple_data)
replace_id(55063, 55522, simple_data)

adv_g4_truncated = setify(tuplify(get_until_course_grade
                                  (simple_data, adv_prog, [4])))

adv_any_strip_grades = setify(
    strip_all_but_codes(
        get_until_course_grade(simple_data, adv_prog, [0, 2, 4])))

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
        premise = lambda tr: fr_itemset <= tr
        consequent = lambda tr: adv_prog in tr
        print(the_base_set, "\n", fr_itemset, "\n", adv_prog, "\n")
        conf = alg.confidence(the_base_set, premise, consequent)
        results.append({'premise': fr_itemset, 'conf': conf})
    return results

def find_interesting_association_rules():
    support_threshold = 0.1
    target_course = "582103"
    target_grade = 4
    target_int = int(target_course) * 10 + target_grade
    transcripts = get_until_course_grade(simple_data, target_course, [0, 2, 4], True)
    transcripts = [set(int(a['id']) * 10 + int(a['grade']) for a in take_best_attempt_only(t)) for t in transcripts]
    apriori_initial_itemsets = [{x} | {target_int} for x in unique_courses_from_codes(transcripts) if x / 10 != int(target_course)]
    frequent_itemsets = alg.apriori_new(support_threshold, apriori_initial_itemsets, transcripts)
    frequent_itemsets.sort(key=lambda x: x[1], reverse=True)
    frequent_itemsets = [x for x in frequent_itemsets if target_int in x[0]]
    itemset_support_confidences = [x + (x[1] / alg.support(x[0] - {target_int}, transcripts),) for x in frequent_itemsets]
    itemset_support_confidence_lifts = [x + (x[2] / alg.support({target_int}, transcripts),) for x in itemset_support_confidences]
    itemset_support_confidence_lift_interestingness = [x + (x[3] if x[3] >= 1 else 1.0/x[3],) for x in itemset_support_confidence_lifts]
    itemset_support_confidence_lift_interestingness.sort(key=lambda x: x[-1], reverse=True)
    print()
    for x in itemset_support_confidence_lift_interestingness:
        print("{} -> {{{}}}".format(x[0] - {target_int}, target_int))
        print("support", round(x[1], decimals))
        print("confidence", round(x[2], decimals))
        print("lift", round(x[3], decimals))
        print("interestingness", round(x[4], decimals))
        print()

find_interesting_association_rules()
