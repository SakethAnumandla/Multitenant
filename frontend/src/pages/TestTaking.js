import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { testAPI } from "../services/api";

function TestTaking() {
  const { testId } = useParams();
  const navigate = useNavigate();
  const [test, setTest] = useState(null);
  const [response, setResponse] = useState(null);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [answers, setAnswers] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [imageFile, setImageFile] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);

  useEffect(() => {
    loadTest();
  }, [testId]);

  const loadTest = async () => {
    try {
      setLoading(true);
      const res = await testAPI.startTest(testId);
      setTest(res.data.test);
      setResponse(res.data.response);
      
      // Load existing answers
      if (res.data.response.responses) {
        setAnswers(res.data.response.responses);
      }
    } catch (err) {
      setError(err.response?.data?.error || "Failed to load test");
    } finally {
      setLoading(false);
    }
  };

  const handleAnswerChange = (questionId, value) => {
    setAnswers({
      ...answers,
      [questionId]: value,
    });
    
    // Auto-submit answer
    if (response) {
      testAPI.submitAnswer(response.id, questionId, value).catch((err) => {
        console.error("Failed to save answer:", err);
      });
    }
  };

  const handleNext = () => {
    if (currentQuestionIndex < test.questions.length - 1) {
      setCurrentQuestionIndex(currentQuestionIndex + 1);
    }
  };

  const handlePrevious = () => {
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex(currentQuestionIndex - 1);
    }
  };

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setImageFile(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setImagePreview(reader.result);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleSubmit = async () => {
    try {
      setSubmitting(true);
      
      // First, submit any unsaved answers
      for (const [questionId, answer] of Object.entries(answers)) {
        if (response && !response.responses[questionId]) {
          await testAPI.submitAnswer(response.id, questionId, answer);
        }
      }
      
      // Upload image if provided
      if (imageFile && response) {
        await testAPI.uploadImage(response.id, imageFile);
      } else if (response) {
        // Complete without image
        await testAPI.completeTest(response.id);
      }
      
      alert("Test submitted successfully!");
      navigate("/user/dashboard");
    } catch (err) {
      setError(err.response?.data?.error || "Failed to submit test");
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="loading">
        <div className="spinner"></div>
        <p>Loading test...</p>
      </div>
    );
  }

  if (error && !test) {
    return (
      <div className="form-container">
        <div className="form-error">{error}</div>
        <button onClick={() => navigate("/user/dashboard")} className="btn btn-primary">
          Go Back
        </button>
      </div>
    );
  }

  const questions = test?.questions || [];
  const isLastQuestion = currentQuestionIndex === questions.length - 1;
  const currentQuestion = questions[currentQuestionIndex];

  if (!currentQuestion) {
    return null;
  }

  const renderQuestionInput = (question) => {
    const value = answers[question.id] || "";
    
    switch (question.question_type) {
      case "text":
        return (
          <input
            type="text"
            value={value}
            onChange={(e) => handleAnswerChange(question.id, e.target.value)}
            placeholder={question.placeholder || "Enter your answer"}
            className="form-control"
            required={question.is_required}
          />
        );
      
      case "textarea":
        return (
          <textarea
            value={value}
            onChange={(e) => handleAnswerChange(question.id, e.target.value)}
            placeholder={question.placeholder || "Enter your answer"}
            className="form-control"
            rows={4}
            required={question.is_required}
          />
        );
      
      case "radio":
        return (
          <div className="radio-group">
            {question.options?.map((option, idx) => (
              <label key={idx} className="radio-label">
                <input
                  type="radio"
                  name={`question-${question.id}`}
                  value={option}
                  checked={value === option}
                  onChange={(e) => handleAnswerChange(question.id, e.target.value)}
                  required={question.is_required}
                />
                <span>{option}</span>
              </label>
            ))}
          </div>
        );
      
      case "checkbox":
        const checkedValues = Array.isArray(value) ? value : [];
        return (
          <div className="checkbox-group">
            {question.options?.map((option, idx) => (
              <label key={idx} className="checkbox-label">
                <input
                  type="checkbox"
                  value={option}
                  checked={checkedValues.includes(option)}
                  onChange={(e) => {
                    const newValues = e.target.checked
                      ? [...checkedValues, option]
                      : checkedValues.filter((v) => v !== option);
                    handleAnswerChange(question.id, newValues);
                  }}
                />
                <span>{option}</span>
              </label>
            ))}
          </div>
        );
      
      case "range":
        return (
          <input
            type="range"
            min={0}
            max={100}
            value={value || 50}
            onChange={(e) => handleAnswerChange(question.id, e.target.value)}
            className="range-input"
          />
        );
      
      default:
        return (
          <input
            type="text"
            value={value}
            onChange={(e) => handleAnswerChange(question.id, e.target.value)}
            className="form-control"
          />
        );
    }
  };

  return (
    <div className="test-taking-container">
      <div className="test-header">
        <h1>{test.title}</h1>
        {test.description && <p className="test-description">{test.description}</p>}
        
        {currentQuestion.section && (
          <div className="section-badge">
            {currentQuestion.section}
          </div>
        )}
        
        <div className="progress-bar">
          <div
            className="progress-fill"
            style={{
              width: `${((currentQuestionIndex + 1) / questions.length) * 100}%`,
            }}
          />
        </div>
        <p className="progress-text">
          Question {currentQuestionIndex + 1} of {questions.length}
        </p>
      </div>

      <div className="question-container">
        <div className="question-header">
          <h2>{currentQuestion.question_text}</h2>
          {currentQuestion.is_required && (
            <span className="required-badge">Required</span>
          )}
        </div>

        <div className="question-input-container">
          {renderQuestionInput(currentQuestion)}
        </div>
      </div>

      {isLastQuestion && (
        <div className="image-upload-container">
          <h3>Upload Image</h3>
          <p>Please upload an image to complete the test</p>
          <input
            type="file"
            accept="image/*"
            onChange={handleImageChange}
            className="file-input"
          />
          {imagePreview && (
            <div className="image-preview">
              <img src={imagePreview} alt="Preview" />
            </div>
          )}
        </div>
      )}

      {error && <div className="form-error">{error}</div>}

      <div className="test-navigation">
        <button
          onClick={handlePrevious}
          disabled={currentQuestionIndex === 0}
          className="btn btn-secondary"
        >
          Previous
        </button>

        {isLastQuestion ? (
          <button
            onClick={handleSubmit}
            disabled={submitting || (currentQuestion.is_required && !answers[currentQuestion.id])}
            className="btn btn-primary"
          >
            {submitting ? "Submitting..." : "Submit Test"}
          </button>
        ) : (
          <button
            onClick={handleNext}
            disabled={currentQuestion.is_required && !answers[currentQuestion.id]}
            className="btn btn-primary"
          >
            Next
          </button>
        )}
      </div>
    </div>
  );
}

export default TestTaking;

