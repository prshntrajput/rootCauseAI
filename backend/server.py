"""
FastAPI Backend Server
Bridge between VSCode extension and rootCauseAI
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn

from backend.graph.runner import AgentRunner
from backend.patcher.patcher import SmartPatcher
from backend.graph.state import FixSuggestion


app = FastAPI(title="rootCauseAI Backend", version="1.0.0")

# Enable CORS for VSCode extension
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response Models
class AnalyzeErrorRequest(BaseModel):
    error_log: str
    project_root: str = "."
    provider: str = "gemini"
    max_retries: int = 2


class FixSuggestionResponse(BaseModel):
    file_path: str
    original_snippet: str
    new_snippet: str
    explanation: str
    confidence: float
    line_number: Optional[int] = None


class AnalyzeErrorResponse(BaseModel):
    status: str
    parsed_error: Optional[dict] = None
    root_cause_analysis: Optional[str] = None
    fixes: List[FixSuggestionResponse] = []
    execution_time: float
    tokens_used: int
    error_message: Optional[str] = None


class ApplyFixRequest(BaseModel):
    fix: FixSuggestionResponse
    language: str
    dry_run: bool = False


class ApplyFixResponse(BaseModel):
    success: bool
    message: str
    fix_id: Optional[str] = None


class HistoryResponse(BaseModel):
    fixes: List[dict]
    total: int


class StatsResponse(BaseModel):
    total_fixes: int
    active_fixes: int
    reverted_count: int
    files_modified: int


# Initialize components
agent_runner = None
patcher = SmartPatcher()


@app.get("/")
def root():
    """Health check"""
    return {"status": "running", "service": "rootCauseAI Backend"}


@app.post("/analyze", response_model=AnalyzeErrorResponse)
def analyze_error(request: AnalyzeErrorRequest):
    """Analyze error and generate fix suggestions"""
    try:
        global agent_runner
        agent_runner = AgentRunner(
            provider=request.provider,
            max_retries=request.max_retries,
            project_root=request.project_root
        )
        
        # Run agent
        result = agent_runner.run(request.error_log)
        
        # Convert fixes to response format
        fixes = []
        if result.get("final_fixes"):
            for fix in result["final_fixes"]:
                fixes.append(FixSuggestionResponse(
                    file_path=fix.file_path,
                    original_snippet=fix.original_snippet,
                    new_snippet=fix.new_snippet,
                    explanation=fix.explanation,
                    confidence=fix.confidence,
                    line_number=fix.line_number
                ))
        
        return AnalyzeErrorResponse(
            status=result["status"],
            parsed_error=result["parsed_error"].dict() if result.get("parsed_error") else None,
            root_cause_analysis=result.get("root_cause_analysis"),
            fixes=fixes,
            execution_time=result["execution_time"],
            tokens_used=result.get("tokens_used", 0),
            error_message=result.get("error_message")
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/apply-fix", response_model=ApplyFixResponse)
def apply_fix(request: ApplyFixRequest):
    """Apply a fix to a file"""
    try:
        # Convert to FixSuggestion
        fix = FixSuggestion(**request.fix.dict())
        
        # Apply using patcher
        results = patcher.apply_fixes(
            fixes=[fix],
            language=request.language,
            dry_run=request.dry_run,
            interactive=False
        )
        
        if results["applied"] > 0:
            # Get fix ID from history
            recent_fixes = patcher.applier.history_tracker.get_recent_fixes(1)
            fix_id = recent_fixes[0]["fix_id"] if recent_fixes else None
            
            return ApplyFixResponse(
                success=True,
                message="Fix applied successfully",
                fix_id=fix_id
            )
        else:
            detail = results["details"][0] if results["details"] else {}
            return ApplyFixResponse(
                success=False,
                message=detail.get("message", "Failed to apply fix")
            )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/undo")
def undo_last_fix():
    """Undo the most recent fix"""
    try:
        success, message = patcher.undo_last_fix()
        return {"success": success, "message": message}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/undo/{fix_id}")
def undo_fix(fix_id: str):
    """Undo a specific fix"""
    try:
        success, message = patcher.undo_fix(fix_id)
        return {"success": success, "message": message}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/history", response_model=HistoryResponse)
def get_history(count: int = 10):
    """Get fix history"""
    try:
        fixes = patcher.applier.history_tracker.get_recent_fixes(count)
        return HistoryResponse(fixes=fixes, total=len(fixes))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats", response_model=StatsResponse)
def get_stats():
    """Get fix statistics"""
    try:
        stats = patcher.applier.history_tracker.get_stats()
        return StatsResponse(**stats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    print("🚀 Starting rootCauseAI Backend Server...")
    print("📍 Server running at: http://localhost:8000")
    print("📖 API docs: http://localhost:8000/docs")
    
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        log_level="info"
    )
