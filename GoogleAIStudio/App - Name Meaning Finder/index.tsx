import React, { useState } from "react";
import { createRoot } from "react-dom/client";
import { GoogleGenAI, GenerateContentResponse } from "@google/genai";

const App: React.FC = () => {
  const [name, setName] = useState("");
  const [meaning, setMeaning] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  
  // process.env.API_KEY is assumed to be set in the execution environment
  const ai = new GoogleGenAI({ apiKey: process.env.API_KEY! });

  const fetchMeaning = async () => {
    if (!name.trim()) return;

    setLoading(true);
    setMeaning("");
    setError("");

    try {
      const prompt = `Provide a concise and friendly explanation of the origin and meaning of the name "${name}". If the name has multiple origins or meanings, briefly mention the most common ones.`;

      const response: GenerateContentResponse = await ai.models.generateContent({
        model: 'gemini-2.5-flash-preview-04-17',
        contents: prompt,
      });

      const text = response.text;
      if (text) {
        setMeaning(text);
      } else {
        setError("Could not retrieve a valid meaning. The response was empty.");
      }
    } catch (err: any) {
      const errorMessage = err.message || "An unexpected error occurred.";
      setError(`Error fetching meaning: ${errorMessage}`);
      console.error(err);
    } finally {
      setLoading(false);
    }
  };
  
  const handleKeyPress = (event: React.KeyboardEvent<HTMLInputElement>) => {
    if (event.key === 'Enter') {
      fetchMeaning();
    }
  };

  return (
    <div className="container">
      <h1 className="title">🔍 Name Meaning Finder</h1>
      <div className="input-group">
        <input
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Enter a name..."
          className="input-field"
          aria-label="Name input"
          disabled={loading}
        />
        <button
          onClick={fetchMeaning}
          className="submit-button"
          disabled={loading || !name.trim()}
        >
          {loading ? 'Searching...' : 'Find Meaning'}
        </button>
      </div>

      {loading && <div className="loading-spinner" aria-label="Loading"></div>}
      
      {error && <p className="error-message" role="alert">{error}</p>}

      {meaning && !loading && (
        <div className="result-container">
          <h3>Meaning of "{name}":</h3>
          <p>{meaning}</p>
        </div>
      )}
    </div>
  );
};

const rootEl = document.getElementById("root");
if (rootEl) {
    const root = createRoot(rootEl);
    root.render(<App />);
} else {
    console.error("Root element not found");
}
