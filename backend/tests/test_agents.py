import pytest
from unittest.mock import Mock, patch
from agents.research_agent import ResearchAgent
from agents.analysis_agent import AnalysisAgent
from agents.writer_agent import WriterAgent
from agents.reviewer_agent import ReviewerAgent

class TestResearchAgent:
    @patch('agents.research_agent.SerpApiService')
    @patch('agents.research_agent.ContentFetcher')
    def test_research(self, mock_fetcher, mock_serp):
        # Setup mocks
        mock_serp.return_value.search.return_value = [
            {
                "title": "Test Result 1",
                "url": "https://example.com/1",
                "snippet": "This is a test snippet",
                "published_date": "2023-01-01",
                "domain": "example.com"
            }
        ]
        
        mock_fetcher.return_value.fetch_content.return_value = {
            "content_preview": "This is a preview of the content",
            "fetched_text": "This is the full content",
            "fetched_text_length": 100
        }
        
        # Test the agent
        agent = ResearchAgent()
        results = agent.research("test topic", 1)
        
        # Assertions
        assert len(results) == 1
        assert results[0]["title"] == "Test Result 1"
        assert results[0]["url"] == "https://example.com/1"
        assert results[0]["snippet"] == "This is a test snippet"
        assert results[0]["content_preview"] == "This is a preview of the content"
        assert results[0]["fetched_text_length"] == 100

class TestAnalysisAgent:
    @patch('agents.analysis_agent.GeminiService')
    def test_analyze(self, mock_gemini):
        # Setup mocks
        mock_gemini.return_value.generate_text.side_effect = [
            "This is a summary of the content",
            "This is an overall analysis summary"
        ]
        
        # Test data
        research_results = [
            {
                "url": "https://example.com/1",
                "title": "Test Result 1",
                "snippet": "This is a test snippet",
                "content_preview": "This is a preview of the content",
                "fetched_text_length": 100
            }
        ]
        
        # Test the agent
        agent = AnalysisAgent()
        result = agent.analyze(research_results)
        
        # Assertions
        assert "analysis_summary" in result
        assert "analysis_tables" in result
        assert result["analysis_summary"] == "This is an overall analysis summary"
        assert "research_overview" in result["analysis_tables"]
        assert "keyword_frequency" in result["analysis_tables"]
        assert "source_summaries" in result["analysis_tables"]

class TestWriterAgent:
    @patch('agents.writer_agent.GeminiService')
    def test_write_report(self, mock_gemini):
        # Setup mocks
        mock_tool = Mock()
        mock_tool.func.return_value = "This is a draft report"
        
        mock_gemini.return_value.create_writer_tool.return_value = mock_tool
        
        # Test data
        analysis_data = {
            "analysis_summary": "This is an analysis summary",
            "analysis_tables": {
                "research_overview": [],
                "keyword_frequency": [],
                "source_summaries": []
            }
        }
        
        # Test the agent
        agent = WriterAgent()
        result = agent.write_report(analysis_data, "concise")
        
        # Assertions
        assert result == "This is a draft report"
        mock_tool.func.assert_called_once()

class TestReviewerAgent:
    @patch('agents.reviewer_agent.GeminiService')
    def test_review_report(self, mock_gemini):
        # Setup mocks
        mock_tool = Mock()
        mock_tool.func.return_value = {
            "final_report": "This is the final report",
            "review_notes": "These are the review notes"
        }
        
        mock_gemini.return_value.create_reviewer_tool.return_value = mock_tool
        
        # Test the agent
        agent = ReviewerAgent()
        result = agent.review_report("This is a draft report")
        
        # Assertions
        assert "final_report" in result
        assert "review_notes" in result
        assert result["final_report"] == "This is the final report"
        assert result["review_notes"] == "These are the review notes"
        mock_tool.func.assert_called_once()