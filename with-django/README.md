# E-Recruitment Platform

A comprehensive recruitment platform leveraging advanced algorithms including Analytic Hierarchy Process (AHP) and Genetic Algorithms for optimal candidate selection and team formation.

## Overview

This platform connects employers with job seekers, offering sophisticated tools for resume analysis, candidate evaluation, and intelligent hiring decision support. The system employs natural language processing for CV data extraction and implements multi-criteria decision-making algorithms to rank candidates.

## Key Features

- **User Management**: Separate registration and dashboards for employers and job seekers
- **Job Management**: Create, update, and view job listings with detailed criteria
- **Application Processing**: Submit and process job applications with CV uploads
- **Intelligent CV Analysis**: Automated extraction of candidate data from PDF resumes
- **Multi-criteria Evaluation**: AHP-based candidate ranking with consistency checks
- **Team Optimization**: Genetic algorithm for optimal team composition
- **Customizable Criteria**: Add, delete, and prioritize job criteria

## Technologies & Libraries

### Backend
- **Django 5.2**: Web framework for rapid development and clean, pragmatic design
- **NumPy**: Scientific computing library used for matrix operations in AHP algorithm
- **Celery**: Distributed task queue for handling asynchronous processing
- **Redis**: Message broker for Celery and caching system
- **PyPDF**: Library for reading and extracting text from PDF files
- **Google Gemini API**: LLM for intelligent CV data extraction and analysis

### Frontend
- **Tailwind CSS**: Utility-first CSS framework for custom designs
- **Alpine.js**: Lightweight JavaScript framework for component behavior
- **HTMX**: Library for AJAX, CSS Transitions, WebSockets without writing JavaScript
- **Django Templates**: Server-side template system

### Data Science & Algorithms
- **AHP (Analytic Hierarchy Process)**: Multi-criteria decision-making algorithm for candidate ranking
- **Genetic Algorithm**: Evolutionary optimization for team selection
- **Natural Language Processing**: For CV data extraction and skill matching
- **Matplotlib**: For data visualization and analytics

### DevOps
- **Docker & Docker Compose**: Container platform for consistent development and deployment
- **SQLite**: Lightweight database for development
- **PostgreSQL**: Robust relational database for production

## Installation & Setup

### Using Docker (Recommended)

1. Make sure you have Docker and Docker Compose installed on your system.

2. Clone the repository:
   ```bash
   git clone <repository-url>
   cd m2-projetsbse-erecruitement-cmr/with-django
   ```

3. Create a `.env` file with the following environment variables:
   ```
   DEBUG=True
   SECRET_KEY=your_secret_key_here
   GOOGLE_API_KEY=your_gemini_api_key_here
   ```

4. Start the Docker containers:
   ```bash
   docker-compose up
   ```

5. Access the application at `http://localhost:8000`

### Manual Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd m2-projetsbse-erecruitement-cmr/with-django
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv env
   source env/bin/activate  # On Windows: env\Scripts\activate
   ```

3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up the database:
   ```bash
   python manage.py migrate
   ```

5. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```

6. Create test users (optional):
   ```bash
   python manage.py create_test_users
   ```

7. Start the development server:
   ```bash
   python manage.py runserver
   ```

8. In a separate terminal, start Redis and Celery (required for CV processing):
   ```bash
   # Start Redis (install if not available)
   redis-server

   # Start Celery worker
   celery -A backend worker -l info
   ```

9. Access the application at `http://localhost:8000`

## Usage Flow

### For Employers:

1. Register as an employer
2. Create a job listing with detailed requirements
3. Add custom criteria for the job
4. Set up priority weights using the AHP matrix
5. Review applications and process candidate CVs
6. View ranked candidates based on criteria
7. Use the genetic algorithm to optimize team selection

### For Job Seekers:

1. Register as a job seeker
2. Browse available job listings
3. Apply for jobs by uploading CV
4. Track application status from dashboard

## Project Structure

- `backend/`: Main project settings and configuration
- `users/`: User authentication and profile management
- `jobs/`: Job listing, criteria management, and candidate evaluation
- `applications/`: Application submission and processing
- `templates/`: HTML templates
- `media/`: Uploaded files like CVs
- `static/`: Static assets

## API Documentation

The system includes several API endpoints for processing applications and retrieving candidate data. Examples:

- `GET /jobs/{id}/processing-status/`: Check CV processing status
- `POST /jobs/{id}/rank-candidates/`: Run AHP ranking algorithm
- `GET /jobs/{id}/genetic-team/`: Run genetic algorithm for team selection

## License

This project is licensed under the MIT License - see the LICENSE file for details.
