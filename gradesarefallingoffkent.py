import random
from datetime import datetime
from getpass import getpass
import sys

ADMIN_PASSWORD = "ahlala"

# ----------- MISC ----------- #

def get_input(prompt):
    value = input(prompt)
    if value == "-1":
        print("Program forcefully terminated.")
        sys.exit()
    return value

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

# ---------------- UI ---------------- #

def print_box(lines):
    width = max(len(line) for line in lines) + 4
    print("=" * width)
    for i, line in enumerate(lines):
        if i == 0:
            print("| " + line.center(width - 4) + " |")
        else:
            print("| " + line.ljust(width - 4) + " |")
    print("=" * width)

def print_table(headers, rows):
    col_widths = [len(h) for h in headers]

    for row in rows:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(cell)))

    total_width = sum(col_widths) + len(col_widths)*3 + 1
    print("=" * total_width)

    header_row = "| " + " | ".join(
        headers[i].ljust(col_widths[i]) for i in range(len(headers))
    ) + " |"
    print(header_row)

    print("=" * total_width)

    for row in rows:
        row_str = "| " + " | ".join(
            str(row[i]).ljust(col_widths[i]) for i in range(len(row))
        ) + " |"
        print(row_str)

    print("=" * total_width)

# ---------------- HELPERS ---------------- #

def student_exists(student_id):
    return any(student_id in sections[s]["students"] for s in sections)

def generate_student_id():
    year = datetime.now().year
    while True:
        sid = f"{year}-{random.randint(100000,999999)}"
        if not student_exists(sid):
            return sid

def select_section():
    print_box(["Available Sections:"] + [
        f"{sec} ({len(sections[sec]['students'])} students)" for sec in sections
    ])
    return get_input("Enter section: ")

def select_student(section):
    print_box(["Students:"] + list(sections[section]["students"].keys()))
    return get_input("Enter student: ")

def list_section_assignments(section):
    print_box([f"{section} Assignments:"] + sorted(sec_act[section]))

# ---------------- VIEW ---------------- #

def view_student_grades():
    section = select_section()
    if section not in sections:
        print("Invalid section!")
        return

    headers = ["STUD NO", "LAST NAME", "FIRST NAME", "MI"] + sorted(sec_act[section])
    rows = []

    for sid, data in sections[section]["students"].items():
        row = [
            sid,
            data["Last Name"],
            data["First Name"],
            data["Middle Initial"]
        ]

        for act in sorted(sec_act[section]):
            row.append(data["grades"].get(act, "-"))

        rows.append(row)

    print_table(headers, rows)

def view_admin_table():
    for section in sections:
        print(f"\nSECTION: {section}")

        headers = ["STUD NO", "LAST NAME", "FIRST NAME", "MI", "STATUS"] + sorted(sec_act[section])
        rows = []

        for sid, data in sections[section]["students"].items():
            row = [
                sid,
                data["Last Name"],
                data["First Name"],
                data["Middle Initial"],
                data["status"]
            ]

            for act in sorted(sec_act[section]):
                row.append(data["grades"].get(act, "-"))

            rows.append(row)

        print_table(headers, rows)

# ---------------- SEARCH ---------------- #

def search_student():
    keyword = get_input("Search Student ID: ").lower()
    results = []

    for sec in sections:
        for sid, data in sections[sec]["students"].items():
            name = f"{data['First Name']} {data['Last Name']}"
            if keyword in sid or keyword in name:
                results.append(f"{sid} - {name} ({sec})")

    print_box(["Results:"] + results if results else ["No results found."])

# ---------------- ADMIN ---------------- #

def add_student():
    section = select_section()
    if section not in sections:
        print("Invalid section!")
        return

    sid = generate_student_id()

    sections[section]["students"][sid] = {
        "Last Name": get_input("Last name: "),
        "First Name": get_input("First name: "),
        "Middle Initial": get_input("Middle initial: "),
        "status": "active",
        "grades": {}
    }

    print(f"\nStudent Created... Generated ID: {sid}")

def update_status():
    section = select_section()
    student = select_student(section)
    sections[section]["students"][student]["status"] = get_input("New status: ")

def add_section():
    sec = get_input("New section: ")
    if sec in sections:
        print("Exists!")
        return
    sections[sec] = {"students": {}}
    sec_act[sec] = set()

def remove_section():
    sec = get_input("Remove section: ")
    if sec in sections:
        del sections[sec]
        del sec_act[sec]

# ---------------- GRADES ---------------- #

def enter_assignment_scores(section):
    list_section_assignments(section)
    a = get_input("Assignment: ")

    if a not in sec_act[section]:
        return

    for student in sections[section]["students"]:
        sections[section]["students"][student]["grades"][a] = float(get_input(f"{student}: "))

def enter_student_scores(section):
    student = select_student(section)

    while True:
        a = get_input("Assignment (done): ")
        if a == "done":
            break
        if a not in sec_act[section]:
            continue
        sections[section]["students"][student]["grades"][a] = float(get_input("Score: "))

def edit_specific_score(section):
    student = select_student(section)
    grades = sections[section]["students"][student]["grades"]

    print_box(["Assignments:"] + list(grades.keys()))
    a = get_input("Assignment: ")

    if a in grades:
        grades[a] = float(get_input("New score: "))

def edit_assignment_scores(section):
    a = get_input("Assignment: ")
    for student in sections[section]["students"]:
        grades = sections[section]["students"][student]["grades"]
        if a in grades:
            grades[a] = float(get_input(f"{student}: "))

def edit_student_scores(section):
    student = select_student(section)
    grades = sections[section]["students"][student]["grades"]

    for a in grades:
        grades[a] = float(get_input(f"{a}: "))

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
            "0 Back"
        ]

        print_box(menu)


        c = get_input("Choice: ")
        if c == "0":
            break

        section = select_section()
        if section not in sections:
            continue

        actions = {
            "1": lambda: enter_assignment_scores(section),
            "2": lambda: enter_student_scores(section),
            "3": lambda: edit_assignment_scores(section),
            "4": lambda: edit_student_scores(section),
            "5": lambda: edit_specific_score(section),
        }

        actions.get(c, lambda: print("Invalid"))()

def teacher_menu():
    while True:
        print_box([
            "TEACHER MENU",
            "1 Manage Grades",
            "2 Search Student",
            "3 View Students + Grades",
            "0 Exit"
        ])

        actions = {
            "1": score_management,
            "2": search_student,
            "3": view_student_grades
        }

        c = get_input("Choice: ")
        if c == "0":
            break

        actions.get(c, lambda: print("Invalid"))()

def admin_menu():
    while True:
        print_box([
            "ADMIN MENU",
            "1 Add Student",
            "2 Update Status",
            "3 Manage Grades",
            "4 Search Student",
            "5 Add Section",
            "6 Remove Section",
            "7 View Full Table",
            "0 Exit"
        ])

        actions = {
            "1": add_student,
            "2": update_status,
            "3": score_management,
            "4": search_student,
            "5": add_section,
            "6": remove_section,
            "7": view_admin_table
        }

        c = get_input("Choice: ")
        if c == "0":
            break

        actions.get(c, lambda: print("Invalid"))()

# ---------------- LOGIN ---------------- #

def main():
    while True:
        print_box([
            "LOGIN",
            "1 Teacher",
            "2 Admin",
            "0 Exit"
        ])

        choice = get_input("Choice: ")

        if choice == "1":
            teacher_menu()

        elif choice == "2":
            for _ in range(3):
                if getpass("Password: ") == ADMIN_PASSWORD:
                    print("Entering Admin Mode...")
                    admin_menu()
                    break
                print("Wrong password")
            else:
                print("Too many attempts")
        elif choice == "0":
            break

# ---------------- RUN ---------------- #

main()