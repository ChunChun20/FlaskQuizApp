from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField, SubmitField,SelectField, BooleanField, RadioField
from wtforms.validators import InputRequired,Length,ValidationError
from models import db,User


class RegisterForm(FlaskForm):
    username = StringField(validators=[InputRequired(),Length(
        min=4,max=20)],render_kw={"placeholder":"Username"})

    email = EmailField(validators=[InputRequired(), Length(
        min=4, max=30)], render_kw={"placeholder": "Email"})

    password = PasswordField(validators=[InputRequired(), Length(
        min=4, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField("Register")

    def validate_username(self,username):
        existing_user_username = User.query.filter_by(username=username.data).first()

        if existing_user_username:
            raise ValidationError(
                f"Username {username} already exists. Please choose another username.")

class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(),Length(
        min=4,max=20)],render_kw={"placeholder":"Username"})

    password = PasswordField(validators=[InputRequired(), Length(
        min=4, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField("Login")

class CategoryForm(FlaskForm):
    category = RadioField('Choose a Category:', choices=[
        ('Science', 'Science'),
        ('History', 'History'),
        ('Technology', 'Technology'),
        ('Literature', 'Literature')
    ])

    difficulty = RadioField('Choose Difficulty:', choices=[
        ('easy', 'Easy'),
        ('normal', 'Normal'),
        ('hard', 'Hard')
    ])

    submit = SubmitField('Start Quiz')

class ScoreFilterForm(FlaskForm):
    category = SelectField(
        'Category:',
        choices=[
            ('','All Categories'),
            ('Science','Science'),
            ('History','History'),
            ('Technology','Technology'),
            ('Literature','Literature')
        ],
        default=''
    )
    difficulty = SelectField(
        'Difficulty:',
        choices=[
            ('','All Difficulties'),
            ('Easy','Easy'),
            ('Normal','Normal'),
            ('Hard','Hard')
        ],
        default=''
    )
    submit = SubmitField("Search")