def calculate_weighted_final_grade(section, student_id, assignment_weights):
    if section not in sections or student_id not in sections[section]["students"]:
        return "Student or Section not found."

    grades = sections[section]["students"][student_id]["grades"]
    weighted_sum = 0
    total_weight_applied = 0

    for assignment, weight in assignment_weights.items():
        if assignment in grades:
            weighted_sum += grades[assignment] * (weight / 100)
            total_weight_applied += weight
    
    if total_weight_applied == 0:
        return 0.0

    # Normalizes the grade in case the applied weights don't equal exactly 100% yet
    final_grade = (weighted_sum / (total_weight_applied / 100))
    return round(final_grade, 2)

def view_grade_distribution_and_stats(section):
    if section not in sections:
        print("Invalid section!")
        return
        
    print(f"\n--- Grade Statistics for Section: {section} ---")
    
    students = sections[section]["students"]
    assignments = sorted(sec_act[section])
    
    if not students:
        print("No students in this section.")
        return
        
    for act in assignments:
        scores = []
        for sid, data in students.items():
            if act in data["grades"]:
                scores.append(data["grades"][act])
                
        if scores:
            highest = max(scores)
            lowest = min(scores)
            avg = sum(scores) / len(scores)
            
            print(f"[{act}]")
            print(f"  Submitted: {len(scores)}/{len(students)} students")
            print(f"  Average:   {avg:.2f}")
            print(f"  Highest:   {highest}")
            print(f"  Lowest:    {lowest}\n")
        else:
            print(f"[{act}]")
            print("  No grades entered yet.\n")