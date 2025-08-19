from typing import Dict
from services.gemini_service import GeminiService
from logger import log_agent_start, log_agent_end
from datetime import datetime
import time
import re

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
            # Check if draft report is empty or too short
            if not draft_report or len(draft_report.strip()) < 100:
                print("=== DRAFT REPORT IS EMPTY OR TOO SHORT ===")
                # Return the draft as-is with a note
                return {
                    "final_report": draft_report,
                    "review_notes": "Draft report was empty or too short for review."
                }
            
            # Create a prompt that explicitly avoids conversational openings
            prompt = f"""
            You are a professional copy editor. Review the following report for clarity, grammar, and professionalism.
            
            Requirements:
            - Maintain a professional, formal tone throughout
            - Remove any conversational openings or phrases like "Of course," "Certainly," etc.
            - Ensure consistent formatting and structure
            - Check for proper grammar and punctuation
            - Improve readability while preserving all factual content
            - Ensure the report uses the current date: {current_date}
            - Begin directly with the report content without any introductory phrases
            
            Please review and improve this report:
            
            {draft_report}
            """
            
            # Get the raw response directly from the Gemini service with retry logic
            raw_response = self._generate_with_retry(prompt)
            
            # Debug preview
            print("=== RAW REVIEWER RESPONSE ===")
            print(str(raw_response)[:500])
            print("================================")
            
            # If we got a valid response, use it as the final report
            if raw_response and len(raw_response.strip()) > 100:
                # Remove any conversational openings that might still be present
                final_report = self._remove_conversational_openings(raw_response)
                
                # Ensure there's exactly one correct date
                final_report = self._ensure_correct_date(final_report, current_date)
                
                # Create a simple review note
                review_notes = "Report reviewed for clarity, grammar, and professionalism. Removed conversational openings and ensured correct date formatting."
                
                return {
                    "final_report": final_report,
                    "review_notes": review_notes
                }
            else:
                # If the response is empty or too short, return the draft
                return {
                    "final_report": draft_report,
                    "review_notes": "Reviewer returned empty response; using draft."
                }
            
        except Exception as e:
            print(f"=== REVIEWER AGENT ERROR === {str(e)}")
            fallback = {
                "final_report": draft_report,
                "review_notes": f"Reviewer error; returned draft. Reason: {str(e)}"
            }
            log_agent_end("ReviewerAgent", start_time, fallback)
            return fallback
    
    def _generate_with_retry(self, prompt, max_retries=3, initial_delay=1):
        """Generate text with retry logic for transient errors."""
        for attempt in range(max_retries):
            try:
                return self.gemini_service.generate_text(prompt)
            except Exception as e:
                if attempt == max_retries - 1:
                    # Last attempt failed, return empty string
                    print(f"=== ALL RETRY ATTEMPTS FAILED === {str(e)}")
                    return ""
                
                # Exponential backoff
                delay = initial_delay * (2 ** attempt)
                print(f"=== RETRY ATTEMPT {attempt + 1}/{max_retries} AFTER {delay}s ===")
                time.sleep(delay)
        
        return ""
    
    def _remove_conversational_openings(self, text: str) -> str:
        """Remove conversational openings from the text."""
        # Common conversational openings to remove
        openings = [
            r"^Of course\.?\s+",
            r"^Certainly\.?\s+",
            r"^Here is\.?\s+",
            r"^This is\.?\s+",
            r"^I have\.?\s+",
            r"^I've\.?\s+",
            r"^Below is\.?\s+",
            r"^Attached is\.?\s+"
        ]
        
        for opening in openings:
            text = re.sub(opening, "", text, flags=re.IGNORECASE | re.MULTILINE)
        
        return text.strip()
    
    def _ensure_correct_date(self, report_text: str, correct_date: str):
        """Ensure the report has exactly one correct date."""
        lines = report_text.split('\n')
        
        # Remove any existing date lines
        filtered_lines = []
        for line in lines:
            # Skip lines that are just date markers
            if line.strip().startswith('**Date:**'):
                continue
            filtered_lines.append(line)
        
        # Find the title (first non-empty line)
        title_line_index = -1
        for i, line in enumerate(filtered_lines):
            if line.strip():
                title_line_index = i
                break
        
        # Insert the date after the title
        if title_line_index >= 0:
            filtered_lines.insert(title_line_index + 1, f"**Date:** {correct_date}")
        else:
            # If no title found, add at the beginning
            filtered_lines.insert(0, f"**Date:** {correct_date}")
        
        # Join the lines back together
        return '\n'.join(filtered_lines)