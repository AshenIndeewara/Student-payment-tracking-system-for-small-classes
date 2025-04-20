# app.py
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import os
from datetime import datetime, timedelta
from calendar import monthrange

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.urandom(24)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Ijse@1234'
app.config['MYSQL_DB'] = 'StudentPaymentTracking'

mysql = MySQL(app)

# Login decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
@app.route('/dashboard')
@login_required
def dashboard():
    cur = mysql.connection.cursor()
    
    # Get classes
    cur.execute("SELECT * FROM Classes WHERE TeacherID = %s", (session['teacher_id'],))
    classes = cur.fetchall()
    
    # Get students
    cur.execute("""
        SELECT s.*, c.Name as ClassName 
        FROM Students s 
        JOIN Enrollments e ON s.StudentID = e.StudentID 
        JOIN Classes c ON e.ClassID = c.ClassID 
        WHERE c.TeacherID = %s
    """, (session['teacher_id'],))
    students = cur.fetchall()
    
    # Get monthly payment total
    cur.execute("""
        SELECT COALESCE(SUM(p.Amount), 0) as monthly_total
        FROM Payments p
        JOIN Classes c ON p.ClassID = c.ClassID
        WHERE c.TeacherID = %s
        AND p.PaymentDate >= DATE_SUB(CURDATE(), INTERVAL 1 MONTH)
    """, (session['teacher_id'],))
    monthly_total = cur.fetchone()[0]
    
    cur.close()
    
    return render_template('dashboard.html', 
                         classes=classes,
                         students=students,
                         monthly_total=monthly_total)

# Authentication routes
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        
        cur = mysql.connection.cursor()
        
        # Create user
        hashed_password = generate_password_hash(password)
        cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", 
                   (username, hashed_password))
        user_id = cur.lastrowid
        
        # Create teacher profile
        cur.execute("INSERT INTO Teachers (userid, Name, Email, Phone) VALUES (%s, %s, %s, %s)",
                   (user_id, name, email, phone))
        
        mysql.connection.commit()
        cur.close()
        
        flash('Registration successful!')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        cur = mysql.connection.cursor()
        cur.execute("SELECT users.*, Teachers.TeacherID FROM users JOIN Teachers ON users.id = Teachers.userid WHERE username = %s", 
                   (username,))
        user = cur.fetchone()
        cur.close()
        
        if user and check_password_hash(user[2], password):
            session['user_id'] = user[0]
            session['teacher_id'] = user[3]
            return redirect(url_for('dashboard'))
            
        flash('Invalid credentials!')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# Class management
# @app.route('/classes', methods=['GET', 'POST'])
# @login_required
# def manage_classes():
#     if request.method == 'POST':
#         name = request.form['name']
#         whatsapp_group = request.form['whatsapp_group']
#         class_time = request.form['class_time']
        
#         cur = mysql.connection.cursor()
#         cur.execute("INSERT INTO Classes (Name, TeacherID, WhatsappGroup, ClassTime) VALUES (%s, %s, %s, %s)",
#                    (name, session['teacher_id'], whatsapp_group, class_time))
#         mysql.connection.commit()
#         cur.close()
        
#         flash('Class added successfully!')
        
#     cur = mysql.connection.cursor()
#     cur.execute("SELECT * FROM Classes WHERE TeacherID = %s", (session['teacher_id'],))
#     classes = cur.fetchall()
#     cur.close()
    
#     return render_template('classes.html', classes=classes)

@app.route('/classes', methods=['GET', 'POST'])
@login_required
def manage_classes():
    if request.method == 'POST':
        name = request.form['name']
        whatsapp_group = request.form['whatsapp_group']
        class_day = request.form['class_day']
        class_time = request.form['class_time']
        
        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO Classes (Name, TeacherID, WhatsappGroup, ClassDay, ClassTime) 
            VALUES (%s, %s, %s, %s, %s)
        """, (name, session['teacher_id'], whatsapp_group, class_day, class_time))
        mysql.connection.commit()
        cur.close()
        
        flash('Class added successfully!', 'success')
        return redirect(url_for('manage_classes'))
        
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM Classes WHERE TeacherID = %s", (session['teacher_id'],))
    classes = cur.fetchall()
    cur.close()
    
    return render_template('classes.html', classes=classes)

@app.route('/edit_class/<int:class_id>', methods=['GET', 'POST'])
@login_required
def edit_class(class_id):
    cur = mysql.connection.cursor()
    
    if request.method == 'POST':
        name = request.form['name']
        whatsapp_group = request.form['whatsapp_group']
        class_day = request.form['class_day']
        class_time = request.form['class_time']
        
        cur.execute("""
            UPDATE Classes 
            SET Name = %s, WhatsappGroup = %s, ClassDay = %s, ClassTime = %s 
            WHERE ClassID = %s AND TeacherID = %s
        """, (name, whatsapp_group, class_day, class_time, class_id, session['teacher_id']))
        mysql.connection.commit()
        
        flash('Class updated successfully!', 'success')
        return redirect(url_for('manage_classes'))
        
    cur.execute("SELECT * FROM Classes WHERE ClassID = %s AND TeacherID = %s", 
                (class_id, session['teacher_id']))
    class_data = cur.fetchone()
    cur.close()
    
    if not class_data:
        flash('Class not found!', 'error')
        return redirect(url_for('manage_classes'))
        
    return render_template('edit_class.html', class_data=class_data)

@app.route('/delete_class/<int:class_id>', methods=['POST'])
@login_required
def delete_class(class_id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM Classes WHERE ClassID = %s AND TeacherID = %s",
                (class_id, session['teacher_id']))
    mysql.connection.commit()
    cur.close()
    
    flash('Class deleted successfully!', 'success')
    return redirect(url_for('manage_classes'))

# Student management
@app.route('/students', methods=['GET', 'POST'])
@login_required
def manage_students():
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        parent_name = request.form['parent_name']
        parent_phone = request.form['parent_phone']
        class_id = request.form['class_id']
        
        cur = mysql.connection.cursor()
        
        # Add student
        cur.execute("INSERT INTO Students (Name, Phone, PerantName, PerantPhone) VALUES (%s, %s, %s, %s)",
                   (name, phone, parent_name, parent_phone))
        student_id = cur.lastrowid
        
        # Enroll in class
        cur.execute("INSERT INTO Enrollments (StudentID, ClassID) VALUES (%s, %s)",
                   (student_id, class_id))
        
        mysql.connection.commit()
        cur.close()
        
        flash('Student added successfully!')
        return redirect(url_for('manage_students'))
    
    # Get filter parameters
    search_query = request.args.get('search', '').strip()
    class_filter = request.args.get('class_filter')
    
    cur = mysql.connection.cursor()
    
    # Base query
    query = """
        SELECT s.*, c.Name as ClassName 
        FROM Students s 
        JOIN Enrollments e ON s.StudentID = e.StudentID 
        JOIN Classes c ON e.ClassID = c.ClassID 
        WHERE c.TeacherID = %s
    """
    params = [session['teacher_id']]
    
    # Add filters if provided
    if search_query:
        query += " AND s.Name LIKE %s"
        params.append(f"%{search_query}%")
    
    if class_filter:
        query += " AND c.ClassID = %s"
        params.append(class_filter)
    
    # Execute the final query
    cur.execute(query, tuple(params))
    students = cur.fetchall()
    
    # Get classes for dropdown
    cur.execute("SELECT * FROM Classes WHERE TeacherID = %s", (session['teacher_id'],))
    classes = cur.fetchall()
    
    cur.close()
    
    return render_template('students.html', 
                         students=students, 
                         classes=classes, 
                         search_query=search_query,
                         class_filter=class_filter)

# Payment management
@app.route('/payments', methods=['GET', 'POST'])
@login_required
def manage_payments():
    if request.method == 'POST':
        student_id = request.form['student_id']
        class_id = request.form['class_id']
        amount = request.form['amount']
        payment_date = request.form['payment_date']
        
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO Payments (StudentID, ClassID, Amount, PaymentDate) VALUES (%s, %s, %s, %s)",
                   (student_id, class_id, amount, payment_date))
        mysql.connection.commit()
        cur.close()
        
        flash('Payment recorded successfully!')
    
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT p.*, s.Name as StudentName, c.Name as ClassName 
        FROM Payments p 
        JOIN Students s ON p.StudentID = s.StudentID 
        JOIN Classes c ON p.ClassID = c.ClassID 
        WHERE c.TeacherID = %s 
        ORDER BY p.PaymentDate DESC
    """, (session['teacher_id'],))
    payments = cur.fetchall()
    
    cur.execute("""
        SELECT s.*, c.Name as ClassName 
        FROM Students s 
        JOIN Enrollments e ON s.StudentID = e.StudentID 
        JOIN Classes c ON e.ClassID = c.ClassID 
        WHERE c.TeacherID = %s
    """, (session['teacher_id'],))
    students = cur.fetchall()
    
    cur.execute("SELECT * FROM Classes WHERE TeacherID = %s", (session['teacher_id'],))
    classes = cur.fetchall()
    cur.close()
    
    return render_template('payments.html', payments=payments, students=students, classes=classes)

@app.route('/student_payments/<int:student_id>')
@login_required
def student_payments(student_id):
    cur = mysql.connection.cursor()
    
    # Get student details
    cur.execute("""
        SELECT s.*, c.Name as ClassName, c.ClassID 
        FROM Students s
        JOIN Enrollments e ON s.StudentID = e.StudentID
        JOIN Classes c ON e.ClassID = c.ClassID
        WHERE s.StudentID = %s AND c.TeacherID = %s
    """, (student_id, session['teacher_id']))
    
    student = cur.fetchone()
    
    if not student:
        flash('Student not found')
        return redirect(url_for('manage_students'))
    
    # Get all payments for the student
    cur.execute("""
        SELECT PaymentID, Amount, PaymentDate
        FROM Payments
        WHERE StudentID = %s AND ClassID = %s
        ORDER BY PaymentDate DESC
    """, (student_id, student[7]))  # student[7] is ClassID
    
    payments = cur.fetchall()
    
    cur.close()
    
    return render_template('student_payments.html', 
                         student=student,
                         payments=payments)

@app.route('/mark_payment/<int:student_id>', methods=['POST'])
@login_required
def mark_payment(student_id):
    amount = request.form.get('amount')
    payment_date = request.form.get('payment_date')
    class_id = request.form.get('class_id')
    
    cur = mysql.connection.cursor()
    cur.execute("""
        INSERT INTO Payments (StudentID, ClassID, Amount, PaymentDate)
        VALUES (%s, %s, %s, %s)
    """, (student_id, class_id, amount, payment_date))
    
    mysql.connection.commit()
    cur.close()
    
    flash('Payment recorded successfully!')
    return redirect(url_for('student_payments', student_id=student_id))

@app.route('/delete_payment/<int:payment_id>')
@login_required
def delete_payment(payment_id):
    cur = mysql.connection.cursor()
    
    # Get student_id before deleting payment
    cur.execute("SELECT StudentID FROM Payments WHERE PaymentID = %s", (payment_id,))
    result = cur.fetchone()
    if not result:
        flash('Payment not found')
        return redirect(url_for('manage_students'))
    
    student_id = result[0]
    
    # Delete the payment
    cur.execute("DELETE FROM Payments WHERE PaymentID = %s", (payment_id,))
    mysql.connection.commit()
    cur.close()
    
    flash('Payment deleted successfully!')
    return redirect(url_for('student_payments', student_id=student_id))

@app.route('/delete_student/<int:student_id>')
@login_required
def delete_student(student_id):
    cur = mysql.connection.cursor()
    
    # First verify this student belongs to the logged-in teacher
    cur.execute("""
        SELECT s.StudentID 
        FROM Students s
        JOIN Enrollments e ON s.StudentID = e.StudentID
        JOIN Classes c ON e.ClassID = c.ClassID
        WHERE s.StudentID = %s AND c.TeacherID = %s
    """, (student_id, session['teacher_id']))
    
    if not cur.fetchone():
        flash('Student not found or access denied')
        return redirect(url_for('manage_students'))
    
    # Delete student (cascading will handle related records)
    cur.execute("DELETE FROM Students WHERE StudentID = %s", (student_id,))
    mysql.connection.commit()
    cur.close()
    
    flash('Student deleted successfully')
    return redirect(url_for('manage_students'))

@app.route('/reports')
@login_required
def reports():
    cur = mysql.connection.cursor()
    
    # Get date range
    end_date = datetime.now()
    #get this month start date
    start_date = datetime(end_date.year, end_date.month, 1)
    
    if request.args.get('start_date'):
        start_date = datetime.strptime(request.args.get('start_date'), '%Y-%m-%d')
    if request.args.get('end_date'):
        end_date = datetime.strptime(request.args.get('end_date'), '%Y-%m-%d')
    
    # Get paid students in the month
    cur.execute("""
        SELECT 
            s.Name AS StudentName,
            c.Name AS ClassName,
            MAX(p.PaymentDate) AS LastPayment,
            SUM(p.Amount) AS TotalAmount
        FROM Students s
        JOIN Enrollments e ON s.StudentID = e.StudentID
        JOIN Classes c ON e.ClassID = c.ClassID
        LEFT JOIN Payments p ON s.StudentID = p.StudentID
        WHERE c.TeacherID = %s
        AND p.PaymentDate BETWEEN %s AND %s
        GROUP BY s.StudentID, s.Name, c.Name
        HAVING LastPayment IS NOT NULL
    """, (session['teacher_id'], start_date, end_date))
    
    class_summaries = cur.fetchall()
    total_amount = 0
    for summary in class_summaries:
        total_amount += summary[3]
        
    # Get unpaid students
    cur.execute("""
        SELECT 
            s.Name as StudentName,
            c.Name as ClassName,
            MAX(p.PaymentDate) as LastPayment
        FROM Students s
        JOIN Enrollments e ON s.StudentID = e.StudentID
        JOIN Classes c ON e.ClassID = c.ClassID
        LEFT JOIN Payments p ON s.StudentID = p.StudentID
        WHERE c.TeacherID = %s
        GROUP BY s.StudentID, c.Name
        HAVING LastPayment < %s OR LastPayment IS NULL
    """, (session['teacher_id'], start_date))
    
    unpaid_students = cur.fetchall()
    
    cur.close()
    
    return render_template('reports.html',
                         class_summaries=class_summaries,
                         unpaid_students=unpaid_students,
                         total_amount=total_amount,
                         start_date=start_date.strftime('%Y-%m-%d'),
                         end_date=end_date.strftime('%Y-%m-%d'))

@app.template_filter('currency')
def currency_filter(value):
    return f"Rs.{value}"

if __name__ == '__main__':
    app.run(debug=True)