// src/pages/Upload.js
import React from "react";

export default function Upload() {
  return (
    <div className="upload-page">
      <h2>Încarcă articol sau video</h2>
      <form>
        <label>
          Selectează tipul de conținut:
          <select>
            <option>Articol text</option>
            <option>Video</option>
          </select>
        </label>
        <label>
          Încarcă fișier:
          <input type="file" />
        </label>
        <button type="submit">Trimite spre analiză</button>
      </form>
    </div>
  );
}