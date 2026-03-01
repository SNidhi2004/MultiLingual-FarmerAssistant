export default function ImagePanel({
  imagePreview,
  setImageFile,
  setImagePreview,
  resetCurrent,
  loadingAnalyze,
  disease,
  confidence
}) {

  return (
    <div className="dash-left">

      {!imagePreview && (
        <div className="upload-card">

          <label className="upload-btn">
            📁 Upload image
            <input
              type="file"
              accept="image/*"
              hidden
              onChange={(e) => {
                const f = e.target.files[0];
                if (!f) return;
                setImageFile(f);
                setImagePreview(URL.createObjectURL(f));
              }}
            />
          </label>

          <label className="upload-btn secondary">
            📷 Use camera
            <input
              type="file"
              accept="image/*"
              capture="environment"
              hidden
              onChange={(e) => {
                const f = e.target.files[0];
                if (!f) return;
                setImageFile(f);
                setImagePreview(URL.createObjectURL(f));
              }}
            />
          </label>

        </div>
      )}

      {imagePreview && (
        <>
          <img
            src={imagePreview}
            className="preview-img"
          />

          <div className="image-actions">
            <button onClick={resetCurrent}>🔄 Retake</button>
            <button onClick={resetCurrent}>➕ New image</button>
          </div>

          <div className="result-card">
            {loadingAnalyze && <div>Analyzing...</div>}

            {!loadingAnalyze && disease && (
              <>
                <div className="disease">{disease}</div>
                <div className="confidence">
                  Confidence : {(confidence * 100).toFixed(1)}%
                </div>
              </>
            )}
          </div>
        </>
      )}

    </div>
  );
}
