-- AI Mock HR Interview Database Schema
-- Run this file to create the database and tables

CREATE DATABASE IF NOT EXISTS ai_hr_interview CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE ai_hr_interview;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(200),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS roles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description VARCHAR(300),
    icon VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS resumes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    filename VARCHAR(300) NOT NULL,
    raw_text LONGTEXT,
    uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS candidate_profiles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    resume_id INT NOT NULL,
    name VARCHAR(200),
    education TEXT,
    skills TEXT,
    technical_skills TEXT,
    projects TEXT,
    internships TEXT,
    experience TEXT,
    certifications TEXT,
    achievements TEXT,
    career_objective TEXT,
    profile_json LONGTEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (resume_id) REFERENCES resumes(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS interviews (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    role_id INT,
    resume_id INT,
    profile_id INT,
    mode VARCHAR(50),
    difficulty VARCHAR(50),
    style VARCHAR(50),
    total_questions INT DEFAULT 8,
    status VARCHAR(20) DEFAULT 'active',
    overall_score FLOAT,
    started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    completed_at DATETIME,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (role_id) REFERENCES roles(id),
    FOREIGN KEY (resume_id) REFERENCES resumes(id),
    FOREIGN KEY (profile_id) REFERENCES candidate_profiles(id)
);

CREATE TABLE IF NOT EXISTS questions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    interview_id INT NOT NULL,
    question_number INT,
    question_text TEXT NOT NULL,
    question_reason TEXT,
    category VARCHAR(100),
    asked_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (interview_id) REFERENCES interviews(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS answers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    question_id INT NOT NULL,
    answer_text TEXT,
    duration_seconds FLOAT,
    filler_words TEXT,
    answered_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS evaluations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    answer_id INT NOT NULL,
    relevance_score FLOAT,
    clarity_score FLOAT,
    completeness_score FLOAT,
    structure_score FLOAT,
    overall_score FLOAT,
    star_situation VARCHAR(20),
    star_task VARCHAR(20),
    star_action VARCHAR(20),
    star_result VARCHAR(20),
    strengths TEXT,
    improvements TEXT,
    eval_json LONGTEXT,
    FOREIGN KEY (answer_id) REFERENCES answers(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS reports (
    id INT AUTO_INCREMENT PRIMARY KEY,
    interview_id INT NOT NULL,
    overall_score FLOAT,
    communication_score FLOAT,
    answer_quality_score FLOAT,
    relevance_score FLOAT,
    clarity_score FLOAT,
    structure_score FLOAT,
    star_score FLOAT,
    hr_readiness_score FLOAT,
    strengths TEXT,
    improvements TEXT,
    improvement_plan TEXT,
    weak_areas TEXT,
    report_json LONGTEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (interview_id) REFERENCES interviews(id) ON DELETE CASCADE
);

-- Seed default roles
INSERT IGNORE INTO roles (name, description, icon) VALUES
('Software Developer', 'Build and maintain software applications', 'fas fa-code'),
('Web Developer', 'Design and develop web applications', 'fas fa-globe'),
('Python Developer', 'Develop applications using Python', 'fab fa-python'),
('Java Developer', 'Build enterprise applications with Java', 'fab fa-java'),
('Data Analyst', 'Analyze data to drive business decisions', 'fas fa-chart-bar'),
('Business Analyst', 'Bridge business needs and technical solutions', 'fas fa-briefcase'),
('HR Executive', 'Manage human resources and talent acquisition', 'fas fa-users'),
('Other', 'Other professional roles', 'fas fa-star');
