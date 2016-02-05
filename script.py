import fileparser as f
import algorithms as alg

students = f.parse_students()

def process_students(students):
    processed_students = []
    for student in students:
        record = [{'grade': attempt.grade, 'id': attempt.course.id_num}
                  for attempt
                  in student.attempts]
        processed_students.append(record)
    return processed_students

simple_data = process_students(students)

#returns true if the student has course codes listed on their
#student record with grades that are in the argument 'grades'
#(yes I know the method is pretty hacky, but whatever)
def in_sets_test(simple_student, course_codes, grades):
    satisfied = True
    for code in course_codes:
        for record in simple_student:
            if(str(record['id']) == str(code) and record['grade'] in grades):
                satisfied = True
                break
            satisfied = False
        if(not satisfied):
            break
    return satisfied

def support_for_adv_prog_grade(simple_students, grade):
    adv_prog = "582103"
    has_done_with_grade = lambda student: in_sets_test(student,
                                                       [adv_prog],
                                                       [grade])
    return alg.relative_frequency(simple_students, has_done_with_grade)

#support_for_adv_prog_grade(simple_data, 4)
#0.22662889518413598

#support_for_adv_prog_grade(simple_data, 2)
#0.10835694050991501

#support_for_adv_prog_grade(simple_data, 0)
#0.051699716713881017

def confidence_for_intro_to_adv(simple_students, intro_grade, adv_grade):
    adv_prog = "582103"
    intro_prog = "581325"
    intro_with_grade = lambda student: in_sets_test(student,
                                                    [intro_prog],
                                                    [intro_grade])
    adv_with_grade = lambda student: in_sets_test(student,
                                                  [adv_prog],
                                                  [adv_grade])
    return alg.confidence(simple_data, intro_with_grade, adv_with_grade)

#confidence_for_intro_to_adv(simple_data, 4, 4)
#0.6498740554156172

#confidence_for_intro_to_adv(simple_data, 2, 2)
#0.477124183006536

#confidence_for_intro_to_adv(simple_data, 0, 0)
#0.4107142857142857
