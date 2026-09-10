import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import ConsolePage from './pages/ConsolePage';
import ArchitecturePage from './pages/ArchitecturePage';
import IngestionPage from './pages/IngestionPage';
import DataContractsPage from './pages/DataContractsPage';
import RequirementsPage from './pages/RequirementsPage';

export default function App() {
  const [isDemoModalOpen, setIsDemoModalOpen] = useState(false);

  return (
    <Router>
      <Routes>
        <Route 
          path="/" 
          element={
            <ConsolePage 
              onOpenDemoModal={() => setIsDemoModalOpen(true)}
              isDemoModalOpen={isDemoModalOpen}
              setIsDemoModalOpen={setIsDemoModalOpen}
            />
          } 
        />
        <Route 
          path="/architecture" 
          element={<ArchitecturePage onOpenDemoModal={() => setIsDemoModalOpen(true)} />} 
        />
        <Route 
          path="/ingestion" 
          element={<IngestionPage onOpenDemoModal={() => setIsDemoModalOpen(true)} />} 
        />
        <Route 
          path="/data-contracts" 
          element={<DataContractsPage onOpenDemoModal={() => setIsDemoModalOpen(true)} />} 
        />
        <Route 
          path="/requirements" 
          element={<RequirementsPage onOpenDemoModal={() => setIsDemoModalOpen(true)} />} 
        />
      </Routes>
    </Router>
  );
}
