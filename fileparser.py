import csv


def open_task_file(filename='data-2016.csv'):
    return open(filename)


def as_rows(file_obj=open_task_file()):
    dataset = csv.reader(file_obj, delimiter = ' ')
    rows = []
    for row in dataset:
        rows.append(row)
    return rows


class Course:
    def __init__(self, id_num, name, credits):
        self.id_num = int(id_num)
        self.name = str(name)
        self.credits = float(credits)

    def __repr__(self):
        return "Id: " + str(self.id_num) + ", Name: " + (self.name
            + ", Credits: " + str(self.credits))

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.id_num == other.id_num

    def __ne__(self, other):
        return not __eq__(self, other)

    def __hash__(self):
        return self.id_num


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
        for i in range(1, len(row), 5):
            course = Course(row[i + 1], row[i + 2], row[i + 3])
            attempt = Attempt(course, row[i], row[i + 4])
            attempts.append(attempt)
        students.append(Student(starting_year, attempts))
    return students
