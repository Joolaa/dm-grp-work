import fileparser
import dateutil.parser
import algorithms


students = fileparser.parse_students()
courses = []

for student in students:
    for attempt in student.attempts:
        courses.append(attempt.course.id_num)

courses = set(courses)

def group(attempts):
    attempts.sort(key=lambda a: dateutil.parser.parse(a.date))
    response = [[attempts[0]]]
    for i in range(1, len(attempts)):
        if attempts[i].date != response[-1][-1].date:
            response.append([attempts[i]])
        else:
            response[-1].append(attempts[i])
    return [set(a.course.id_num for a in x) for x in response]

data = list(group(s.attempts) for s in students)

print(sorted(algorithms.apriori_sequence(0.05, courses, data, 8), key=lambda x: x[1], reverse=True)[0:30])