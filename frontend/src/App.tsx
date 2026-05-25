import { BrowserRouter, Routes, Route } from "react-router-dom";
import { MainLayout } from "@/components/layout/MainLayout";
import HomePage from "@/pages/HomePage";
import SearchPage from "@/pages/SearchPage";
import CatalogPage from "@/pages/CatalogPage";
import CutterDetailPage from "@/pages/CutterDetailPage";
import ComparePage from "@/pages/ComparePage";
import RecommendationPage from "@/pages/RecommendationPage";
import ScenarioPage from "@/pages/ScenarioPage";
import QAPage from "@/pages/QAPage";
import GCodePage from "@/pages/GCodePage";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<MainLayout />}>
          <Route path="/" element={<HomePage />} />
          <Route path="/search" element={<SearchPage />} />
          <Route path="/catalog" element={<CatalogPage />} />
          <Route path="/cutter/:id" element={<CutterDetailPage />} />
          <Route path="/compare" element={<ComparePage />} />
          <Route path="/recommend" element={<RecommendationPage />} />
          <Route path="/scenario" element={<ScenarioPage />} />
          <Route path="/qa" element={<QAPage />} />
          <Route path="/gcode" element={<GCodePage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
