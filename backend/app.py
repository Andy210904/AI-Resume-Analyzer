from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import PyPDF2
import docx
import re
import nltk
import spacy
from nltk.tokenize import word_tokenize
import json
from textblob import TextBlob
from industry_analyzer import IndustryAnalyzer

nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

nlp = spacy.load('en_core_web_sm')

app = Flask(__name__, static_folder='../frontend/build', static_url_path='')
CORS(app, resources={r"/api/*": {"origins": "*"}})

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

ALLOWED_EXTENSIONS = {'pdf', 'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_pdf(file_path):
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
    return text

def extract_text_from_docx(file_path):
    doc = docx.Document(file_path)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return '\n'.join(full_text)

def extract_sections(text):
    # Simple section extraction based on common headings
    sections = {}
    
    # Education section
    education_pattern = r'(?i)(EDUCATION|ACADEMIC BACKGROUND).*?(?=(EXPERIENCE|SKILLS|PROJECTS|$))'
    education_match = re.search(education_pattern, text, re.DOTALL)
    sections['education'] = education_match.group(0) if education_match else ""
    
    # Experience section
    experience_pattern = r'(?i)(EXPERIENCE|WORK EXPERIENCE|EMPLOYMENT).*?(?=(EDUCATION|SKILLS|PROJECTS|$))'
    experience_match = re.search(experience_pattern, text, re.DOTALL)
    sections['experience'] = experience_match.group(0) if experience_match else ""
    
    # Skills section
    skills_pattern = r'(?i)(SKILLS|TECHNICAL SKILLS|EXPERTISE).*?(?=(EDUCATION|EXPERIENCE|PROJECTS|$))'
    skills_match = re.search(skills_pattern, text, re.DOTALL)
    sections['skills'] = skills_match.group(0) if skills_match else ""
    
    # Projects section
    projects_pattern = r'(?i)(PROJECTS|PERSONAL PROJECTS).*?(?=(EDUCATION|EXPERIENCE|SKILLS|$))'
    projects_match = re.search(projects_pattern, text, re.DOTALL)
    sections['projects'] = projects_match.group(0) if projects_match else ""
    
    return sections

def analyze_resume(text,filename=None):
    # Extract basic information
    sections = extract_sections(text)
    
    # Analyze the content
    results = {
        "overall_score": 0,
        "sections": {},
        "suggestions": [],
        "strengths": [],
        "word_count": len(word_tokenize(text))
    }
    
    # Check if essential sections exist and analyze them
    section_weights = {
        "education": 20,
        "experience": 35,
        "skills": 25,
        "projects": 20
    }
    
    total_score = 0
    
    # Analyze education section
    if sections['education']:
        edu_score, edu_feedback = analyze_education(sections['education'])
        results["sections"]["education"] = {
            "exists": True,
            "score": edu_score,
            "feedback": edu_feedback
        }
        total_score += edu_score * section_weights["education"] / 100
    else:
        results["sections"]["education"] = {
            "exists": False,
            "score": 0,
            "feedback": ["Education section is missing"]
        }
        results["suggestions"].append("Add an Education section with your degrees, institutions, and graduation dates")
    
    # Analyze experience section
    if sections['experience']:
        exp_score, exp_feedback = analyze_experience(sections['experience'])
        results["sections"]["experience"] = {
            "exists": True,
            "score": exp_score,
            "feedback": exp_feedback
        }
        total_score += exp_score * section_weights["experience"] / 100
    else:
        results["sections"]["experience"] = {
            "exists": False,
            "score": 0,
            "feedback": ["Experience section is missing"]
        }
        results["suggestions"].append("Add a Work Experience section with your job titles, employers, and achievements")
    
    # Analyze skills section
    if sections['skills']:
        skills_score, skills_feedback = analyze_skills(sections['skills'])
        results["sections"]["skills"] = {
            "exists": True,
            "score": skills_score,
            "feedback": skills_feedback
        }
        total_score += skills_score * section_weights["skills"] / 100
    else:
        results["sections"]["skills"] = {
            "exists": False,
            "score": 0,
            "feedback": ["Skills section is missing"]
        }
        results["suggestions"].append("Add a Skills section highlighting your technical and soft skills")
    
    # Analyze projects section
    if sections['projects']:
        proj_score, proj_feedback = analyze_projects(sections['projects'])
        results["sections"]["projects"] = {
            "exists": True,
            "score": proj_score,
            "feedback": proj_feedback
        }
        total_score += proj_score * section_weights["projects"] / 100
    else:
        results["sections"]["projects"] = {
            "exists": False,
            "score": 0,
            "feedback": ["Projects section is missing or not clearly defined"]
        }
        results["suggestions"].append("Consider adding a Projects section to showcase your practical skills")
    
    # Calculate overall score (out of 100)
    results["overall_score"] = round(total_score)
    
    # Check for action verbs
    action_verbs = check_action_verbs(text)
    if action_verbs["score"] < 70:
        results["suggestions"].append("Use more strong action verbs to describe your achievements")
    else:
        results["strengths"].append("Good use of action verbs")
    
    # Check for keywords
    keywords = extract_keywords(text)
    if len(keywords) < 10:
        results["suggestions"].append("Include more industry-specific keywords to pass ATS screening")
    else:
        results["strengths"].append("Good use of industry keywords")
    
    # Check resume length
    if results["word_count"] < 300:
        results["suggestions"].append("Your resume seems too short. Consider adding more details about your experience and skills")
    elif results["word_count"] > 700:
        results["suggestions"].append("Your resume may be too lengthy. Try to make it more concise")
    else:
        results["strengths"].append("Resume has an appropriate length")
        
    return results

def analyze_education(text):
    score = 100  # Base score
    feedback = []
    
    # Check for degree mentions
    degree_keywords = [
    "bachelor", "master", "phd", "doctorate", "diploma", "certificate", "degree",
    "btech", "b.tech", "b.e", "be", "beng", "b.eng",
    "mtech", "m.tech", "m.e", "me", "meng", "m.eng",
    "bca", "mca",
    "bsc", "b.sc", "msc", "m.sc",
    "bcom", "b.com", "mcom", "m.com",
    "bba", "mba", "pgdm", "pgdbm",
    "ba", "b.a", "ma", "m.a",
    "llb", "ll.m", "llm",
    "mbbs", "bds", "b.pharm", "m.pharm", "bpt", "bams", "bhms",
    "b.ed", "bed", "m.ed", "med",
    "associate", "undergraduate", "postgraduate",
    "high school", "hsc", "ssc", "10th", "12th"
    ]
    has_degree = any(keyword in text.lower() for keyword in degree_keywords)
    
    if not has_degree:
        score -= 20
        feedback.append("No clear mention of degree type")
    
    # Check for dates
    date_pattern = r'(19|20)\d{2}'
    dates = re.findall(date_pattern, text)
    
    if not dates:
        score -= 15
        feedback.append("No graduation dates mentioned")
    
    # Check for institutions
    institution_keywords = ["university", "college", "institute", "school"]
    has_institution = any(keyword in text.lower() for keyword in institution_keywords)
    
    if not has_institution:
        score -= 15
        feedback.append("No clear mention of educational institutions")
    
    # Check for GPA or honors
    gpa_pattern = r'(gpa|grade point average|cum laude|honors|distinction)'
    has_gpa = re.search(gpa_pattern, text.lower())
    
    if not has_gpa:
        feedback.append("Consider adding GPA or academic honors if they're strong")
    
    # Return the results (cap score between 0-100)
    score = max(0, min(100, score))
    
    if score >= 80:
        feedback.append("Education section is well-structured")
    
    return score, feedback

def analyze_experience(text):
    score = 100 # Base score
    feedback = []
    
    # Check for company names
    company_pattern = r'(inc|llc|ltd|corporation|corp|company)'
    has_companies = re.search(company_pattern, text.lower())
    
    if not has_companies:
        score -= 10
        feedback.append("Company names may not be clearly mentioned")
    
    # Check for job titles
    job_keywords = ["manager", "developer", "engineer", "analyst", "assistant", "director", "coordinator", "specialist"]
    has_job_titles = any(keyword in text.lower() for keyword in job_keywords)
    
    if not has_job_titles:
        score -= 15
        feedback.append("Job titles are not clearly stated")
    
    # Check for dates
    date_pattern = r'(19|20)\d{2}|present|current|now'
    dates = re.findall(date_pattern, text.lower())
    
    if len(dates) < 2:
        score -= 15
        feedback.append("Employment dates may be missing or incomplete")
    
    # Check for bullet points
    bullet_pattern = r'•|\*|\-'
    bullets = re.findall(bullet_pattern, text)
    
    if len(bullets) < 3:
        score -= 10
        feedback.append("Consider using bullet points to highlight achievements")
    
    # Check for metrics and achievements
    metrics_pattern = r'(\d+%|\d+ percent|increased|decreased|improved|reduced|led|managed|created)'
    metrics = re.findall(metrics_pattern, text.lower())
    
    if len(metrics) < 3:
        score -= 15
        feedback.append("Add more quantifiable achievements with metrics")
    else:
        score += 10
        feedback.append("Good use of quantifiable metrics")
    
    # Return the results (cap score between 0-100)
    score = max(0, min(100, score))
    
    if score >= 80:
        feedback.append("Experience section effectively highlights your work history")
    
    return score, feedback

def analyze_skills(text):
    score = 100 # Base score
    feedback = []
    
    # Count number of skills
    text = text.lower()
    
    # Technical skills
    tech_skills = ["python", "java", "javascript", "html", "css", "react", "angular", 
                   "node", "sql", "database", "aws", "azure", "cloud", "docker", 
                   "kubernetes", "git", "agile", "scrum", "machine learning", "ai","c++","c"]
    
    tech_count = sum(1 for skill in tech_skills if skill in text)
    
    # Soft skills
    soft_skills = ["communication", "leadership", "teamwork", "problem solving", 
                   "critical thinking", "time management", "project management", 
                   "collaboration", "adaptability", "creativity"]
    
    soft_count = sum(1 for skill in soft_skills if skill in text)
    
    if tech_count < 5:
        score -= 15
        feedback.append("Add more technical skills relevant to your field")
    
    if soft_count < 3:
        score -= 10
        feedback.append("Include some soft skills to show your workplace effectiveness")
    
    # Check organization of skills section
    organization_patterns = [r',', r'•', r'\|', r'\\']
    has_organization = any(re.search(pattern, text) for pattern in organization_patterns)
    
    if not has_organization:
        score -= 10
        feedback.append("Organize your skills better (e.g., using categories or separators)")
    
    # Return the results (cap score between 0-100)
    score = max(0, min(100, score))
    
    if tech_count >= 8 and soft_count >= 5:
        score += 10
        feedback.append("Excellent variety of skills listed")
    
    return score, feedback

def analyze_projects(text):
    score = 100  # Base score
    feedback = []
    
    # Check for project titles
    project_count = len(re.findall(r'(?:^|\n)([A-Z][^\n]+)(?:\n|$)', text))
    
    if project_count < 2:
        score -= 15
        feedback.append("Include more projects to showcase your abilities")
    
    # Check for technologies used
    tech_pattern = r'(tech stack|tools used|using|with|built on|developed in|utilizing) ([^.]*)'
    has_tech = re.search(tech_pattern, text.lower())
    
    if not has_tech:
        score -= 15
        feedback.append("Mention technologies used in each project")
    
    # Check for project descriptions
    if len(text.split('\n')) < 5:
        score -= 10
        feedback.append("Add more detailed descriptions of your projects")
    
    # Check for results or impact
    impact_pattern = r'(resulted in|improved|increased|decreased|reduced|enhanced)'
    has_impact = re.search(impact_pattern, text.lower())
    
    if not has_impact:
        score -= 10
        feedback.append("Describe the impact or results of your projects")
    
    # Return the results (cap score between 0-100)
    score = max(0, min(100, score))
    
    if score >= 80:
        feedback.append("Project section effectively demonstrates your practical skills")
    
    return score, feedback

def check_action_verbs(text):
    action_verbs = [
        "achieved", "improved", "trained", "maintained", "managed", "created",
        "resolved", "volunteered", "influenced", "increased", "decreased",
        "researched", "authored", "developed", "launched", "designed",
        "implemented", "established", "coordinated", "generated", "delivered",
        "produced", "performed", "directed", "organized", "supervised"
    ]
    
    # Count occurrences of action verbs
    text_lower = text.lower()
    verb_count = sum(1 for verb in action_verbs if verb in text_lower)
    
    # Calculate score based on number of unique action verbs found
    score = min(100, verb_count * 5)
    
    return {
        "score": score,
        "count": verb_count,
        "suggested_verbs": action_verbs[:10]  # Return some suggested verbs
    }

def extract_keywords(text):
    # Extract potential keywords using NLP
    doc = nlp(text)
    
    # Extract noun phrases as potential keywords
    keywords = [chunk.text.lower() for chunk in doc.noun_chunks]
    
    # Filter out common words and keep only unique keywords
    stopwords = nltk.corpus.stopwords.words('english')
    keywords = [word for word in keywords if word not in stopwords and len(word) > 3]
    
    return list(set(keywords))[:20]  



@app.route('/api/analyze', methods=['POST'])
def analyze():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    industry= request.form.get('job_role') 
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    if file and allowed_file(file.filename):
        filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filename)
        
        # Extract text based on file type
        if filename.endswith('.pdf'):
            text = extract_text_from_pdf(filename)
        elif filename.endswith('.docx'):
            text = extract_text_from_docx(filename)
        else:
            return jsonify({"error": "Unsupported file format"}), 400
        
        
        # Analyze the resume text
        analysis_results = analyze_resume(text,filename)
        
        # Add industry-specific analysis if requested
        if industry:
            industry_analyzer = IndustryAnalyzer()
            industry_analysis = industry_analyzer.analyze_for_industry(text, industry)
            analysis_results["industry_analysis"] = industry_analysis
        
        # Add advanced NLP analysis
        blob = TextBlob(text)
        analysis_results["sentiment"] = {
            "polarity": round(blob.sentiment.polarity, 2),
            "subjectivity": round(blob.sentiment.subjectivity, 2)
        }

        # Clean up the uploaded file
        os.remove(filename)
        
        return jsonify(analysis_results)
    
    return jsonify({"error": "File type not allowed"}), 400

@app.route('/')
def serve():
    return send_from_directory(app.static_folder, 'index.html')

@app.errorhandler(404)
def not_found(e):
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    debug_mode = os.environ.get("FLASK_ENV") != "production"
    app.run(host='0.0.0.0', port=port, debug=debug_mode)