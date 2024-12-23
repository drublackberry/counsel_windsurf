from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length

class DirectionForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    submit = SubmitField('Submit')

class EditDirectionForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    submit = SubmitField('Save Changes')

class ChatMessageForm(FlaskForm):
    message = TextAreaField('How do you want to grow?', validators=[DataRequired()])
    submit = SubmitField('Send')

class PasswordChangeForm(FlaskForm):
    current_password = StringField('Current Password', validators=[DataRequired()])
    new_password = StringField('New Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = StringField('Confirm New Password', validators=[DataRequired()])
    submit = SubmitField('Change Password')
