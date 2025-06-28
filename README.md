# 🩸 Blood Test Report Analyser v2.0

A comprehensive AI-powered blood test analysis system built with CrewAI that provides detailed health insights, nutrition recommendations, and exercise planning based on blood test reports. **Now with concurrent processing, database storage, and scalable architecture!**

## 🚀 New in v2.0

- **⚡ Concurrent Processing**: Handle multiple requests simultaneously with Celery
- **🗄️ Database Storage**: Persistent storage with SQLite/PostgreSQL
- **📊 Real-time Progress**: Track analysis progress in real-time
- **🔍 Task Monitoring**: Monitor and manage background tasks
- **🔄 Parallel Processing**: Run agents in parallel for faster results
- **📈 Scalable Architecture**: Add more workers for increased throughput

## 📋 Table of Contents

- Overview
- Architecture
- Bugs Found and Fixed
- Setup and Installation
- Usage Instructions
- API Documentation
- Tech Stack
- Project Structure
- Contributing

## 🎯 Overview

The Blood Test Report Analyser is an intelligent system that leverages multiple AI agents to provide comprehensive analysis of blood test reports. The system uses a crew of specialized agents:

- **Doctor Agent**: Provides medical analysis and health recommendations
- **Verifier Agent**: Validates and verifies blood test reports
- **Nutritionist Agent**: Offers nutrition and supplement recommendations
- **Exercise Specialist Agent**: Creates personalized exercise plans

### Key Features

- 🔍 **PDF Report Analysis**: Automatically extracts and processes blood test data from PDF files
- 🤖 **Multi-Agent AI**: Uses specialized CrewAI agents for different aspects of health analysis
- 💊 **Comprehensive Recommendations**: Provides medical, nutritional, and fitness advice
- 🔒 **Secure File Handling**: Temporary file storage with automatic cleanup
- 🌐 **RESTful API**: Easy integration with web and mobile applications
- ⚡ **Async Processing**: Non-blocking request handling with background processing
- 📊 **Progress Tracking**: Real-time status updates and progress monitoring
- 🗄️ **Data Persistence**: Store analysis results and user metadata
- 🔄 **Parallel Processing**: Run multiple agents simultaneously for faster results

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FastAPI App   │    │   Celery        │    │   Database      │
│   (Web Server)  │───▶│   Workers       │───▶│   (SQLite/PG)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │
         │                       │
         ▼                       ▼
┌─────────────────┐    ┌─────────────────┐
│   Redis Broker  │    │   File Storage  │
│   (Message Q)   │    │   (PDF Files)   │
└─────────────────┘    └─────────────────┘
```

### System Components

1. **FastAPI Application**: Handles HTTP requests and manages file uploads
2. **Celery Workers**: Process analysis tasks in the background
3. **Redis Broker**: Message queue for task distribution
4. **Database**: Stores analysis results and user metadata
5. **File Storage**: Temporary storage for uploaded PDF files

## 🐛 Bugs Found and Fixed

During the code review, I identified and fixed **10 critical bugs** that were preventing the application from running:

### 1. **Missing LLM Configuration** 
- **Issue**: `llm` variable was undefined, causing `NameError`
- **Fix**: Added proper OpenAI LLM configuration with environment variable support
- **Impact**: Critical runtime error that prevented application startup

### 2. **Missing PDFLoader Import**
- **Issue**: `PDFLoader` class used but not imported
- **Fix**: Added `from langchain_community.document_loaders import PyPDFLoader`
- **Impact**: PDF reading functionality would fail completely

### 3. **Incorrect Tool Structure for CrewAI**
- **Issue**: Tools weren't properly structured for CrewAI integration
- **Fix**: Restructured `BloodTestReportTool` to inherit from `BaseTool`
- **Impact**: Tools wouldn't be recognized by CrewAI agents

### 4. **Async/Sync Method Mismatch**
- **Issue**: Tools defined as async but used synchronously
- **Fix**: Converted all tool methods to synchronous `_run()` methods
- **Impact**: Runtime errors when calling async methods synchronously

### 5. **Incomplete Crew Configuration**
- **Issue**: Only one agent included in crew instead of all four
- **Fix**: Added all agents (`doctor`, `verifier`, `nutritionist`, `exercise_specialist`) to crew
- **Impact**: Only one agent would work, others ignored

### 6. **Missing Agent Imports**
- **Issue**: Tasks referenced unimported agents
- **Fix**: Added missing agent imports in `task.py`
- **Impact**: `ImportError` when trying to use unimported agents

### 7. **Incorrect Tool Usage in Tasks**
- **Issue**: Tasks used `BloodTestReportTool.read_data_tool` incorrectly
- **Fix**: Updated to use `BloodTestReportTool()` instance
- **Impact**: Tasks wouldn't have access to PDF reading functionality

### 8. **Missing Dependencies**
- **Issue**: Required packages not in requirements.txt
- **Fix**: Added `langchain_openai`, `langchain_community`, `python-dotenv`, `uvicorn`
- **Impact**: Import errors and missing functionality

### 9. **Missing File Path Context**
- **Issue**: File path not passed to crew context
- **Fix**: Added `file_path` to crew kickoff context
- **Impact**: Tasks wouldn't know which file to process

### 10. **Incorrect Agent Assignment in Tasks**
- **Issue**: All tasks assigned to same agent instead of specialized agents
- **Fix**: Assigned each task to its appropriate specialized agent
- **Impact**: Loss of specialization and expertise

For detailed bug fix information, see [BUG_FIXES_SUMMARY.md](./BUG_FIXES_SUMMARY.md).

## 🚀 Setup and Installation

### Prerequisites

- Python 3.8 or higher
- OpenAI API key
- Redis server (for Celery)
- Git (for cloning)

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd blood-test-analyser-debug
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your configuration:
   # - OPENAI_API_KEY=your_openai_api_key_here
   # - DATABASE_URL=sqlite:///./blood_test_analyser.db
   # - CELERY_BROKER_URL=redis://localhost:6379/0
   ```

4. **Initialize database**
   ```bash
   python init_db.py
   ```

5. **Start Redis server**
   ```bash
   # On Windows (with WSL or Docker)
   redis-server
   
   # On macOS
   brew services start redis
   
   # On Linux
   sudo systemctl start redis
   ```

6. **Start Celery worker** (in a new terminal)
   ```bash
   python start_worker.py worker
   ```

7. **Start the application** (in another terminal)
   ```bash
   python main.py
   ```

8. **Verify installation**
   ```bash
   curl http://localhost:8000/health
   ```

## 📖 Usage Instructions

### Running the Application

1. **Start all components**
   ```bash
   # Terminal 1: Start Redis
   redis-server
   
   # Terminal 2: Start Celery worker
   python start_worker.py worker
   
   # Terminal 3: Start FastAPI app
   python main.py
   ```

2. **Access the API**
   - Health check: `http://localhost:8000/`
   - API documentation: `http://localhost:8000/docs`
   - Celery monitor: `http://localhost:5555` (optional)

### Using the API

#### Submit Analysis (Async - Recommended)
```bash
curl -X POST "http://localhost:8000/analyze" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@path/to/your/blood_test.pdf" \
  -F "query=Analyze my blood test results and provide health recommendations" \
  -F "parallel=true"
```

#### Check Analysis Status
```bash
curl "http://localhost:8000/status/{analysis_id}"
```

#### Submit Analysis (Sync - Legacy)
```bash
curl -X POST "http://localhost:8000/analyze/sync" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@path/to/your/blood_test.pdf" \
  -F "query=Analyze my blood test results"
```

## 📚 API Documentation

### Base URL
```
http://localhost:8000
```

### Endpoints

#### 1. Health Check
**GET** `/`

Returns the health status of the API.

**Response:**
```json
{
  "message": "Blood Test Report Analyser API is running",
  "version": "2.0.0",
  "features": ["async_processing", "database_storage", "concurrent_analysis"]
}
```

#### 2. Comprehensive Health Check
**GET** `/health`

Returns health status of all system components.

**Response:**
```json
{
  "api": "healthy",
  "celery": "healthy",
  "database": "healthy"
}
```

#### 3. Analyze Blood Test Report (Async)
**POST** `/analyze`

Analyzes a blood test report PDF asynchronously and returns immediately with a task ID.

**Parameters:**
- `file` (required): PDF file containing blood test report
- `query` (optional): Specific analysis request (default: "Summarise my Blood Test Report")
- `user_id` (optional): User identifier for tracking
- `parallel` (optional): Use parallel processing (default: false)

**Request Example:**
```bash
curl -X POST "http://localhost:8000/analyze" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@blood_test_report.pdf" \
  -F "query=What are the key health indicators in my blood test?" \
  -F "parallel=true"
```

**Response Example:**
```json
{
  "status": "processing",
  "analysis_id": "550e8400-e29b-41d4-a716-446655440000",
  "task_id": "12345678-1234-1234-1234-123456789012",
  "message": "Analysis started successfully. Use /status/{analysis_id} to check progress.",
  "query": "What are the key health indicators in my blood test?",
  "file_processed": "blood_test_report.pdf"
}
```

#### 4. Get Analysis Status
**GET** `/status/{analysis_id}`

Get the current status and results of an analysis.

**Response Example:**
```json
{
  "analysis_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "progress": 1.0,
  "query": "What are the key health indicators in my blood test?",
  "original_filename": "blood_test_report.pdf",
  "created_at": "2024-01-15T10:30:00Z",
  "started_at": "2024-01-15T10:30:05Z",
  "completed_at": "2024-01-15T10:35:00Z",
  "error_message": null,
  "results": {
    "doctor": "Based on your blood test results...",
    "verifier": "I have verified your blood test report...",
    "nutritionist": "Here are my nutrition recommendations...",
    "exercise": "Here's your personalized exercise plan..."
  }
}
```

#### 5. Get Task Status
**GET** `/task/{task_id}`

Get the status of a Celery task.

**Response:**
```json
{
  "task_id": "12345678-1234-1234-1234-123456789012",
  "status": "SUCCESS",
  "result": {"status": "success", "analysis_id": "..."},
  "info": null,
  "traceback": null
}
```

#### 6. List Analyses
**GET** `/analyses`

List all analyses with optional filtering.

**Parameters:**
- `limit` (optional): Number of results to return (default: 10)
- `offset` (optional): Number of results to skip (default: 0)
- `status` (optional): Filter by status (pending, processing, completed, failed)

**Response:**
```json
{
  "analyses": [
    {
      "analysis_id": "550e8400-e29b-41d4-a716-446655440000",
      "status": "completed",
      "progress": 1.0,
      "query": "Analyze my blood test results",
      "original_filename": "blood_test.pdf",
      "created_at": "2024-01-15T10:30:00Z",
      "completed_at": "2024-01-15T10:35:00Z"
    }
  ],
  "total": 1,
  "limit": 10,
  "offset": 0
}
```

#### 7. Delete Analysis
**DELETE** `/analysis/{analysis_id}`

Delete an analysis and its associated file.

**Response:**
```json
{
  "message": "Analysis deleted successfully"
}
```

#### 8. Analyze Blood Test Report (Sync - Legacy)
**POST** `/analyze/sync`

Synchronous analysis endpoint (legacy compatibility).

**Response:**
```json
{
  "status": "success",
  "query": "Analyze my blood test results",
  "analysis": "Based on your blood test results...",
  "file_processed": "blood_test.pdf"
}
```

### Sample Blood Test Report Format

The system accepts standard PDF blood test reports. Sample reports are included in the `data/` directory:
- `sample.pdf` - Example blood test report
- `blood_test_report.pdf` - Additional sample report

## 🛠 Tech Stack

### Core Technologies
- **Python 3.8+** - Primary programming language
- **FastAPI** - Modern, fast web framework for building APIs
- **CrewAI** - Multi-agent AI framework for complex task orchestration
- **LangChain** - Framework for developing applications with LLMs

### AI/ML Components
- **OpenAI GPT-3.5-turbo** - Large Language Model for analysis
- **LangChain OpenAI** - OpenAI integration for LangChain
- **LangChain Community** - Community tools and integrations

### PDF Processing
- **PyPDFLoader** - PDF text extraction and processing
- **LangChain Document Loaders** - Document processing utilities

### Concurrent Processing
- **Celery** - Distributed task queue for background processing
- **Redis** - Message broker and result backend for Celery
- **Flower** - Web-based monitoring tool for Celery

### Database & Storage
- **SQLAlchemy** - SQL toolkit and Object-Relational Mapping
- **SQLite** - Lightweight database (default)
- **PostgreSQL** - Advanced database (optional)
- **Alembic** - Database migration tool

### Development & Deployment
- **Uvicorn** - ASGI server for FastAPI
- **Python-dotenv** - Environment variable management
- **Pydantic** - Data validation and settings management

### Dependencies Overview
```
crewai==0.130.0          # Multi-agent AI framework
fastapi==0.110.3         # Web framework
celery==5.3.4            # Distributed task queue
redis==5.0.1             # Message broker
sqlalchemy==2.0.23       # Database ORM
langchain_openai==0.1.0  # OpenAI integration
langchain_community==0.0.20  # Community tools
uvicorn==0.27.1          # ASGI server
python-dotenv==1.0.0     # Environment management
```

## 📁 Project Structure

```
blood-test-analyser-debug/
├── main.py                 # FastAPI application and endpoints
├── models.py              # SQLAlchemy database models
├── database.py            # Database configuration and utilities
├── celery_app.py          # Celery configuration
├── workers.py             # Celery worker tasks
├── init_db.py             # Database initialization script
├── start_worker.py        # Celery worker startup script
├── agents.py              # CrewAI agent definitions
├── tools.py               # Custom tools for PDF processing
├── task.py                # Task definitions for agents
├── requirements.txt       # Python dependencies
├── env.example            # Environment configuration template
├── README.md             # Project documentation
├── BUG_FIXES_SUMMARY.md  # Detailed bug fix documentation
├── UPGRADE_GUIDE.md      # System upgrade documentation
├── data/                 # Sample PDF files
│   ├── sample.pdf
│   └── blood_test_report.pdf
└── outputs/              # Generated outputs (if any)
```

## 🔍 Monitoring & Debugging

### Celery Flower (Web UI)
- URL: http://localhost:5555
- Monitor tasks, workers, and queues
- View task history and results

### Health Check Endpoint
```bash
curl http://localhost:8000/health
```

### Database Inspection
```python
from database import SessionLocal
from models import BloodTestAnalysis

db = SessionLocal()
analyses = db.query(BloodTestAnalysis).all()
for analysis in analyses:
    print(f"ID: {analysis.analysis_id}, Status: {analysis.status}")
```

## ⚡ Performance Benefits

### Before vs After
| Metric | Before (v1.0) | After (v2.0) |
|--------|---------------|--------------|
| **Concurrent Requests** | 1 | Unlimited |
| **Response Time** | 30-60 seconds | Immediate |
| **Scalability** | Single instance | Multiple workers |
| **Reliability** | No persistence | Database storage |
| **Monitoring** | None | Full observability |

### Scalability Features
- **Horizontal Scaling**: Add more Celery workers
- **Load Balancing**: Redis distributes tasks
- **Fault Tolerance**: Failed tasks can be retried
- **Progress Tracking**: Real-time status updates
- **Resource Management**: Configurable time limits

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 style guidelines
- Add tests for new features
- Update documentation for API changes
- Ensure all agents and tools are properly configured
- Test with both SQLite and PostgreSQL databases

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
1. Check the [BUG_FIXES_SUMMARY.md](./BUG_FIXES_SUMMARY.md) for common issues
2. Review the [UPGRADE_GUIDE.md](./UPGRADE_GUIDE.md) for system details
3. Review the API documentation at `http://localhost:8000/docs`
4. Open an issue in the repository

## 📈 Roadmap

### Planned Features
- [ ] User authentication and authorization
- [ ] API rate limiting
- [ ] Webhook notifications
- [ ] Batch processing
- [ ] Advanced analytics dashboard
- [ ] Multi-language support
- [ ] PDF report generation
- [ ] Email notifications

### Scalability Improvements
- [ ] Kubernetes deployment
- [ ] Auto-scaling workers
- [ ] CDN integration
- [ ] Database sharding
- [ ] Caching layer

## Contact

For any questions, please contact Aditya Nikam at adityanikam9502@gmail.com.

---

**Note**: This application is for educational and demonstration purposes. Always consult with healthcare professionals for medical advice based on blood test results.
