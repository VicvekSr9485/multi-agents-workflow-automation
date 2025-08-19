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
            # Check if we have meaningful content
            meaningful_results = [r for r in research_results if r.get("fetched_text_length", 0) > 500]
            
            if len(meaningful_results) == 0:
                # All results are login walls or have minimal content
                analysis_summary = self._create_limited_content_summary(research_results)
            else:
                # Generate summaries for each meaningful result
                summaries = []
                for result in meaningful_results:
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
            analysis_tables = self._generate_tables(research_results, meaningful_results)
            
            result = {
                "analysis_summary": analysis_summary,
                "analysis_tables": analysis_tables
            }
            
            log_agent_end("AnalysisAgent", start_time, result)
            return result
            
        except Exception as e:
            log_agent_end("AnalysisAgent", start_time, None)
            raise Exception(f"Analysis failed: {str(e)}")
    
    def _create_limited_content_summary(self, research_results: List[Dict[str, Any]]) -> str:
        """Create a summary when content is limited due to login walls."""
        # Count how many results have meaningful content
        meaningful_count = sum(1 for r in research_results if r.get("fetched_text_length", 0) > 500)
        
        # Create a summary based on the limited content
        summary = f"""
        Analysis of the research topic was significantly limited by content accessibility issues. 
        Out of {len(research_results)} sources examined, only {meaningful_count} contained accessible content 
        suitable for analysis. The remaining sources were behind login walls or contained minimal content. 
        This limitation prevented a comprehensive analysis of the research topic. Recommendations include 
        exploring alternative sources or implementing authenticated access methods for future research.
        """
        
        return summary
    
    def _generate_tables(self, research_results: List[Dict[str, Any]], meaningful_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate data tables from research results."""
        tables = {}
        
        # Table 1: Research results overview
        overview_data = []
        for result in research_results:
            content_status = "Accessible" if result.get("fetched_text_length", 0) > 500 else "Limited/Behind Login"
            overview_data.append({
                "Title": result["title"],
                "URL": result["url"],
                "Content Length": result.get("fetched_text_length", 0),
                "Content Status": content_status,
                "Snippet": result["snippet"][:100] + "..." if len(result["snippet"]) > 100 else result["snippet"]
            })
        
        tables["research_overview"] = overview_data
        
        # Table 2: Keyword frequency (only from meaningful results)
        if meaningful_results:
            all_text = " ".join([r["content_preview"] for r in meaningful_results if r["content_preview"]])
            words = re.findall(r'\b[a-zA-Z]{3,}\b', all_text.lower())
            word_freq = Counter(words).most_common(10)
            
            tables["keyword_frequency"] = [{"Keyword": word, "Count": count} for word, count in word_freq]
        else:
            tables["keyword_frequency"] = [{"Keyword": "N/A", "Count": 0}]
        
        # Table 3: Source summaries (only from meaningful results)
        if meaningful_results:
            tables["source_summaries"] = meaningful_results
        else:
            tables["source_summaries"] = []
        
        return tables