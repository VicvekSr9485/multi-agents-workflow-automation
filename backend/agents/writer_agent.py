from typing import Dict, Any
from services.gemini_service import GeminiService
from logger import log_agent_start, log_agent_end
from datetime import datetime

class WriterAgent:
    def __init__(self):
        self.gemini_service = GeminiService()
    
    def write_report(self, analysis_data: Dict[str, Any], report_style: str = "concise") -> str:
        """
        Generate a draft report based on analysis data.
        
        Args:
            analysis_data: Output from AnalysisAgent
            report_style: Style of the report (concise, detailed, academic)
            
        Returns:
            Draft report text
        """
        start_time = log_agent_start("WriterAgent", {"report_style": report_style})
        
        try:
            # Get current date
            current_date = datetime.now().strftime("%B %d, %Y")
            
            # Format analysis data for the writer
            analysis_summary = analysis_data.get("analysis_summary", "")
            research_overview = analysis_data.get("analysis_tables", {}).get("research_overview", [])
            keyword_frequency = analysis_data.get("analysis_tables", {}).get("keyword_frequency", [])
            source_summaries = analysis_data.get("analysis_tables", {}).get("source_summaries", [])
            
            # Create a direct prompt with the actual analysis data
            prompt = f"""
            Generate a professional business report in a {report_style} style based on the provided analysis data.
            
            Analysis Summary:
            {analysis_summary}
            
            Research Overview:
            {self._format_data_for_prompt(research_overview)}
            
            Keyword Frequency:
            {self._format_data_for_prompt(keyword_frequency)}
            
            Source Summaries:
            {self._format_data_for_prompt(source_summaries)}
            
            The report must include the following sections:
            1. Executive Summary
            2. Key Findings
            3. Data Tables (present the research overview and keyword frequency as markdown tables)
            4. Recommendations
            5. Sources
            
            Requirements:
            - Begin directly with the report title and date without any introductory phrases
            - Use the current date: {current_date}
            - Maintain a professional, formal tone throughout
            - Use clear, concise language
            - Structure content with appropriate headings and subheadings
            - Present data in well-formatted tables using markdown table syntax
            - Ensure all recommendations are actionable and specific
            - Include all sources with proper citations
            - Do not include conversational openings such as "Of course," "Certainly," or similar phrases
            - Avoid excessive markdown symbols (like multiple # or *) - use minimal formatting for clarity
            - Return ONLY the report content, nothing else
            """
            
            # Generate the report directly
            draft_report = self.gemini_service.generate_text(prompt)
            
            # If the generated report is empty or too short, create one using the actual analysis data
            if not draft_report or len(draft_report.strip()) < 100:
                print("=== GENERATED REPORT WAS EMPTY, CREATING FROM ANALYSIS DATA ===")
                draft_report = self._create_report_from_analysis(
                    analysis_summary, 
                    research_overview, 
                    keyword_frequency, 
                    source_summaries, 
                    current_date
                )
            
            log_agent_end("WriterAgent", start_time, draft_report)
            return draft_report
            
        except Exception as e:
            log_agent_end("WriterAgent", start_time, None)
            raise Exception(f"Report writing failed: {str(e)}")
    
    def _format_data_for_prompt(self, data):
        """Format data for inclusion in the prompt."""
        if not data:
            return "No data available"
        
        if isinstance(data, list):
            # Format list of dictionaries
            result = []
            for item in data:
                if isinstance(item, dict):
                    result.append(", ".join([f"{k}: {v}" for k, v in item.items()]))
                else:
                    result.append(str(item))
            return "\n".join(result)
        
        return str(data)
    
    def _create_report_from_analysis(self, analysis_summary, research_overview, keyword_frequency, source_summaries, current_date):
        """Create a report using the analysis data when the generated report is empty."""
        
        # Format tables
        research_table = self._format_table(research_overview)
        keyword_table = self._format_table(keyword_frequency)
        
        # Create a report using the actual analysis data
        report = f"""# AI Research Report
**Date:** {current_date}

## Executive Summary
{analysis_summary}

## Key Findings
Based on the analysis of current trends in artificial intelligence, several key patterns have emerged that are shaping the industry landscape.

## Data Tables

### Research Overview
{research_table}

### Keyword Frequency
{keyword_table}

## Recommendations
Organizations should stay informed about AI developments and consider how these technologies might impact their operations. Strategic investments in AI capabilities should align with business objectives and market opportunities.

## Sources
Research data was gathered from multiple sources including technology publications and industry reports.
"""
        
        return report
    
    def _format_table(self, table_data):
        """Format table data as markdown."""
        if not table_data or len(table_data) == 0:
            return "No data available"
        
        # Extract headers from first row
        if isinstance(table_data, list) and len(table_data) > 0:
            if isinstance(table_data[0], dict):
                headers = list(table_data[0].keys())
                
                # Create markdown table
                markdown = "| " + " | ".join(headers) + " |\n"
                markdown += "|" + "|".join(["---" for _ in headers]) + "|\n"
                
                for row in table_data:
                    row_values = [str(row.get(header, "")) for header in headers]
                    markdown += "| " + " | ".join(row_values) + " |\n"
                
                return markdown
        return str(table_data)