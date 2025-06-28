#!/usr/bin/env python3
"""
Celery worker startup script
Starts workers for processing blood test analysis tasks
"""

import os
import sys
import subprocess
from celery_app import celery_app

def start_worker():
    """Start Celery worker"""
    print("🚀 Starting Celery Worker for Blood Test Analyser...")
    
    # Worker configuration
    worker_args = [
        "celery", "-A", "celery_app", "worker",
        "--loglevel=info",
        "--concurrency=2",  # Number of worker processes
        "--queues=blood_analysis",
        "--hostname=blood_worker@%h",
        "--max-tasks-per-child=1000",
        "--time-limit=600",  # 10 minutes
        "--soft-time-limit=300"  # 5 minutes
    ]
    
    try:
        print("📋 Worker Configuration:")
        print(f"   Concurrency: 2 workers")
        print(f"   Queue: blood_analysis")
        print(f"   Time limit: 10 minutes")
        print(f"   Soft time limit: 5 minutes")
        print(f"   Max tasks per child: 1000")
        print("\n🔄 Starting worker...")
        
        # Start the worker
        subprocess.run(worker_args)
        
    except KeyboardInterrupt:
        print("\n⏹️  Worker stopped by user")
    except Exception as e:
        print(f"❌ Error starting worker: {e}")
        sys.exit(1)

def start_beat():
    """Start Celery beat scheduler (for periodic tasks)"""
    print("⏰ Starting Celery Beat Scheduler...")
    
    beat_args = [
        "celery", "-A", "celery_app", "beat",
        "--loglevel=info",
        "--scheduler=celery.beat.PersistentScheduler"
    ]
    
    try:
        subprocess.run(beat_args)
    except KeyboardInterrupt:
        print("\n⏹️  Beat scheduler stopped by user")
    except Exception as e:
        print(f"❌ Error starting beat scheduler: {e}")
        sys.exit(1)

def start_monitor():
    """Start Celery monitor (Flower)"""
    print("📊 Starting Celery Monitor (Flower)...")
    
    monitor_args = [
        "celery", "-A", "celery_app", "flower",
        "--port=5555",
        "--broker=redis://localhost:6379/0"
    ]
    
    try:
        subprocess.run(monitor_args)
    except KeyboardInterrupt:
        print("\n⏹️  Monitor stopped by user")
    except Exception as e:
        print(f"❌ Error starting monitor: {e}")
        sys.exit(1)

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Start Celery components")
    parser.add_argument("component", choices=["worker", "beat", "monitor"], 
                       help="Component to start")
    
    args = parser.parse_args()
    
    if args.component == "worker":
        start_worker()
    elif args.component == "beat":
        start_beat()
    elif args.component == "monitor":
        start_monitor()

if __name__ == "__main__":
    main() 