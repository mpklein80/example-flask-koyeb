#  gunicorn does not run on windows, but works on koyeb
#  pip3 freeze > requirements.txt
# also need in requirement ...    gunicorn==20.1.0

import sys  #only for printing python number
import sqlite3
from flask import Flask, session, request, render_template, redirect, url_for

app = Flask(__name__, static_folder='static')

def init_db(the_db):
    conn = sqlite3.connect(the_db)
    conn.execute('PRAGMA journal_mode=WAL;') #enable WAL mode
    conn.isolation_level = None # Enable auto commit mode
    return conn

id_form = '''<form action='' method="post"> ID <input type="text" name="id"> Password <input type="text" name="password"> <input type="submit" value="Login" /> </form>'''



def submit_score(score):
    conn = sqlite3.connect('scores.db')
    conn.execute("REPLACE INTO " + str(session['category']) + "(id,name,exercise,score) VALUES(" + "'" + str(session['id']) + "','" + str(session['name']) + "','" + str(session['exercise']) + "','" + str(score) + "')")
    conn.commit()
    conn.close()


def load_quiz(category,exercise):
    content = ""
    answers = ""
    conn = sqlite3.connect('quiz.db')
    cursor = conn.execute("SELECT * from " + category + " where exercise = '" + exercise + "'")
    i=1
    for row in cursor:
        content += "<p>" + str(i) + ".  " + row[1] + "</p>"
        i+=1
        if not row[2] == None:
            content += "<img src='" + row[2] + "'/>"
        answers += row[3]
        content += "<br><select class='quiz_q'>"
        content += "<option value = 'A'>" + row[4] + "</option>"
        content += "<option value = 'B'>" + row[5] + "</option>"
        content += "<option value = 'C'>" + row[6] + "</option>"
        content += "<option value = 'D'>" + row[7] + "</option>"
        content += "</select><HR>"
    content += "<button onclick='grade();'>Submit</button>"
    session['answers'] = answers
    return content

def quiz_form():
    tables=['as_physics','as_electronics','a2_physics','a2_electronics','eng1']
    exercises=''
    for table in tables:
        exercises += "<form action='' method='get'><input type='hidden' name='category' value='" + table + "'/>"
        exercises += "<select name='exercise'>"
        conn = sqlite3.connect('exercises.db')
        cursor = conn.execute("SELECT distinct exercise from " + table)
        response = cursor.fetchall()
        for row in response:
            exercises += "<option value='" + row[0] + "'>" + row[0] + "</option>"
        exercises += "</select><input type='submit' value='&#10148;' ></form>"
        conn.close()
    return exercises



def valid_login(the_id,the_password):
    the_id = "".join([c for c in the_id if c.isalnum()])
    the_password = "".join([c for c in the_password if c.isalnum()])
    conn = init_db('ids.db')
    cursor = conn.execute("SELECT id,name from ids where id='" + the_id + "' and password='" + the_password + "'")
    response = cursor.fetchone()
    if response is None:
        conn.close()
        return False
    else:
        session["id"] = response[0]
        session["name"] = response[1]
        conn.close()
        return True

@app.route('/test', methods=['GET', 'POST'])
def test():
    if "name" not in session:
        return redirect('/')
    conn = init_db('ids.db')
    cursor = conn.execute("SELECT * from ids")
    response = cursor.fetchall()
    return str(response)

@app.route('/', methods=['GET', 'POST'])
def root():
    session['tmp'] = 43

    if request.form.get('id') is not None:
        if valid_login(request.form.get('id'), request.form.get('password')):
            return "Hi " + session["name"] + " , you have logged in"
        else:
            return "INCORRECT LOGIN"


    if request.method == "GET":

        if 'category' in request.args and 'exercise' in request.args:
            session["category"] = request.args['category']
            session["exercise"] = request.args['exercise']
            return head() + quiz_form() + load_quiz(session["category"],session["exercise"])

        if 'response' in request.args and 'id' in session:
            score = 0
            response = request.args['response']
            answers = session['answers']
            for i in range(0, len(response)):
                if answers[i] ==  response[i]:
                    score += 1
            score = round(100*(score / len(response)))
            submit_score(score)
            score = "Thanks " + session['id'] + ", you scored " + str(score) + "%"
            return head() + quiz_form() + "<br><br>" + response + "<br>" + answers + "<br>" + score


    #return head() + id_form
    return render_template("index.html")

if __name__ == '__main__':
    app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
    app.run(host="0.0.0.0", port=8000)
    #app.run(debug=True)
