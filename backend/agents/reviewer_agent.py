from typing import Dict
from services.gemini_service import GeminiService
from logger import log_agent_start, log_agent_end
import json
import re
import ast

class ReviewerAgent:
    def __init__(self):
        self.gemini_service = GeminiService()
        self.reviewer_tool = self.gemini_service.create_reviewer_tool()
    
    def review_report(self, draft_report: str) -> Dict[str, str]:
        """
        Always returns:
        {
          "final_report": str,
          "review_notes": str
        }
        """
        start_time = log_agent_start("ReviewerAgent", {})
        try:
            # Create a more robust prompt with explicit formatting instructions
            prompt = (
                "You are a professional copy editor. Your task is to improve the draft report for clarity, "
                "grammar, and presentation without changing any facts. Keep the structure and length similar.\n\n"
                "IMPORTANT: Respond with ONLY a valid JSON object. Do not include any explanations or text outside the JSON.\n\n"
                "JSON schema:\n"
                '{\n'
                '  "final_report": "<polished report>",\n'
                '  "review_notes": "<max 80 words describing the changes made>"\n'
                '}\n\n'
                f"Draft report:\n{draft_report}"
            )
            
            # Get the raw response
            raw_response = self.reviewer_tool.func(prompt)
            
            # Debug preview
            print("=== RAW REVIEWER RESPONSE ===")
            print(str(raw_response)[:500])
            print("================================")
            
            # Normalize the response
            data = self._normalize_response(raw_response, draft_report)
            log_agent_end("ReviewerAgent", start_time, data)
            return data
            
        except Exception as e:
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
        # If it's already a dict with the right keys, use it
        if isinstance(raw, dict) and "final_report" in raw and "review_notes" in raw:
            return {
                "final_report": raw["final_report"].strip(),
                "review_notes": raw["review_notes"].strip()
            }
        
        # Convert to string if not already
        if not isinstance(raw, str):
            raw = str(raw)
        
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
        except Exception:
            pass
        
        # extract JSON from the response
        json_str = self._extract_json(raw)
        
        if json_str:
            try:
                # parse as JSON
                data = json.loads(json_str)
                if isinstance(data, dict) and "final_report" in data and "review_notes" in data:
                    return {
                        "final_report": data["final_report"].strip(),
                        "review_notes": data["review_notes"].strip()
                    }
            except json.JSONDecodeError:
                pass
        
        # If all parsing fails, extract content manually
        return self._manual_extraction(raw, draft_report)
    
    def _extract_json(self, text: str) -> str:
        """Extract JSON object from text."""
        # Look for JSON object pattern
        json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
        matches = re.findall(json_pattern, text, re.DOTALL)
        
        if matches:
            # Return the largest match (likely a complete JSON)
            return max(matches, key=len)
        
        return ""
    
    def _manual_extraction(self, raw: str, draft_report: str) -> Dict[str, str]:
        """Manually extract final_report and review_notes from text."""
        # find the final_report section
        final_report_match = re.search(r'["\']?final_report["\']?\s*:\s*["\']([^"\']*)["\']', raw, re.DOTALL)
        
        # find the review_notes section
        review_notes_match = re.search(r'["\']?review_notes["\']?\s*:\s*["\']([^"\']*)["\']', raw, re.DOTALL)
        
        # Extract values or use defaults
        final_report = final_report_match.group(1).strip() if final_report_match else draft_report
        review_notes = review_notes_match.group(1).strip() if review_notes_match else "Reviewer returned invalid format; using draft."
        
        return {
            "final_report": final_report,
            "review_notes": review_notes
        }