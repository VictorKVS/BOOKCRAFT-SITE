import { Navigate, Route, Routes } from "react-router-dom";
import AppShell from "./components/AppShell.jsx";
import HomePage from "./pages/HomePage.jsx";
import CreatePage from "./pages/CreatePage.jsx";
import MailingPage from "./pages/MailingPage.jsx";
import PodcastPage from "./pages/PodcastPage.jsx";
import VideoAvatarPage from "./pages/VideoAvatarPage.jsx";
import ImagesPage from "./pages/ImagesPage.jsx";
import AnalyticsPage from "./pages/AnalyticsPage.jsx";
import FeaturesPage from "./pages/FeaturesPage.jsx";
import ExamplesPage from "./pages/ExamplesPage.jsx";
import PricingPage from "./pages/PricingPage.jsx";
import BlogPage from "./pages/BlogPage.jsx";
import StudioPage from "./pages/StudioPage.jsx";
import SearchPage from "./pages/SearchPage.jsx";
import LoginPage from "./pages/LoginPage.jsx";
import BooksPage from "./pages/BooksPage.jsx";
import ScriptsPage from "./pages/ScriptsPage.jsx";

export default function App() {
  return (
    <Routes>
      <Route element={<AppShell />}>
        <Route path="/" element={<HomePage />} />
        <Route path="/create" element={<CreatePage />} />
        <Route path="/mailing" element={<MailingPage />} />
        <Route path="/podcast" element={<PodcastPage />} />
        <Route path="/video-avatar" element={<VideoAvatarPage />} />
        <Route path="/images" element={<ImagesPage />} />
        <Route path="/analytics" element={<AnalyticsPage />} />
        <Route path="/books" element={<BooksPage />} />
        <Route path="/scripts" element={<ScriptsPage />} />
        <Route path="/features" element={<FeaturesPage />} />
        <Route path="/examples" element={<ExamplesPage />} />
        <Route path="/pricing" element={<PricingPage />} />
        <Route path="/blog" element={<BlogPage />} />
        <Route path="/studio" element={<StudioPage />} />
        <Route path="/search" element={<SearchPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  );
}
