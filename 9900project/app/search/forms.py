from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_wtf.file import FileRequired, FileField

class SearchForm(FlaskForm):
    search = StringField('', validators=[DataRequired(), Length(min=2, max=30)])