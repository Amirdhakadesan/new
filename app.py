from flask import Flask, render_template, request, redirect, url_for, session
from flask_mail import Mail, Message
from config import Config
from db import get_db_connection

app = Flask(__name__)
app.config.from_object(Config)
mail = Mail(app)

@app.route('/')
def home():
    return render_template('Home.html')

@app.route('/Faculty')
def faculty():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM faculty")
    faculty_list = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template('Faculty.html', faculty_list=faculty_list)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']

        try:
            msg = Message(subject=f"New Contact Message from {name}",
                          recipients=[app.config['MAIL_USERNAME']])
            msg.body = f"From: {name} <{email}>\n\nMessage:\n{message}"
            mail.send(msg)
            return render_template('Contact.html', success="Your message has been sent successfully.")
        except Exception as e:
            print(e)
            return render_template('Contact.html', error="Failed to send message.")

    return render_template('Contact.html')

@app.route('/facultylist')
def facultylist():
    return render_template('facultylist.html')

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == 'admin' and password == 'admin123':
            session['admin_logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            error = "Invalid username or password"

    return render_template('adminpage.html', logged_in=False, error=error)

@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin'))

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM faculty")
    faculty = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template('adminpage.html', logged_in=True, faculty=faculty)

@app.route('/add', methods=['GET', 'POST'])
def add_faculty():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin'))

    if request.method == 'POST':
        name = request.form['name']
        dept = request.form['dept']
        title = request.form['title']

        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute("INSERT INTO faculty (name, dept, title) VALUES (%s, %s, %s)", (name, dept, title))
        db.commit()
        cursor.close()
        db.close()

        return redirect(url_for('admin_dashboard'))

    return render_template('add_faculty.html')

@app.route('/edit/<int:faculty_id>', methods=['GET', 'POST'])
def edit_faculty(faculty_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin'))

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    if request.method == 'POST':
        name = request.form['name']
        dept = request.form['dept']
        title = request.form['title']
        cursor.execute("UPDATE faculty SET name=%s, dept=%s, title=%s WHERE id=%s", (name, dept, title, faculty_id))
        db.commit()
        cursor.close()
        db.close()
        return redirect(url_for('admin_dashboard'))

    cursor.execute("SELECT * FROM faculty WHERE id = %s", (faculty_id,))
    faculty = cursor.fetchone()
    cursor.close()
    db.close()

    if faculty:
        return render_template('edit_faculty.html', faculty=faculty)
    else:
        return "Faculty not found", 404

@app.route('/delete/<int:faculty_id>')
def delete_faculty(faculty_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin'))

    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("DELETE FROM faculty WHERE id = %s", (faculty_id,))
    db.commit()
    cursor.close()
    db.close()
    return redirect(url_for('admin_dashboard'))

@app.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin'))

if __name__ == '__main__':
    app.run()
