import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from '@/components/layout/Layout';
import DashboardOverview from '@/pages/DashboardOverview';
import YouTubeInsights from '@/pages/YouTubeInsights';
import InstagramStoryboard from '@/pages/InstagramStoryboard';
import PredictiveIntelligence from '@/pages/PredictiveIntelligence';
import SentimentReport from '@/pages/SentimentReport';
import { CreatorProvider } from '@/context/CreatorContext';

function App() {
  return (
    <CreatorProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Layout />}>
            <Route index element={<DashboardOverview />} />
            <Route path="youtube" element={<YouTubeInsights />} />
            <Route path="instagram" element={<InstagramStoryboard />} />
            <Route path="predictions" element={<PredictiveIntelligence />} />
            <Route path="sentiment" element={<SentimentReport />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </CreatorProvider>
  );
}

export default App;
