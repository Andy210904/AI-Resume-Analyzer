import json
import re
import os

class IndustryAnalyzer:
    def __init__(self):
        self.industries = {
            "software_engineer": {
                "required_skills": [
                    "python", "java", "javascript", "c++", "ruby", "go", "rust",
                    "react", "angular", "vue", "django", "flask", "spring", "node",
                    "database", "sql", "nosql", "mongodb", "postgresql", "mysql",
                    "aws", "azure", "gcp", "cloud", "docker", "kubernetes",
                    "git", "ci/cd", "testing", "algorithms", "data structures"
                ],
                "recommended_sections": [
                    "technical skills", "projects", "experience", "education",
                    "github", "open source contributions", "certifications"
                ],
                "action_verbs": [
                    "developed", "implemented", "architected", "designed", "built",
                    "optimized", "debugged", "refactored", "deployed", "maintained",
                    "tested", "automated", "integrated", "solved", "improved"
                ],
                "achievements_keywords": [
                    "hackathon", "coding","competition", "ideathon", "optimization", "deployment", 
                    "refactoring", "scalability", "automation", "integration", "debugging",
                    "performance", "contribution", "latency", "efficiency", "innovation"
                ]

            },
            "data_scientist": {
                "required_skills": [
                    "python", "r", "sql", "pandas", "numpy", "scikit-learn", "tensorflow",
                    "pytorch", "machine learning", "data analysis", "data visualization",
                    "statistics", "big data", "hadoop", "spark", "data mining",
                    "nlp", "computer vision", "deep learning", "tableau", "power bi",
                    "a/b testing", "experiment design", "feature engineering"
                ],
                "recommended_sections": [
                    "technical skills", "projects", "experience", "education",
                    "publications", "research", "certifications"
                ],
                "action_verbs": [
                    "analyzed", "modeled", "predicted", "improved", "developed",
                    "implemented", "researched", "visualized", "extracted", "processed",
                    "trained", "evaluated", "optimized", "designed", "deployed"
                ],
                "achievements_keywords": [
                    "hackathon", "coding","competition", "ideathon", "optimization", "deployment", 
                    "refactoring", "scalability", "automation", "integration", "debugging",
                    "performance", "contribution", "latency", "efficiency", "innovation",
                    "accuracy", "insights", "prediction", "analysis", "visualization",
                ]
            },
            "marketing": {
                "required_skills": [
                    "social media", "content marketing", "seo", "sem", "email marketing",
                    "google analytics", "copywriting", "market research", "brand management",
                    "campaign management", "adobe creative suite", "canva", "hubspot", 
                    "mailchimp", "facebook ads", "google ads", "marketing strategy",
                    "analytics", "customer acquisition", "a/b testing"
                ],
                "recommended_sections": [
                    "skills", "experience", "education", "campaigns", "portfolio",
                    "certifications", "achievements"
                ],
                "action_verbs": [
                    "launched", "created", "managed", "designed", "generated",
                    "implemented", "developed", "increased", "grew", "coordinated",
                    "executed", "optimized", "analyzed", "strategized", "produced"
                ],
                "achievements_keywords": [
                    "conversion", "traffic", "engagement", "growth", "reach", 
                    "branding", "roi", "campaign", "strategy", "leads",
                    "acquisition", "retention", "optimization", "content", "promotion"
                ]

            },
            "finance": {
                "required_skills": [
                    "financial analysis", "excel", "financial modeling", "accounting",
                    "budgeting", "forecasting", "bloomberg", "capital markets", "valuation",
                    "financial reporting", "risk management", "investment", "portfolio management",
                    "quickbooks", "sap", "cfa", "financial statements", "taxes", "regulations"
                ],
                "recommended_sections": [
                    "skills", "experience", "education", "certifications", "achievements",
                    "financial expertise", "licenses"
                ],
                "action_verbs": [
                    "analyzed", "managed", "increased", "reduced", "improved",
                    "developed", "forecasted", "budgeted", "reconciled", "audited",
                    "allocated", "assessed", "calculated", "evaluated", "streamlined"
                ],
                "achievements_keywords": [
                    "profit", "costs", "savings", "forecast", "budgeting", 
                    "modeling", "valuation", "compliance", "accuracy", "investment",
                    "reporting", "auditing", "efficiency", "risk", "regulation"
                ]

            }
        }
    
    def analyze_for_industry(self, text, industry):
        """Analyze a resume for a specific industry"""
        if industry not in self.industries:
            return {"error": f"Industry '{industry}' not supported"}
        
        industry_data = self.industries[industry]
        text_lower = text.lower()
        
        # Skills analysis
        found_skills = []
        missing_skills = []
        for skill in industry_data["required_skills"]:
            if skill.lower() in text_lower:
                found_skills.append(skill)
            else:
                missing_skills.append(skill)
        
        skills_score = min(100, int((len(found_skills) / len(industry_data["required_skills"])) * 100))
        
        # Section analysis
        found_sections = []
        missing_sections = []
        for section in industry_data["recommended_sections"]:
            if section.lower() in text_lower:
                found_sections.append(section)
            else:
                missing_sections.append(section)
        
        sections_score = min(100, int((len(found_sections) / len(industry_data["recommended_sections"])) * 100))
        
        # Action verbs analysis
        found_verbs = []
        for verb in industry_data["action_verbs"]:
            if verb.lower() in text_lower:
                found_verbs.append(verb)
        
        verbs_score = min(100, int((len(found_verbs) / 10) * 100))  # We just need around 10 good verbs
        
        # Achievements analysis
        found_achievements = []
        for achievement in industry_data["achievements_keywords"]:
            if achievement.lower() in text_lower:
                found_achievements.append(achievement)
        
        achievements_score = min(100, int((len(found_achievements) / 5) * 100))  # Need around 5 achievement phrases
        
        # Calculate overall industry-specific score
        overall_score = int((skills_score * 0.4) + (sections_score * 0.2) + 
                           (verbs_score * 0.2) + (achievements_score * 0.2))
        
        # Generate suggestions
        suggestions = []
        
        if skills_score < 80:
            top_missing = missing_skills[:5]  # Get top 5 missing skills
            suggestions.append(f"Add more skills to your resume. Consider including: {', '.join(top_missing)}")
        
        if sections_score < 80:
            top_missing_sections = missing_sections[:3]  # Get top 3 missing sections
            suggestions.append(f"Include these important sections: {', '.join(top_missing_sections)}")
        
        if verbs_score < 80:
            top_verbs = [v for v in industry_data["action_verbs"][:5] if v not in found_verbs]
            suggestions.append(f"Use stronger action verbs like: {', '.join(top_verbs)}")
        
        if achievements_score < 80:
            suggestions.append("Focus more on quantifiable achievements relevant to your industry")
        
        return {
            "industry": industry,
            "overall_score": overall_score,
            "skills_analysis": {
                "score": skills_score,
                "found_skills": found_skills,
                "missing_important_skills": missing_skills[:7]  # Show top 7 missing skills
            },
            "sections_analysis": {
                "score": sections_score,
                "found_sections": found_sections,
                "missing_sections": missing_sections
            },
            "verbs_analysis": {
                "score": verbs_score,
                "found_verbs": found_verbs,
                "recommended_verbs": [v for v in industry_data["action_verbs"][:7] if v not in found_verbs]
            },
            "achievements_analysis": {
                "score": achievements_score,
                "achievement_phrases_found": found_achievements
            },
            "suggestions": suggestions
        }