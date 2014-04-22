from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import deferred
from database import *

class User(Base):
	__tablename__ = 'users'
	id = Column(Integer, primary_key = True)
	name = Column(String, nullable = False)
	email = Column(String, nullable = False)
	pw_hash = deferred(Column(String, nullable = False))

	def __init__(self, name = None, email = None, password = None):
		self.name = name
		self.email = email

		if password:
			self.set_password(password)

	def set_password(self, password):
		self.pw_hash = generate_password_hash(password)

	def check_password(self, password):
		return check_password_hash(self.pw_hash, password)

	def __repr__(self):
		return '<User %r>' % (self.name)

book_author = Table('book_author', Base.metadata,
	Column('book_id', Integer, ForeignKey('books.id', ondelete='CASCADE')),
	Column('author_id', Integer, ForeignKey('authors.id', ondelete='CASCADE'))
)

class Book(Base):
	__tablename__ = 'books'
	id = Column(Integer, primary_key = True)
	title = Column(String(120), nullable = False)
	author = relationship('Author',
					passive_deletes=True,
					secondary=book_author,
					backref= 'books')
	
	def __init__(self, title = None):
		self.title = title

	def __repr__(self):
		return '<Book %r>' % (self.title)

class Author(Base):
	__tablename__ = 'authors'
	id = Column(Integer, primary_key = True)
	first_name = Column(String(120), nullable = False)
	# book = relationship('Book',
	# 				passive_deletes=True,
	# 				secondary=book_author,
	# 				backref='authors')

	def __init__(self, first_name = None):
		self.first_name = first_name
		
	def __repr__(self):
		return '<Author %r>' % (self.first_name)

Base.metadata.create_all(engine)
