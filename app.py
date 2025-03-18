from flask import Flask, render_template, request, jsonify, send_file
from quiz_generator import generate_quiz
import os
from datetime import datetime
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')
app.config['QUIZZES_DIR'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'quizzes')

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
def index():
    return render_template('index.html')

@app.route('/rules')
def rules():
    return render_template('rules.html')

@app.route('/saved-quizzes')
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000))) 