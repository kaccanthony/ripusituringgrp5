PASSING = 70

def needed_points(current_grade, passing=PASSING):
    """Return how many more points a student needs to pass."""
    grade = float(current_grade)
    return max(0.0, float(passing) - grade)


def report_needed(name, current_grade, passing=PASSING):
    need = needed_points(current_grade, passing)
    grade = float(current_grade)
    if need == 0:
        return f"{name} has already passed with {grade:.1f} points."
    return f"{name} needs {need:.1f} more points to reach {passing}."


if __name__ == "__main__":
    name = input("Enter student name: ") or "Student"
    grade = input("Enter current raw grade: ")

    try:
        print(report_needed(name, grade))
    except ValueError:
        print("Please enter a valid number for the grade.")