import os
from typing import Dict, Any, List
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage
from langchain.tools import Tool
from langchain.agents import AgentType, initialize_agent

class GeminiService:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")
        
        self.model = ChatGoogleGenerativeAI(
            model="gemini-2.5-pro",
            google_api_key=self.api_key,
            temperature=0.2,
            convert_system_message_to_human=True
        )
    
    def generate_text(self, prompt: str) -> str:
        """
        Generate text using Gemini model.
        
        Args:
            prompt: Input prompt
            
        Returns:
            Generated text response
        """
        try:
            response = self.model.invoke([HumanMessage(content=prompt)])
            return response.content
        except Exception as e:
            raise Exception(f"Gemini API call failed: {str(e)}")
    
    def create_writer_tool(self) -> Tool:
        """Create a tool for the writer agent."""
        def write_report(analysis_data: str, report_style: str) -> str:
            prompt = f"""
            Based on the following analysis data, generate a professional business report in a {report_style} style.
            
            Analysis Data:
            {analysis_data}
            
            The report should include the following sections:
            1. Executive Summary
            2. Key Findings
            3. Data Tables
            4. Recommendations
            5. Sources
            
            Format the report with clear headings and well-structured paragraphs.
            """
            return self.generate_text(prompt)
        
        return Tool(
            name="report_writer",
            description="Writes a professional business report based on analysis data",
            func=write_report
        )
    
    def create_reviewer_tool(self) -> Tool:
        """Create a tool for the reviewer agent."""
        def review_report(draft_report: str) -> Dict[str, str]:
            prompt = f"""
            Review the following draft report for clarity, tone, and conciseness. 
            Provide an improved version of the report and notes on the changes made.
            
            Draft Report:
            {draft_report}
            
            Return your response as a JSON object with two keys:
            1. "final_report": The improved version of the report
            2. "review_notes": Notes on the changes made and why
            """
            response = self.generate_text(prompt)
            
            # Try to parse as JSON, but handle cases where it's not properly formatted
            try:
                import json
                result = json.loads(response)
                return result
            except:
                # Fallback if response is not valid JSON
                return {
                    "final_report": "Error: Could not parse the review response.",
                    "review_notes": "The reviewer agent returned an invalid response format."
                }
        
        return Tool(
            name="report_reviewer",
            description="Reviews and improves a draft report",
            func=review_report
        )