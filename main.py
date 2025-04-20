from flask import Flask, redirect, render_template, request, make_response
from crud import *
from cookies import *

def create_cookie(username, password, teacher):
    class_list = get_teacher_classes(teacher[0])
    print(class_list)
    response = make_response(render_template('home.html', username=username, teacher=teacher, class_list=class_list))
    response.set_cookie('username', username)
    response.set_cookie('userid', encrypt_text(str(teacher[0])))
    return response

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    username = request.cookies.get('username')
    if username:
        userid = request.cookies.get('userid')
        print(userid)
        teacher = get_teacher_by_id(decrypt_text(userid))
        if teacher:
            class_list = get_teacher_classes(teacher[0])
            return render_template('home.html', username=username, teacher=teacher, class_list=class_list)
        else:
            return redirect('/login')
    else:
        return redirect('/login')

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        teacher, hashed_password = teacher_login(username, password)
        if teacher:
            cookie = create_cookie(username, hashed_password, teacher)
            return cookie
        else:
            return 'Invalid username or password'
    return render_template('login.html')

@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        return 'Username: ' + username + ' Password: ' + password
    return render_template('signup.html')

@app.route("/get_students/<int:class_id>", methods=['GET'])
def get_students(class_id):
    students = get_students_in_class(class_id)
    return students
    

if __name__ == '__main__':
    app.run(debug=True)