import React from "react";
import { AppBar, Toolbar, Typography } from "@mui/material";
import LocalFloristIcon from "@mui/icons-material/LocalFlorist";

export default function Header() {
  return (
    <AppBar position="static" color="success">
      <Toolbar>
        <LocalFloristIcon sx={{ mr: 1 }} />
        <Typography variant="h6" fontWeight="bold">Plant Disease Detection</Typography>
      </Toolbar>
    </AppBar>
  );
}
