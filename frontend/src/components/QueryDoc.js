import React, { useState } from "react";
import { Button, CircularProgress, Box, TextField, Typography } from "@mui/material";
import { queryDoc } from "../api/docQueryApi";

function QueryDoc({ docId }) {
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [answer, setAnswer] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setAnswer("");
    setError("");
    try {
      const res = await queryDoc(docId, query);
      setAnswer(res.answer);
    } catch {
      setError("Query failed. Try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ p: 3, border: '1px solid #e0e0e0', borderRadius: 2, mt: 4 }}>
      <Typography variant="h6" gutterBottom>Ask a Question</Typography>
      <form onSubmit={handleSubmit}>
        <TextField
          label="Your question"
          fullWidth
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          sx={{ mb: 2 }}
        />
        <Button type="submit" variant="contained" disabled={loading || !query}>
          Ask
        </Button>
        {loading && <CircularProgress size={20} sx={{ ml: 2 }} />}
      </form>
      {error && <Typography color="error">{error}</Typography>}
      {answer && (
        <Box sx={{ mt: 2 }}>
          <Typography variant="subtitle1">Answer:</Typography>
          <Typography>{answer}</Typography>
        </Box>
      )}
    </Box>
  );
}
export default QueryDoc;
