from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import os
from src.db import db, User, Habit, UserHabit, DailyHabitCompletion

app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///habits.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Create tables
with app.app_context():
    db.create_all()

@app.route("/")
def index():
    return jsonify({
        "message": "Habit Tracker API is running ✅",
        "endpoints": {
            "list_global_habits": "GET /api/habits",
            "create_global_habit": "POST /api/habits",
            "create_user": "POST /api/users",
            "get_user": "GET /api/users/<user_id>",
            "get_user_habits": "GET /api/users/<user_id>/habits",
            "get_daily_habits": "GET /api/users/<user_id>/habits/daily?date=YYYY-MM-DD",
            "mark_habit_complete": "POST /api/users/<user_id>/habits/<habit_id>/complete?date=YYYY-MM-DD",
            "unmark_habit_complete": "DELETE /api/users/<user_id>/habits/<habit_id>/complete?date=YYYY-MM-DD",
            "get_habit_streak": "GET /api/users/<user_id>/habits/<habit_id>/streak"
        }
    })
# -----------------------------------------------------------

# Helper functions
def validate_date(date_str):
    """Validate date string in YYYY-MM-DD format"""
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False

def get_date_range(start_date, end_date):
    """Get list of dates between start and end"""
    start = datetime.strptime(start_date, '%Y-%m-%d')
    end = datetime.strptime(end_date, '%Y-%m-%d')
    dates = []
    current = start
    while current <= end:
        dates.append(current.strftime('%Y-%m-%d'))
        current += timedelta(days=1)
    return dates

# Habit endpoints
@app.route('/api/habits', methods=['POST'])
def create_habit():
    """Create a global habit template"""
    data = request.get_json()

    if not data or 'title' not in data:
        return jsonify({'error': 'Title is required'}), 400

    habit = Habit(
        title=data['title'],
        description=data.get('description')
    )

    db.session.add(habit)
    db.session.commit()

    return jsonify({
        'id': habit.id,
        'title': habit.title,
        'description': habit.description
    }), 201

@app.route('/api/habits', methods=['GET'])
def get_habits():
    """Get all global habits"""
    habits = Habit.query.all()
    return jsonify([{
        'id': habit.id,
        'title': habit.title,
        'description': habit.description
    } for habit in habits])

# User endpoints
@app.route('/api/users', methods=['POST'])
def create_user():
    """Create a user"""
    data = request.get_json()

    user = User(name=data.get('name'))
    db.session.add(user)
    db.session.commit()

    return jsonify({
        'id': user.id,
        'name': user.name
    }), 201

@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Get a user by ID"""
    user = User.query.get_or_404(user_id)
    return jsonify({
        'id': user.id,
        'name': user.name
    })

# User-Habit relationship endpoints
@app.route('/api/users/<int:user_id>/habits/<int:habit_id>', methods=['POST'])
def add_user_habit(user_id, habit_id):
    """Add (subscribe) a habit to a user's personal habit list"""
    # Check if user exists
    user = User.query.get_or_404(user_id)

    # Check if habit exists
    habit = Habit.query.get_or_404(habit_id)

    # Check if relationship already exists
    existing = UserHabit.query.filter_by(user_id=user_id, habit_id=habit_id).first()
    if existing:
        return jsonify({'error': 'User is already tracking this habit'}), 400

    user_habit = UserHabit(user_id=user_id, habit_id=habit_id)
    db.session.add(user_habit)
    db.session.commit()

    return jsonify({
        'message': 'Habit added to user successfully',
        'user_id': user_id,
        'habit_id': habit_id
    }), 201

@app.route('/api/users/<int:user_id>/habits/<int:habit_id>', methods=['DELETE'])
def remove_user_habit(user_id, habit_id):
    """Remove a habit from a user's habit list"""
    user_habit = UserHabit.query.filter_by(user_id=user_id, habit_id=habit_id).first_or_404()

    db.session.delete(user_habit)
    db.session.commit()

    return jsonify({'message': 'Habit removed from user successfully'})

@app.route('/api/users/<int:user_id>/habits', methods=['GET'])
def get_user_habits(user_id):
    """Get all habits a user is tracking"""
    # Check if user exists
    User.query.get_or_404(user_id)

    user_habits = UserHabit.query.filter_by(user_id=user_id).all()
    habits = []
    for user_habit in user_habits:
        habits.append({
            'id': user_habit.habit.id,
            'title': user_habit.habit.title,
            'description': user_habit.habit.description
        })

    return jsonify(habits)

# Daily completion endpoints
@app.route('/api/users/<int:user_id>/habits/daily', methods=['GET'])
def get_daily_habits(user_id):
    """Get all habits a user is tracking with today's completion status"""
    date = request.args.get('date')
    if not date:
        date = datetime.now().strftime('%Y-%m-%d')
    elif not validate_date(date):
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400

    # Check if user exists
    User.query.get_or_404(user_id)

    user_habits = UserHabit.query.filter_by(user_id=user_id).all()
    habits_with_status = []

    for user_habit in user_habits:
        completion = DailyHabitCompletion.query.filter_by(
            user_id=user_id,
            habit_id=user_habit.habit_id,
            date=date
        ).first()

        habits_with_status.append({
            'id': user_habit.habit.id,
            'title': user_habit.habit.title,
            'description': user_habit.habit.description,
            'completed': completion is not None,
            'date': date
        })

    return jsonify(habits_with_status)

@app.route('/api/users/<int:user_id>/habits/<int:habit_id>/complete', methods=['POST'])
def mark_habit_complete(user_id, habit_id):
    """Mark a habit complete for that user on a specific day"""
    date = request.args.get('date')
    if not date:
        date = datetime.now().strftime('%Y-%m-%d')
    elif not validate_date(date):
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400

    # Check if user-habit relationship exists
    user_habit = UserHabit.query.filter_by(user_id=user_id, habit_id=habit_id).first()
    if not user_habit:
        return jsonify({'error': 'User is not tracking this habit'}), 400

    # Check if already completed
    existing = DailyHabitCompletion.query.filter_by(
        user_id=user_id,
        habit_id=habit_id,
        date=date
    ).first()

    if existing:
        return jsonify({'error': 'Habit already marked complete for this date'}), 400

    completion = DailyHabitCompletion(user_id=user_id, habit_id=habit_id, date=date)
    db.session.add(completion)
    db.session.commit()

    return jsonify({
        'message': 'Habit marked as complete',
        'user_id': user_id,
        'habit_id': habit_id,
        'date': date
    }), 201

@app.route('/api/users/<int:user_id>/habits/<int:habit_id>/complete', methods=['DELETE'])
def unmark_habit_complete(user_id, habit_id):
    """Unmark a habit complete for that user on that day"""
    date = request.args.get('date')
    if not date:
        return jsonify({'error': 'Date parameter is required'}), 400
    elif not validate_date(date):
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400

    completion = DailyHabitCompletion.query.filter_by(
        user_id=user_id,
        habit_id=habit_id,
        date=date
    ).first_or_404()

    db.session.delete(completion)
    db.session.commit()

    return jsonify({
        'message': 'Habit completion unmarked',
        'user_id': user_id,
        'habit_id': habit_id,
        'date': date
    })

# Streak endpoint
@app.route('/api/users/<int:user_id>/habits/<int:habit_id>/streak', methods=['GET'])
def get_habit_streak(user_id, habit_id):
    """Get a user's current + longest streak for a habit"""
    # Check if user-habit relationship exists
    user_habit = UserHabit.query.filter_by(user_id=user_id, habit_id=habit_id).first()
    if not user_habit:
        return jsonify({'error': 'User is not tracking this habit'}), 400

    # Get all completions for this habit, ordered by date descending
    completions = DailyHabitCompletion.query.filter_by(
        user_id=user_id,
        habit_id=habit_id
    ).order_by(DailyHabitCompletion.date.desc()).all()

    if not completions:
        return jsonify({
            'current_streak': 0,
            'longest_streak': 0
        })

    # Calculate current streak
    current_streak = 0
    today = datetime.now().strftime('%Y-%m-%d')

    # Check if completed today
    today_completion = next((c for c in completions if c.date == today), None)
    if today_completion:
        current_streak = 1
        check_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

        while True:
            completion = next((c for c in completions if c.date == check_date), None)
            if completion:
                current_streak += 1
                check_date = (datetime.strptime(check_date, '%Y-%m-%d') - timedelta(days=1)).strftime('%Y-%m-%d')
            else:
                break

    # Calculate longest streak
    longest_streak = 0
    temp_streak = 0
    prev_date = None

    for completion in sorted(completions, key=lambda x: x.date):
        if prev_date is None:
            temp_streak = 1
        else:
            # Check if dates are consecutive
            prev_dt = datetime.strptime(prev_date, '%Y-%m-%d')
            curr_dt = datetime.strptime(completion.date, '%Y-%m-%d')
            if (curr_dt - prev_dt).days == 1:
                temp_streak += 1
            else:
                longest_streak = max(longest_streak, temp_streak)
                temp_streak = 1

        prev_date = completion.date

    longest_streak = max(longest_streak, temp_streak)

    return jsonify({
        'current_streak': current_streak,
        'longest_streak': longest_streak
    })

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
