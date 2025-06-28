"""
Celery workers for blood test analysis
Handles concurrent processing of analysis tasks
"""

import os
import uuid
from datetime import datetime
from celery import current_task
from celery_app import celery_app
from database import SessionLocal, update_analysis_status, update_analysis_result
from agents import doctor, verifier, nutritionist, exercise_specialist
from task import help_patients, nutrition_analysis, exercise_planning, verification
from crewai import Crew, Process

@celery_app.task(bind=True, name="workers.process_blood_analysis")
def process_blood_analysis(self, analysis_id: str, file_path: str, query: str):
    """
    Main worker task for processing blood test analysis
    Coordinates all agent tasks and updates progress
    """
    db = SessionLocal()
    
    try:
        # Update status to processing
        update_analysis_status(db, analysis_id, "processing", 0.0)
        
        # Create crew with all agents
        medical_crew = Crew(
            agents=[doctor, verifier, nutritionist, exercise_specialist],
            tasks=[help_patients, nutrition_analysis, exercise_planning, verification],
            process=Process.sequential,
        )
        
        # Process with crew
        result = medical_crew.kickoff({
            'query': query,
            'file_path': file_path
        })
        
        # Update progress to 100%
        update_analysis_status(db, analysis_id, "completed", 1.0)
        
        return {
            "status": "success",
            "analysis_id": analysis_id,
            "result": str(result)
        }
        
    except Exception as e:
        # Update status to failed
        update_analysis_status(db, analysis_id, "failed", error_message=str(e))
        
        # Re-raise exception for Celery
        raise
        
    finally:
        db.close()

@celery_app.task(bind=True, name="workers.doctor_analysis")
def doctor_analysis(self, analysis_id: str, file_path: str, query: str):
    """
    Doctor agent analysis task
    """
    db = SessionLocal()
    
    try:
        # Update task status
        current_task.update_state(
            state="PROGRESS",
            meta={"current": 0, "total": 1, "status": "Doctor analyzing..."}
        )
        
        # Run doctor analysis
        doctor_crew = Crew(
            agents=[doctor],
            tasks=[help_patients],
            process=Process.sequential,
        )
        
        result = doctor_crew.kickoff({
            'query': query,
            'file_path': file_path
        })
        
        # Update database with result
        update_analysis_result(db, analysis_id, "doctor", str(result))
        
        # Update progress
        current_task.update_state(
            state="PROGRESS",
            meta={"current": 1, "total": 4, "status": "Doctor analysis completed"}
        )
        
        return {
            "status": "success",
            "agent": "doctor",
            "result": str(result)
        }
        
    except Exception as e:
        update_analysis_result(db, analysis_id, "doctor", f"Error: {str(e)}")
        raise
        
    finally:
        db.close()

@celery_app.task(bind=True, name="workers.verifier_analysis")
def verifier_analysis(self, analysis_id: str, file_path: str, query: str):
    """
    Verifier agent analysis task
    """
    db = SessionLocal()
    
    try:
        current_task.update_state(
            state="PROGRESS",
            meta={"current": 1, "total": 4, "status": "Verifier analyzing..."}
        )
        
        verifier_crew = Crew(
            agents=[verifier],
            tasks=[verification],
            process=Process.sequential,
        )
        
        result = verifier_crew.kickoff({
            'query': query,
            'file_path': file_path
        })
        
        update_analysis_result(db, analysis_id, "verifier", str(result))
        
        current_task.update_state(
            state="PROGRESS",
            meta={"current": 2, "total": 4, "status": "Verifier analysis completed"}
        )
        
        return {
            "status": "success",
            "agent": "verifier",
            "result": str(result)
        }
        
    except Exception as e:
        update_analysis_result(db, analysis_id, "verifier", f"Error: {str(e)}")
        raise
        
    finally:
        db.close()

@celery_app.task(bind=True, name="workers.nutritionist_analysis")
def nutritionist_analysis(self, analysis_id: str, file_path: str, query: str):
    """
    Nutritionist agent analysis task
    """
    db = SessionLocal()
    
    try:
        current_task.update_state(
            state="PROGRESS",
            meta={"current": 2, "total": 4, "status": "Nutritionist analyzing..."}
        )
        
        nutritionist_crew = Crew(
            agents=[nutritionist],
            tasks=[nutrition_analysis],
            process=Process.sequential,
        )
        
        result = nutritionist_crew.kickoff({
            'query': query,
            'file_path': file_path
        })
        
        update_analysis_result(db, analysis_id, "nutritionist", str(result))
        
        current_task.update_state(
            state="PROGRESS",
            meta={"current": 3, "total": 4, "status": "Nutritionist analysis completed"}
        )
        
        return {
            "status": "success",
            "agent": "nutritionist",
            "result": str(result)
        }
        
    except Exception as e:
        update_analysis_result(db, analysis_id, "nutritionist", f"Error: {str(e)}")
        raise
        
    finally:
        db.close()

@celery_app.task(bind=True, name="workers.exercise_analysis")
def exercise_analysis(self, analysis_id: str, file_path: str, query: str):
    """
    Exercise specialist analysis task
    """
    db = SessionLocal()
    
    try:
        current_task.update_state(
            state="PROGRESS",
            meta={"current": 3, "total": 4, "status": "Exercise specialist analyzing..."}
        )
        
        exercise_crew = Crew(
            agents=[exercise_specialist],
            tasks=[exercise_planning],
            process=Process.sequential,
        )
        
        result = exercise_crew.kickoff({
            'query': query,
            'file_path': file_path
        })
        
        update_analysis_result(db, analysis_id, "exercise", str(result))
        
        current_task.update_state(
            state="SUCCESS",
            meta={"current": 4, "total": 4, "status": "Exercise analysis completed"}
        )
        
        return {
            "status": "success",
            "agent": "exercise",
            "result": str(result)
        }
        
    except Exception as e:
        update_analysis_result(db, analysis_id, "exercise", f"Error: {str(e)}")
        raise
        
    finally:
        db.close()

@celery_app.task(bind=True, name="workers.parallel_analysis")
def parallel_analysis(self, analysis_id: str, file_path: str, query: str):
    """
    Parallel analysis using all agents simultaneously
    """
    db = SessionLocal()
    
    try:
        # Update status to processing
        update_analysis_status(db, analysis_id, "processing", 0.0)
        
        # Start all analysis tasks in parallel
        tasks = [
            doctor_analysis.delay(analysis_id, file_path, query),
            verifier_analysis.delay(analysis_id, file_path, query),
            nutritionist_analysis.delay(analysis_id, file_path, query),
            exercise_analysis.delay(analysis_id, file_path, query)
        ]
        
        # Wait for all tasks to complete
        results = []
        for i, task in enumerate(tasks):
            try:
                result = task.get(timeout=300)  # 5 minute timeout per task
                results.append(result)
                
                # Update progress
                progress = (i + 1) / len(tasks)
                update_analysis_status(db, analysis_id, "processing", progress)
                
            except Exception as e:
                results.append({"status": "failed", "error": str(e)})
        
        # Check if all tasks completed successfully
        all_success = all(r.get("status") == "success" for r in results)
        
        if all_success:
            update_analysis_status(db, analysis_id, "completed", 1.0)
        else:
            update_analysis_status(db, analysis_id, "failed", error_message="Some analysis tasks failed")
        
        return {
            "status": "success" if all_success else "failed",
            "analysis_id": analysis_id,
            "results": results
        }
        
    except Exception as e:
        update_analysis_status(db, analysis_id, "failed", error_message=str(e))
        raise
        
    finally:
        db.close()

# Task status monitoring
@celery_app.task(name="workers.monitor_task_status")
def monitor_task_status(task_id: str):
    """
    Monitor task status and update database
    """
    task_result = celery_app.AsyncResult(task_id)
    
    return {
        "task_id": task_id,
        "status": task_result.status,
        "result": task_result.result if task_result.ready() else None,
        "info": task_result.info if hasattr(task_result, 'info') else None
    } 