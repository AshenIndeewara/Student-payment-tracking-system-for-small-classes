-- Users table (no changes needed)
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL
);

-- Teachers table (fixed typos and added index)
CREATE TABLE Teachers (
    TeacherID INT AUTO_INCREMENT PRIMARY KEY,
    userid INT NOT NULL,
    Name VARCHAR(255) NOT NULL,
    Email VARCHAR(255) UNIQUE,
    Phone VARCHAR(15),
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (userid) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_teacher_user (userid)
);

-- Classes table (modified time-related columns)
CREATE TABLE Classes (
    ClassID INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(255) NOT NULL,
    TeacherID INT NOT NULL,
    WhatsappGroup VARCHAR(255),
    ClassDay VARCHAR(10),
    ClassTime TIME,
    FOREIGN KEY (TeacherID) REFERENCES Teachers(TeacherID) ON DELETE CASCADE,
    INDEX idx_class_teacher (TeacherID)
);

-- Students table (fixed typo in ParentName)
CREATE TABLE Students (
    StudentID INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(255) NOT NULL,
    Phone VARCHAR(15),
    PerantName VARCHAR(255),
    PerantPhone VARCHAR(15),
    EnrolledAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_student_name (Name)
);

-- Enrollments table (added index)
CREATE TABLE Enrollments (
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

-- Payments table (added index and payment status)
CREATE TABLE Payments (
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