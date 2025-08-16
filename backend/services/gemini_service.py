import os
from typing import Dict, Any, List
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage
from langchain.tools import Tool

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
        def write_report(analysis_data: str, report_style: str, current_date: str) -> str:
            prompt = f"""
            Generate a professional business report in a {report_style} style based on the provided analysis data.
            
            Analysis Data:
            {analysis_data}
            
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
            return self.generate_text(prompt)
        
        return Tool(
            name="report_writer",
            description="Writes a professional business report based on analysis data",
            func=write_report
        )
    
    def create_reviewer_tool(self) -> Tool:
        """Create a tool for the reviewer agent."""
        def review_report(draft_report: str) -> Dict[str, str]:
            from datetime import datetime
            current_date = datetime.now().strftime("%B %d, %Y")
            
            prompt = (
                "You are a professional copy editor. Your task is to improve the draft report for clarity, "
                "grammar, and presentation without changing any facts. Keep the structure and length similar.\n\n"
                "Requirements:\n"
                "- Maintain a professional, formal tone throughout\n"
                "- Remove any conversational openings or phrases\n"
                "- Ensure consistent formatting and structure\n"
                "- Check for proper grammar and punctuation\n"
                "- Improve readability while preserving all factual content\n"
                "- Ensure headings and subheadings are properly formatted with minimal markdown symbols\n"
                "- Verify that tables are correctly formatted using markdown table syntax\n"
                "- Remove excessive markdown symbols (like multiple # or *)\n"
                "- Ensure the report uses the current date: " + current_date + "\n\n"
                "IMPORTANT: Respond with ONLY a valid JSON object. Do not include any explanations or text outside the JSON.\n\n"
                "JSON schema:\n"
                '{\n'
                '  "final_report": "<polished report>",\n'
                '  "review_notes": "<max 80 words describing the changes made>"\n'
                '}\n\n'
                f"Draft report:\n{draft_report}"
            )
            response = self.generate_text(prompt)
            
            # Try to parse as JSON
            try:
                import json
                result = json.loads(response)
                return result
            except:
                # Fallback if response is not properly formatted
                return {
                    "final_report": "Error: Could not parse the review response.",
                    "review_notes": "The reviewer agent returned an invalid response format."
                }
        
        return Tool(
            name="report_reviewer",
            description="Reviews and improves a draft report",
            func=review_report
        )