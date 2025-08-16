from typing import Dict, Any
from services.gemini_service import GeminiService
from logger import log_agent_start, log_agent_end

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
            
            # Use the writer tool to generate the report
            draft_report = self.writer_tool.func(analysis_text, report_style)
            
            log_agent_end("WriterAgent", start_time, draft_report)
            return draft_report
            
        except Exception as e:
            log_agent_end("WriterAgent", start_time, None)
            raise Exception(f"Report writing failed: {str(e)}")