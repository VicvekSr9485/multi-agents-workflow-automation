import React, { useState } from 'react';
import TopicInput from '../components/TopicInput';
import ReportViewer from '../components/ReportViewer';
import type { ResearchRequest, ResearchResponse } from '../api';
import { researchApi } from '../api';

const Home: React.FC = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [researchData, setResearchData] = useState<ResearchResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleGenerate = async (topic: string, numResults: number, reportStyle: string) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const request: ResearchRequest = {
        topic,
        num_results: numResults,
        report_style: reportStyle
      };
      
      const response = await researchApi.generateReport(request);
      setResearchData(response);
    } catch (err) {
      setError('Failed to generate report. Please try again.');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4">
        <header className="text-center mb-10">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Product Research & Report Generator</h1>
          <p className="text-gray-600">
            Enter a research topic to generate a comprehensive business report
          </p>
        </header>

        <main>
          <TopicInput onGenerate={handleGenerate} isLoading={isLoading} />
          
          {error && (
            <div className="mt-6 p-4 bg-red-50 text-red-700 rounded-md">
              {error}
            </div>
          )}
          
          {isLoading && (
            <div className="mt-6 p-6 bg-white rounded-lg shadow-md">
              <div className="flex items-center justify-center">
                <div className="text-center">
                  <svg className="animate-spin h-12 w-12 text-blue-600 mx-auto" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  <p className="mt-4 text-gray-600">Researching and analyzing your topic...</p>
                  <p className="text-sm text-gray-500 mt-2">This may take a minute or two</p>
                </div>
              </div>
            </div>
          )}
          
          {researchData && (
            <div className="mt-8">
              <div className="mb-4 flex justify-between items-center">
                <h2 className="text-xl font-bold text-gray-800">Research Report</h2>
                {researchData.processing_time && (
                  <span className="text-sm text-gray-500">
                    Generated in {researchData.processing_time.toFixed(2)} seconds
                  </span>
                )}
              </div>
              
              <ReportViewer
                researchResults={researchData.research_results}
                analysisSummary={researchData.analysis_summary}
                analysisTables={researchData.analysis_tables}
                draftReport={researchData.draft_report}
                finalReport={researchData.final_report}
                reviewNotes={researchData.review_notes}
              />
            </div>
          )}
        </main>
        
        <footer className="mt-12 pt-6 border-t border-gray-200 text-center text-gray-500 text-sm">
          <p>Product Research & Report Generator © {new Date().getFullYear()}</p>
        </footer>
      </div>
    </div>
  );
};

export default Home;