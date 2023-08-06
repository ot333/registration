import sqlite3
import tkinter as tk
from tkinter import messagebox

Current_Student_Amount = 10

menu_options = '''
1) Logout
2) Add/Remove Course From Semester Schedule
3) Assemble and print course Roster 
4) Add/Remove Courses from System
5) Search All Courses
6) Search Course By CRN Number
7) Print Individual Schedule
8) Quit
'''


def list_to_string(lst):
    return ', '.join(str(item) for item in lst)


def csv_string_to_list(csv_string):
    return [item.strip() for item in csv_string.split(',') if item.strip()]


def connect():
    try:
        return sqlite3.connect('assignment3.db')
    except sqlite3.Error:
        print("Could Not find .db File")


def print_table(cur, table):
    cur.execute("SELECT * FROM {}".format(table))
    r = cur.fetchall()
    for row in r:
        print(row)
    return


class User:
    def __init__(self, fname, lname):
        self.firstname = fname
        self.lastname = lname

    def print_available_classes(self, cursor):
        print("Here are the Available Classes this Semester:\n")
        cursor.execute("Select CRN, Title, department, time, days, semester, year, credits, instructor FROM COURSE")
        rows = cursor.fetchall()
        for row in rows:
            print(
                f"CRN:{row[0]} Title:{row[1]} Department:{row[2]} Time:{row[3]} Days:{row[4]} Semester:{row[5]} Year:{row[6]} Credits:{row[7]} Instructor:{row[8]}")

    def print_classes_from_crn(self, cursor, crn):
        print("Here are the Available Classes this Semester:\n")
        cursor.execute("Select CRN, Title, department, time, days, semester, year, credits, instructor FROM COURSE "
                       "WHERE CRN = '{}'".format(crn))
        rows = cursor.fetchall()
        for row in rows:
            print(
                f"CRN:{row[0]} Title:{row[1]} Department:{row[2]} Time:{row[3]} Days:{row[4]} Semester:{row[5]} Year:{row[6]} Credits:{row[7]} Instructor:{row[8]}")


class Student(User):
    def print_name(self):
        print("{} {}".format(self.firstname, self.lastname))

    def add_remove_course(self, cursor):
        action = input("Would you like to add or remove a course: ").lower()
        if action == 'add':
            crn_add = input("What is the CRN of the Course you would like to add: ")
            cursor.execute("SELECT CLASSES FROM STUDENT WHERE NAME = '{}'".format(self.firstname))
            current_classes = cursor.fetchone()[0]
            new_value = current_classes + crn_add + ","
            cursor.execute("UPDATE STUDENT SET CLASSES = '{}' WHERE NAME = '{}'".format(new_value, self.firstname))
        elif action == 'remove':
            crn_remove = input("What is the CRN of the Course you would like to remove: ")
            cursor.execute("SELECT CLASSES FROM STUDENT WHERE NAME = '{}'".format(self.firstname))
            current_classes = cursor.fetchone()[0]
            current_classes = current_classes.strip().split(',')
            new_class_list = []
            for classes in current_classes:
                if classes != crn_remove:
                    new_class_list.append(classes)
            new_class_list = list_to_string(new_class_list)
            cursor.execute("UPDATE STUDENT SET CLASSES = '{}' WHERE NAME = '{}'".format(new_class_list, self.firstname))

    def class_list(self, cursor):
        students = []
        class_query = input("Input the CRN to the Class you would like the classlist for: ")
        cursor.execute("SELECT NAME, CLASSES FROM STUDENT")
        rows = cursor.fetchall()
        for row in rows:
            student_classes = csv_string_to_list(row[1])
            if class_query in student_classes:
                students.append(row[0])
        print(students)

    def print_individual_schedule(self, cursor):
        cursor.execute("SELECT CLASSES FROM STUDENT WHERE NAME = '{}'".format(self.firstname))
        classes = cursor.fetchone()[0]
        classes = csv_string_to_list(classes)
        print("Individual Schedule for {}: ".format(self.firstname))
        for crn in classes:
            cursor.execute("SELECT * FROM COURSE WHERE CRN = '{}'".format(crn))
            course = cursor.fetchone()
            print("CRN: {}, Title: {}, Department: {}, Time: {}, Days: {}, Semester: {}, Year: {}, Credits: {}, Instructor: {}".format(
                course[0], course[1], course[2], course[3], course[4], course[5], course[6], course[7], course[8]))


class Instructor(User):
    def print_name(self):
        print("{} {}".format(self.firstname, self.lastname))

    def class_list(self, cursor):
        class_query = input("Input the CRN to the Class you would like the classlist for: ")
        cursor.execute("SELECT NAME FROM STUDENT WHERE CLASSES LIKE ?", ('%'+class_query+'%',))
        rows = cursor.fetchall()
        print("Class list for CRN {}: ".format(class_query))
        for row in rows:
            print(row[0])


class Admin(User):
    def print_name(self):
        print("{} {}".format(self.firstname, self.lastname))

    def add_remove_courses(self, cursor):
        action = input("Would you like to add or remove courses from the system: ").lower()
        if action == "add":
            crn_add = input("CRN of new Course: ")
            title = input("Title of new Course: ")
            department = input("Dept. of new Course: ")
            time = input("Time of new Course: ")
            days = input("Days of the Week(M,T,W,R,F) of new Course: ")
            semester = input("Semester of new Course: ")
            year = input("Year of new Course: ")
            creditss = input("Credits of new Course: ")
            instructor = input("Instructor of new Course: ")
            cursor.execute(
                "INSERT INTO COURSE VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')".format(crn_add,
                                                                                                          title,
                                                                                                          department,
                                                                                                          time, days,
                                                                                                          semester,
                                                                                                          year,
                                                                                                          creditss,
                                                                                                          instructor))
            print(f"Successfully Added Course with CRN {crn_add}")
        elif action == 'remove':
            crn_remove = input("Input the CRN of the Class you would like to remove: ")
            cursor.execute(f"DELETE FROM COURSE WHERE CRN = '{crn_remove}")
            print(f"Successfully Deleted Course with CRN {crn_remove}")


def login(cursor):
    while True:
        login_type = input("Are you a Student, Instructor or Admin: ").lower()
        if login_type == 'admin':
            user = input("Username:  ")
            password = input("Password: ")
            cursor.execute("Select NAME, SURNAME FROM ADMIN")
            rows = cursor.fetchall()
            for row in rows:
                col1 = row[0]
                col2 = row[1]
                if col1.lower() == user.lower() and col2.lower() == password.lower():
                    print("Hello {} {}. Welcome to Leopard Web".format(col1, col2))
                    return Admin(col1, col2)
            print("Unrecognized Login.\n")
        elif login_type == 'instructor':
            user = input("Username:  ")
            password = input("Password: ")
            cursor.execute("Select NAME, SURNAME FROM INSTRUCTOR")
            rows = cursor.fetchall()
            for row in rows:
                col1 = row[0]
                col2 = row[1]
                if col1.lower() == user.lower() and col2.lower() == password.lower():
                    print("Hello {} {}. Welcome to Leopard Web".format(col1, col2))
                    return Instructor(col1, col2)
            print("Unrecognized Login.\n")
        elif login_type == 'student':
            user = input("Username:  ")
            password = input("Password: ")
            cursor.execute("Select NAME, SURNAME FROM STUDENT")
            rows = cursor.fetchall()
            for row in rows:
                col1 = row[0]
                col2 = row[1]
                if col1.lower() == user.lower() and col2.lower() == password.lower():
                    print("Hello {} {}. Welcome to Leopard Web".format(col1, col2))
                    return Student(col1, col2)
            print("Unrecognized Login.\n")
        else:
            print("Invalid Input. Try again\n")










#############################
#         Login GUI
#############################


def login_gui(sql_handle):
    def handle_login():
        login_type = login_type_var.get().lower()
        username = username_entry.get().strip()
        password = password_entry.get().strip()

        if not username or not password:
            messagebox.showerror("Error", "Username and password cannot be empty.")
            return

        cursor = sql_handle.cursor()

        if login_type == 'admin':
            cursor.execute("SELECT NAME, SURNAME FROM ADMIN")
            rows = cursor.fetchall()
            for row in rows:
                col1 = row[0]
                col2 = row[1]
                if col1.lower() == username.lower() and col2.lower() == password.lower():
                    messagebox.showinfo("Success", f"Hello {col1} {col2}. Welcome to Leopard Web.")
                    user = Instructor(col1, col2)
                    admin_gui(sql_handle, user)  # Call the admin GUI function
                    return
        elif login_type == 'instructor':
            cursor.execute("SELECT NAME, SURNAME FROM INSTRUCTOR")
            rows = cursor.fetchall()
            for row in rows:
                col1 = row[0]
                col2 = row[1]
                if col1.lower() == username.lower() and col2.lower() == password.lower():
                    messagebox.showinfo("Success", f"Hello {col1} {col2}. Welcome to Leopard Web.")
                    user = Instructor(col1, col2)
                    instructor_gui(sql_handle, user)  # Call the instructor GUI function
                    return
        elif login_type == 'student':
            cursor.execute("SELECT NAME, SURNAME FROM STUDENT")
            rows = cursor.fetchall()
            for row in rows:
                col1 = row[0]
                col2 = row[1]
                if col1.lower() == username.lower() and col2.lower() == password.lower():
                    messagebox.showinfo("Success", f"Hello {col1} {col2}. Welcome to Leopard Web.")
                    user = Student(col1, col2)
                    student_gui(sql_handle, user)  # Call the student GUI function
                    return
        else:
            messagebox.showerror("Error", "Invalid login type.")
            return

        messagebox.showerror("Error", "Invalid username or password.")

    
    
    
    


    root = tk.Tk()
    root.title("Leopard Web Login")
    root.geometry("1000x600")

    login_type_var = tk.StringVar()
    login_type_var.set("student")

    login_type_label = tk.Label(root, text="Login Type:")
    login_type_label.pack()
    login_type_radio_student = tk.Radiobutton(root, text="Student", variable=login_type_var, value="student")
    login_type_radio_student.pack(anchor=tk.CENTER)
    login_type_radio_instructor = tk.Radiobutton(root, text="Instructor", variable=login_type_var, value="instructor")
    login_type_radio_instructor.pack(anchor=tk.CENTER)
    login_type_radio_admin = tk.Radiobutton(root, text="Admin", variable=login_type_var, value="admin")
    login_type_radio_admin.pack(anchor=tk.CENTER)

    username_label = tk.Label(root, text="Username:")
    username_label.pack()
    username_entry = tk.Entry(root)
    username_entry.pack()

    password_label = tk.Label(root, text="Password:")
    password_label.pack()
    password_entry = tk.Entry(root, show="*")
    password_entry.pack()

    login_button = tk.Button(root, text="Login", command=handle_login)
    login_button.pack()

    root.mainloop()








#############################
#        Student GUI
#############################


def student_gui(sql_handle, student):     #, root):
    def handle_add_remove_course():
        crn = crn_entry.get().strip()
        action = add_remove_var.get()

        if not crn:
            messagebox.showerror("Error", "Please enter a valid CRN.")
            return

        cursor = sql_handle.cursor()
        cursor.execute("SELECT * FROM COURSE WHERE CRN=?", (crn,))
        course = cursor.fetchone()

        if not course:
            messagebox.showerror("Error", "Course not found.")
            return

        if action == 'add':
            cursor.execute("SELECT CLASSES FROM STUDENT WHERE NAME=?", (student.firstname,))
            current_classes = cursor.fetchone()[0]
            current_classes = csv_string_to_list(current_classes)
            if crn in current_classes:
                messagebox.showinfo("Info", "You are already enrolled in this course.")
            else:
                current_classes.append(crn)
                new_classes = list_to_string(current_classes)
                cursor.execute("UPDATE STUDENT SET CLASSES=? WHERE NAME=?", (new_classes, student.firstname))
                sql_handle.commit()
                messagebox.showinfo("Success", f"Course with CRN {crn} has been added to your schedule.")
        elif action == 'remove':
            cursor.execute("SELECT CLASSES FROM STUDENT WHERE NAME=?", (student.firstname,))
            current_classes = cursor.fetchone()[0]
            current_classes = csv_string_to_list(current_classes)
            if crn not in current_classes:
                messagebox.showinfo("Info", "You are not enrolled in this course.")
            else:
                current_classes.remove(crn)
                new_classes = list_to_string(current_classes)
                cursor.execute("UPDATE STUDENT SET CLASSES=? WHERE NAME=?", (new_classes, student.firstname))
                sql_handle.commit()
                messagebox.showinfo("Success", f"Course with CRN {crn} has been removed from your schedule.")
        else:
            messagebox.showerror("Error", "Invalid action.")


    def handle_search_course():
        search_query = search_entry.get().strip()
        if not search_query:
            # If the search query is empty, fetch and display all available courses
            cursor = sql_handle.cursor()
            cursor.execute("SELECT * FROM COURSE")
            courses = cursor.fetchall()

            if not courses:
                messagebox.showinfo("Info", "No courses found.")
                return

            course_list.delete(0, tk.END)
            for course in courses:
                course_list.insert(tk.END, f"CRN: {course[0]}, Title: {course[1]}, Department: {course[2]}, "
                                          f"Time: {course[3]}, Days: {course[4]}, Semester: {course[5]}, "
                                          f"Year: {course[6]}, Credits: {course[7]}, Instructor: {course[8]}")
        else:
            cursor = sql_handle.cursor()
            cursor.execute("SELECT * FROM COURSE WHERE Title LIKE ? OR CRN=?", ('%'+search_query+'%', search_query))
            courses = cursor.fetchall()

            if not courses:
                messagebox.showinfo("Info", "No courses found.")
                return

            course_list.delete(0, tk.END)
            for course in courses:
                course_list.insert(tk.END, f"CRN: {course[0]}, Title: {course[1]}, Department: {course[2]}, "
                                          f"Time: {course[3]}, Days: {course[4]}, Semester: {course[5]}, "
                                          f"Year: {course[6]}, Credits: {course[7]}, Instructor: {course[8]}")


    def handle_print_schedule():
        cursor = sql_handle.cursor()
        cursor.execute("SELECT CLASSES FROM STUDENT WHERE NAME = '{}'".format(student.firstname))
        classes = cursor.fetchone()[0]
        classes = csv_string_to_list(classes)
        schedule_text.delete(1.0, tk.END)
        schedule_text.insert(tk.END, "Individual Schedule for {}: \n".format(student.firstname))
        for crn in classes:
            cursor.execute("SELECT * FROM COURSE WHERE CRN = '{}'".format(crn))
            course = cursor.fetchone()
            schedule_text.insert(tk.END, "CRN: {}, Title: {}, Department: {}, Time: {}, Days: {}, Semester: {}, "
                                        "Year: {}, Credits: {}, Instructor: {}\n".format(
                course[0], course[1], course[2], course[3], course[4], course[5], course[6], course[7], course[8]))

    root = tk.Tk()
    root.title("Leopard Web - Student")
    root.geometry("2400x1200")

    add_remove_var = tk.StringVar()
    add_remove_var.set("add")

    label = tk.Label(root, text="Welcome, {} {}. You are logged in as a Student.".format(student.firstname, student.lastname))
    label.pack()

    add_remove_frame = tk.Frame(root)
    add_remove_frame.pack()

    crn_label = tk.Label(add_remove_frame, text="CRN:")
    crn_label.grid(row=0, column=0)

    crn_entry = tk.Entry(add_remove_frame)
    crn_entry.grid(row=0, column=1)

    add_radio = tk.Radiobutton(add_remove_frame, text="Add Course", variable=add_remove_var, value="add")
    add_radio.grid(row=1, column=0)

    remove_radio = tk.Radiobutton(add_remove_frame, text="Remove Course", variable=add_remove_var, value="remove")
    remove_radio.grid(row=1, column=1)

    add_remove_button = tk.Button(add_remove_frame, text="Add/Remove Course", command=handle_add_remove_course)
    add_remove_button.grid(row=1, column=2)

    search_frame = tk.Frame(root)
    search_frame.pack()

    search_label = tk.Label(search_frame, text="Search Courses:")
    search_label.grid(row=0, column=0)

    search_entry = tk.Entry(search_frame)
    search_entry.grid(row=0, column=1)

    search_button = tk.Button(search_frame, text="Search", command=handle_search_course)
    search_button.grid(row=0, column=2)

    course_list = tk.Listbox(root, height=10, width=120)  # Increase the height
    course_list.pack()

    logout_button = tk.Button(root, text="Logout", command=root.destroy)# command=lambda: logout(root))  # Pass root to logout function
    logout_button.pack()

    schedule_button = tk.Button(root, text="Print Individual Schedule", command=handle_print_schedule)
    schedule_button.pack()

    schedule_text = tk.Text(root, height=10, width=150)
    schedule_text.pack()

    root.mainloop()
    
    
    
    
    
    
    
    
#############################
#      Instructor GUI
#############################
    
def instructor_gui(sql_handle, instructor):
    
    def handle_search_course():
        search_query = search_entry.get().strip()
        if not search_query:
            # If the search query is empty, fetch and display all available courses
            cursor = sql_handle.cursor()
            cursor.execute("SELECT * FROM COURSE")
            courses = cursor.fetchall()

            if not courses:
                messagebox.showinfo("Info", "No courses found.")
                return

            course_list.delete(0, tk.END)
            for course in courses:
                course_list.insert(tk.END, f"CRN: {course[0]}, Title: {course[1]}, Department: {course[2]}, "
                                          f"Time: {course[3]}, Days: {course[4]}, Semester: {course[5]}, "
                                          f"Year: {course[6]}, Credits: {course[7]}, Instructor: {course[8]}")
        else:
            cursor = sql_handle.cursor()
            cursor.execute("SELECT * FROM COURSE WHERE Title LIKE ? OR CRN=?", ('%'+search_query+'%', search_query))
            courses = cursor.fetchall()

            if not courses:
                messagebox.showinfo("Info", "No courses found.")
                return

            course_list.delete(0, tk.END)
            for course in courses:
                course_list.insert(tk.END, f"CRN: {course[0]}, Title: {course[1]}, Department: {course[2]}, "
                                          f"Time: {course[3]}, Days: {course[4]}, Semester: {course[5]}, "
                                          f"Year: {course[6]}, Credits: {course[7]}, Instructor: {course[8]}")
    
    
    root = tk.Tk()
    root.title("Leopard Web - Instructor")
    root.geometry("2400x1200")

    welcome_label = tk.Label(root, text=f"Welcome, {instructor.firstname} {instructor.lastname}. You are logged in as an Instructor.")
    welcome_label.pack()

    search_frame = tk.Frame(root)
    search_frame.pack()

    search_label = tk.Label(search_frame, text="Search Courses:")
    search_label.grid(row=0, column=0)

    search_entry = tk.Entry(search_frame)
    search_entry.grid(row=0, column=1)

    search_button = tk.Button(search_frame, text="Search", command=handle_search_course)
    search_button.grid(row=0, column=2)

    logout_button = tk.Button(root, text="Logout", command=root.destroy)
    logout_button.pack()

    root.mainloop()

#############################
#         Admin GUI
#############################
    
def admin_gui(sql_handle, admin):
    
    def handle_search_course():
        search_query = search_entry.get().strip()
        if not search_query:
            # If the search query is empty, fetch and display all available courses
            cursor = sql_handle.cursor()
            cursor.execute("SELECT * FROM COURSE")
            courses = cursor.fetchall()

            if not courses:
                messagebox.showinfo("Info", "No courses found.")
                return

            course_list.delete(0, tk.END)
            for course in courses:
                course_list.insert(tk.END, f"CRN: {course[0]}, Title: {course[1]}, Department: {course[2]}, "
                                          f"Time: {course[3]}, Days: {course[4]}, Semester: {course[5]}, "
                                          f"Year: {course[6]}, Credits: {course[7]}, Instructor: {course[8]}")
        else:
            cursor = sql_handle.cursor()
            cursor.execute("SELECT * FROM COURSE WHERE Title LIKE ? OR CRN=?", ('%'+search_query+'%', search_query))
            courses = cursor.fetchall()

            if not courses:
                messagebox.showinfo("Info", "No courses found.")
                return

            course_list.delete(0, tk.END)
            for course in courses:
                course_list.insert(tk.END, f"CRN: {course[0]}, Title: {course[1]}, Department: {course[2]}, "
                                          f"Time: {course[3]}, Days: {course[4]}, Semester: {course[5]}, "
                                          f"Year: {course[6]}, Credits: {course[7]}, Instructor: {course[8]}")
    
    
    root = tk.Tk()
    root.title("Leopard Web - Admin")
    root.geometry("2400x1200")

    welcome_label = tk.Label(root, text=f"Welcome, {admin.firstname} {admin.lastname}. You are logged in as an Admin.")
    welcome_label.pack()

    search_frame = tk.Frame(root)
    search_frame.pack()

    search_label = tk.Label(search_frame, text="Search Courses:")
    search_label.grid(row=0, column=0)

    search_entry = tk.Entry(search_frame)
    search_entry.grid(row=0, column=1)

    search_button = tk.Button(search_frame, text="Search", command=handle_search_course)
    search_button.grid(row=0, column=2)

    logout_button = tk.Button(root, text="Logout", command=root.destroy)
    logout_button.pack()

    root.mainloop()


    
    
def logout(root):
    root.destroy()
    main()


def main_program(user):
    while True:
        command = input(menu_options)
        if command == "1":
            print("Logged out successfully.")
            return
        elif command == "2":
            user.add_remove_course(cur)
        elif command == "3":
            user.class_list(cur)
        elif command == "4":
            user.add_remove_courses(cur)
        elif command == "5":
            user.print_available_classes(cur)
        elif command == "6":
            temp = input("What is the CRN of the Class you are looking for: ")
            user.print_classes_from_crn(cur, temp)
        elif command == "7":
            user.print_individual_schedule(cur)
        elif command == "8":
            sql_handle.commit()
            sql_handle.close()
            print("Exiting program.")
            return


def main():
    sql_handle = connect()
    cur = sql_handle.cursor()
    #root = tk.Tk()  # Create the root window here
    login_gui(sql_handle)  # Pass the root window to login_gui
    while True:
        print("Welcome to Leopard Web Please login")
        user = login(cur)
        main_program(user)


main()

