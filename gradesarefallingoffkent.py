import random
from datetime import datetime

# ---------------- DATA ---------------- #

sections = {
    "TN23": {
        "students": {
            "2024-11487": {
                "Last Name": "Capuno",
                "First Name": "Kent Anthony",
                "Middle Initial": "C.",
                "status": "active",
                "grades": {"SA1": 90}
            }
        }
    }
}

sec_act = {
    "TN23": {"SA1", "SA2", "SA3", "SA4", "ME", "FE"}
}

# ---------------- UI BOX ---------------- #

def print_box(lines):
    width = max(len(line) for line in lines) + 4
    print("=" * width)
    for i, line in enumerate(lines):
        if i == 0:
            print("| " + line.center(width - 4) + " |")
        else:
            print("| " + line.ljust(width - 4) + " |")
    print("=" * width)

# ---------------- HELPERS ---------------- #

def student_exists(student_id):
    for sec in sections:
        if student_id in sections[sec]["students"]:
            return True
    return False

def generate_student_id():
    year = datetime.now().year
    while True:
        student_id = f"{year}-{random.randint(100000,999999)}"
        if not student_exists(student_id):
            return student_id

def select_section():
    lines = ["Available Sections:"]
    for sec in sections:
        count = len(sections[sec]["students"])
        lines.append(f"{sec} ({count} students)")
    print_box(lines)
    return input("Enter section: ")

def select_student(section):
    students = sections[section]["students"]
    lines = ["Students:"]
    for s in students:
        lines.append(s)
    print_box(lines)
    return input("Enter student: ")

def list_section_assignments(section):
    lines = [f"Assignments for {section}:"]
    for act in sorted(sec_act[section]):
        lines.append(act)
    print_box(lines)

# ---------------- SEARCH ---------------- #

def search_student():
    keyword = input("Search name or ID: ").lower()
    results = []

    for sec in sections:
        for sid, data in sections[sec]["students"].items():
            name = f"{data['First Name']} {data['Last Name']}".lower()
            if keyword in sid or keyword in name:
                results.append(f"{sid} - {name} ({sec})")

    if results:
        print_box(["Results:"] + results)
    else:
        print("No results found.")

# ---------------- ADMIN ---------------- #

def add_student():
    section = select_section()
    if section not in sections:
        print("Invalid section!")
        return

    sid = generate_student_id()

    lname = input("Last name: ")
    fname = input("First name: ")
    mi = input("Middle initial: ")

    sections[section]["students"][sid] = {
        "Last Name": lname,
        "First Name": fname,
        "Middle Initial": mi,
        "status": "active",
        "grades": {}
    }

    print(f"Added {sid} to {section}")

def update_status():
    section = select_section()
    student = select_student(section)

    status = input("New status: ")
    sections[section]["students"][student]["status"] = status
    print("Updated.")

def add_section():
    sec = input("New section: ")
    if sec in sections:
        print("Already exists!")
        return

    sections[sec] = {"students": {}}
    sec_act[sec] = set()
    print("Section added.")

def remove_section():
    sec = input("Section to remove: ")
    if sec not in sections:
        print("Not found!")
        return

    del sections[sec]
    del sec_act[sec]
    print("Removed.")

# ---------------- GRADES ---------------- #

def enter_assignment_scores(section):
    list_section_assignments(section)
    assignment = input("Assignment: ")

    if assignment not in sec_act[section]:
        print("Invalid!")
        return

    for student in sections[section]["students"]:
        score = float(input(f"{student}: "))
        sections[section]["students"][student]["grades"][assignment] = score

def enter_student_scores(section):
    student = select_student(section)

    while True:
        list_section_assignments(section)
        assignment = input("Assignment (done to stop): ")

        if assignment.lower() == "done":
            break

        if assignment not in sec_act[section]:
            print("Invalid!")
            continue

        score = float(input("Score: "))
        sections[section]["students"][student]["grades"][assignment] = score

def edit_specific_score(section):
    student = select_student(section)
    grades = sections[section]["students"][student]["grades"]

    print_box(["Assignments:"] + list(grades.keys()))
    assignment = input("Assignment: ")

    if assignment in grades:
        score = float(input("New score: "))
        grades[assignment] = score

def edit_assignment_scores(section):
    list_section_assignments(section)
    assignment = input("Enter assignment to edit: ")

    if assignment not in sec_act[section]:
        print("Invalid assignment!")
        return

    for student in sections[section]["students"]:
        grades = sections[section]["students"][student]["grades"]

        if assignment in grades:
            score = float(input(f"New score for {student}: "))
            grades[assignment] = score
        else:
            print(f"{student} has no score for {assignment}")

def edit_student_scores(section):
    student = select_student(section)
    grades = sections[section]["students"][student]["grades"]

    for assignment in grades:
        score = float(input(f"New score for {assignment}: "))
        grades[assignment] = score

# ---------------- MENUS ---------------- #

def score_management():
    while True:
        menu = [
            "GRADE MANAGEMENT MENU",
            "",
            "1 Enter scores for one assignment (all students)",
            "2 Enter scores for one student (all assignments)",
            "3 Edit scores for one assignment",
            "4 Edit scores for one student",
            "5 Edit specific score",
            "6 View Data",
            "0 Back"
        ]

        print_box(menu)

        choice = input("Choice: ")

        if choice == "0":
            break

        section = select_section()

        if section not in sections:
            print("Invalid section!")
            continue

        if choice == "1":
            enter_assignment_scores(section)
        elif choice == "2":
            enter_student_scores(section)
        elif choice == "3":
            edit_assignment_scores(section)
        elif choice == "4":
            edit_student_scores(section)
        elif choice == "5":
            edit_specific_score(section)
        elif choice == "6":
            print(sections)
        else:
            print("Invalid choice!")

def teacher_menu():
    while True:
        menu = [
            "TEACHER MENU",
            "1 Manage Grades",
            "2 Search Student",
            "3 View Data",
            "0 Exit"
        ]
        print_box(menu)

        c = input("Choice: ")

        if c == "1":
            score_management()
        elif c == "2":
            search_student()
        elif c == "3":
            print(sections)
        elif c == "0":
            break

def admin_menu():
    while True:
        menu = [
            "ADMIN MENU",
            "1 Add Student",
            "2 Update Status",
            "3 Manage Grades",
            "4 Search Student",
            "5 Add Section",
            "6 Remove Section",
            "7 View Data",
            "0 Exit"
        ]
        print_box(menu)

        c = input("Choice: ")

        if c == "1":
            add_student()
        elif c == "2":
            update_status()
        elif c == "3":
            score_management()
        elif c == "4":
            search_student()
        elif c == "5":
            add_section()
        elif c == "6":
            remove_section()
        elif c == "7":
            print(sections)
        elif c == "0":
            break

# ---------------- LOGIN ---------------- #

def main():
    while True:
        menu = [
            "LOGIN",
            "1 Teacher",
            "2 Admin",
            "0 Exit"
        ]
        print_box(menu)

        choice = input("Choice: ")

        if choice == "1":
            teacher_menu()
        elif choice == "2":
            admin_menu()
        elif choice == "0":
            break

# ---------------- RUN ---------------- #

main()