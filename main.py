from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import os
import uuid
import asyncio
from typing import Optional

from crewai import Crew, Process
from agents import doctor, verifier, nutritionist, exercise_specialist
from task import help_patients, nutrition_analysis, exercise_planning, verification
from database import get_db, create_analysis, get_analysis_by_id, update_analysis_status
from workers import process_blood_analysis, parallel_analysis
from celery_app import celery_app

app = FastAPI(title="Blood Test Report Analyser", version="2.0.0")

def run_crew_sync(query: str, file_path: str="data/sample.pdf"):
    """Synchronous crew execution (for backward compatibility)"""
    medical_crew = Crew(
        agents=[doctor, verifier, nutritionist, exercise_specialist],
        tasks=[help_patients, nutrition_analysis, exercise_planning, verification],
        process=Process.sequential,
    )
    
    result = medical_crew.kickoff({
        'query': query,
        'file_path': file_path
    })
    return result

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Blood Test Report Analyser API is running",
        "version": "2.0.0",
        "features": ["async_processing", "database_storage", "concurrent_analysis"]
    }

@app.get("/health")
async def health_check():
    """Comprehensive health check including Celery and database"""
    health_status = {
        "api": "healthy",
        "celery": "unknown",
        "database": "unknown"
    }
    
    # Check Celery status
    try:
        i = celery_app.control.inspect()
        stats = i.stats()
        if stats:
            health_status["celery"] = "healthy"
        else:
            health_status["celery"] = "no_workers"
    except Exception as e:
        health_status["celery"] = f"error: {str(e)}"
    
    # Check database status
    try:
        db = next(get_db())
        db.execute("SELECT 1")
        health_status["database"] = "healthy"
        db.close()
    except Exception as e:
        health_status["database"] = f"error: {str(e)}"
    
    return health_status

@app.post("/analyze")
async def analyze_blood_report(
    file: UploadFile = File(...),
    query: str = Form(default="Summarise my Blood Test Report"),
    user_id: Optional[str] = Form(default=None),
    parallel: bool = Form(default=False),
    db: Session = Depends(get_db)
):
    """Analyze blood test report and provide comprehensive health recommendations"""
    
    # Generate unique filename to avoid conflicts
    file_id = str(uuid.uuid4())
    file_path = f"data/blood_test_report_{file_id}.pdf"
    
    try:
        # Ensure data directory exists
        os.makedirs("data", exist_ok=True)
        
        # Save uploaded file
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Validate query
        if query == "" or query is None:
            query = "Summarise my Blood Test Report"
        
        # Create analysis record in database
        analysis = create_analysis(
            db=db,
            original_filename=file.filename,
            file_path=file_path,
            query=query.strip(),
            user_id=user_id
        )
        
        # Start async processing
        if parallel:
            # Use parallel processing
            task = parallel_analysis.delay(analysis.analysis_id, file_path, query.strip())
        else:
            # Use sequential processing
            task = process_blood_analysis.delay(analysis.analysis_id, file_path, query.strip())
        
        return {
            "status": "processing",
            "analysis_id": analysis.analysis_id,
            "task_id": task.id,
            "message": "Analysis started successfully. Use /status/{analysis_id} to check progress.",
            "query": query,
            "file_processed": file.filename
        }
        
    except Exception as e:
        # Clean up file if it was created
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except:
                pass
        
        raise HTTPException(status_code=500, detail=f"Error processing blood report: {str(e)}")

@app.post("/analyze/sync")
async def analyze_blood_report_sync(
    file: UploadFile = File(...),
    query: str = Form(default="Summarise my Blood Test Report")
):
    """Synchronous analysis (legacy endpoint)"""
    
    # Generate unique filename to avoid conflicts
    file_id = str(uuid.uuid4())
    file_path = f"data/blood_test_report_{file_id}.pdf"
    
    try:
        # Ensure data directory exists
        os.makedirs("data", exist_ok=True)
        
        # Save uploaded file
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Validate query
        if query == "" or query is None:
            query = "Summarise my Blood Test Report"
            
        # Process the blood report synchronously
        response = run_crew_sync(query=query.strip(), file_path=file_path)
        
        return {
            "status": "success",
            "query": query,
            "analysis": str(response),
            "file_processed": file.filename
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing blood report: {str(e)}")
    
    finally:
        # Clean up uploaded file
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except:
                pass

@app.get("/status/{analysis_id}")
async def get_analysis_status(analysis_id: str, db: Session = Depends(get_db)):
    """Get analysis status and results"""
    
    analysis = get_analysis_by_id(db, analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    return {
        "analysis_id": analysis.analysis_id,
        "status": analysis.status,
        "progress": analysis.progress,
        "query": analysis.query,
        "original_filename": analysis.original_filename,
        "created_at": analysis.created_at,
        "started_at": analysis.started_at,
        "completed_at": analysis.completed_at,
        "error_message": analysis.error_message,
        "results": {
            "doctor": analysis.doctor_analysis,
            "verifier": analysis.verifier_analysis,
            "nutritionist": analysis.nutritionist_analysis,
            "exercise": analysis.exercise_analysis
        } if analysis.status == "completed" else None
    }

@app.get("/task/{task_id}")
async def get_task_status(task_id: str):
    """Get Celery task status"""
    
    task_result = celery_app.AsyncResult(task_id)
    
    return {
        "task_id": task_id,
        "status": task_result.status,
        "result": task_result.result if task_result.ready() else None,
        "info": task_result.info if hasattr(task_result, 'info') else None,
        "traceback": task_result.traceback if task_result.failed() else None
    }

@app.get("/analyses")
async def list_analyses(
    limit: int = 10,
    offset: int = 0,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List all analyses with optional filtering"""
    
    from models import BloodTestAnalysis
    
    query = db.query(BloodTestAnalysis)
    
    if status:
        query = query.filter(BloodTestAnalysis.status == status)
    
    analyses = query.order_by(BloodTestAnalysis.created_at.desc()).offset(offset).limit(limit).all()
    
    return {
        "analyses": [
            {
                "analysis_id": analysis.analysis_id,
                "status": analysis.status,
                "progress": analysis.progress,
                "query": analysis.query,
                "original_filename": analysis.original_filename,
                "created_at": analysis.created_at,
                "completed_at": analysis.completed_at
            }
            for analysis in analyses
        ],
        "total": query.count(),
        "limit": limit,
        "offset": offset
    }

@app.delete("/analysis/{analysis_id}")
async def delete_analysis(analysis_id: str, db: Session = Depends(get_db)):
    """Delete an analysis and its associated file"""
    
    analysis = get_analysis_by_id(db, analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    try:
        # Delete the file
        if os.path.exists(analysis.file_path):
            os.remove(analysis.file_path)
        
        # Delete from database
        db.delete(analysis)
        db.commit()
        
        return {"message": "Analysis deleted successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting analysis: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)