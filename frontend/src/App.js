import React, { useState } from "react";
import axios from "axios";
import './App.css';

function App() {
  const [selectedOption, setSelectedOption] = useState('text');
  const [textInput, setTextInput] = useState('');
  const [result, setResult] = useState(null);
  const [fileInput, setFileInput] = useState(null);
  const [fileName, setFileName] = useState('No File Chosen');
  const [loading, setLoading] = useState(false);

  const handleOptionChange = (e) => {
    setSelectedOption(e.target.value);
    setResult(null);
    setTextInput('');
    setFileInput(null);
    setFileName('No File Chosen')
  };

  const handleTextChange = (e) => {
    setTextInput(e.target.value);
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    setFileInput(file);
    setFileName(file ? file.name : 'No File Chosen');
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    setResult(null)
    const formData = new FormData();

    if (selectedOption === 'text') {
      formData.append('textInput', textInput);
    }
    else if (selectedOption === 'file' && fileInput) {
      formData.append('fileInput', fileInput);
    }

    setLoading(true)

    axios
      .post("http://localhost:8000/review_result/", formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        }
      })
      .then((response) => {
        setResult(response.data);
        setLoading(false);
      })
      .catch((error) => {
        console.error("There was an error submitting the review!", error);
        setLoading(false);
      });
  };

  return (
    <div className="App">
      <h1>Product Review Sentiment Analyzer</h1>
      <div className="toggle-buttons">
        <label className={`toggle-label ${selectedOption === 'text' ? 'active' : ''}`}>
          <input
            type="radio"
            value="text"
            checked={selectedOption === 'text'}
            onChange={handleOptionChange}
          />
          Text
        </label>
        <label className={`toggle-label ${selectedOption === 'file' ? 'active' : ''}`}>
          <input
            type="radio"
            value="file"
            checked={selectedOption === 'file'}
            onChange={handleOptionChange}
          />
          File
        </label>
      </div>

      <form onSubmit={handleSubmit} method="POST" encType="multipart/form-data">
        {selectedOption === 'text' ? (
          <div className="text-input-container">
            <label htmlFor="textInput" className="text-input-label">Your Text :</label>
            <textarea
              id="textInput"
              name="textInput"
              value={textInput}
              onChange={handleTextChange}
              placeholder="Enter your text here"
              rows="10"
              cols="50"
            ></textarea>
          </div>
        ) : (
          <div>
            <div className="file-input-container">
              <input
                type="file"
                id="fileInput"
                name="fileInput"
                onChange={handleFileChange}
                className="file-input"
              />
              <button
                type="button"
                className="file-input-button"
                onClick={() => document.getElementById("fileInput").click()}
              >
                Choose File
              </button>
              <span className="file-name">{fileName}</span>
            </div>
          </div>
        )}
        <button type="submit" disabled={loading}>Submit</button>
      </form>

      {loading && (
        <div className="loading-spinner">
          <div className="spinner">
          </div>
        </div>
      )}

      {result && (
        <div className="result">
          <h2>Sentiment for the reviews:</h2>
          {result.text === undefined ? (
            <div className="sentiment-score">
              <p><span>Positive Reviews: </span>{result.Positive_Reviews}%</p>
              <p><span>Neutral_Reviews: </span>{result.Neutral_Reviews}%</p>
              <p><span>Negative_Reviews: </span>{result.Negative_Reviews}%</p>
              {/* <p><span>Average Sentiment Score: </span>{result.Average_Sentiment_Score}%</p> */}
              <p><span>Overall Sentiment: </span>{result.Overall_Sentiment}</p>
              <p><span>Product Summary: </span>{result.Product_Summary}</p>
            </div>
          ) : (
            <div className="sentiment-score">
              <p><span>Sentiment: </span>{result.sentiment}</p>
              <p><span>Sentiment Score: </span>{result.sentiment_score}%</p>
              <p><span>Summary: </span>{result.summary}</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default App;