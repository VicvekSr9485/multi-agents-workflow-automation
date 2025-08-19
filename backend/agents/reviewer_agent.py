from typing import Dict
from services.gemini_service import GeminiService
from logger import log_agent_start, log_agent_end
from datetime import datetime

class ReviewerAgent:
    def __init__(self):
        self.gemini_service = GeminiService()
    
    def review_report(self, draft_report: str) -> Dict[str, str]:
        """
        Always returns:
        {
          "final_report": str,
          "review_notes": str
        }
        """
        # Log the draft report length for debugging
        print(f"=== DRAFT REPORT LENGTH === {len(draft_report)} characters")
        
        # Get current date
        current_date = datetime.now().strftime("%B %d, %Y")
        
        start_time = log_agent_start("ReviewerAgent", {"draft_report_length": len(draft_report)})
        try:
            # Create a simpler prompt that doesn't require JSON
            prompt = (
                "You are a professional copy editor. Review the following report for clarity, grammar, and professionalism.\n\n"
                "Requirements:\n"
                "- Maintain a professional, formal tone throughout\n"
                "- Remove any conversational openings or phrases\n"
                "- Ensure consistent formatting and structure\n"
                "- Check for proper grammar and punctuation\n"
                "- Improve readability while preserving all factual content\n"
                "- Ensure the report uses the current date: " + current_date + "\n\n"
                "Please provide your response in two parts:\n"
                "1. IMPROVED REPORT: [Your improved version of the report]\n"
                "2. REVIEW NOTES: [Brief notes on the changes made]\n\n"
                f"Report to review:\n{draft_report}"
            )
            
            # Get the raw response directly from the Gemini service
            raw_response = self.gemini_service.generate_text(prompt)
            
            # Debug preview
            print("=== RAW REVIEWER RESPONSE ===")
            print(str(raw_response)[:500])
            print("================================")
            
            # Parse the response using a simpler approach
            data = self._parse_simple_response(raw_response, draft_report)
            log_agent_end("ReviewerAgent", start_time, data)
            return data
            
        except Exception as e:
            print(f"=== REVIEWER AGENT ERROR === {str(e)}")
            fallback = {
                "final_report": draft_report,
                "review_notes": f"Reviewer error; returned draft. Reason: {str(e)}"
            }
            log_agent_end("ReviewerAgent", start_time, fallback)
            return fallback
    
    def _parse_simple_response(self, response: str, draft_report: str) -> Dict[str, str]:
        """Parse a simple response with two parts."""
        # Split the response into two parts
        parts = response.split("REVIEW NOTES:")
        
        if len(parts) < 2:
            # If we can't split properly, try alternative splitting
            parts = response.split("2.")
        
        if len(parts) < 2:
            # If still can't split, return draft
            return {
                "final_report": draft_report,
                "review_notes": "Could not parse review response; using draft."
            }
        
        # Extract the improved report (remove the "IMPROVED REPORT:" prefix if present)
        improved_report = parts[0].replace("IMROVED REPORT:", "").strip()
        
        # Extract the review notes
        review_notes = parts[1].strip()
        
        # If the improved report is empty, use the draft
        if not improved_report:
            improved_report = draft_report
            review_notes = f"{review_notes} (No improved report provided, using draft)"
        
        return {
            "final_report": improved_report,
            "review_notes": review_notes[:200]  # Limit to 200 characters
        }