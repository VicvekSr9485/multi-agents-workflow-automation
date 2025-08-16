import pandas as pd
from typing import Dict, Any, List
from collections import Counter
import re
from services.gemini_service import GeminiService
from logger import log_agent_start, log_agent_end

class AnalysisAgent:
    def __init__(self):
        self.gemini_service = GeminiService()
    
    def analyze(self, research_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze research results and generate summaries and data tables.
        
        Args:
            research_results: List of research results from ResearchAgent
            
        Returns:
            Dictionary with analysis summary and tables
        """
        start_time = log_agent_start("AnalysisAgent", {"num_results": len(research_results)})
        
        try:
            # Generate summaries for each result
            summaries = []
            for result in research_results:
                if result["fetched_text_length"] > 0:
                    # Create a summary prompt
                    prompt = f"""
                    Summarize the following content in 2-3 sentences, focusing on key points related to the research topic:
                    
                    Title: {result["title"]}
                    URL: {result["url"]}
                    Content: {result["content_preview"]}
                    """
                    
                    summary = self.gemini_service.generate_text(prompt)
                    summaries.append({
                        "url": result["url"],
                        "title": result["title"],
                        "summary": summary
                    })
            
            # Combine all summaries into an overall analysis summary
            combined_summaries = "\n\n".join([f"{s['title']}: {s['summary']}" for s in summaries])
            
            analysis_prompt = f"""
            Based on the following summarized research findings, provide a comprehensive analysis summary that identifies key trends, patterns, and insights:
            
            {combined_summaries}
            """
            
            analysis_summary = self.gemini_service.generate_text(analysis_prompt)
            
            # Generate data tables
            analysis_tables = self._generate_tables(research_results, summaries)
            
            result = {
                "analysis_summary": analysis_summary,
                "analysis_tables": analysis_tables
            }
            
            log_agent_end("AnalysisAgent", start_time, result)
            return result
            
        except Exception as e:
            log_agent_end("AnalysisAgent", start_time, None)
            raise Exception(f"Analysis failed: {str(e)}")
    
    def _generate_tables(self, research_results: List[Dict[str, Any]], summaries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate data tables from research results."""
        tables = {}
        
        # Table 1: Research results overview
        overview_data = []
        for result in research_results:
            overview_data.append({
                "Title": result["title"],
                "URL": result["url"],
                "Content Length": result["fetched_text_length"],
                "Snippet": result["snippet"][:100] + "..." if len(result["snippet"]) > 100 else result["snippet"]
            })
        
        tables["research_overview"] = overview_data
        
        # Table 2: Keyword frequency
        all_text = " ".join([r["content_preview"] for r in research_results if r["content_preview"]])
        words = re.findall(r'\b[a-zA-Z]{3,}\b', all_text.lower())
        word_freq = Counter(words).most_common(10)
        
        tables["keyword_frequency"] = [{"Keyword": word, "Count": count} for word, count in word_freq]
        
        # Table 3: Summary of sources
        tables["source_summaries"] = summaries
        
        return tables