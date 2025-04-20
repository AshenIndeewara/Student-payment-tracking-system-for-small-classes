import mysql.connector
from mysql.connector import Error
import hashlib

# Function to create a connection to the MySQL database
def create_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Ijse@1234",
        database="StudentPaymentTracking"
    )

# Function to hash passwords (for better security)
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Create Teacher Account (Register) (C)
def create_teacher_account(name, email, phone, username, password):
    try:
        connection = create_connection()
        cursor = connection.cursor()

        # First, insert into the users table for authentication
        hashed_password = hash_password(password)  # Hash the password before storing
        query = "INSERT INTO users (username, password) VALUES (%s, %s)"
        cursor.execute(query, (username, hashed_password))
        connection.commit()

        # Get the id of the new user
        user_id = cursor.lastrowid

        # Now, insert the teacher information into the Teachers table
        query = "INSERT INTO Teachers (userid, Name, Email, Phone) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (user_id, name, email, phone))
        connection.commit()

        print(f"Teacher {name} registered successfully.")
        return True
    except Error as e:
        print(f"Error: {e}")
        return False
    finally:
        cursor.close()
        connection.close()

# Teacher Login (R)
def teacher_login(username, password):
    try:
        connection = create_connection()
        cursor = connection.cursor()

        # Hash the provided password
        hashed_password = hash_password(password)

        # Verify if the username and hashed password match a record in the users table
        query = "SELECT * FROM users WHERE username = %s AND password = %s"
        cursor.execute(query, (username, hashed_password))
        user = cursor.fetchone()

        if user:
            # Fetch teacher info by using the user ID
            query = "SELECT * FROM Teachers WHERE userid = %s"
            cursor.execute(query, (user[0],))  # user[0] is the user ID from users table
            teacher = cursor.fetchone()
            print(teacher)
            if teacher:
                print(f"Login successful! Welcome {teacher[1]} ({teacher[2]})")
                return teacher,hashed_password
            else:
                print("Teacher not found.")
                return False
        else:
            print("Invalid username or password.")
            return False
    except Error as e:
        print(f"Error: {e}")
    finally:
        cursor.close()
        connection.close()

# Register a new teacher
# create_teacher_account("John Doe", "john.doe@example.com", "0123456789", "johndoe", "password123")

# Teacher login
# teacher_login("johndoe", "password123")

# Add a new class (C)
def add_class(teacher_id, class_name, class_time, whatsapp_group):
    try:
        connection = create_connection()
        cursor = connection.cursor()

        # Insert class data into the Classes table
        query = "INSERT INTO Classes (Name, TeacherID, ClassTime, WhatsappGroup) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (class_name, teacher_id, class_time, whatsapp_group))
        connection.commit()

        print(f"Class '{class_name}' added successfully!")
    except Error as e:
        print(f"Error: {e}")
    finally:
        cursor.close()
        connection.close()

# Get all classes for a specific teacher (R)
def get_teacher_classes(teacher_id):
    try:
        connection = create_connection()
        cursor = connection.cursor()

        # Query to get all classes for the teacher
        query = "SELECT * FROM Classes WHERE TeacherID = %s"
        cursor.execute(query, (teacher_id,))
        classes = cursor.fetchall()

        if classes:
            print(f"Classes taught by Teacher with TeacherID = {teacher_id}:")
            return classes
        else:
            print(f"No classes found for Teacher with TeacherID = {teacher_id}.")
            return "No classes found."
    except Error as e:
        print(f"Error: {e}")
        return False
    finally:
        cursor.close()
        connection.close()

# Example Usage:
# Assuming a teacher with TeacherID = 1 wants to view their classes
# get_teacher_classes(1)

# Get Teacher Details by TeacherID (R)
def get_teacher_by_id(teacher_id):
    try:
        connection = create_connection()
        cursor = connection.cursor()

        # Query to get the teacher's details by TeacherID
        query = "SELECT * FROM Teachers WHERE TeacherID = %s"
        cursor.execute(query, (teacher_id,))
        teacher = cursor.fetchone()

        if teacher:
            print(f"Teacher Details (TeacherID = {teacher_id}):")
            print(f"Name: {teacher[2]}")
            print(f"Email: {teacher[3]}")
            print(f"Phone: {teacher[4]}")
            print(f"Created At: {teacher[5]}")
            return teacher
        else:
            print(f"No teacher found with TeacherID = {teacher_id}.")
            return False
    except Error as e:
        print(f"Error: {e}")
        return False
    finally:
        cursor.close()
        connection.close()

# Get all students in a specific class (R)
def get_students_in_class(class_id):
    try:
        connection = create_connection()
        cursor = connection.cursor()

        # Query to get the students in the given class using the Enrollments table
        query = """
        SELECT s.StudentID, s.Name, s.Phone, s.PerantName, s.PerantPhone, e.EnrolledDate
        FROM Students s
        JOIN Enrollments e ON s.StudentID = e.StudentID
        WHERE e.ClassID = %s
        """
        cursor.execute(query, (class_id,))
        students = cursor.fetchall()

        if students:
            return students
        else:
            print(f"No students found in ClassID = {class_id}.")
            return "No students found."
    except Error as e:
        print(f"Error: {e}")
        return False
    finally:
        cursor.close()
        connection.close()

# Example Usage:
# Assuming you want to fetch the students for ClassID = 1
# get_students_in_class(1)