from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=True)

    # Relationships
    user_habits = db.relationship('UserHabit', back_populates='user')
    completions = db.relationship('DailyHabitCompletion', back_populates='user')

class Habit(db.Model):
    __tablename__ = 'habits'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)

    # Relationships
    user_habits = db.relationship('UserHabit', back_populates='habit')
    completions = db.relationship('DailyHabitCompletion', back_populates='habit')

class UserHabit(db.Model):
    __tablename__ = 'user_habits'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    habit_id = db.Column(db.Integer, db.ForeignKey('habits.id'), nullable=False)

    # Relationships
    user = db.relationship('User', back_populates='user_habits')
    habit = db.relationship('Habit', back_populates='user_habits')

    # Ensure unique combination of user_id and habit_id
    __table_args__ = (db.UniqueConstraint('user_id', 'habit_id'),)

class DailyHabitCompletion(db.Model):
    __tablename__ = 'daily_habit_completions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    habit_id = db.Column(db.Integer, db.ForeignKey('habits.id'), nullable=False)
    date = db.Column(db.String(10), nullable=False)  # YYYY-MM-DD format

    # Relationships
    user = db.relationship('User', back_populates='completions')
    habit = db.relationship('Habit', back_populates='completions')

    # Ensure unique combination of user_id, habit_id, and date
    __table_args__ = (db.UniqueConstraint('user_id', 'habit_id', 'date'),)
