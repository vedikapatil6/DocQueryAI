import React, { useState } from "react";
import { Button, CircularProgress, Typography, Box } from "@mui/material";
import { uploadPDF } from "../api/docQueryApi";

function UploadPDF({ onSuccess }) {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleFileChange = (e) => setFile(e.target.files[0]);

  const handleUpload = async () => {
    if (!file) return setError("Please select a PDF file.");
    setLoading(true);
    setError("");
    try {
      const res = await uploadPDF(file);
      onSuccess(res.doc_id);
    } catch {
      setError("Upload failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ p: 3, border: '1px solid #e0e0e0', borderRadius: 2, mt: 4 }}>
      <Typography variant="h6" gutterBottom>Upload a PDF</Typography>
      <input
        type="file"
        accept="application/pdf"
        onChange={handleFileChange}
        style={{ marginBottom: 10 }}
      />
      <Button
        onClick={handleUpload}
        variant="contained"
        disabled={loading}
      >Upload</Button>
      {loading && <CircularProgress size={20} sx={{ ml: 2 }} />}
      {error && <Typography color="error">{error}</Typography>}
    </Box>
  );
}
export default UploadPDF;
