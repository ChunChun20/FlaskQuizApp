import random

from flask import Flask,render_template,url_for,redirect,flash,request,session,jsonify
from forms import RegisterForm, LoginForm, CategoryForm, ScoreFilterForm
from models import db, User, Questions, Score
from flask_bcrypt import Bcrypt
from flask_login import login_user,LoginManager,login_required,logout_user,current_user
from datetime import datetime


app = Flask(__name__)
bcrypt = Bcrypt(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = "hehesecrets"
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/menu',methods=["GET","POST"])
@login_required
def menu():
    form = CategoryForm()

    if form.validate_on_submit():
        category = form.category.data
        difficulty = form.difficulty.data
        return redirect(url_for('quiz', category=category, difficulty=difficulty))

    return render_template('menu.html',form=form)


@app.route('/quiz',methods=["GET","POST"])
def quiz():
    category = request.args.get("category")
    difficulty = request.args.get("difficulty").capitalize()
    message = f'Playing quiz with category: {category} and difficulty: {difficulty}.'
    questions = Questions.query.filter_by(category=category,difficulty=difficulty).all()
    #randomly select 10 or less questions if there aren't enough
    game_questions = random.sample(questions,min(len(questions),10))
    random.shuffle(game_questions)

    session['questions'] = [q.id for q in game_questions]
    session['current_index'] = 0
    session['score'] = 0
    session['correct_answers'] = 0
    session['category'] = category
    session['difficulty'] = difficulty
    session['bonus_points'] = 0

    return render_template('quiz.html',message=message)



@app.route('/scoreboard',methods=["GET","POST"])
def scoreboard():
    form = ScoreFilterForm()
    query = Score.query

    if form.validate_on_submit():
        if form.category.data:
            query = query.filter_by(category=form.category.data)
        if form.difficulty.data:
            query = query.filter_by(difficulty=form.difficulty.data)



    top_scores = (query.order_by(Score.score.desc())
                  .limit(10)
                  .all())

    return render_template('scoreboard.html',scores=top_scores,enumerate=enumerate,form=form)


@app.route("/get_question",methods=["GET"])
def get_question():
    questions = session.get('questions',[])
    current_index = session.get('current_index',0)

    if current_index < len(questions):
        question_id = questions[current_index]
        question = Questions.query.get(question_id)

        wrong_answers = question.get_wrong_answers()


        print("Wrong Answers:", wrong_answers)


        return jsonify({
            'id' : question.id,
            'question_text': question.question_text,
            'correct_answer': question.correct_answer,
            'wrong_answers': wrong_answers
        })
    else:
        score = session['score']
        category = session['category']
        difficulty = session['difficulty']
        date = datetime.now()


        new_score = Score(user_id=current_user.id,
                          username=current_user.username,
                          score=score,
                          category=category,
                          difficulty=difficulty,
                          date=date)
        db.session.add(new_score)
        db.session.commit()

        return jsonify({'message': 'Quiz completed!',
                        'score': session['score'],
                        'correct_answers': session['correct_answers']})


@app.route("/submit_answer",methods=["POST"])
def submit_answer():
    data = request.get_json()
    selected_answer = data.get("selected_answer")
    question_id = data.get('question_id')
    remaining_time = data.get("remaining_time",0)


    question = Questions.query.get(question_id)

    if not question:
        return jsonify({'error': 'Question not found'}), 404

    is_correct = selected_answer == question.correct_answer

    question_score = 0

    if is_correct:
        question_score = findScore()
        session['bonus_points'] = remaining_time
        session['score'] = session['score'] + question_score + session['bonus_points']
        session['correct_answers'] += 1

    session['current_index'] += 1

    return jsonify({'is_correct': is_correct,
                    'score': session['score'],
                    'question_score': question_score,
                    'bonus_points': session.get('bonus_points',0)})


def findScore():
    if session['difficulty'] == "Easy":
        return 100
    elif session['difficulty'] == "Normal":
        return 150
    elif session['difficulty'] == "Hard":
        return 200




@app.route('/login',methods=["GET","POST"])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password,form.password.data):
                login_user(user)
                # session['user_id'] = user.id
                flash('Login successful! You can now play a quizz game.', 'success')
                return redirect(url_for('menu'))
            else:
                flash('Wrong username or password. Please try again.', 'danger')
        else:
            flash('Wrong username or password. Please try again.', 'danger')
    elif form.is_submitted():
        flash('Wrong username or password. Please try again.', 'danger')

    return render_template('login.html',form=form)

@app.route('/register',methods=["GET","POST"])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(username=form.username.data,email=form.email.data,password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! You can now log in.','success')
        return redirect(url_for('login'))
    elif form.is_submitted():
        flash('Username is already taken. Please use another.', 'danger')

    return render_template('register.html',form=form)

@app.route('/logout',methods=["GET","POST"])
@login_required
def logout():
    logout_user()
    flash('You have logged out!', 'info')

    return redirect(url_for('login'))


if __name__ == "__main__":
    # with app.app_context():
    #     db.create_all()

    #     db.session.commit()



    app.run(debug=True)