from flask import Flask, render_template, request, jsonify
import os
from werkzeug.utils import secure_filename
import re
from PyPDF2 import PdfReader
from docx import Document

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'docx'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Criteria for evaluation
CRITERIA = {
    'contact_info': {'weight': 0.1, 'keywords': ['phone', 'email', 'address', 'linkedin']},
    'summary': {'weight': 0.1, 'keywords': ['summary', 'objective', 'profile']},
    'experience': {'weight': 0.3, 'keywords': ['experience', 'work history', 'employment']},
    'education': {'weight': 0.15, 'keywords': ['education', 'degree', 'university']},
    'skills': {'weight': 0.2, 'keywords': ['skills', 'technical skills', 'competencies']},
    'achievements': {'weight': 0.15, 'keywords': ['achievements', 'awards', 'certifications']}
}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_pdf(pdf_path):
    text = ""
    with open(pdf_path, 'rb') as file:
        reader = PdfReader(file)
        for page in reader.pages:
            text += page.extract_text()
    return text.lower()

def extract_text_from_docx(docx_path):
    doc = Document(docx_path)
    return "\n".join([para.text for para in doc.paragraphs]).lower()

def analyze_resume(text):
    results = {}
    total_score = 0
    
    for section, criteria in CRITERIA.items():
        found = False
        for keyword in criteria['keywords']:
            if re.search(r'\b' + re.escape(keyword) + r'\b', text):
                found = True
                break
        
        if found:
            score = criteria['weight'] * 100
            results[section] = {
                'score': score,
                'feedback': f"Good {section} section found"
            }
        else:
            score = 0
            results[section] = {
                'score': score,
                'feedback': f"Missing or weak {section} section"
            }
        
        total_score += score
    
    # Overall evaluation
    if total_score >= 80:
        overall = "Excellent"
    elif total_score >= 60:
        overall = "Good"
    elif total_score >= 40:
        overall = "Needs Improvement"
    else:
        overall = "Poor"
    
    return {
        'sections': results,
        'total_score': total_score,
        'overall': overall,
        'suggestions': generate_suggestions(results)
    }

def generate_suggestions(results):
    suggestions = []
    for section, data in results.items():
        if data['score'] < CRITERIA[section]['weight'] * 50:  # Less than half points
            suggestions.append(f"Consider adding a strong {section} section with relevant details.")
    
    if not suggestions:
        suggestions.append("Your resume looks good! Consider tailoring it for specific job applications.")
    
    return suggestions

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'resume' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['resume']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            if filename.endswith('.pdf'):
                text = extract_text_from_pdf(filepath)
            elif filename.endswith('.docx'):
                text = extract_text_from_docx(filepath)
            else:
                return jsonify({'error': 'Unsupported file format'}), 400
            
            analysis = analyze_resume(text)
            return jsonify(analysis)
        
        except Exception as e:
            return jsonify({'error': f'Error processing file: {str(e)}'}), 500
        
        finally:
            # Clean up - remove the uploaded file
            if os.path.exists(filepath):
                os.remove(filepath)
    else:
        return jsonify({'error': 'Allowed file types are pdf, docx'}), 400

if __name__ == '__main__':
    app.run(debug=True)