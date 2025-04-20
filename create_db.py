import mysql.connector

# Database connection parameters
host = "megarun.mysql.pythonanywhere-services.com"       # Your MySQL server address
user = "megarun"            # Your MySQL username
password = "Ijse@1234"    # Your MySQL password
database_name = "StudentPaymentTracking"  # Name of the database to create

# Connect to MySQL server
try:
    conn = mysql.connector.connect(
        host=host,
        user=user,
        password=password
    )
    cursor = conn.cursor()
    print("Connected to MySQL server.")

    # Create database
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database_name};")
    print(f"Database '{database_name}' created or already exists.")

    # Use the newly created database
    cursor.execute(f"USE {database_name};")

    # Create tables
    tables = {
        "users": """
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(255) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL
            );
        """,
        "Teachers": """
            CREATE TABLE IF NOT EXISTS Teachers (
                TeacherID INT AUTO_INCREMENT PRIMARY KEY,
                userid INT NOT NULL,
                Name VARCHAR(255) NOT NULL,
                Email VARCHAR(255) UNIQUE,
                Phone VARCHAR(15),
                CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (userid) REFERENCES users(id) ON DELETE CASCADE,
                INDEX idx_teacher_user (userid)
            );
        """,
        "Classes": """
            CREATE TABLE IF NOT EXISTS Classes (
                ClassID INT AUTO_INCREMENT PRIMARY KEY,
                Name VARCHAR(255) NOT NULL,
                TeacherID INT NOT NULL,
                WhatsappGroup VARCHAR(255),
                ClassDay VARCHAR(10),
                ClassTime TIME,
                FOREIGN KEY (TeacherID) REFERENCES Teachers(TeacherID) ON DELETE CASCADE,
                INDEX idx_class_teacher (TeacherID)
            );
        """,
        "Students": """
            CREATE TABLE IF NOT EXISTS Students (
                StudentID INT AUTO_INCREMENT PRIMARY KEY,
                Name VARCHAR(255) NOT NULL,
                Phone VARCHAR(15),
                PerantName VARCHAR(255),
                ParentPhone VARCHAR(15),
                EnrolledAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_student_name (Name)
            );
        """,
        "Enrollments": """
            CREATE TABLE IF NOT EXISTS Enrollments (
                EnrollmentID INT AUTO_INCREMENT PRIMARY KEY,
                StudentID INT NOT NULL,
                ClassID INT NOT NULL,
                EnrolledDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (StudentID) REFERENCES Students(StudentID) ON DELETE CASCADE,
                FOREIGN KEY (ClassID) REFERENCES Classes(ClassID) ON DELETE CASCADE,
                UNIQUE (StudentID, ClassID),
                INDEX idx_enrollment_class (ClassID),
                INDEX idx_enrollment_student (StudentID)
            );
        """,
        "Payments": """
            CREATE TABLE IF NOT EXISTS Payments (
                PaymentID INT AUTO_INCREMENT PRIMARY KEY,
                StudentID INT NOT NULL,
                ClassID INT NOT NULL,
                Amount DECIMAL(10, 2) NOT NULL,
                PaymentDate DATE NOT NULL,
                PaymentStatus ENUM('pending', 'completed', 'failed') DEFAULT 'pending',
                FOREIGN KEY (StudentID) REFERENCES Students(StudentID) ON DELETE CASCADE,
                FOREIGN KEY (ClassID) REFERENCES Classes(ClassID) ON DELETE CASCADE,
                INDEX idx_payment_student (StudentID),
                INDEX idx_payment_class (ClassID)
            );
        """
    }

    for table_name, table_query in tables.items():
        cursor.execute(table_query)
        print(f"Table '{table_name}' created or already exists.")

    # Close connection
    cursor.close()
    conn.close()
    print("Database setup complete and connection closed.")

except mysql.connector.Error as err:
    print(f"Error: {err}")
