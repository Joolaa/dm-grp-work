import csv

def open_task_file(filename = 'data-2016.csv'):
    return open(filename)

def as_rows(file_obj = open_task_file()):
    dataset = csv.reader(file_obj, delimiter = ' ')
    rows = []
    for row in dataset:
        rows.append(row)
    return rows

class Course:
    def __init__(self, id_num, name, credits):
        self.id_num = str(id_num)
        self.name = str(name)
        self.credits = float(credits)
    def __repr__(self):
        return "Id: " + self.id_num + ", Name: " + (self.name 
            + ", Credits: " + str(self.credits))

class Attempt:
    def __init__(self, course, date, grade):
        self.course = course
        self.date = str(date)
        self.grade = int(grade)
    def __repr__(self):
        return "\"Date: " + self.date + ", " + str(self.course) + (", Grade: " 
                + str(self.grade) + "\"")

class Student:
    def __init__(self, starting_year, attempts):
        self.starting_year = str(starting_year)
        self.attempts = attempts
    def __repr__(self):
        return "\"Starting year: " + (self.starting_year 
                + ", Course attempts: " + str(self.attempts) + "\"")

def parse_students(csv_rows = as_rows()):
    students = []
    for row in csv_rows:
        attempts = []
        starting_year = row[0]
        for i in xrange(1, len(row), 5):
            course = Course(row[i + 1], row[i + 2], row[i + 3])
            attempt = Attempt(course, row[i], row[i + 4])
            attempts.append(attempt)
        students.append(Student(starting_year, attempts))

    return students

#test_course = Course("32984872", "ldskjflsdkjf", 5.0)
#test_attempt = Attempt(test_course, "2012-3", 4)
#test_student = Student(2011, [test_attempt, test_attempt])
