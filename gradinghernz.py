import json
import os

# ============================================
# FEATURE 1: GRADING CATEGORIES WITH CUSTOM WEIGHTS
# ============================================

class GradingCategory:
    """Represents a single grading category with weight"""
    
    def __init__(self, category_id, name, weight, max_score=100):
        self.category_id = category_id
        self.name = name
        self.weight = weight  # Percentage weight (e.g., 30 for 30%)
        self.max_score = max_score
        self.grades = []  # List of grades for this category
    
    def add_grade(self, score, student_id, assignment_name=""):
        """Add a grade to this category"""
        grade = {
            'student_id': student_id,
            'score': score,
            'assignment_name': assignment_name,
            'max_score': self.max_score
        }
        self.grades.append(grade)
        return grade
    
    def get_student_average(self, student_id):
        """Calculate average grade for a specific student in this category"""
        student_grades = [g['score'] for g in self.grades if g['student_id'] == student_id]
        if not student_grades:
            return 0
        return sum(student_grades) / len(student_grades)
    
    def to_dict(self):
        """Convert to dictionary for JSON storage"""
        return {
            'category_id': self.category_id,
            'name': self.name,
            'weight': self.weight,
            'max_score': self.max_score,
            'grades': self.grades
        }
    
    @staticmethod
    def from_dict(data):
        """Create category from dictionary"""
        category = GradingCategory(
            data['category_id'],
            data['name'],
            data['weight'],
            data.get('max_score', 100)
        )
        category.grades = data.get('grades', [])
        return category


class Gradebook:
    """Manages grading categories with weights"""
    
    def __init__(self, gradebook_file='gradebook_data.json'):
        self.gradebook_file = gradebook_file
        self.categories = {}  # category_id -> GradingCategory
        self.total_weight = 0
        self.load_gradebook()
    
    def load_gradebook(self):
        """Load grading categories from file"""
        if os.path.exists(self.gradebook_file):
            try:
                with open(self.gradebook_file, 'r') as f:
                    data = json.load(f)
                    self.categories = {
                        cat_id: GradingCategory.from_dict(cat_data)
                        for cat_id, cat_data in data.get('categories', {}).items()
                    }
                    self.total_weight = data.get('total_weight', 0)
                print(f"✓ Loaded {len(self.categories)} grading categories")
            except:
                print("! No gradebook data found, starting fresh")
    
    def save_gradebook(self):
        """Save grading categories to file"""
        with open(self.gradebook_file, 'w') as f:
            json.dump({
                'categories': {cid: cat.to_dict() for cid, cat in self.categories.items()},
                'total_weight': self.total_weight
            }, f, indent=4)
    
    def add_category(self, category_id, name, weight, max_score=100):
        """
        Add a new grading category with custom weight
        Returns: (success, message)
        """
        # Check if category already exists
        if category_id in self.categories:
            return False, f"Category '{category_id}' already exists!"
        
        # Check if weight is valid
        if weight <= 0:
            return False, "Weight must be greater than 0"
        
        # Check if total weight would exceed 100
        if self.total_weight + weight > 100:
            return False, f"Cannot add category. Total weight would be {self.total_weight + weight}% (maximum is 100%)"
        
        # Create and add category
        category = GradingCategory(category_id, name, weight, max_score)
        self.categories[category_id] = category
        self.total_weight += weight
        self.save_gradebook()
        
        return True, f"✓ Category '{name}' added with {weight}% weight (Total weight: {self.total_weight}%)"
    
    def remove_category(self, category_id):
        """Remove a grading category"""
        if category_id not in self.categories:
            return False, "Category not found"
        
        removed_weight = self.categories[category_id].weight
        del self.categories[category_id]
        self.total_weight -= removed_weight
        self.save_gradebook()
        
        return True, f"✓ Category removed. Total weight is now {self.total_weight}%"
    
    def update_category_weight(self, category_id, new_weight):
        """Update the weight of an existing category"""
        if category_id not in self.categories:
            return False, "Category not found"
        
        old_weight = self.categories[category_id].weight
        weight_difference = new_weight - old_weight
        
        # Check if total would exceed 100
        if self.total_weight + weight_difference > 100:
            return False, f"Total weight would be {self.total_weight + weight_difference}% (maximum 100%)"
        
        if new_weight <= 0:
            return False, "Weight must be greater than 0"
        
        self.categories[category_id].weight = new_weight
        self.total_weight += weight_difference
        self.save_gradebook()
        
        return True, f"✓ Category weight updated from {old_weight}% to {new_weight}%"
    
    def enter_grade(self, category_id, student_id, score, assignment_name=""):
        """
        Enter a grade for a student in a specific category
        Returns: (success, message)
        """
        if category_id not in self.categories:
            return False, "Category not found"
        
        if score < 0 or score > self.categories[category_id].max_score:
            return False, f"Score must be between 0 and {self.categories[category_id].max_score}"
        
        category = self.categories[category_id]
        category.add_grade(score, student_id, assignment_name)
        self.save_gradebook()
        
        return True, f"✓ Grade {score}/{category.max_score} recorded for student {student_id} in {category.name}"
    
    def calculate_student_grade(self, student_id):
        """
        Calculate final numerical grade based on weighted categories
        Returns: weighted average grade (0-100)
        """
        if self.total_weight == 0:
            return 0
        
        weighted_sum = 0
        categories_used = 0
        
        for category in self.categories.values():
            avg = category.get_student_average(student_id)
            if avg > 0:  # Only include categories with grades
                weighted_sum += avg * (category.weight / 100)
                categories_used += 1
        
        if categories_used == 0:
            return 0
        
        # Normalize based on actual weight percentage
        final_grade = weighted_sum * 100
        return round(final_grade, 2)
    
    def get_category_summary(self):
        """Get summary of all grading categories"""
        if not self.categories:
            print("\n📭 No grading categories created yet")
            return
        
        print("\n" + "="*60)
        print("GRADING CATEGORIES".center(60))
        print("="*60)
        print(f"{'ID':<15} {'Category':<20} {'Weight':<12} {'Max Score':<12}")
        print("-"*60)
        
        for cid, category in self.categories.items():
            print(f"{cid:<15} {category.name:<20} {category.weight}%{'':<9} {category.max_score}")
        
        print("-"*60)
        print(f"Total Weight: {self.total_weight}%")
        remaining = 100 - self.total_weight
        if remaining > 0:
            print(f"⚠️ Remaining weight to allocate: {remaining}%")
        elif self.total_weight == 100:
            print("✅ Total weight is 100% - Ready for grade calculation!")
        else:
            print(f"⚠️ Total weight exceeds 100% by {abs(remaining)}%")


# ============================================
# FEATURE 2: CONVERT NUMERICAL GRADES TO LETTER GRADES
# ============================================

class LetterGradeConverter:
    """Converts numerical grades to letter grades"""
    
    # Standard grade scale
    GRADE_SCALE = [
        (97, 'A+'), (93, 'A'), (90, 'A-'),
        (87, 'B+'), (83, 'B'), (80, 'B-'),
        (77, 'C+'), (73, 'C'), (70, 'C-'),
        (67, 'D+'), (63, 'D'), (60, 'D-'),
        (0, 'F')
    ]
    
    # Custom grade scale (can be modified)
    def __init__(self, custom_scale=None):
        """
        Initialize with custom grade scale if provided
        custom_scale: list of (minimum_score, letter_grade) tuples
        """
        if custom_scale:
            self.grade_scale = sorted(custom_scale, key=lambda x: x[0], reverse=True)
        else:
            self.grade_scale = self.GRADE_SCALE
    
    def convert_to_letter(self, numerical_grade):
        """
        Convert numerical grade to letter grade
        Returns: letter grade string
        """
        if numerical_grade < 0 or numerical_grade > 100:
            return "Invalid"
        
        for min_score, letter in self.grade_scale:
            if numerical_grade >= min_score:
                return letter
        return 'F'
    
    def convert_with_gpa(self, numerical_grade):
        """
        Convert numerical grade to letter grade and GPA
        Returns: (letter_grade, gpa_points)
        """
        letter = self.convert_to_letter(numerical_grade)
        
        # GPA conversion
        gpa_map = {
            'A+': 4.0, 'A': 4.0, 'A-': 3.7,
            'B+': 3.3, 'B': 3.0, 'B-': 2.7,
            'C+': 2.3, 'C': 2.0, 'C-': 1.7,
            'D+': 1.3, 'D': 1.0, 'D-': 0.7,
            'F': 0.0
        }
        
        gpa = gpa_map.get(letter, 0.0)
        return letter, gpa
    
    def get_grade_description(self, letter_grade):
        """Get description for letter grade"""
        descriptions = {
            'A+': 'Excellent (Outstanding)',
            'A': 'Excellent (Superior)',
            'A-': 'Excellent (Very Good)',
            'B+': 'Good (Above Average)',
            'B': 'Good (Satisfactory)',
            'B-': 'Good (Acceptable)',
            'C+': 'Fair (Average)',
            'C': 'Fair (Below Average)',
            'C-': 'Fair (Minimal Passing)',
            'D+': 'Poor (Barely Passing)',
            'D': 'Poor (Weak)',
            'D-': 'Poor (Very Weak)',
            'F': 'Failing'
        }
        return descriptions.get(letter_grade, 'Unknown')
    
    def display_grade_scale(self):
        """Display the current grade scale"""
        print("\n" + "="*50)
        print("GRADE CONVERSION SCALE".center(50))
        print("="*50)
        print(f"{'Numerical Grade':<20} {'Letter Grade':<15} {'GPA':<8}")
        print("-"*50)
        
        # Display in reverse order (highest to lowest)
        for min_score, letter in self.grade_scale:
            if min_score == 0:
                print(f"{'0-59':<20} {letter:<15} {self.get_gpa_value(letter):<8.1f}")
            else:
                next_lower = self.get_next_lower_bound(min_score)
                if next_lower:
                    print(f"{min_score}-{next_lower-1:<7} {letter:<15} {self.get_gpa_value(letter):<8.1f}")
                else:
                    print(f"{min_score}-100{'':<4} {letter:<15} {self.get_gpa_value(letter):<8.1f}")
        print("="*50)
    
    def get_gpa_value(self, letter):
        """Get GPA value for a letter grade"""
        gpa_map = {
            'A+': 4.0, 'A': 4.0, 'A-': 3.7,
            'B+': 3.3, 'B': 3.0, 'B-': 2.7,
            'C+': 2.3, 'C': 2.0, 'C-': 1.7,
            'D+': 1.3, 'D': 1.0, 'D-': 0.7,
            'F': 0.0
        }
        return gpa_map.get(letter, 0.0)
    
    def get_next_lower_bound(self, current_min):
        """Helper to find next lower grade bound"""
        for min_score, _ in self.grade_scale:
            if min_score < current_min:
                return min_score
        return None
    
    def generate_report(self, student_name, numerical_grade):
        """
        Generate a complete grade report
        Returns: dictionary with all grade information
        """
        letter, gpa = self.convert_with_gpa(numerical_grade)
        description = self.get_grade_description(letter)
        
        return {
            'student_name': student_name,
            'numerical_grade': numerical_grade,
            'letter_grade': letter,
            'gpa': gpa,
            'description': description,
            'status': 'PASS' if letter != 'F' else 'FAIL'
        }
    
    def display_report(self, report):
        """Display a formatted grade report"""
        print("\n" + "="*60)
        print("STUDENT GRADE REPORT".center(60))
        print("="*60)
        print(f"Student Name: {report['student_name']}")
        print(f"Numerical Grade: {report['numerical_grade']:.2f}%")
        print(f"Letter Grade: {report['letter_grade']}")
        print(f"GPA: {report['gpa']:.2f}")
        print(f"Status: {report['status']}")
        print(f"Description: {report['description']}")
        print("="*60)