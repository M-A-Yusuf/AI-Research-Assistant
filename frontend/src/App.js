
import React, { useState } from "react";
import { Box, Button, Typography, Grid, Paper, TextField, MenuItem, Select, InputLabel, FormControl } from "@mui/material";
import { Document, Page, pdfjs } from "react-pdf";
import axios from "axios";

pdfjs.GlobalWorkerOptions.workerSrc = `//cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjs.version}/pdf.worker.js`;


function App() {
  const [file, setFile] = useState(null);
  const [pdfUrl, setPdfUrl] = useState(null);
  const [summary, setSummary] = useState("");
  const [numPages, setNumPages] = useState(null);
  const [citations, setCitations] = useState(null);
  const [loadingCitations, setLoadingCitations] = useState(false);

  // Co-Author states
  const [section, setSection] = useState("Introduction");
  const [topic, setTopic] = useState("");
  const [style, setStyle] = useState("");
  const [draft, setDraft] = useState("");
  const [proofText, setProofText] = useState("");
  const [proofread, setProofread] = useState("");
  // Plagiarism check state
  const [plagiarismResult, setPlagiarismResult] = useState(null);
  const [plagiarismLoading, setPlagiarismLoading] = useState(false);
  // Formatting state
  const [formatStyle, setFormatStyle] = useState("IEEE");
  const [formattedDraft, setFormattedDraft] = useState("");
  const [formatting, setFormatting] = useState(false);
  // Version control state
  const [versionName, setVersionName] = useState("");
  const [savedVersions, setSavedVersions] = useState([]);
  const [loadingVersions, setLoadingVersions] = useState(false);
  // Export state
  const [exporting, setExporting] = useState(false);
  const [exportFormat, setExportFormat] = useState("docx");
  const [exportFilename, setExportFilename] = useState("");
  // Export handler
  const handleExport = async () => {
    if (!formattedDraft) return;
    setExporting(true);
    const res = await axios.post("http://localhost:8000/export_draft/", {
      text: formattedDraft,
      format: exportFormat,
    });
    setExportFilename(res.data.filename);
    setExporting(false);
    // Download file
    window.open(`http://localhost:8000/download_export/${res.data.filename}`, "_blank");
  };
  // Comments state
  const [commentUser, setCommentUser] = useState("");
  const [commentText, setCommentText] = useState("");
  const [comments, setComments] = useState([]);
  const [loadingComments, setLoadingComments] = useState(false);
  // Comments handlers
  const handleAddComment = async () => {
    if (!commentUser || !commentText) return;
    await axios.post("http://localhost:8000/add_comment/", {
      user: commentUser,
      text: commentText,
    });
    setCommentText("");
    handleGetComments();
  };

  const handleGetComments = async () => {
    setLoadingComments(true);
    const res = await axios.get("http://localhost:8000/get_comments/");
    setComments(res.data.comments);
    setLoadingComments(false);
  };
  // Version control handlers
  const handleSaveDraft = async () => {
    if (!draft || !versionName) return;
    await axios.post("http://localhost:8000/save_draft/", {
      draft,
      name: versionName,
    });
    setVersionName("");
    handleListDrafts();
  };

  const handleListDrafts = async () => {
    setLoadingVersions(true);
    const res = await axios.get("http://localhost:8000/list_drafts/");
    setSavedVersions(res.data.drafts);
    setLoadingVersions(false);
  };

  const handleRestoreDraft = async (name) => {
    const res = await axios.get(`http://localhost:8000/get_draft/${name}`);
    setDraft(res.data.draft);
  };
  // Formatting handler
  const handleFormatDraft = async () => {
    if (!draft) return;
    setFormatting(true);
    const res = await axios.post("http://localhost:8000/format_draft/", {
      text: draft,
      style: formatStyle,
    });
    setFormattedDraft(res.data.formatted);
    setFormatting(false);
  };
  // Plagiarism check handler
  const handlePlagiarismCheck = async () => {
    if (!file || !draft) return;
    setPlagiarismLoading(true);
    const formData = new FormData();
    formData.append("file", file);
    formData.append("draft", draft);
    const res = await axios.post("http://localhost:8000/plagiarism_check/", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    setPlagiarismResult(res.data.overlap);
    setPlagiarismLoading(false);
  };

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setPdfUrl(URL.createObjectURL(e.target.files[0]));
    setCitations(null);
  };

  const handleSummarize = async () => {
    if (!file) return;
    const formData = new FormData();
    formData.append("file", file);
    const res = await axios.post("http://localhost:8000/summarize/", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    setSummary(res.data.summary);
  };

  const handleCitations = async () => {
    if (!file) return;
    setLoadingCitations(true);
    const formData = new FormData();
    formData.append("file", file);
    const res = await axios.post("http://localhost:8000/citations/", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    setCitations(res.data);
    setLoadingCitations(false);
  };

  // Co-Author handlers
  const handleDraft = async () => {
    if (!topic) return;
    const res = await axios.post("http://localhost:8000/draft_section/", {
      section,
      topic,
      style,
    });
    setDraft(res.data.draft);
  };

  const handleProofread = async () => {
    if (!proofText) return;
    const res = await axios.post("http://localhost:8000/proofread/", {
      text: proofText,
    });
    setProofread(res.data.proofread);
  };

  return (
    <Box sx={{ flexGrow: 1, p: 2 }}>
      <Typography variant="h4" gutterBottom>
        AI-Powered Research Assistant
      </Typography>
      <input type="file" accept="application/pdf" onChange={handleFileChange} />
      <Button variant="contained" onClick={handleSummarize} sx={{ ml: 2 }}>
        Summarize
      </Button>
      <Button variant="outlined" onClick={handleCitations} sx={{ ml: 2 }}>
        Show Citations
      </Button>
      <Grid container spacing={2} sx={{ mt: 2 }}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2, minHeight: 500 }}>
            <Typography variant="h6">PDF Preview</Typography>
            {pdfUrl && (
              <Document file={pdfUrl} onLoadSuccess={({ numPages }) => setNumPages(numPages)}>
                {Array.from(new Array(numPages), (el, index) => (
                  <Page key={`page_${index + 1}`} pageNumber={index + 1} />
                ))}
              </Document>
            )}
          </Paper>
        </Grid>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2, minHeight: 500 }}>
            <Typography variant="h6">AI Summary</Typography>
            <Typography>{summary}</Typography>
            <Box sx={{ mt: 3 }}>
              <Typography variant="h6">Citations</Typography>
              {loadingCitations && <Typography>Loading...</Typography>}
              {citations && (
                <>
                  <Typography variant="subtitle1">APA:</Typography>
                  <ul>
                    {citations.apa && citations.apa.length > 0 ? citations.apa.map((c, i) => <li key={i}>{c}</li>) : <li>None found</li>}
                  </ul>
                  <Typography variant="subtitle1">IEEE:</Typography>
                  <ul>
                    {citations.ieee && citations.ieee.length > 0 ? citations.ieee.map((c, i) => <li key={i}>{c}</li>) : <li>None found</li>}
                  </ul>
                </>
              )}
            </Box>
          </Paper>
        </Grid>
      </Grid>

      {/* Co-Author Section */}
      <Box sx={{ mt: 4 }}>
        <Typography variant="h5" gutterBottom>
          AI Research Co-Author
        </Typography>
        <Grid container spacing={2}>
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 2 }}>
              <FormControl fullWidth sx={{ mb: 2 }}>
                <InputLabel>Section</InputLabel>
                <Select value={section} label="Section" onChange={e => setSection(e.target.value)}>
                  <MenuItem value="Introduction">Introduction</MenuItem>
                  <MenuItem value="Literature Review">Literature Review</MenuItem>
                  <MenuItem value="Methodology">Methodology</MenuItem>
                  <MenuItem value="Results">Results</MenuItem>
                  <MenuItem value="Discussion">Discussion</MenuItem>
                  <MenuItem value="Conclusion">Conclusion</MenuItem>
                </Select>
              </FormControl>
              <TextField label="Topic" fullWidth sx={{ mb: 2 }} value={topic} onChange={e => setTopic(e.target.value)} />
              <TextField label="Style (optional)" fullWidth sx={{ mb: 2 }} value={style} onChange={e => setStyle(e.target.value)} />
              <Button variant="contained" onClick={handleDraft}>Draft Section</Button>
              <Box sx={{ mt: 2 }}>
                <Typography variant="subtitle1">Draft Output</Typography>
                <Paper sx={{ p: 1, background: '#f5f5f5' }}>{draft}</Paper>
                <Button variant="outlined" sx={{ mt: 2, mr: 2 }} onClick={handlePlagiarismCheck} disabled={!draft || !file}>
                  Plagiarism Check
                </Button>
                {plagiarismLoading && <Typography>Checking for overlap...</Typography>}
                {plagiarismResult !== null && (
                  <Typography sx={{ mt: 1 }} color={plagiarismResult > 0.2 ? 'error' : 'success.main'}>
                    Overlap: {(plagiarismResult * 100).toFixed(2)}% {plagiarismResult > 0.2 ? '(Possible Plagiarism)' : '(Low Overlap)'}
                  </Typography>
                )}
                <FormControl sx={{ mt: 2, minWidth: 120 }}>
                  <InputLabel>Format</InputLabel>
                  <Select value={formatStyle} label="Format" onChange={e => setFormatStyle(e.target.value)}>
                    <MenuItem value="IEEE">IEEE</MenuItem>
                    <MenuItem value="ACM">ACM</MenuItem>
                    <MenuItem value="APA">APA</MenuItem>
                    <MenuItem value="MLA">MLA</MenuItem>
                  </Select>
                </FormControl>
                <Button variant="contained" sx={{ mt: 2, ml: 2 }} onClick={handleFormatDraft} disabled={!draft}>
                  Format Draft
                </Button>
                {formatting && <Typography>Formatting...</Typography>}
                {formattedDraft && (
                  <Box sx={{ mt: 2 }}>
                    <Typography variant="subtitle1">Formatted Draft</Typography>
                    <Paper sx={{ p: 1, background: '#e3f2fd' }}>{formattedDraft}</Paper>
                    <FormControl sx={{ mt: 2, minWidth: 120 }}>
                      <InputLabel>Export</InputLabel>
                      <Select value={exportFormat} label="Export" onChange={e => setExportFormat(e.target.value)}>
                        <MenuItem value="docx">Word (.docx)</MenuItem>
                        <MenuItem value="pdf">PDF (.pdf)</MenuItem>
                        <MenuItem value="latex">LaTeX (.tex)</MenuItem>
                      </Select>
                    </FormControl>
                    <Button variant="contained" sx={{ mt: 2, ml: 2 }} onClick={handleExport} disabled={!formattedDraft}>
                      Export
                    </Button>
                    {exporting && <Typography>Exporting...</Typography>}
                  </Box>
                )}
                {/* Version Control */}
                <Box sx={{ mt: 3 }}>
                  <Typography variant="subtitle1">Version Control</Typography>
                  <TextField label="Version Name" size="small" sx={{ mr: 1 }} value={versionName} onChange={e => setVersionName(e.target.value)} />
                  <Button variant="outlined" size="small" onClick={handleSaveDraft} disabled={!draft || !versionName}>
                    Save Version
                  </Button>
                  <Button variant="text" size="small" sx={{ ml: 1 }} onClick={handleListDrafts}>
                    List Versions
                  </Button>
                  {loadingVersions && <Typography>Loading versions...</Typography>}
                  {savedVersions.length > 0 && (
                    <ul>
                      {savedVersions.map((v, i) => (
                        <li key={i}>
                          <Button size="small" onClick={() => handleRestoreDraft(v)}>{v}</Button>
                        </li>
                      ))}
                    </ul>
                  )}
                </Box>
              </Box>
            </Paper>
          </Grid>
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="subtitle1">Proofread Text</Typography>
              <TextField
                label="Paste text to proofread"
                multiline
                minRows={6}
                fullWidth
                value={proofText}
                onChange={e => setProofText(e.target.value)}
                sx={{ mb: 2 }}
              />
              <Button variant="outlined" onClick={handleProofread}>Proofread</Button>
              <Box sx={{ mt: 2 }}>
                <Typography variant="subtitle1">Proofread Output</Typography>
                <Paper sx={{ p: 1, background: '#f5f5f5' }}>{proofread}</Paper>
              </Box>
            </Paper>
          </Grid>
        </Grid>
      </Box>
      {/* Collaboration: Shared Review Comments */}
      <Box sx={{ mt: 4 }}>
        <Typography variant="h5" gutterBottom>
          Shared Review Comments
        </Typography>
        <TextField label="Your Name" size="small" sx={{ mr: 1 }} value={commentUser} onChange={e => setCommentUser(e.target.value)} />
        <TextField label="Comment" size="small" sx={{ mr: 1, width: 300 }} value={commentText} onChange={e => setCommentText(e.target.value)} />
        <Button variant="outlined" size="small" onClick={handleAddComment} disabled={!commentUser || !commentText}>
          Add Comment
        </Button>
        <Button variant="text" size="small" sx={{ ml: 1 }} onClick={handleGetComments}>
          Refresh Comments
        </Button>
        {loadingComments && <Typography>Loading comments...</Typography>}
        {comments.length > 0 && (
          <ul>
            {comments.map((c, i) => (
              <li key={i}><b>{c.user}:</b> {c.text}</li>
            ))}
          </ul>
        )}
      </Box>
    </Box>
  );
}

export default App;