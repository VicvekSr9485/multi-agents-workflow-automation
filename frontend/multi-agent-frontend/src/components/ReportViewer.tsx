import React, { useState } from 'react';
import { FiCopy, FiDownload } from 'react-icons/fi';
import CollapsiblePanel from './CollapsiblePanel';

interface ReportViewerProps {
  researchResults: any[];
  analysisSummary: string;
  analysisTables: Record<string, any>;
  draftReport: string;
  finalReport: string;
  reviewNotes: string;
}

const ReportViewer: React.FC<ReportViewerProps> = ({
  researchResults,
  analysisSummary,
  analysisTables,
  draftReport,
  finalReport,
  reviewNotes
}) => {
  const [copied, setCopied] = useState(false);

  const copyToClipboard = () => {
    navigator.clipboard.writeText(finalReport);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const downloadAsMarkdown = () => {
    const element = document.createElement('a');
    const file = new Blob([finalReport], { type: 'text/markdown' });
    element.href = URL.createObjectURL(file);
    element.download = 'research-report.md';
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };

  const renderTable = (tableData: any[]) => {
    if (!tableData || tableData.length === 0) return null;
    
    const headers = Object.keys(tableData[0]);
    
    return (
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              {headers.map(header => (
                <th key={header} className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  {header}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {tableData.map((row, index) => (
              <tr key={index}>
                {headers.map(header => (
                  <td key={`${index}-${header}`} className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {header === 'URL' ? (
                      <a href={row[header]} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
                        {row[header]}
                      </a>
                    ) : (
                      row[header]
                    )}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  };

  return (
    <div className="space-y-6">
      {/* Research Results Panel */}
      <CollapsiblePanel title="Research Results" defaultOpen={true}>
        <div className="space-y-4">
          {researchResults.map((result, index) => (
            <div key={index} className="border-l-4 border-blue-500 pl-4 py-2">
              <h4 className="font-medium text-gray-900">
                <a href={result.url} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
                  {result.title}
                </a>
              </h4>
              <p className="text-sm text-gray-600 mt-1">{result.snippet}</p>
              {result.content_preview && (
                <p className="text-sm text-gray-500 mt-2">{result.content_preview}</p>
              )}
              <div className="text-xs text-gray-400 mt-1">
                {result.fetched_text_length && `Content length: ${result.fetched_text_length} characters`}
              </div>
            </div>
          ))}
        </div>
      </CollapsiblePanel>

      {/* Analysis Output Panel */}
      <CollapsiblePanel title="Analysis Output">
        <div className="space-y-4">
          <div>
            <h4 className="font-medium text-gray-900 mb-2">Summary</h4>
            <p className="text-gray-700 whitespace-pre-line">{analysisSummary}</p>
          </div>
          
          {Object.entries(analysisTables).map(([tableName, tableData]) => (
            <div key={tableName}>
              <h4 className="font-medium text-gray-900 mb-2 capitalize">{tableName.replace('_', ' ')}</h4>
              {renderTable(tableData)}
            </div>
          ))}
        </div>
      </CollapsiblePanel>

      {/* Draft Report Panel */}
      <CollapsiblePanel title="Draft Report">
        <div className="prose max-w-none">
          <p className="text-gray-700 whitespace-pre-line">{draftReport}</p>
        </div>
      </CollapsiblePanel>

      {/* Final Report Panel */}
      <CollapsiblePanel title="Final Reviewed Report" defaultOpen={true}>
        <div className="flex justify-end space-x-2 mb-4">
          <button
            onClick={copyToClipboard}
            className="flex items-center px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded hover:bg-gray-200"
          >
            <FiCopy className="mr-1" />
            {copied ? 'Copied!' : 'Copy'}
          </button>
          <button
            onClick={downloadAsMarkdown}
            className="flex items-center px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded hover:bg-gray-200"
          >
            <FiDownload className="mr-1" />
            Download
          </button>
        </div>
        
        <div className="prose max-w-none">
          <div className="text-gray-700 whitespace-pre-line">{finalReport}</div>
        </div>
        
        {reviewNotes && (
          <div className="mt-6 p-4 bg-yellow-50 rounded-md">
            <h4 className="font-medium text-yellow-800 mb-2">Review Notes</h4>
            <p className="text-yellow-700 whitespace-pre-line">{reviewNotes}</p>
          </div>
        )}
      </CollapsiblePanel>
    </div>
  );
};

export default ReportViewer;