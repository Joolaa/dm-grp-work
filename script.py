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

simple_data = process_students(students)
simpler_semester_data = strip_all_but_codes(flatten_a_level(
    [partition_by_semester(student) for student in simple_data]))
unique_simpler_courses = unique_courses_from_codes(simpler_semester_data)


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
