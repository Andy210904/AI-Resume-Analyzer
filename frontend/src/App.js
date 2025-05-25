import React, { useState } from 'react';
import axios from 'axios';
import 'bootstrap/dist/css/bootstrap.min.css';
import './App.css';

function App() {
  const [file, setFile] = useState(null);
  const [fileName, setFileName] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error,setError] = useState('');
  const [error_file, setErrorFile] = useState('');
  const[error_role,setErrorRole] = useState('');
  const [selectedJob, setSelectedJob] = useState('');

  const handleDropdownChange = (event) => {
    setSelectedJob(event.target.value);
  };

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      if (selectedFile.type === 'application/pdf' || 
          selectedFile.type === 'application/vnd.openxmlformats-officedocument.wordprocessingml.document') {
        setFile(selectedFile);
        setFileName(selectedFile.name);
        setErrorFile('');
      } else {
        setFile(null);
        setFileName('');
        setErrorFile('Please upload a PDF or DOCX file');
      }
    }
  };

  function formatIndustry(industry) {
    if (!industry) return "";
    return industry
      .split('_')                      // Split at underscores
      .map(word => word.charAt(0).toUpperCase() + word.slice(1)) // Capitalize
      .join(' ');                      // Join with space
  }


  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!file) {
      setErrorFile('Please select a file first');
      return;
    }

    if (!selectedJob) {
      setErrorRole('Please select a job role');
      return;
    }

    setLoading(true);
    setErrorRole('');

    const formData = new FormData();
    formData.append('file', file);
    formData.append('job_role', selectedJob); // add job role

    try {
      const response = await axios.post('http://localhost:5000/api/analyze', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      setResults(response.data);
    } catch (err) {
      setError(err.response?.data?.error || 'Error analyzing resume');
    } finally {
      setLoading(false);
    }
  };


  const getSectionFeedback = (section) => {
    if (!results || !results.sections || !results.sections[section]) {
      return null;
    }
    
    const sectionData = results.sections[section];
    return (
      <div className="section-feedback">
        <h4 className="mt-3">{section.charAt(0).toUpperCase() + section.slice(1)}</h4>
        {sectionData.exists ? (
          <>
            <div className="progress mb-2">
              <div 
                className={`progress-bar ${sectionData.score >= 90 ? 'bg-success' : sectionData.score >= 40 ? 'bg-warning' : 'bg-danger'}`} 
                role="progressbar" 
                style={{ width: `${sectionData.score}%` }} 
                aria-valuenow={sectionData.score} 
                aria-valuemin="0" 
                aria-valuemax="100">
                {sectionData.score}%
              </div>
            </div>
            <ul className="section-feedback-list">
              {sectionData.feedback.map((item, index) => (
                <li key={index}>{item}</li>
              ))}
            </ul>
          </>
        ) : (
          <div className="alert alert-warning">This section is missing from your resume</div>
        )}
      </div>
    );
  };

  const getIndustryAnalysisFeedback = (title, analysis) => {
    if (!results?.industry_analysis?.[analysis]) {
      return null;
    }

    const sectionData = results.industry_analysis[analysis];

    return (
      <div className="section-feedback">
        <h4 className="mt-3">{title}</h4>

        {/* Progress Bar */}
        <div className="progress mb-2">
          <div
            className={`progress-bar ${
              sectionData.score >= 90
                ? 'bg-success'
                : sectionData.score >= 40
                ? 'bg-warning'
                : 'bg-danger'
            }`}
            role="progressbar"
            style={{ width: `${sectionData.score}%` }}
            aria-valuenow={sectionData.score}
            aria-valuemin="0"
            aria-valuemax="100"
          >
            {sectionData.score}%
          </div>
        </div>

        {/* Feedback Lists */}
        <ul className="section-feedback-list">
          {sectionData.found_skills && (
            <li><strong>Found Skills:</strong> {sectionData.found_skills.join(', ')}</li>
          )}
          {sectionData.missing_important_skills && (
            <li><strong>Missing Important Skills:</strong> {sectionData.missing_important_skills.join(', ')}</li>
          )}
          {sectionData.found_sections && (
            <li><strong>Found Sections:</strong> {sectionData.found_sections.join(', ')}</li>
          )}
          {sectionData.missing_sections && (
            <li><strong>Missing Sections:</strong> {sectionData.missing_sections.join(', ')}</li>
          )}
          {sectionData.found_verbs && (
            <li><strong>Found Verbs:</strong> {sectionData.found_verbs.join(', ')}</li>
          )}
          {sectionData.recommended_verbs && (
            <li><strong>Recommended Verbs:</strong> {sectionData.recommended_verbs.join(', ')}</li>
          )}
          {sectionData.achievement_phrases_found && (
            <li><strong>Achievement Phrases Found:</strong> {sectionData.achievement_phrases_found.join(', ')}</li>
          )}
        </ul>
      </div>
    );
  };


return (
    <div className="container-fluid">
      <div className="row mt-5">
        <div className="col-12 text-center">
          <h1>Resume Analyzer</h1>
          <p className="lead">Upload your resume to get detailed analysis and personalized suggestions</p>
        </div>
      </div>

      <div className="row justify-content-center mt-4">
        <div className="col-md-8">
          <div className="card">
            <div className="card-body">
              <form onSubmit={handleSubmit}>
                <div className="mb-3">
                  <label htmlFor="resumeFile" className="form-label">Upload Resume (PDF or DOCX)</label>
                  <input 
                    type="file" 
                    className="form-control" 
                    id="resumeFile" 
                    onChange={handleFileChange}
                    accept=".pdf,.docx"
                  />
                  {fileName && <div className="mt-2">Selected file: {fileName}</div>}
                  {error_file && <div className="text-danger mt-2">{error_file}</div>}
                </div>
                <div className="mb-3">
                  <label htmlFor="jobDescription" className="form-label">Select your Job Description</label>
                  <select
                    id="jobDescription"
                    className="form-select"
                    value={selectedJob}
                    onChange={handleDropdownChange}
                  >
                    <option value="">-- Select a role --</option>
                    <option value="software_engineer">Software Engineer</option>
                    <option value="finance">Finance</option>
                    <option value="data_scientist">Data Scientist</option>
                    <option value="marketing">Marketing</option>
                  </select>

                  {error_role && <div className="text-danger mt-2">{error_role}</div>}
                </div>

                <button 
                  type="submit" 
                  className="btn btn-primary"
                  disabled={loading || !file}
                >
                  {loading ? 'Analyzing...' : 'Analyze Resume'}
                </button>
              </form>
            </div>
          </div>
        </div>
      </div>

      {loading && (
        <div className="row justify-content-center mt-4">
          <div className="col-md-8 text-center">
            <div className="spinner-border text-primary" role="status">
              <span className="visually-hidden">Loading...</span>
            </div>
            <p className="mt-2">Analyzing your resume... This may take a moment.</p>
          </div>
        </div>
      )}

      {results && !loading && (
      <div className='container-fluid h-screen p-4'>
        <div className="row h-full">
          <div className="col-md-6 mt-4 h-full flex flex-col">
            {/* General Analysis Card */}
            <div className="card">
              <div className="card-header">
                <h2>Analysis Results</h2>
              </div>
              <div className="card-body">
                <div className="text-center mb-4">
                  <h3>Overall Score</h3>
                  <div className="d-inline-flex align-items-center justify-content-center rounded-circle border border-3 p-3" style={{width: "100px", height: "100px"}}>
                    <span className={`fs-2 fw-bold ${results.overall_score >= 70 ? 'text-success' : results.overall_score >= 50 ? 'text-warning' : 'text-danger'}`}>
                      {results.overall_score}%
                    </span>
                  </div>
                </div>

                <div className="mb-4">
                  {getSectionFeedback('education')}
                  {getSectionFeedback('experience')}
                  {getSectionFeedback('skills')}
                  {getSectionFeedback('projects')}
                </div>

                <div className="mb-4">
                  <div className="section-feedback">
                    <h4 className="mt-3">Suggestions for Improvement</h4>
                    {results?.suggestions?.length > 0 ? (
                      <ul className="section-feedback-list">
                        {results.suggestions.map((suggestion, index) => (
                          <li key={index}>{suggestion}</li>
                        ))}
                      </ul>
                    ) : (
                      <div className="alert alert-success">
                        Great job! We don't have any major suggestions for improvement.
                      </div>
                    )}
                  </div>
                </div>

                <div className="mb-4">
                  <div className="section-feedback">
                    <h4 className="mt-3">Resume Strengths</h4>
                    {results?.strengths?.length > 0 ? (
                      <ul className="section-feedback-list">
                        {results.strengths.map((strength, index) => (
                          <li key={index}>{strength}</li>
                        ))}
                      </ul>
                    ) : (
                      <div className="alert alert-warning">
                        We couldn't identify any particular strengths. Follow our suggestions to improve your resume.
                      </div>
                    )}
                  </div>
                </div>

                <div className='mb-4'>
                  <div className="section-feedback">
                    <h4 className="mt-3">Resume Statistics</h4>
                    <p><strong>Word Count:</strong> {results.word_count}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="col-md-6 h-full flex flex-col mt-4">
            {/* Industry Analysis Card */}
            <div className="card h-100">
              <div className="card-header">
                <h2>Industry Analysis: {formatIndustry(results.industry_analysis?.industry)}</h2>
              </div>
              <div className="card-body">
                <div className="text-center mb-4">
                  <h3>Industry Score</h3>
                <div className="d-inline-flex align-items-center justify-content-center rounded-circle border border-3 p-3" style={{width: "100px", height: "100px"}}>
                    <span className={`fs-2 fw-bold ${results.industry_analysis?.overall_score >= 70 ? 'text-success' : results.industry_analysis?.overall_score >= 50 ? 'text-warning' : 'text-danger'}`}>
                      {results.industry_analysis?.overall_score}%
                    </span>
                  </div>
                </div>


                {getIndustryAnalysisFeedback("Skills Analysis", "skills_analysis")}
                {getIndustryAnalysisFeedback("Sections Analysis", "sections_analysis")}
                {getIndustryAnalysisFeedback("Verbs Analysis", "verbs_analysis")}
                {getIndustryAnalysisFeedback("Achievements", "achievements_analysis")}


                <div className="mb-4">
                  <div className="section-feedback">
                    <h4 className="mt-3">Suggestions</h4>
                    {results.industry_analysis?.suggestions?.length > 0 ? (
                      <ul className="section-feedback-list">
                        {results.industry_analysis.suggestions.map((suggestion, index) => (
                          <li key={index}>{suggestion}</li>
                        ))}
                      </ul>
                    ) : (
                      <div className="alert alert-success">
                        Great job! We don't have any major suggestions for improvement.
                      </div>
                    )}
                  </div>
                </div>

              </div>
            </div>
          </div>
        </div>
        </div>
      )}
    </div>
  );
}

export default App;