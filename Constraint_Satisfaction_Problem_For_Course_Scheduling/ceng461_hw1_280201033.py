import csv
import sys

#Created two data classes to increase the readability of the code.
class course:
    def __init__(self, name:str, instructor:str, students:int, hours:int) -> None:
        self.name = name
        self.instructor = instructor
        self.students = students
        self.hours = hours

class scheduled_course:
    def __init__(self, Course:course, time_slots:list[str], classroom:str) -> None:
        self.Course = Course
        self.time_slots = time_slots
        self.classroom = classroom

class CourseSchedulingCSP:
    """The class that the problem is solved."""
    def __init__(self, courses:list[course], classrooms:dict[str,int], preferences:dict[str, list[str]], coordinations:list[list[str]], time_slots:list[str]) -> None:
        self.courses = courses
        self.classrooms = classrooms
        self.preferences = preferences
        self.coordinations = coordinations
        self.time_slots = time_slots
        self.solutions = []

    
    def exclusive_classroom(self,schedule:list[scheduled_course], time_slot:str, classroom:str) -> bool:
        """This function will check if the time slot is available for the classroom.

        Keyword arguments:

        schedule: Contains already assigned courses and their time slots with the classroom.

        time_slot: The time slot that we try to assign the new course.

        classroom: The classroom that we try to assign the new course.
        """
        for assigned_course in schedule:
            if (assigned_course.classroom == classroom):
                if(time_slot in assigned_course.time_slots):
                    return False
        return True

    def capacity_compliance(self,to_be_assigned_course:course, classroom:str) -> bool:
        """This function will check if the classroom has enough capacity for the course.

        Keyword arguments:

        to_be_assigned_course: The to be assigned course object.

        classroom: The classroom that we try to assign the new course.
        """
        return to_be_assigned_course.students <= self.classrooms[classroom]
    
    def instructor_availability(self,to_be_assigned_course:course,schedule:list[scheduled_course], time_slot) -> bool:
        """This function will check if the instructor is already assigned to another course in this time slot or not.

        Keyword arguments:

        to_be_assigned_course: The to be assigned course object.

        schedule: Contains already assigned courses and their time slots with the classroom.

        time_slot: The time slot that we try to assign the new course.
        """
        for assigned_course in schedule:
            if(assigned_course.Course.instructor == to_be_assigned_course.instructor):
                if(time_slot in assigned_course.time_slots):
                    return False
        return True
    
    def consecutive_scheduling(self, assigned_time_slots:list[str]) -> bool:
        """This function will check if the time slot array is consecutive or not.

        Keyword arguments:

        assigned_time_slots: The array of time slots.
        """
        for i in range(len(assigned_time_slots) - 1):
            if(assigned_time_slots[i][-1] == "4" and assigned_time_slots[i+1][-1] == "5"): #If there is a break between the slots
                return False
            if(assigned_time_slots[i][-1] == "8" and assigned_time_slots[i+1][-1] == "1"): #If the slots are in different days
                return False
        return True
    
    def instructor_preferences_compliance(self, to_be_assigned_course:course, time_slot) -> bool:
        """This function will check if the time slots complies with the preferences of the instructor.

        Keyword arguments:

        to_be_assigned_course: The to be assigned course object.

        time_slot: The time slot that we try to assign the new course.
        """
        return time_slot in self.preferences[to_be_assigned_course.instructor]
    
    def coordination_restrictions(self, to_be_assigned_course:course, schedule:list[scheduled_course], time_slot) -> bool:
        """This function will check if the to be assigned course does have any coordination restriction and checks if it complies with already assigned courses.

        Keyword arguments:

        to_be_assigned_course: The to be assigned course object.

        schedule: Contains already assigned courses and their time slots with the classroom.

        time_slot: The time slot that we try to assign the new course.
        """
        for assigned_course in schedule:
            for coordination in self.coordinations:
                if((to_be_assigned_course.name in coordination) and (assigned_course.Course.name in coordination)):
                    if(time_slot in assigned_course.time_slots):
                        return False
        return True
    
    def backtrack(self, schedule:list[scheduled_course]) -> None:
        """This function is the main solver of our class.In every function call, it will try to assign a new course to the solution and checks if it complies with all the restrictions.
        If the course complies with all the restrictions in that assigned classroom and the time slots, it adds it to the schedule list and goes for the next course.When it finishes
        assigning all the courses, it adds the schedule in the solutions list and starts backtracking and finds a new solution.In this way, the algoritm is able to find all possible
        solutions with the given constraints and the datas.

        Keyword arguments:

        schedule: Contains already assigned courses and their time slots with the classroom.
        """
        if(len(schedule) == len(self.courses)): #Base case is that the schedule has all the courses assigned.
            solution = []
            for Course in schedule: #Create a deep copy since the schedule's elements will be removed later.
                solution.append(Course)
            self.solutions.append(solution)
            return
        
        to_be_assigned_course = self.courses[len(schedule)] #Choose the next course to be assigned.

        for classroom in self.classrooms:
            if(not self.capacity_compliance(to_be_assigned_course, classroom)): #This is checked here because there is no need to check other requirements if the class is not suitible.
                continue
            for time_slot in self.time_slots:
                index = self.time_slots.index(time_slot)
                to_be_assigned_time_slots = self.time_slots[index:(index+to_be_assigned_course.hours)] #For a time slot, I created a block of time slots that the course will be in and check if its consecutive.
                if(not self.consecutive_scheduling(to_be_assigned_time_slots)):                        #If it is, then the algorithm will check if all the time slots are suitible for assignment.
                    continue
                willBeAssigned = True
                for assignable_time_slot in to_be_assigned_time_slots:
                    if(not self.instructor_preferences_compliance(to_be_assigned_course, assignable_time_slot)): #This is checked first because this constraint is most of the time the most decisive.
                        willBeAssigned = False
                        break
                    if(not self.exclusive_classroom(schedule, assignable_time_slot, classroom)):
                        willBeAssigned = False
                        break
                    if(not self.instructor_availability(to_be_assigned_course, schedule, assignable_time_slot)):
                        willBeAssigned = False
                        break
                    if(not self.coordination_restrictions(to_be_assigned_course, schedule, assignable_time_slot)):
                        willBeAssigned = False
                        break
                
                if(willBeAssigned): #If all the constraints are satisfied, the algorithm assigns the course to the specific class and time slots.
                    assigned_course = scheduled_course(to_be_assigned_course, to_be_assigned_time_slots, classroom)
                    schedule.append(assigned_course)

                    self.backtrack(schedule) 
                    
                    schedule.remove(assigned_course) #The course is removed from the schedule because we want to find all the solutions.If this is not done, the algoritm only finds a single solution.


def main():
    #Reading the data from problem here
    courses = []
    with open(sys.argv[1]+"/courses.csv") as file:
        reader = csv.DictReader(file)
        for row in reader:
            Course = course(row['Course'], row['Instructor'], int(row['Students']), int(row['Hours']))
            courses.append(Course)

    classrooms = {}
    with open(sys.argv[1]+"/classrooms.csv") as file:
        reader = csv.DictReader(file)
        for row in reader:
            classrooms[row["Classroom"]] = int(row["Capacity"])

    preferences = {}
    with open(sys.argv[1]+"/preferences.csv") as file:
        reader = csv.DictReader(file)
        for row in reader:
            preferences[row['Instructor']] = row['Times'].split()

    coordinations = []
    with open(sys.argv[1]+"/coordinations.csv") as file:
        reader = csv.reader(file)
        for row in reader:
            if(row == ["Courses"]):
                continue
            coordinated_courses = row[0]
            coordinated_courses = coordinated_courses.split()
            coordinations.append(coordinated_courses)

    time_slots = ["Mon1","Mon2","Mon3","Mon4","Mon5","Mon6","Mon7","Mon8",
                "Tue1","Tue2","Tue3","Tue4","Tue5","Tue6","Tue7","Tue8",
                "Wed1","Wed2","Wed3","Wed4","Wed5","Wed6","Wed7","Wed8",
                "Thu1","Thu2","Thu3","Thu4","Thu5","Thu6","Thu7","Thu8",
                "Fri1","Fri2","Fri3","Fri4","Fri5","Fri6","Fri7","Fri8",]

    #Solving the problem
    course_scheduling_problem = CourseSchedulingCSP(courses, classrooms, preferences, coordinations, time_slots)

    course_scheduling_problem.backtrack([])

    #To create a csv for every solution with its index.
    for index, solution in enumerate(course_scheduling_problem.solutions, start=1):
        with open((sys.argv[2] + f"/{index}.csv"), "w") as output_file:
            output_file.write("Course,Time,Classroom\n")
            for assigned_course in solution:
                output_file.write(f"{assigned_course.Course.name},{assigned_course.time_slots[0]},{assigned_course.classroom}\n")

if __name__ == "__main__":
    main()


