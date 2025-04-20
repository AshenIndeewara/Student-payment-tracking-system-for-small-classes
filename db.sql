CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL
);
CREATE TABLE Teachers (
    TeacherID INT AUTO_INCREMENT PRIMARY KEY, -- Unique identifier for teachers
    userid INT NOT NULL,                      -- Links to the users table
    Name VARCHAR(255) NOT NULL,
    Email VARCHAR(255) UNIQUE,
    Phone VARCHAR(15),
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (userid) REFERENCES users(id) ON DELETE CASCADE
);
CREATE TABLE Classes (
    ClassID INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(255) NOT NULL,
    TeacherID INT NOT NULL,
    WhatsappGroup VARCHAR(255),
    ClassTime VARCHAR(255),
    FOREIGN KEY (TeacherID) REFERENCES Teachers(TeacherID) ON DELETE CASCADE
);
CREATE TABLE Students (
    StudentID INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(255) NOT NULL,
    Phone VARCHAR(15),
    PerantName VARCHAR(255),
    PerantPhone VARCHAR(15),
    EnrolledAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE Enrollments (
    EnrollmentID INT AUTO_INCREMENT PRIMARY KEY,
    StudentID INT NOT NULL,
    ClassID INT NOT NULL,
    EnrolledDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (StudentID) REFERENCES Students(StudentID) ON DELETE CASCADE,
    FOREIGN KEY (ClassID) REFERENCES Classes(ClassID) ON DELETE CASCADE,
    UNIQUE (StudentID, ClassID) -- To avoid duplicate enrollments
);
CREATE TABLE Payments (
    PaymentID INT AUTO_INCREMENT PRIMARY KEY,
    StudentID INT NOT NULL,
    ClassID INT NOT NULL,
    Amount DECIMAL(10, 2) NOT NULL,
    PaymentDate DATE NOT NULL,
    FOREIGN KEY (StudentID) REFERENCES Students(StudentID) ON DELETE CASCADE,
    FOREIGN KEY (ClassID) REFERENCES Classes(ClassID) ON DELETE CASCADE
);

ALTER TABLE Classes 
DROP COLUMN ClassTime;

ALTER TABLE Classes 
ADD COLUMN ClassDay VARCHAR(10),
ADD COLUMN ClassTime TIME;

CREATE INDEX idx_student_name ON Students(Name);
CREATE INDEX idx_enrollment_class ON Enrollments(ClassID);
CREATE INDEX idx_class_teacher ON Classes(TeacherID);