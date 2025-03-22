from flask import Flask, render_template, request, jsonify, send_file, session
from quiz_generator import generate_quiz
import os
from datetime import datetime, timedelta
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
import json
from flask_talisman import Talisman
from models import db, Section, Question, Answer, Quiz, QuizQuestion, Tag, User, UserProgress

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')
app.config['QUIZZES_DIR'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'quizzes')
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

# Configure the SQLAlchemy database
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///irpcs_quiz.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Create database tables
with app.app_context():
    db.create_all()

# Add security headers with Talisman
talisman = Talisman(
    app,
    content_security_policy={
        'default-src': ["'self'", 'cdn.jsdelivr.net', 'cdnjs.cloudflare.com'],
        'img-src': ["'self'", 'data:', 'cdn.jsdelivr.net', 'cdnjs.cloudflare.com'],
        'script-src': ["'self'", "'unsafe-inline'", 'cdn.jsdelivr.net', 'cdnjs.cloudflare.com'],
        'style-src': ["'self'", "'unsafe-inline'", 'cdn.jsdelivr.net', 'cdnjs.cloudflare.com'],
        'font-src': ["'self'", 'cdn.jsdelivr.net', 'cdnjs.cloudflare.com']
    },
    force_https=True,
    strict_transport_security=True,
    session_cookie_secure=True,
    session_cookie_http_only=True
)

# Ensure quizzes directory exists
os.makedirs(app.config['QUIZZES_DIR'], exist_ok=True)

def create_word_document(questions, title="IRPCS Quiz", show_answers=False):
    doc = Document()
    
    # Add title
    title_paragraph = doc.add_paragraph()
    title_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title_run = title_paragraph.add_run(title)
    title_run.font.size = Pt(16)
    title_run.font.bold = True
    doc.add_paragraph()  # Add spacing
    
    # Add questions
    for i, question in enumerate(questions, 1):
        # Question text
        question_paragraph = doc.add_paragraph()
        question_paragraph.add_run(f"{i}. ").bold = True
        question_paragraph.add_run(question['question'])
        
        # Add choices for multiple choice questions
        if question['type'] == 'Multiple Choice':
            for choice in question['choices']:
                doc.add_paragraph(choice, style='List Bullet')
        
        # Add answer space for fill in the gap and written answer
        elif question['type'] in ['Fill in the Gap', 'Written Answer']:
            doc.add_paragraph("Answer: _________________________________________________")
        
        # Add rule reference if available
        if question.get('rule_reference'):
            doc.add_paragraph(f"Rule Reference: {question['rule_reference']}", style='Intense Quote')
        
        # Add answer if showing answers
        if show_answers:
            answer_paragraph = doc.add_paragraph()
            answer_paragraph.add_run("Answer: ").bold = True
            if question['type'] == 'Multiple Choice':
                answer_paragraph.add_run(question['answer'])
            else:
                answer_paragraph.add_run(question['answer'])
            answer_paragraph.style = 'Intense Quote'
        
        doc.add_paragraph()  # Add spacing between questions
    
    return doc

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/generate_quiz')
def generate_quiz_page():
    return render_template('generate_quiz.html')

@app.route('/online_quiz')
def online_quiz():
    return render_template('online_quiz.html')

@app.route('/rules')
def rules():
    return render_template('rules.html')

@app.route('/saved_quizzes')
def saved_quizzes():
    return render_template('saved_quizzes.html')

@app.route('/api/saved-quizzes')
def get_saved_quizzes():
    quizzes = []
    for filename in os.listdir(app.config['QUIZZES_DIR']):
        if filename.endswith('.json'):
            with open(os.path.join(app.config['QUIZZES_DIR'], filename), 'r') as f:
                quiz_data = json.load(f)
                quizzes.append({
                    'id': filename.replace('.json', ''),
                    'name': quiz_data.get('name', 'Unnamed Quiz'),
                    'description': quiz_data.get('description', ''),
                    'date': datetime.fromtimestamp(os.path.getctime(os.path.join(app.config['QUIZZES_DIR'], filename))).strftime('%Y-%m-%d %H:%M:%S')
                })
    return jsonify(quizzes)

@app.route('/generate', methods=['POST'])
def generate():
    try:
        data = request.get_json()
        num_questions = int(data.get('num_questions', 10))
        difficulty = data.get('difficulty', 'all')
        question_types = data.get('question_types', ['Multiple Choice', 'Fill in the Gap', 'Written Answer'])
        
        quiz = generate_quiz(num_questions, difficulty, question_types)
        return jsonify({'success': True, 'quiz': quiz})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/save', methods=['POST'])
def save():
    try:
        data = request.get_json()
        quiz = data.get('quiz')
        name = data.get('name', 'Unnamed Quiz')
        description = data.get('description', '')
        
        if not quiz:
            return jsonify({'success': False, 'message': 'No quiz data provided'})
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}.json"
        
        # Save quiz data
        quiz_data = {
            'name': name,
            'description': description,
            'questions': quiz
        }
        
        with open(os.path.join(app.config['QUIZZES_DIR'], filename), 'w') as f:
            json.dump(quiz_data, f, indent=2)
        
        # Generate Word documents
        student_doc = create_word_document(quiz, name)
        teacher_doc = create_word_document(quiz, f"{name} - Teacher Version", show_answers=True)
        
        student_doc.save(os.path.join(app.config['QUIZZES_DIR'], f"{timestamp}_student.docx"))
        teacher_doc.save(os.path.join(app.config['QUIZZES_DIR'], f"{timestamp}_teacher.docx"))
        
        return jsonify({'success': True, 'message': 'Quiz saved successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/download/<version>/<quiz_id>')
def download(version, quiz_id):
    try:
        if version not in ['student', 'teacher']:
            return jsonify({'success': False, 'message': 'Invalid version'})
        
        file_path = os.path.join(app.config['QUIZZES_DIR'], f"{quiz_id}_{version}.docx")
        
        if not os.path.exists(file_path):
            return jsonify({'success': False, 'message': 'Quiz file not found'})
        
        return send_file(file_path, as_attachment=True)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/delete-quiz/<quiz_id>', methods=['DELETE'])
def delete_quiz(quiz_id):
    try:
        # Delete JSON file
        json_path = os.path.join(app.config['QUIZZES_DIR'], f"{quiz_id}.json")
        if os.path.exists(json_path):
            os.remove(json_path)
        
        # Delete Word documents
        for version in ['student', 'teacher']:
            doc_path = os.path.join(app.config['QUIZZES_DIR'], f"{quiz_id}_{version}.docx")
            if os.path.exists(doc_path):
                os.remove(doc_path)
        
        return jsonify({'success': True, 'message': 'Quiz deleted successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/policy')
def policy():
    return render_template('policy.html')

@app.route('/api/rules')
def get_rules():
    rules_data = [
        {
            "number": 1,
            "title": "Application",
            "content": "These Rules shall apply to all vessels upon the high seas and in all waters connected therewith navigable by seagoing vessels."
        },
        {
            "number": 2,
            "title": "Responsibility",
            "content": "Nothing in these Rules shall exonerate any vessel, or the owner, master, or crew thereof, from the consequences of any neglect to comply with these Rules or of the neglect of any precaution which may be required by the ordinary practice of seamen, or by the special circumstances of the case."
        },
        {
            "number": 3,
            "title": "General Definitions",
            "content": "For the purpose of these Rules, except where the context otherwise requires: (a) The word 'vessel' includes every description of water craft, including non-displacement craft, WIG craft and seaplanes, used or capable of being used as a means of transportation on water."
        },
        {
            "number": 4,
            "title": "Application",
            "content": "Rules in Section I apply to any condition of visibility."
        },
        {
            "number": 5,
            "title": "Look-out",
            "content": "Every vessel shall at all times maintain a proper look-out by sight and hearing as well as by all available means appropriate in the prevailing circumstances and conditions so as to make a full appraisal of the situation and of the risk of collision."
        },
        {
            "number": 6,
            "title": "Safe Speed",
            "content": "Every vessel shall at all times proceed at a safe speed so that she can take proper and effective action to avoid collision and be stopped within a distance appropriate to the prevailing circumstances and conditions."
        },
        {
            "number": 7,
            "title": "Risk of Collision",
            "content": "Every vessel shall use all available means appropriate to the prevailing circumstances and conditions to determine if risk of collision exists. If there is any doubt such risk shall be deemed to exist."
        },
        {
            "number": 8,
            "title": "Action to Avoid Collision",
            "content": "Any action taken to avoid collision shall be taken in accordance with the Rules of this Part and shall, if the circumstances of the case admit, be positive, made in ample time and with due regard to the observance of good seamanship."
        },
        {
            "number": 9,
            "title": "Narrow Channels",
            "content": "A vessel proceeding along the course of a narrow channel or fairway shall keep as near to the outer limit of the channel or fairway which lies on her starboard side as is safe and practicable."
        },
        {
            "number": 10,
            "title": "Traffic Separation Schemes",
            "content": "This Rule applies to traffic separation schemes adopted by the Organization and does not relieve any vessel of her obligation under any other Rule."
        },
        {
            "number": 11,
            "title": "Application",
            "content": "Rules in Section II apply to vessels in sight of one another."
        },
        {
            "number": 12,
            "title": "Sailing Vessels",
            "content": "When two sailing vessels are approaching one another, so as to involve risk of collision, one of them shall keep out of the way of the other as follows: (a) when each has the wind on a different side, the vessel which has the wind on the port side shall keep out of the way of the other; (b) when both have the wind on the same side, the vessel which is to windward shall keep out of the way of the vessel which is to leeward."
        },
        {
            "number": 13,
            "title": "Overtaking",
            "content": "Any vessel overtaking any other shall keep out of the way of the vessel being overtaken."
        },
        {
            "number": 14,
            "title": "Head-on Situation",
            "content": "When two power-driven vessels are meeting on reciprocal or nearly reciprocal courses so as to involve risk of collision each shall alter her course to starboard so that each shall pass on the port side of the other."
        },
        {
            "number": 15,
            "title": "Crossing Situation",
            "content": "When two power-driven vessels are crossing so as to involve risk of collision, the vessel which has the other on her own starboard side shall keep out of the way and shall, if the circumstances of the case admit, avoid crossing ahead of the other vessel."
        },
        {
            "number": 16,
            "title": "Action by Give-way Vessel",
            "content": "Every vessel which is directed by these Rules to keep out of the way of another vessel shall, so far as possible, take early and substantial action to keep well clear."
        },
        {
            "number": 17,
            "title": "Action by Stand-on Vessel",
            "content": "Where one of two vessels is to keep out of the way the other shall keep her course and speed. The latter vessel may however take action to avoid collision by her manoeuvre alone, as soon as it becomes apparent to her that the vessel required to keep out of the way is not taking appropriate action in compliance with these Rules."
        },
        {
            "number": 18,
            "title": "Responsibilities Between Vessels",
            "content": "Except where Rules 9, 10 and 13 otherwise require: (a) A power-driven vessel underway shall keep out of the way of: (i) a vessel not under command; (ii) a vessel restricted in her ability to manoeuvre; (iii) a vessel engaged in fishing; (iv) a sailing vessel."
        },
        {
            "number": 19,
            "title": "Conduct in Restricted Visibility",
            "content": "This Rule applies to vessels not in sight of one another when navigating in or near an area of restricted visibility. Every vessel shall proceed at a safe speed adapted to the prevailing circumstances and conditions of restricted visibility. A power-driven vessel shall have her engines ready for immediate manoeuvre."
        },
        {
            "number": 20,
            "title": "Application",
            "content": "Rules in Part C shall be complied with in all weathers. The Rules concerning lights shall be complied with from sunset to sunrise, and during such times no other lights shall be exhibited."
        },
        {
            "number": 21,
            "title": "Definitions",
            "content": "(a) 'Masthead light' means a white light placed over the fore and aft centreline of the vessel showing an unbroken light over an arc of the horizon of 225 degrees. (b) 'Sidelights' means a green light on the starboard side and a red light on the port side."
        },
        {
            "number": 22,
            "title": "Visibility of Lights",
            "content": "The lights prescribed in these Rules shall have an intensity as specified in Section 8 of Annex I to these Regulations so as to be visible at minimum ranges."
        },
        {
            "number": 23,
            "title": "Power-driven Vessels Underway",
            "content": "A power-driven vessel underway shall exhibit: (a) a masthead light forward; (b) a second masthead light abaft of and higher than the forward one; except that a vessel of less than 50 metres in length shall not be obliged to exhibit such light but may do so; (c) sidelights; (d) a sternlight."
        },
        {
            "number": 24,
            "title": "Towing and Pushing",
            "content": "A power-driven vessel when towing shall exhibit: (a) instead of the light prescribed in Rule 23(a)(i) or (a)(ii), two masthead lights in a vertical line; (b) sidelights; (c) a sternlight; (d) a towing light in a vertical line above the sternlight; (e) when the length of the tow exceeds 200 metres, a diamond shape where it can best be seen."
        },
        {
            "number": 25,
            "title": "Sailing Vessels Underway and Vessels Under Oars",
            "content": "A sailing vessel underway shall exhibit: (a) sidelights; (b) a sternlight. In a sailing vessel of less than 20 metres in length the lights prescribed in paragraph (a) of this Rule may be combined in one lantern carried at or near the top of the mast where it can best be seen."
        },
        {
            "number": 26,
            "title": "Fishing Vessels",
            "content": "A vessel engaged in fishing, whether underway or at anchor, shall exhibit only the lights and shapes prescribed in this Rule."
        },
        {
            "number": 27,
            "title": "Vessels Not Under Command or Restricted in Ability to Manoeuvre",
            "content": "A vessel not under command shall exhibit: (a) two all-round red lights in a vertical line where they can best be seen; (b) two balls or similar shapes in a vertical line where they can best be seen; (c) when making way through the water, in addition to the lights prescribed in this paragraph, sidelights and a sternlight."
        },
        {
            "number": 28,
            "title": "Vessels Constrained by Their Draught",
            "content": "A vessel constrained by her draught may, in addition to the lights prescribed for power-driven vessels in Rule 23, exhibit where they can best be seen three all-round red lights in a vertical line, or a cylinder."
        },
        {
            "number": 29,
            "title": "Pilot Vessels",
            "content": "A vessel engaged on pilotage duty shall exhibit: (a) at or near the masthead, two all-round lights in a vertical line, the upper being white and the lower red; (b) when underway, in addition, sidelights and a sternlight; (c) when at anchor, in addition to the lights prescribed in paragraph (a), the light, lights, or shape prescribed for a vessel at anchor."
        },
        {
            "number": 30,
            "title": "Anchored Vessels and Vessels Aground",
            "content": "A vessel at anchor shall exhibit where it can best be seen: (a) in the fore part, an all-round white light or one ball; (b) at or near the stern and at a lower level than the light prescribed in paragraph (a), an all-round white light."
        },
        {
            "number": 31,
            "title": "Seaplanes",
            "content": "Where it is impracticable for a seaplane or a WIG craft to exhibit lights and shapes of the characteristics or in the positions prescribed in the Rules of this Part she shall exhibit lights and shapes as closely similar in characteristics and position as is possible."
        },
        {
            "number": 32,
            "title": "Definitions",
            "content": "(a) The word 'whistle' means any sound signalling appliance capable of producing the prescribed blasts. (b) The term 'short blast' means a blast of about one second's duration. (c) The term 'prolonged blast' means a blast of from four to six seconds' duration."
        }
    ]
    
    rule_number = request.args.get('number')
    if rule_number:
        try:
            rule_number = int(rule_number)
            filtered_rules = [rule for rule in rules_data if rule["number"] == rule_number]
            if filtered_rules:
                return jsonify(filtered_rules[0])
            else:
                return jsonify({"error": "Rule not found"}), 404
        except ValueError:
            return jsonify({"error": "Invalid rule number"}), 400
    
    return jsonify(rules_data)

@app.route('/api/sections')
def get_sections():
    """Get all rule sections"""
    sections = Section.query.all()
    return jsonify([{
        'id': section.id,
        'name': section.name,
        'description': section.description,
        'rule_range': section.rule_range
    } for section in sections])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000))) 