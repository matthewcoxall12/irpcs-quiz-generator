from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Initialize SQLAlchemy
db = SQLAlchemy()

# Association table for Question-Tag many-to-many relationship
question_tags = db.Table('question_tags',
    db.Column('question_id', db.Integer, db.ForeignKey('question.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True)
)

class Section(db.Model):
    """IRPCS Rule Sections (Parts A through E)"""
    __tablename__ = 'sections'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    rule_range = db.Column(db.String(50))  # e.g., "Rules 1-3"
    
    # Relationships
    questions = db.relationship('Question', backref='section', lazy=True)
    
    def __repr__(self):
        return f"<Section {self.name}>"

class Tag(db.Model):
    """Tags for categorizing questions (e.g., "lights", "sailing vessels")"""
    __tablename__ = 'tags'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    
    def __repr__(self):
        return f"<Tag {self.name}>"

class Question(db.Model):
    """Quiz questions with metadata"""
    __tablename__ = 'questions'
    
    id = db.Column(db.Integer, primary_key=True)
    rule_number = db.Column(db.String(10), nullable=False)  # e.g., "Rule 5"
    section_id = db.Column(db.Integer, db.ForeignKey('sections.id'), nullable=False)
    
    # Different question format texts
    question_text_multiple_choice = db.Column(db.Text, nullable=False)
    question_text_short_answer = db.Column(db.Text)
    question_text_fill_blank = db.Column(db.Text)
    
    # Question metadata
    difficulty_level = db.Column(db.String(20), default='Medium')  # Easy, Medium, Hard
    marks = db.Column(db.Integer, default=1)
    question_type = db.Column(db.String(30), nullable=False)  # Multiple Choice, Short Answer, Fill in the Blank
    image_url = db.Column(db.String(255))  # Optional image
    
    # Classification metadata
    is_definition = db.Column(db.Boolean, default=False)
    is_application = db.Column(db.Boolean, default=False)
    is_scenario = db.Column(db.Boolean, default=False)
    
    # Creation and update timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    answers = db.relationship('Answer', backref='question', lazy=True, cascade="all, delete-orphan")
    tags = db.relationship('Tag', secondary=question_tags, lazy='subquery',
                          backref=db.backref('questions', lazy=True))
    
    def __repr__(self):
        return f"<Question {self.id}: {self.question_text_multiple_choice[:30]}...>"

class Answer(db.Model):
    """Multiple choice answers or correct answers for other question types"""
    __tablename__ = 'answers'
    
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    answer_text = db.Column(db.Text, nullable=False)
    is_correct = db.Column(db.Boolean, default=False)
    explanation = db.Column(db.Text)  # Explanation for why this answer is correct/incorrect
    
    def __repr__(self):
        return f"<Answer {self.id} for Question {self.question_id}>"

class Quiz(db.Model):
    """Saved quizzes"""
    __tablename__ = 'quizzes'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Quiz configuration
    length = db.Column(db.Integer, default=10)
    difficulty = db.Column(db.String(20), default='mixed')
    section_focus = db.Column(db.String(50), default='all')  # 'all' or comma-separated section IDs
    
    # Relationships
    questions = db.relationship('Question', secondary='quiz_question', lazy='subquery',
                              backref=db.backref('quizzes', lazy=True))
    quiz_questions = db.relationship('QuizQuestion', backref='quiz', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Quiz {self.id}: {self.name}>"

class QuizQuestion(db.Model):
    """Junction table for quizzes and questions, with additional data for quiz reports"""
    __tablename__ = 'quiz_questions'
    
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), primary_key=True)
    position = db.Column(db.Integer, nullable=False)  # Order in the quiz
    
    # For storing user's answers and quiz reports
    user_answer = db.Column(db.Text)
    is_correct = db.Column(db.Boolean)
    time_spent = db.Column(db.Integer)  # Time spent on question in seconds
    
    # Relationship to the Question model
    question = db.relationship('Question', lazy=True)
    
    def __repr__(self):
        return f"<QuizQuestion {self.quiz_id}-{self.question_id} at position {self.position}>"

class User(db.Model):
    """Simple user model (can be enhanced with Flask-Login)"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    quizzes = db.relationship('Quiz', backref='user', lazy=True)
    progress = db.relationship('UserProgress', backref='user', lazy=True)
    
    def __repr__(self):
        return f"<User {self.username}>"

class UserProgress(db.Model):
    """Tracks user progress on rules and mastery levels"""
    __tablename__ = 'user_progress'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    rule_number = db.Column(db.String(10), nullable=False)  # e.g., "Rule 5"
    
    # Learning metrics
    questions_attempted = db.Column(db.Integer, default=0)
    questions_correct = db.Column(db.Integer, default=0)
    mastery_level = db.Column(db.Float, default=0.0)  # 0.0 to 1.0
    last_practiced = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<UserProgress user_id={self.user_id} rule={self.rule_number} mastery={self.mastery_level}>" 