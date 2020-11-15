from flask_wtf import FlaskForm
from wtforms import validators
from wtforms import StringField, PasswordField, SubmitField, SelectField, BooleanField,TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo

class RateForm(FlaskForm):
    rating = SelectField(
        label="Rate this film",
        choices=(
            (1, "★"),
            (2, "★★"),
            (3, "★★★"),
            (4, "★★★★"),
            (5, "★★★★★")
        )
    )
    submit = SubmitField('submit')

class PostForm(FlaskForm):

    text = TextAreaField('Write a film comment:', validators=[DataRequired(), Length(min=10, max=140)])
    submit = (SubmitField('Post Comment'))
