from fastapi import APIRouter, HTTPException
from schemas.request import ResearchRequest
from schemas.response import ResearchResponse
from agents.research_agent import ResearchAgent
from agents.analysis_agent import AnalysisAgent
from agents.writer_agent import WriterAgent
from agents.reviewer_agent import ReviewerAgent
import time, traceback

router = APIRouter()

@router.post("/research", response_model=ResearchResponse)
async def research_topic(request: ResearchRequest):
    """
    Research a topic and generate a comprehensive report.
    
    Args:
        request: Research request with topic, number of results, and report style
        
    Returns:
        Research response with all agent outputs
    """
    start_time = time.time()
    agent_logs = {}

    print("📌 Incoming request payload:", request.dict())

    try:
        # Initialize agents
        print("🔹 Initializing agents...")
        research_agent = ResearchAgent()
        analysis_agent = AnalysisAgent()
        writer_agent = WriterAgent()
        reviewer_agent = ReviewerAgent()
        print("✅ Agents initialized")

        # Step 1: Research
        print("🔍 Running ResearchAgent...")
        research_results = research_agent.research(request.topic, request.num_results)
        print(f"✅ Research completed. Results found: {len(research_results)}")
        agent_logs["research"] = {
            "status": "completed",
            "results_count": len(research_results)
        }

        # Step 2: Analysis
        print("📊 Running AnalysisAgent...")
        analysis_output = analysis_agent.analyze(research_results)
        print("✅ Analysis completed")
        agent_logs["analysis"] = {
            "status": "completed",
            "summary_length": len(analysis_output.get("analysis_summary", "")),
            "tables_count": len(analysis_output.get("analysis_tables", []))
        }

        # Step 3: Writing
        print("📝 Running WriterAgent...")
        draft_report = writer_agent.write_report(analysis_output, request.report_style)
        print(f"✅ Draft report generated. Length: {len(draft_report)} characters")
        agent_logs["writer"] = {
            "status": "completed",
            "draft_length": len(draft_report)
        }

        # Step 4: Review
        print("🔎 Running ReviewerAgent...")
        review_output = reviewer_agent.review_report(draft_report)
        print("✅ Review completed")
        agent_logs["reviewer"] = {
            "status": "completed",
            "final_report_length": len(review_output.get("final_report", "")),
            "review_notes_length": len(review_output.get("review_notes", ""))
        }

        # Calculate total processing time
        processing_time = time.time() - start_time
        print(f"⏱️ Total processing time: {processing_time:.2f} seconds")

        # Return the complete response
        return ResearchResponse(
            research_results=research_results,
            analysis_summary=analysis_output["analysis_summary"],
            analysis_tables=analysis_output["analysis_tables"],
            draft_report=draft_report,
            final_report=review_output["final_report"],
            review_notes=review_output["review_notes"],
            processing_time=processing_time,
            agent_logs=agent_logs
        )

    except Exception as e:
        print("❌ ERROR in /research route:", str(e))
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Research process failed: {str(e)}")
