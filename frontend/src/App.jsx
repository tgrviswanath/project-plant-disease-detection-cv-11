import React from "react";
import { Container } from "@mui/material";
import Header from "./components/Header";
import PlantPage from "./pages/PlantPage";

export default function App() {
  return (
    <>
      <Header />
      <Container maxWidth="md" sx={{ py: 4 }}><PlantPage /></Container>
    </>
  );
}
