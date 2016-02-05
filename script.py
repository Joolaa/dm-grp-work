import fileparser as f
import algorithms as alg
import dateutil.parser

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

simple_data = process_students(students)


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
    return transcript


def take_best_attempt_only(transcript):
    d = {}
    for a in transcript:
        id = a['id']
        if id not in d.keys() or a['grade'] > d[id]['grade']:
            d[id] = a
    return sorted(d.values(), key=lambda a: a['date'])


def print_confidence_for_intro_to_adv_all_grade_combinations(simple_students):
    for a in [0, 2, 4]:
        for b in [0, 2, 4]:
            print(
                  a, b,
                  confidence_for_intro_to_adv(simple_students, a, b),
                  alg.absolute_frequency(
                    simple_students,
                    lambda t: in_sets_test(t, [intro_prog], [a]) and in_sets_test(t, [adv_prog], [b])
                  )
            )

print_confidence_for_intro_to_adv_all_grade_combinations(simple_data)
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

print_confidence_for_intro_to_adv_all_grade_combinations([truncate_after_match(t, adv_prog) for t in simple_data])
# 0 0 0.39215686274509803 20
# 0 2 0.1568627450980392 8
# 0 4 0.09803921568627451 5

# 2 0 0.24161073825503357 36
# 2 2 0.3825503355704698 57
# 2 4 0.24161073825503357 36

# 4 0 0.0625 24
# 4 2 0.171875 66
# 4 4 0.6354166666666666 244

print_confidence_for_intro_to_adv_all_grade_combinations(
    [take_best_attempt_only(truncate_after_match(t, adv_prog)) for t in simple_data]
)
# 0 0 0.39215686274509803 20
# 0 2 0.1568627450980392 8
# 0 4 0.09803921568627451 5

# 2 0 0.24161073825503357 36
# 2 2 0.3825503355704698 57
# 2 4 0.24161073825503357 36

# 4 0 0.0625 24
# 4 2 0.171875 66
# 4 4 0.6354166666666666 244

# count how many times a student has the intro on record
# for datum in simple_data:
#    if (in_sets_test(datum, ["581325"], [0, 2, 4])):
#        count = 0
#        for courses in datum:
#            if (str(courses['id']) == "581325"):
#                count += 1
#        print(count)
