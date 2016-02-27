import fileparser
import dateutil.parser
import algorithms

#parse begin
students = fileparser.parse_students()
courses = []
for student in students:
    for attempt in student.attempts:
        courses.append(attempt.course)
courses = set(courses)
courseCodes = set(course.id_num for course in courses)
#parse end

courseYcode=582219#käyttöjärjestelmä
yGrade=0
minsupp=0.2
k_item_set=7
def group(attempts):
    attempts.sort(key=lambda a: dateutil.parser.parse(a.date))
    response = [[attempts[0]]]
    for i in range(1, len(attempts)):
        if attempts[i].date != response[-1][-1].date:
            response.append([attempts[i]])
        else:
            response[-1].append(attempts[i])
    return [set(a.course.id_num for a in x) for x in response]
def preprocess(students,courses,courseCodes,target_course_code,target_grade):
    newCode=target_course_code*1000+target_grade
    newCourse=None
    for course in courses:
        if course.id_num==target_course_code:
            newCourse=fileparser.Course(newCode,course.name,course.credits)
    print(newCourse)
    data=[]
    #only with target course
    for student in students:
        for attempt in student.attempts:
            if attempt.course.id_num==target_course_code:
                data.append(student.attempts)
    #new course code
    for attempts in data:
        for attempt in attempts:
            if attempt.course.id_num==target_course_code and attempt.grade==target_grade:
                attempt.course=newCourse
    newCourses=courses|set([newCourse])
    newCourseCodes=courseCodes|set([newCode])
    data = list(group(d) for d in data)
    return[data,newCode,newCourse,newCourseCodes,newCourses]
[data,newCode,newCourse,newCourseCodes,newCourses]=preprocess(students,courses,courseCodes,courseYcode,yGrade)

apriori=algorithms.apriori_sequence(minsupp,newCourseCodes,data,k_item_set)
support_target=algorithms.support_sequence([(newCode,)],data)
result=[]
for a in apriori:
    if (newCode,) == a[0][-1]:
        support_sequence=algorithms.support_sequence(a[0][:-1],data)
        support_sequence_arrow_target=a[1]
        result.append((a[0],support_sequence,support_sequence_arrow_target,support_sequence_arrow_target/support_sequence,support_sequence_arrow_target/support_sequence/support_target))
result.sort(key=lambda x:x[4])

courseMap={c.id_num:c.name for c in newCourses}
lifthreshold=0.3
for r in result:
    if abs(1-r[4])<lifthreshold:
        continue
    print(r[0])
    names=[[courseMap[num] for num in ele] for ele in r[0]]
    print(names)
    print("supp sequ",round(r[1],3))
    print("supp rule",round(r[2],3))
    print("confidence",round(r[3],3))
    print("lift",round(r[4],3))
print("target course, grade",newCourse)
print("support threshold", minsupp)
print("<=k-item-set",k_item_set)
print("lift threshold",lifthreshold)
#print(sorted(algorithms.apriori_sequence(0.06, courses, data, 8), key=lambda x: x[1], reverse=True)[0:30])