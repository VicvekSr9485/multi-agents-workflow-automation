from typing import Dict, Any
from services.gemini_service import GeminiService
from logger import log_agent_start, log_agent_end
from datetime import datetime

class WriterAgent:
    def __init__(self):
        self.gemini_service = GeminiService()
        self.writer_tool = self.gemini_service.create_writer_tool()
    
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
            # Format analysis data for the writer
            analysis_text = f"""
            Analysis Summary:
            {analysis_data["analysis_summary"]}
            
            Analysis Tables:
            - Research Overview: {analysis_data["analysis_tables"]["research_overview"]}
            - Keyword Frequency: {analysis_data["analysis_tables"]["keyword_frequency"]}
            - Source Summaries: {analysis_data["analysis_tables"]["source_summaries"]}
            """
            
            # Get current date
            current_date = datetime.now().strftime("%B %d, %Y")
            
            # Create a more professional prompt
            prompt = f"""
            Generate a professional business report in a {report_style} style based on the provided analysis data.
            
            Analysis Data:
            {analysis_text}
            
            The report must include the following sections:
            1. Executive Summary
            2. Key Findings
            3. Data Tables
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
            """
            
            # Use the writer tool to generate the report
            draft_report = self.writer_tool.func(analysis_text, report_style, current_date)
            
            log_agent_end("WriterAgent", start_time, draft_report)
            return draft_report
            
        except Exception as e:
            log_agent_end("WriterAgent", start_time, None)
            raise Exception(f"Report writing failed: {str(e)}")