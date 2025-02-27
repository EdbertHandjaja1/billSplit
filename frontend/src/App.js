import React, { useState } from "react";
import axios from "axios";

const App = () => {
  const [file, setFile] = useState(null);
  const [extractedText, setExtractedText] = useState("");
  const [parsedItems, setParsedItems] = useState([]);

  const handleFileChange = (event) => {
    setFile(event.target.files[0]);
  };

  const handleUpload = async () => {
    if (!file) {
      alert("Please upload an image.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await axios.post("http://127.0.0.1:8000/upload-and-parse", formData, {
        headers: { "Content-Type": "multipart/form-data" },
        withCredentials: true, // Important for CORS
      });
      

      setExtractedText(response.data.text);
      setParsedItems(response.data.items);
    } catch (error) {
      console.error("Error processing receipt:", error);
    }
  };

  return (
    <div>
      <h2>Upload Receipt</h2>
      <input type="file" accept="image/*" onChange={handleFileChange} />
      <button onClick={handleUpload}>Upload & Parse</button>

      <h3>Extracted Text:</h3>
      <pre>{extractedText}</pre>

      <h3>Parsed Items:</h3>
      <ul>
        {parsedItems.map((item, index) => (
          <li key={index}>
            {item.name}: ${item.price.toFixed(2)}
          </li>
        ))}
      </ul>
    </div>
  );
};

export default App;
