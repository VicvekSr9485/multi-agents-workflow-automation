from typing import Dict
from services.gemini_service import GeminiService
from logger import log_agent_start, log_agent_end
import json
import re
import ast
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
            # Create a more professional prompt
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
            
            # Get the raw response directly from the Gemini service
            raw_response = self.gemini_service.generate_text(prompt)
            
            # Debug preview
            print("=== RAW REVIEWER RESPONSE ===")
            print(str(raw_response)[:500])
            print("================================")
            
            # Normalize the response
            data = self._normalize_response(raw_response, draft_report)
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
    
    def _normalize_response(self, raw, draft_report: str) -> Dict[str, str]:
        """
        Force any raw response into a dict with keys:
        'final_report' and 'review_notes'.
        Fallback to draft if parsing fails.
        """
        # Convert to string if not already
        if not isinstance(raw, str):
            raw = str(raw)
        
        # Check if the response contains error messages
        if "Error: Could not parse the review response" in raw or "The reviewer agent returned an invalid response format" in raw:
            # This is a known error pattern from the model, use the draft report
            print("=== DETECTED ERROR PATTERN IN RESPONSE ===")
            return {
                "final_report": draft_report,
                "review_notes": "Model returned error response; using original draft."
            }
        
        # Try to extract JSON from the response
        json_str = self._extract_json(raw)
        
        if json_str:
            print("=== EXTRACTED JSON STRING ===")
            print(json_str[:200])
            print("==========================")
            
            try:
                # Try to parse as JSON
                data = json.loads(json_str)
                if isinstance(data, dict) and "final_report" in data and "review_notes" in data:
                    return {
                        "final_report": data["final_report"].strip(),
                        "review_notes": data["review_notes"].strip()
                    }
            except json.JSONDecodeError as e:
                print(f"=== JSON PARSE ERROR === {str(e)}")
                pass
        
        # Try to parse as a Python dictionary (handles string representations of dicts)
        try:
            # Remove any leading/trailing whitespace and newlines
            raw = raw.strip()
            
            # If it looks like a dictionary string, try to parse it
            if raw.startswith('{') and raw.endswith('}'):
                try:
                    # First try as JSON (double quotes)
                    data = json.loads(raw)
                    if isinstance(data, dict) and "final_report" in data and "review_notes" in data:
                        return {
                            "final_report": data["final_report"].strip(),
                            "review_notes": data["review_notes"].strip()
                        }
                except json.JSONDecodeError:
                    pass
                
                try:
                    # Then try as Python literal (handles single quotes)
                    data = ast.literal_eval(raw)
                    if isinstance(data, dict) and "final_report" in data and "review_notes" in data:
                        return {
                            "final_report": data["final_report"].strip(),
                            "review_notes": data["review_notes"].strip()
                        }
                except (ValueError, SyntaxError):
                    pass
        except Exception as e:
            print(f"=== DICT PARSE ERROR === {str(e)}")
            pass
        
        # If all parsing fails, try to extract the content manually
        return self._manual_extraction(raw, draft_report)
    
    def _extract_json(self, text: str) -> str:
        """Extract JSON object from text."""
        # Look for JSON object pattern
        json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
        matches = re.findall(json_pattern, text, re.DOTALL)
        
        if matches:
            # Return the largest match (most likely to be the complete JSON)
            return max(matches, key=len)
        
        return ""
    
    def _manual_extraction(self, raw: str, draft_report: str) -> Dict[str, str]:
        """Manually extract final_report and review_notes from text."""
        print("=== ATTEMPTING MANUAL EXTRACTION ===")
        
        # Try to find the final_report section
        final_report_match = re.search(r'["\']?final_report["\']?\s*:\s*["\']([^"\']*)["\']', raw, re.DOTALL)
        
        # Try to find the review_notes section
        review_notes_match = re.search(r'["\']?review_notes["\']?\s*:\s*["\']([^"\']*)["\']', raw, re.DOTALL)
        
        # Extract values or use defaults
        final_report = final_report_match.group(1).strip() if final_report_match else draft_report
        review_notes = review_notes_match.group(1).strip() if review_notes_match else "Reviewer returned invalid format; using draft."
        
        print(f"=== EXTRACTION RESULTS ===")
        print(f"final_report found: {final_report_match is not None}")
        print(f"review_notes found: {review_notes_match is not None}")
        print("========================")
        
        return {
            "final_report": final_report,
            "review_notes": review_notes
        }