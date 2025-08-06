import React, { useState } from "react";
import { Box, CssBaseline, Typography, Container, Paper } from "@mui/material";
import { ThemeProvider } from "@mui/material/styles";
import theme from "./theme";
import UploadPDF from "./components/UploadPDF";
import QueryDoc from "./components/QueryDoc";

function App() {
  const [docId, setDocId] = useState(null);

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Container maxWidth="sm">
        <Paper sx={{ p: 4, mt: 8, textAlign: "center" }}>
          <Typography variant="h4" gutterBottom>DocQueryAI</Typography>
          <Typography variant="subtitle1">
            Chat with your own PDFs using FastAPI & Gemini AI
          </Typography>
          {!docId ? (
            <UploadPDF onSuccess={setDocId} />
          ) : (
            <>
              <Box sx={{ mt: 4, mb: 2 }}>
                <Typography variant="body2">
                  <strong>Document ID:</strong> {docId}
                </Typography>
              </Box>
              <QueryDoc docId={docId} />
            </>
          )}
        </Paper>
      </Container>
    </ThemeProvider>
  );
}
export default App;
