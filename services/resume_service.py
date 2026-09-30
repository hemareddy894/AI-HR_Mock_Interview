import os
import re
import pdfplumber
import docx

ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_file(filepath):
    ext = filepath.rsplit('.', 1)[1].lower()
    if ext == 'pdf':
        return _extract_pdf(filepath)
    elif ext in ('doc', 'docx'):
        return _extract_docx(filepath)
    return ''

def _extract_pdf(filepath):
    text = ''
    try:
        with pdfplumber.open(filepath) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + '\n'
    except Exception as e:
        raise ValueError(f"Could not read PDF: {str(e)}")
    return text.strip()

def _extract_docx(filepath):
    try:
        doc = docx.Document(filepath)
        return '\n'.join(p.text for p in doc.paragraphs if p.text.strip())
    except Exception as e:
        raise ValueError(f"Could not read DOCX: {str(e)}")

def count_filler_words(text):
    fillers = ['um', 'uh', 'like', 'actually', 'you know', 'basically', 'literally',
               'kind of', 'sort of', 'i mean', 'right', 'okay so', 'so yeah']
    text_lower = text.lower()
    found = {}
    for filler in fillers:
        count = len(re.findall(r'\b' + re.escape(filler) + r'\b', text_lower))
        if count > 0:
            found[filler] = count
    return found
