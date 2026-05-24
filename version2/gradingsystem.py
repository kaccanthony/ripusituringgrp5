import random
from datetime import datetime
from getpass import getpass
import sys

ADMIN_PASSWORD = "ahlala"
PASSING        = 70
# minor update after phase 1

# ─────────────────────────────────────────────
#  GRADING CATEGORY  (owns its assignment codes)
# ─────────────────────────────────────────────

class GradingCategory:
    def __init__(self, category_id, name, weight, max_score=100):
        self.category_id  = category_id
        self.name         = name
        self.weight       = weight       # e.g. 30 = 30%
        self.max_score    = max_score
        self.assignments  = set()        # sec_act codes that belong here

    def add_assignment(self, code):
        self.assignments.add(code)

    def remove_assignment(self, code):
        self.assignments.discard(code)


# ─────────────────────────────────────────────
#  GRADEBOOK  (per-section, owns categories)
# ─────────────────────────────────────────────

class Gradebook:
    def __init__(self):
        self.categories   = {}
        self.total_weight = 0

    def add_category(self, category_id, name, weight, max_score=100):
        if category_id in self.categories:
            return False, f"Category '{category_id}' already exists."
        if weight <= 0:
            return False, "Weight must be greater than 0."
        if self.total_weight + weight > 100:
            return False, f"Would exceed 100% (currently {self.total_weight}%)."
        self.categories[category_id] = GradingCategory(category_id, name, weight, max_score)
        self.total_weight += weight
        return True, f"Category '{name}' added ({weight}%). Total: {self.total_weight}%"

    def remove_category(self, category_id):
        if category_id not in self.categories:
            return False, "Category not found."
        self.total_weight -= self.categories[category_id].weight
        del self.categories[category_id]
        return True, f"Category removed. Total weight: {self.total_weight}%"

    def update_weight(self, category_id, new_weight):
        if category_id not in self.categories:
            return False, "Category not found."
        if new_weight <= 0:
            return False, "Weight must be greater than 0."
        diff = new_weight - self.categories[category_id].weight
        if self.total_weight + diff > 100:
            return False, f"Would exceed 100% (currently {self.total_weight}%)."
        old = self.categories[category_id].weight
        self.categories[category_id].weight = new_weight
        self.total_weight += diff
        return True, f"Weight updated {old}% → {new_weight}%. Total: {self.total_weight}%"

    def add_assignment(self, code, category_id):
        if category_id not in self.categories:
            return False, "Category not found."
        existing = self.find_category_of(code)
        if existing:
            return False, f"'{code}' already belongs to category '{existing}'."
        self.categories[category_id].add_assignment(code)
        return True, f"Assignment '{code}' added to category '{self.categories[category_id].name}'."

    def remove_assignment(self, code):
        cat_id = self.find_category_of(code)
        if not cat_id:
            return False, f"Assignment '{code}' not found in any category."
        self.categories[cat_id].remove_assignment(code)
        return True, f"Assignment '{code}' removed from '{self.categories[cat_id].name}'."

    def find_category_of(self, code):
        for cid, cat in self.categories.items():
            if code in cat.assignments:
                return cid
        return None

    def all_assignments(self):
        result = set()
        for cat in self.categories.values():
            result |= cat.assignments
        return result

    def calculate_final_grade(self, student_grades: dict):
        if self.total_weight == 0:
            return 0.0, []

        weighted_sum = 0.0
        total_weight_used = 0.0
        breakdown = []

        for cat in self.categories.values():
            scores = [student_grades[a] for a in cat.assignments if a in student_grades]
            if not scores:
                breakdown.append((cat.name, cat.weight, None, 0.0))
                continue
            avg          = sum(scores) / len(scores)
            contribution = avg * (cat.weight / 100)
            weighted_sum      += contribution
            total_weight_used += cat.weight
            breakdown.append((cat.name, cat.weight, avg, contribution))

        if total_weight_used == 0:
            return 0.0, breakdown

        final = weighted_sum / (total_weight_used / 100)
        return round(final, 2), breakdown

    def display(self):
        if not self.categories:
            print("  (no categories defined)")
            return
        print(f"\n  {'ID':<10} {'Category':<18} {'Weight':>7}   {'Max':>5}   Assignments")
        print("  " + "-" * 65)
        for cid, cat in self.categories.items():
            assignments_str = ", ".join(sorted(cat.assignments)) if cat.assignments else "(none)"
            print(f"  {cid:<10} {cat.name:<18} {cat.weight:>6}%   {cat.max_score:>5}   {assignments_str}")
        print("  " + "-" * 65)
        remaining = 100 - self.total_weight
        status = (
            f"  ✓ Fully allocated — ready!"         if remaining == 0  else
            f"  ⚠  {remaining}% still unallocated"  if remaining > 0   else
            f"  ⚠  Over-allocated by {abs(remaining)}%"
        )
        print(f"  Total Weight: {self.total_weight}%   {status}")


# ─────────────────────────────────────────────
#  DATA STORE  (in-memory)
# ─────────────────────────────────────────────

def _make_section_gradebook():
    gb = Gradebook()
    gb.add_category("SA",   "Seatwork",   30, 100)
    gb.add_category("EXAM", "Exams",      40, 100)
    gb.add_category("PROJ", "Projects",   20, 100)
    gb.add_category("RECIT","Recitation", 10, 100)
    return gb

sections = {
    "TN23": {
        "gradebook": _make_section_gradebook(),
        "students": {
            "2024-11487": {
                "Last Name": "Capuno", "First Name": "Kent Anthony",
                "Middle Initial": "C.", "status": "active",
                "grades": {"SA1": 90.0, "SA2": 85.0, "ME": 88.0, "FE": 91.0}
            },
            "2024-67676": {
                "Last Name": "Theresa", "First Name": "Maria",
                "Middle Initial": "L.", "status": "active",
                "grades": {"SA1": 75.0, "SA2": 60.0, "ME": 72.0}
            },
            "2024-33892": {
                "Last Name": "Dela Cruz", "First Name": "Juan",
                "Middle Initial": "D.", "status": "inactive",
                "grades": {"SA1": 55.0}
            },
        }
    },
    "TN24": {
        "gradebook": _make_section_gradebook(),
        "students": {
            "2024-44512": {
                "Last Name": "Cruz", "First Name": "Ana",
                "Middle Initial": "L.", "status": "active",
                "grades": {"SA1": 92, "ME": 95}
            },
        }
    },
}

def _seed_assignments():
    for sec_data in sections.values():
        gb = sec_data["gradebook"]
        for code in ["SA1", "SA2", "SA3", "SA4"]:
            gb.categories["SA"].add_assignment(code)
        for code in ["ME", "FE"]:
            gb.categories["EXAM"].add_assignment(code)

_seed_assignments()


# ─────────────────────────────────────────────
#  INPUT HELPER
# ─────────────────────────────────────────────

def get_input(prompt):
    value = input(prompt)
    if value == "-1":
        print("Program forcefully terminated.")
        sys.exit()
    return value


# ─────────────────────────────────────────────
#  GRADE INPUT HELPER  (FIX: GS19, GS20, GS74, GS76, GS78, GS79)
# ─────────────────────────────────────────────

def get_grade_input(prompt, allow_empty=False):
    """
    Prompt for a grade (0–100). Returns float or None if allow_empty and blank.
    Prints an error and returns None on invalid input instead of crashing.
    """
    raw = get_input(prompt).strip()
    if raw == "" and allow_empty:
        return None
    if raw == "":
        print("  Invalid input: grade cannot be empty.")
        return None
    try:
        val = float(raw)
    except ValueError:
        print(f"  Invalid input: '{raw}' is not a number.")
        return None
    if val < 0 or val > 100:
        print(f"  Invalid grade: {val}. Grade must be between 0 and 100.")
        return None
    return val


# ─────────────────────────────────────────────
#  UI HELPERS
# ─────────────────────────────────────────────

def print_box(lines):
    width = max(len(line) for line in lines) + 4
    print("=" * width)
    for i, line in enumerate(lines):
        print("| " + (line.center(width - 4) if i == 0 else line.ljust(width - 4)) + " |")
    print("=" * width)

def print_table(headers, rows):
    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(cell)))
    total_width = sum(col_widths) + len(col_widths) * 3 + 1
    print("=" * total_width)
    print("| " + " | ".join(headers[i].ljust(col_widths[i]) for i in range(len(headers))) + " |")
    print("=" * total_width)
    for row in rows:
        print("| " + " | ".join(str(row[i]).ljust(col_widths[i]) for i in range(len(row))) + " |")
    print("=" * total_width)


# ─────────────────────────────────────────────
#  GENERAL HELPERS
# ─────────────────────────────────────────────

def student_exists(student_id):
    return any(student_id in sections[s]["students"] for s in sections)

def generate_student_id():
    year = datetime.now().year
    while True:
        sid = f"{year}-{random.randint(100000, 999999)}"
        if not student_exists(sid):
            return sid

def select_section():
    print_box(["Available Sections:"] + [
        f"{sec} ({len(sections[sec]['students'])} students)" for sec in sections
    ])
    return get_input("Enter section: ")

def select_student(section):
    print_box(["Students in " + section + ":"] + list(sections[section]["students"].keys()))
    return get_input("Enter student ID: ")

def list_section_assignments(section):
    gb = sections[section]["gradebook"]
    lines = [f"{section} Assignments by Category:"]
    for cat in gb.categories.values():
        codes = ", ".join(sorted(cat.assignments)) if cat.assignments else "(none)"
        lines.append(f"  [{cat.name} {cat.weight}%]  {codes}")
    print_box(lines)


# ─────────────────────────────────────────────
#  VIEW
# ─────────────────────────────────────────────

def view_student_grades():
    section = select_section()
    if section not in sections:
        print("Invalid section!")
        return
    gb           = sections[section]["gradebook"]
    all_codes    = sorted(gb.all_assignments())
    headers      = ["STUD NO", "LAST NAME", "FIRST NAME", "MI"] + all_codes
    rows = []
    for sid, data in sections[section]["students"].items():
        row = [sid, data["Last Name"], data["First Name"], data["Middle Initial"]]
        for code in all_codes:
            row.append(data["grades"].get(code, "-"))
        rows.append(row)
    print_table(headers, rows)

def view_admin_table():
    for section, sec_data in sections.items():
        print(f"\nSECTION: {section}")
        gb        = sec_data["gradebook"]
        all_codes = sorted(gb.all_assignments())
        headers   = ["STUD NO", "LAST NAME", "FIRST NAME", "MI", "STATUS"] + all_codes
        rows = []
        for sid, data in sec_data["students"].items():
            row = [sid, data["Last Name"], data["First Name"], data["Middle Initial"], data["status"]]
            for code in all_codes:
                row.append(data["grades"].get(code, "-"))
            rows.append(row)
        print_table(headers, rows)


# ─────────────────────────────────────────────
#  SEARCH
# ─────────────────────────────────────────────

def search_student():
    keyword = get_input("Search (ID or name): ").lower()
    results = []
    for sec, sec_data in sections.items():
        for sid, data in sec_data["students"].items():
            name = f"{data['First Name']} {data['Last Name']}"
            if keyword in sid.lower() or keyword in name.lower():
                results.append(f"{sid} - {name} ({sec}) [{data['status']}]")
    print_box(["Results:"] + results if results else ["No results found."])


# ─────────────────────────────────────────────
#  ADMIN CRUD
# ─────────────────────────────────────────────

def add_student():
    section = select_section()
    if section not in sections:
        print("Invalid section!")
        return

    # FIX GS3: Reject empty first name
    last_name = get_input("Last name: ").strip()
    first_name = get_input("First name: ").strip()
    if not first_name:
        print("Error: First name cannot be empty.")
        return
    if not last_name:
        print("Error: Last name cannot be empty.")
        return

    sid = generate_student_id()
    sections[section]["students"][sid] = {
        "Last Name":      last_name,
        "First Name":     first_name,
        "Middle Initial": get_input("Middle initial (leave blank if none): ").strip(),
        "status":         "active",
        "grades":         {}
    }
    print(f"\nStudent created. Generated ID: {sid}")

def update_status():
    section = select_section()
    if section not in sections:
        print("Invalid section!")
        return
    student = select_student(section)
    if student not in sections[section]["students"]:
        print("Student not found!")
        return
    new_status = get_input("New status (active/inactive): ")
    sections[section]["students"][student]["status"] = new_status
    print(f"Status updated to '{new_status}'.")

# FIX GS5: Remove student from section (admin only)
def remove_student():
    section = select_section()
    if section not in sections:
        print("Invalid section!")
        return
    student = select_student(section)
    if student not in sections[section]["students"]:
        print("Student not found!")
        return
    confirm = get_input(f"Remove student '{student}' from {section}? (yes/no): ").strip().lower()
    if confirm == "yes":
        del sections[section]["students"][student]
        print(f"Student '{student}' removed from section '{section}'.")
    else:
        print("Removal cancelled.")

def add_section():
    # FIX GS83: Reject empty section name
    sec = get_input("New section name: ").strip()
    if not sec:
        print("Error: Section name cannot be empty.")
        return
    if sec in sections:
        print("Section already exists!")
        return
    sections[sec] = {"gradebook": Gradebook(), "students": {}}
    print(f"Section '{sec}' created. Use 'Manage Gradebook' to add categories and assignments.")

def remove_section():
    sec = get_input("Section to remove: ")
    if sec in sections:
        del sections[sec]
        print(f"Section '{sec}' removed.")
    else:
        print("Section not found.")

def add_assignment_to_section():
    section = select_section()
    if section not in sections:
        print("Invalid section!")
        return
    gb = sections[section]["gradebook"]
    gb.display()

    # FIX GS42: Reject empty assignment code
    code = get_input("New assignment code (e.g. SA5, QUIZ1): ").strip().upper()
    if not code:
        print("Error: Assignment code cannot be empty.")
        return

    existing = gb.find_category_of(code)
    if existing:
        print(f"'{code}' already belongs to category '{existing}'.")
        return

    if not gb.categories:
        print("No categories defined yet. Add categories first via Manage Gradebook.")
        return

    cat_id = get_input(f"Which category ID does '{code}' belong to? ").strip()
    ok, msg = gb.add_assignment(code, cat_id)
    print(("  ✓ " if ok else "  ❌ ") + msg)

def remove_assignment_from_section():
    section = select_section()
    if section not in sections:
        print("Invalid section!")
        return
    gb   = sections[section]["gradebook"]
    gb.display()
    code = get_input("Assignment code to remove: ").strip().upper()
    ok, msg = gb.remove_assignment(code)
    print(("  ✓ " if ok else "  ❌ ") + msg)


# ─────────────────────────────────────────────
#  GRADE ENTRY & EDITING
# ─────────────────────────────────────────────

def enter_assignment_scores(section):
    gb = sections[section]["gradebook"]
    list_section_assignments(section)
    a = get_input("Assignment code: ").strip().upper()
    if not gb.find_category_of(a):
        print(f"Assignment '{a}' not found in any category for this section.")
        return
    for sid in sections[section]["students"]:
        val = get_grade_input(f"  Score for {sid} (0-100): ")
        if val is not None:
            sections[section]["students"][sid]["grades"][a] = val
        else:
            print(f"  Skipping {sid} due to invalid input.")

def enter_student_scores(section):
    student = select_student(section)
    if student not in sections[section]["students"]:
        print("Student not found!")
        return
    gb = sections[section]["gradebook"]
    print("Type 'done' to stop.")
    while True:
        a = get_input("Assignment code (or 'done'): ").strip().upper()
        if a == "DONE":
            break
        if not gb.find_category_of(a):
            print(f"  '{a}' not found in any category. Available: {sorted(gb.all_assignments())}")
            continue
        val = get_grade_input("Score (0-100): ")
        if val is not None:
            sections[section]["students"][student]["grades"][a] = val

def edit_specific_score(section):
    student = select_student(section)
    if student not in sections[section]["students"]:
        print("Student not found!")
        return
    grades = sections[section]["students"][student]["grades"]
    print_box(["Current Grades:"] + [f"{a}: {v}" for a, v in sorted(grades.items())])
    a = get_input("Assignment to edit: ").strip().upper()
    if a in grades:
        val = get_grade_input(f"New score for {a} (0-100): ")
        if val is not None:
            grades[a] = val
            print("Score updated.")
    else:
        print("Assignment not found for this student.")

def edit_assignment_scores(section):
    gb = sections[section]["gradebook"]
    list_section_assignments(section)
    a = get_input("Assignment code: ").strip().upper()
    if not gb.find_category_of(a):
        print(f"Assignment '{a}' not found in any category.")
        return
    for sid in sections[section]["students"]:
        grades = sections[section]["students"][sid]["grades"]
        if a in grades:
            val = get_grade_input(f"  New score for {sid} (current {grades[a]}, 0-100): ")
            if val is not None:
                grades[a] = val

def edit_student_scores(section):
    student = select_student(section)
    if student not in sections[section]["students"]:
        print("Student not found!")
        return
    grades = sections[section]["students"][student]["grades"]
    for a in sorted(grades):
        val = get_grade_input(f"  {a} (current {grades[a]}, 0-100): ")
        if val is not None:
            grades[a] = val


# ─────────────────────────────────────────────
#  ANALYTICS
# ─────────────────────────────────────────────

def view_grade_distribution_and_stats(section):
    gb       = sections[section]["gradebook"]
    students = sections[section]["students"]
    if not students:
        print("No students in this section.")
        return

    print(f"\n{'='*55}")
    print(f"  Grade Statistics — Section {section}".center(55))
    print(f"{'='*55}")

    for cat in gb.categories.values():
        print(f"\n  [{cat.name}  {cat.weight}%]")
        for code in sorted(cat.assignments):
            scores = [
                data["grades"][code]
                for data in students.values()
                if code in data["grades"]
            ]
            print(f"    {code}:", end="")
            if scores:
                print(f"  submitted {len(scores)}/{len(students)} | "
                      f"avg {sum(scores)/len(scores):.1f} | "
                      f"high {max(scores)} | low {min(scores)}")
            else:
                print("  no grades yet")

def calculate_and_display_final_grade(section, student_id):
    gb      = sections[section]["gradebook"]
    student = sections[section]["students"].get(student_id)
    if not student:
        print("Student not found!")
        return

    final, breakdown = gb.calculate_final_grade(student["grades"])

    converter   = LetterGradeConverter()
    letter, gpa = converter.convert_with_gpa(final)
    desc        = converter.get_grade_description(letter)

    name = f"{student['First Name']} {student['Last Name']}"
    print(f"\n  {'='*50}")
    print(f"  Final Grade Report — {name}")
    print(f"  {'='*50}")
    print(f"  {'Category':<18} {'Weight':>7}   {'Avg Score':>10}   {'Contribution':>12}")
    print(f"  {'-'*50}")
    for cat_name, weight, avg, contrib in breakdown:
        avg_str = f"{avg:.2f}" if avg is not None else "—"
        print(f"  {cat_name:<18} {weight:>6}%   {avg_str:>10}   {contrib:>11.2f}%")
    print(f"  {'='*50}")
    print(f"  Final Grade : {final:.2f}%")
    print(f"  Letter      : {letter}   GPA: {gpa:.2f}")
    print(f"  Status      : {'PASS' if letter != 'F' else 'FAIL'}")
    print(f"  Description : {desc}")
    print(report_needed(name, final))

def menu_final_grade():
    section = select_section()
    if section not in sections:
        print("Invalid section!")
        return
    student_id = select_student(section)
    if student_id not in sections[section]["students"]:
        print("Student not found!")
        return
    calculate_and_display_final_grade(section, student_id)


# ─────────────────────────────────────────────
#  SIMPLE GRADE HELPERS
# ─────────────────────────────────────────────

def simple_letter_grade(score):
    x = float(score)
    return "A" if x >= 90 else "B" if x >= 80 else "C" if x >= 70 else "D" if x >= 60 else "F"

def needed_points(current_grade, passing=PASSING):
    return max(0.0, float(passing) - float(current_grade))

def report_needed(name, current_grade, passing=PASSING):
    need  = needed_points(current_grade, passing)
    grade = float(current_grade)
    if need == 0:
        return f"  ✓ {name} has passed with {grade:.1f} points."
    return f"  ✗ {name} needs {need:.1f} more points to reach {passing}."

# FIX GS37 & GS38: "No subjects provided" message and PASS/FAIL in report card
def generate_report_card(name, scores):
    if not scores:
        return f"Report Card for {name}\nNo subjects provided."
    items = list(scores.items()) if isinstance(scores, dict) else scores
    rows  = [(sub, float(val), simple_letter_grade(val)) for sub, val in items]
    lines = [
        "+" + "=" * 38 + "+",
        f"| Report Card for {name:<22}|",
        "+" + "=" * 38 + "+",
        f"| {'Subject':<20} | {'Score':<5} | {'Grade':<5} |",
        "+" + "-" * 38 + "+",
    ]
    total = 0
    for sub, val, grd in rows:
        total += val
        lines.append(f"| {sub:<20} | {val:>5.1f} | {grd:<5} |")
    avg = total / len(rows)
    avg_letter = simple_letter_grade(avg)
    status = "PASS" if avg >= PASSING else "FAIL"
    lines += [
        "+" + "-" * 38 + "+",
        f"| {'Average':<20} | {avg:>5.1f} | {avg_letter:<5} |",
        f"| {'Status':<20} | {status:<11} |",
        "+" + "=" * 38 + "+",
    ]
    return "\n".join(lines)


# ─────────────────────────────────────────────
#  LETTER GRADE CONVERTER
# ─────────────────────────────────────────────

class LetterGradeConverter:
    GRADE_SCALE = [
        (97,"A+"), (93,"A"), (90,"A-"),
        (87,"B+"), (83,"B"), (80,"B-"),
        (77,"C+"), (73,"C"), (70,"C-"),
        (67,"D+"), (63,"D"), (60,"D-"),
        (0, "F"),
    ]
    GPA_MAP = {
        "A+":4.0,"A":4.0,"A-":3.7,
        "B+":3.3,"B":3.0,"B-":2.7,
        "C+":2.3,"C":2.0,"C-":1.7,
        "D+":1.3,"D":1.0,"D-":0.7,
        "F":0.0,
    }
    DESCRIPTIONS = {
        "A+":"Excellent (Outstanding)","A":"Excellent (Superior)","A-":"Excellent (Very Good)",
        "B+":"Good (Above Average)","B":"Good (Satisfactory)","B-":"Good (Acceptable)",
        "C+":"Fair (Average)","C":"Fair (Below Average)","C-":"Fair (Minimal Passing)",
        "D+":"Poor (Barely Passing)","D":"Poor (Weak)","D-":"Poor (Very Weak)",
        "F":"Failing",
    }

    def __init__(self, custom_scale=None):
        self.grade_scale = (
            sorted(custom_scale, key=lambda x: x[0], reverse=True)
            if custom_scale else self.GRADE_SCALE
        )

    def convert_to_letter(self, numerical_grade):
        if numerical_grade < 0 or numerical_grade > 100:
            return "Invalid"
        for min_score, letter in self.grade_scale:
            if numerical_grade >= min_score:
                return letter
        return "F"

    def convert_with_gpa(self, numerical_grade):
        letter = self.convert_to_letter(numerical_grade)
        return letter, self.GPA_MAP.get(letter, 0.0)

    def get_grade_description(self, letter_grade):
        return self.DESCRIPTIONS.get(letter_grade, "Unknown")

    def display_grade_scale(self):
        print(f"\n  {'Range':<15} {'Letter':<10} {'GPA'}")
        print("  " + "-" * 35)
        for i, (min_score, letter) in enumerate(self.grade_scale):
            next_min = self.grade_scale[i+1][0] if i+1 < len(self.grade_scale) else 0
            rng = "0–59" if min_score == 0 else f"{min_score}–{next_min-1 if next_min else 100}"
            print(f"  {rng:<15} {letter:<10} {self.GPA_MAP.get(letter,0.0):.1f}")

    def generate_report(self, student_name, numerical_grade):
        letter, gpa = self.convert_with_gpa(numerical_grade)
        return {
            "student_name": student_name, "numerical_grade": numerical_grade,
            "letter_grade": letter, "gpa": gpa,
            "description": self.get_grade_description(letter),
            "status": "PASS" if letter != "F" else "FAIL",
        }

    def display_report(self, report):
        print(f"\n  {'='*45}")
        print("  STUDENT GRADE REPORT".center(45))
        print(f"  {'='*45}")
        print(f"  Student    : {report['student_name']}")
        print(f"  Numerical  : {report['numerical_grade']:.2f}%")
        print(f"  Letter     : {report['letter_grade']}")
        print(f"  GPA        : {report['gpa']:.2f}")
        print(f"  Status     : {report['status']}")
        print(f"  Description: {report['description']}")
        print(f"  {'='*45}")


# ─────────────────────────────────────────────
#  GRADE MANAGEMENT MENU
# ─────────────────────────────────────────────

def score_management():
    while True:
        print_box([
            "GRADE MANAGEMENT",
            "1 Enter scores for one assignment (all students)",
            "2 Enter scores for one student",
            "3 Edit scores for one assignment",
            "4 Edit scores for one student",
            "5 Edit specific score",
            "6 View grade stats for a section",
            "7 Calculate weighted final grade for a student",
            "0 Back",
        ])
        c = get_input("Choice: ")
        if c == "0":
            break
        if c == "7":
            menu_final_grade()
            continue

        section = select_section()
        if section not in sections:
            print("Invalid section!")
            continue

        if c == "6":
            view_grade_distribution_and_stats(section)
            continue

        {
            "1": lambda: enter_assignment_scores(section),
            "2": lambda: enter_student_scores(section),
            "3": lambda: edit_assignment_scores(section),
            "4": lambda: edit_student_scores(section),
            "5": lambda: edit_specific_score(section),
        }.get(c, lambda: print("Invalid choice."))()


# ─────────────────────────────────────────────
#  GRADEBOOK MENU  (categories + assignments)
# ─────────────────────────────────────────────

def gradebook_menu():
    while True:
        print_box([
            "GRADEBOOK — CATEGORIES & ASSIGNMENTS",
            "1 View section gradebook",
            "2 Add category",
            "3 Remove category",
            "4 Update category weight",
            "5 Add assignment to category",
            "6 Remove assignment from section",
            "7 View grade scale",
            "0 Back",
        ])
        c = get_input("Choice: ")
        if c == "0":
            break

        if c == "7":
            LetterGradeConverter().display_grade_scale()
            continue

        section = select_section()
        if section not in sections:
            print("Invalid section!")
            continue
        gb = sections[section]["gradebook"]

        if c == "1":
            gb.display()

        elif c == "2":
            cid  = get_input("Category ID: ").strip().upper()
            name = get_input("Category name: ").strip()
            try:
                weight    = float(get_input("Weight (%): "))
                max_score = float(get_input("Max score (default 100, press Enter): ").strip() or "100")
            except ValueError:
                print("Invalid number.")
                continue
            ok, msg = gb.add_category(cid, name, weight, max_score)
            print(("  ✓ " if ok else "  ❌ ") + msg)

        elif c == "3":
            gb.display()
            cid     = get_input("Category ID to remove: ").strip().upper()
            ok, msg = gb.remove_category(cid)
            print(("  ✓ " if ok else "  ❌ ") + msg)

        elif c == "4":
            gb.display()
            cid = get_input("Category ID to update: ").strip().upper()
            try:
                new_w = float(get_input("New weight (%): "))
            except ValueError:
                print("Invalid number.")
                continue
            ok, msg = gb.update_weight(cid, new_w)
            print(("  ✓ " if ok else "  ❌ ") + msg)

        elif c == "5":
            gb.display()
            # FIX GS42: also applies here — reject empty code
            code = get_input("Assignment code to add (e.g. SA5): ").strip().upper()
            if not code:
                print("Error: Assignment code cannot be empty.")
                continue
            cat_id = get_input("Category ID it belongs to: ").strip().upper()
            ok, msg = gb.add_assignment(code, cat_id)
            print(("  ✓ " if ok else "  ❌ ") + msg)

        elif c == "6":
            gb.display()
            code    = get_input("Assignment code to remove: ").strip().upper()
            ok, msg = gb.remove_assignment(code)
            print(("  ✓ " if ok else "  ❌ ") + msg)

        else:
            print("Invalid choice.")


# ─────────────────────────────────────────────
#  REPORT CARD MENU
# ─────────────────────────────────────────────

def report_card_menu():
    converter = LetterGradeConverter()
    while True:
        print_box([
            "REPORT CARD TOOLS",
            "1 Generate report card (manual subjects)",
            "2 Convert a single numerical grade",
            "3 Check points needed to pass",
            "4 View grade conversion scale",
            "0 Back",
        ])
        c = get_input("Choice: ")
        if c == "0":
            break

        if c == "1":
            name     = get_input("Student name: ")
            subjects = {}
            print("Enter subjects and scores. Type 'done' to finish.")
            while True:
                sub = get_input("Subject (or 'done'): ")
                if sub.lower() == "done":
                    break
                try:
                    subjects[sub] = float(get_input(f"  Score for {sub}: "))
                except ValueError:
                    print("  Invalid score, skipping.")
            # FIX GS37: Always print result; "No subjects provided" if empty
            print(generate_report_card(name, subjects))

        elif c == "2":
            name = get_input("Student name: ")
            try:
                num    = float(get_input("Numerical grade: "))
                report = converter.generate_report(name, num)
                converter.display_report(report)
            except ValueError:
                print("Invalid grade.")

        elif c == "3":
            name = get_input("Student name: ")
            try:
                current = float(get_input("Current grade: "))
                print(report_needed(name, current))
            except ValueError:
                print("Invalid grade.")

        elif c == "4":
            converter.display_grade_scale()

        else:
            print("Invalid choice.")


# ─────────────────────────────────────────────
#  ROLE MENUS
# ─────────────────────────────────────────────

def teacher_menu():
    while True:
        print_box([
            "TEACHER MENU",
            "1 Manage Grades",
            "2 Search Student",
            "3 View Students + Grades",
            "4 Gradebook (Categories & Assignments)",
            "5 Report Card Tools",
            "0 Exit",
        ])
        c = get_input("Choice: ")
        if c == "0":
            break
        {
            "1": score_management,
            "2": search_student,
            "3": view_student_grades,
            "4": gradebook_menu,
            "5": report_card_menu,
        }.get(c, lambda: print("Invalid choice."))()

def admin_menu():
    while True:
        print_box([
            "ADMIN MENU",
            "1  Add Student",
            "2  Update Status",
            "3  Remove Student",
            "4  Manage Grades",
            "5  Search Student",
            "6  Add Section",
            "7  Remove Section",
            "8  Add Assignment to Section",
            "9  Remove Assignment from Section",
            "10 View Full Table",
            "11 Gradebook (Categories & Assignments)",
            "12 Report Card Tools",
            "0  Exit",
        ])
        c = get_input("Choice: ")
        if c == "0":
            break
        {
            "1":  add_student,
            "2":  update_status,
            "3":  remove_student,
            "4":  score_management,
            "5":  search_student,
            "6":  add_section,
            "7":  remove_section,
            "8":  add_assignment_to_section,
            "9":  remove_assignment_from_section,
            "10": view_admin_table,
            "11": gradebook_menu,
            "12": report_card_menu,
        }.get(c, lambda: print("Invalid choice."))()


# ─────────────────────────────────────────────
#  LOGIN / ENTRY POINT
# ─────────────────────────────────────────────

def main():
    while True:
        print_box(["GRADING SYSTEM", "1 Teacher", "2 Admin", "0 Exit"])
        choice = get_input("Choice: ")
        if choice == "1":
            teacher_menu()
        elif choice == "2":
            for _ in range(3):
                if getpass("Password: ") == ADMIN_PASSWORD:
                    print("Entering Admin Mode...")
                    admin_menu()
                    break
                print("Wrong password.")
            else:
                print("Too many failed attempts.")
        elif choice == "0":
            print("Goodbye!")
            break
        else:
            print("Invalid choice.")

main()
