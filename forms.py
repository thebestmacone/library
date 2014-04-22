from wtforms import Form, TextField, PasswordField, validators

class RegistrationForm(Form):
	username = TextField('Username', [validators.Required(), validators.Length(4, 25)])
	email = TextField('Email Address', [validators.Required(), validators.Email()])
	password = PasswordField('Password', [validators.Required(), validators.Length(6, 25),
		validators.EqualTo('confirm', 'Passwords must much')
	])
	confirm = PasswordField('Repeat Password')

class AddBook(Form):
	title = TextField('Title', [validators.Required()])
	author = TextField('Author', [validators.Required()])
