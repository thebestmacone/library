from flask import Flask, request, session, redirect, url_for, \
	 abort, render_template, flash
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import asc
from forms import *
from models import *

app = Flask(__name__)
app.config.from_object('config')

@app.route('/')
@app.route('/library')
def library():
	books = Book.query.order_by(asc(Book.title)).all()

	return render_template('library.html', books=books)

@app.route('/book/title/<title>')
def book(title):
	books = Book.query.filter(Book.title == title).all()

	return render_template('book.html', books=books)

@app.route('/author/name/<name>')
def author(name):
	authors = Author.query.filter(Author.first_name == name).all()

	return render_template('author.html', authors=authors)

@app.route('/search', methods = ['POST'])
def search():
	if not session.get('logged_in'):
		abort(401)

	name = request.form['something']

	if request.form['search_type'] == 'title':
		result = Book.query.filter(Book.title.like('%' + name + '%')).all()

		return render_template('book_search_results.html', books=result)
	else:
		result = Author.query.filter(Author.first_name.like('%' + name + '%')).all()

		return render_template('author_search_results.html', authors=result)

@app.route('/edit_book/title/<title>', methods = ['POST'])
def edit_book(title):
	book = Book.query.filter(Book.title == title).first()

	return render_template('edit_book.html', book=book)

@app.route('/edited_book/title/<title>', methods = ['POST'])
def edited_book(title):
	book = Book.query.filter(Book.title == title).first()

	return render_template('edit_book.html', book=book)

@app.route('/delete_book/title/<title>', methods = ['POST'])
def delete_book(title):
	if not session.get('logged_in'):
		abort(401)

	book = Book.query.filter(Book.title == title).first()

	db_session.delete(book)
	db_session.commit()

	authors = Author.query.all()
	
	for author in authors:
		if len(author.books) == 0:
			db_session.delete(author)
			db_session.commit()

	books = Book.query.order_by(asc(Book.title)).all()

	flash('book was deleted')

	return render_template('library.html', books=books)

@app.route('/edit_author/name/<name>', methods = ['POST'])
def edit_author(name):
	author = Author.query.filter(Author.first_name == name).first()

	return render_template('edit_author.html', author=author)

@app.route('/delete_author/name/<name>', methods = ['POST'])
def delete_author(name):
	if not session.get('logged_in'):
		abort(401)

	authors = Author.query.all()

	for author in authors:
		if author.first_name == name:
			for book in author.books:
				db_session.delete(book)
				db_session.commit()

	for author in authors:
		if len(author.books) == 0:
			db_session.delete(author)
			db_session.commit()

	books = Book.query.order_by(asc(Book.title)).all()

	flash('author was deleted')

	return render_template('library.html', books=books)

@app.route('/all_books')
def all_books():
	books = Book.query.order_by(asc(Book.title)).all()

	return render_template('all_books.html', books=books)

@app.route('/all_authors')
def all_authors():
	authors = Author.query.order_by(asc(Author.first_name)).all()

	return render_template('all_authors.html', authors=authors)

@app.route('/add', methods = ['POST'])
def add_book():
	if not session.get('logged_in'):
		abort(401)

	form = AddBook(request.form)
	books = Book.query.order_by(asc(Book.title)).all()

	if request.method == 'POST' and form.validate():
		book = Book(request.form['title'])
		
		for key in request.form.keys():
			for value in request.form.getlist(key):
				if key != 'title':
					existing_author = Author.query.filter_by(first_name=value).first()

					if not existing_author:
						author = Author(value)
						book.author.append(author)
					else:
						book.author.append(existing_author)

		db_session.add(book)
		db_session.commit()

		flash('new book was successfully added')

		return redirect(url_for('library'))
	flash('All fields required')

	return render_template('library.html', books=books)

@app.route('/register', methods = ['GET', 'POST'])
def register():
	form = RegistrationForm(request.form)

	if request.method == 'POST' and form.validate():
		existing_user = User.query.filter_by(name=request.form['username']).first()

		if existing_user:
			flash('Username is already in use')
		else:
			used_email = User.query.filter_by(email=request.form['email']).first()

			if used_email:
				flash('Email is already in use')
			else:
				session['logged_in'] = True
				user = User(request.form['username'], request.form['email'], request.form['password'])
				db_session.add(user)
				db_session.commit()

				flash('Thanks for registering')

				return redirect(url_for('library'))
	return render_template('registration.html', form=form)

@app.route('/login', methods = ['GET', 'POST'])
def login():
	error = None
	form = RegistrationForm(request.form)

	if request.method == 'POST':
		existing_user = User.query.filter_by(name=request.form['username']).first()

		if not existing_user:
			error = 'Invalid username'
		else:
			right_password = existing_user.check_password(request.form['password'])

			if not right_password:
				error = 'Invalid password'
			else:
				session['logged_in'] = True
				flash('You were logged in')

				return redirect(url_for('library'))
	return render_template('login.html', error=error)

@app.route('/logout')
def logout():
	session.pop('logged_in', None)
	flash('You were logged out')

	return redirect(url_for('library'))

if __name__ == '__main__':
	app.run()
