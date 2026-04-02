import React, { useState, useRef } from "react";
import {
  Box, CircularProgress, Alert, Typography, Paper,
  Chip, LinearProgress, Divider,
} from "@mui/material";
import UploadFileIcon from "@mui/icons-material/UploadFile";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import WarningIcon from "@mui/icons-material/Warning";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell,
} from "recharts";
import { predictDisease } from "../services/plantApi";

export default function PlantPage() {
  const [preview, setPreview] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const fileRef = useRef();

  const handleFile = async (file) => {
    if (!file) return;
    setPreview(URL.createObjectURL(file));
    setLoading(true); setError(""); setResult(null);
    try {
      const fd = new FormData();
      fd.append("file", file);
      const r = await predictDisease(fd);
      setResult(r.data);
    } catch (e) {
      setError(e.response?.data?.detail || "Prediction failed.");
    } finally {
      setLoading(false);
    }
  };

  const chartData = result?.top5.map((t) => ({
    label: t.label.split("___")[1]?.replace(/_/g, " ").slice(0, 20) || t.label.slice(0, 20),
    confidence: t.confidence,
    healthy: t.is_healthy,
  })) || [];

  return (
    <Box>
      <Paper
        variant="outlined"
        onClick={() => fileRef.current.click()}
        onDrop={(e) => { e.preventDefault(); handleFile(e.dataTransfer.files[0]); }}
        onDragOver={(e) => e.preventDefault()}
        sx={{ p: 3, mb: 2, textAlign: "center", cursor: "pointer", borderStyle: "dashed", "&:hover": { bgcolor: "action.hover" } }}
      >
        <input ref={fileRef} type="file" hidden accept=".jpg,.jpeg,.png,.bmp,.webp"
          onChange={(e) => handleFile(e.target.files[0])} />
        {loading
          ? <Box><CircularProgress size={28} sx={{ mb: 1 }} /><Typography color="text.secondary">Analyzing leaf…</Typography></Box>
          : <Box sx={{ display: "flex", alignItems: "center", justifyContent: "center", gap: 1 }}>
              <UploadFileIcon color="action" />
              <Typography color="text.secondary">Upload a plant leaf image — JPG / PNG / WEBP</Typography>
            </Box>
        }
      </Paper>

      {preview && (
        <Box sx={{ display: "flex", justifyContent: "center", mb: 2 }}>
          <img src={preview} alt="preview"
            style={{ maxHeight: 220, maxWidth: "100%", borderRadius: 8, border: "1px solid #e0e0e0" }} />
        </Box>
      )}

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      {result && (
        <Paper variant="outlined" sx={{ p: 2.5 }}>
          {/* Health status banner */}
          <Box sx={{
            display: "flex", alignItems: "center", gap: 1.5, mb: 2, p: 1.5,
            borderRadius: 2,
            bgcolor: result.is_healthy ? "success.light" : "error.light",
          }}>
            {result.is_healthy
              ? <CheckCircleIcon color="success" fontSize="large" />
              : <WarningIcon color="error" fontSize="large" />
            }
            <Box>
              <Typography variant="h6" fontWeight="bold">
                {result.is_healthy ? "✅ Healthy Plant" : "⚠️ Disease Detected"}
              </Typography>
              <Typography variant="body2">
                {result.plant} — {result.disease}
              </Typography>
            </Box>
            <Chip label={`${result.confidence}%`}
              color={result.is_healthy ? "success" : "error"}
              sx={{ ml: "auto", fontWeight: "bold" }} />
          </Box>

          <LinearProgress variant="determinate" value={result.confidence}
            color={result.is_healthy ? "success" : "error"}
            sx={{ height: 8, borderRadius: 4, mb: 2 }} />

          <Divider sx={{ mb: 2 }} />

          {/* Top-5 chart */}
          <Typography variant="subtitle2" gutterBottom>Top 5 Predictions</Typography>
          <ResponsiveContainer width="100%" height={180}>
            <BarChart data={chartData} layout="vertical"
              margin={{ top: 0, right: 40, bottom: 0, left: 140 }}>
              <XAxis type="number" domain={[0, 100]} unit="%" tick={{ fontSize: 11 }} />
              <YAxis type="category" dataKey="label" tick={{ fontSize: 11 }} width={140} />
              <Tooltip formatter={(v) => `${v}%`} />
              <Bar dataKey="confidence" radius={[0, 4, 4, 0]}>
                {chartData.map((d, i) => (
                  <Cell key={i} fill={d.healthy ? "#4caf50" : i === 0 ? "#f44336" : "#ff9800"} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </Paper>
      )}
    </Box>
  );
}
