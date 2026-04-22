# Scholarship Discovery & Recommendation System

## 1. Project Overview
The **Scholarship Discovery & Recommendation System** is a comprehensive platform designed to automate the discovery of scholarships across the web and dynamically match them to students based on their profile. It reduces the manual effort required by students to find and verify their eligibility for financial aid. The system features a modern REST API, an automated web crawler, and an AI-driven document verification and recommendation engine.






## 2. Artificial Intelligence (AI) & intelligent Automation
The core value of this project lies in its intelligent automation and AI components, which solve two major problems in scholarship distribution: **Eligibility Matching** and **Document Verification**.

### 2.1. AI-Powered Document Verification (Computer Vision & NLP)
To streamline the application process and prevent fraud, the system includes an automated **Document Processor (`src/document_processor.py`)**. 
- **Optical Character Recognition (OCR)**: When a user uploads a document (like an Income Certificate or Caste Certificate), the system uses **Tesseract OCR (via `pytesseract`)** and image processing libraries (`Pillow` / `OpenCV`) to visually read and extract raw text from image files.
- **Natural Language Parsing & Heuristics**: Once the text is extracted, the system uses Natural Language Processing (NLP) techniques (regular expressions and keyword heuristics) to autonomously determine the **Document Type** (e.g., "Income Certificate" vs "Education Marksheet").
- **Data Extraction**: The AI extracts key data points directly from the document—such as detecting the exact family income limit (e.g., explicitly finding `Rs. 2,50,000` from the OCR text) or identifying the specific caste category (SC/ST/OBC). It assigns a **Confidence Score** to the extraction, alerting administrators if manual review is needed.

### 2.2. Intelligent Recommendation Engine
The platform features a sophisticated scoring algorithm (`src/recommendation.py`) that acts as an expert system to rank scholarships for a given user.
- **Dynamic Scoring Weights**: Rather than simple filtering, the engine assigns weighted scores across multiple parameters: `education_match_score`, `income_match_score`, and `demographic_match_score`.
- **NLP Income Normalization**: The engine intelligently parses natural language income constraints (e.g., converting "2.5 lakh" or "8.0 LPA" into a numeric threshold of `250000`).
- **Demographic & Educational Matching**: The recommendation engine strictly enforces eligibility, heavily penalizing or disqualifying mismatches (e.g., gender-specific scholarships) while boosting scores for category/minority alignments. Scholarships scoring above a 60% threshold are classified as "strong matches" and ranked accordingly.

### 2.3. Automated Web Crawler & Discovery
The data pipeline is driven by a web crawler (`scheduler.py` & `src/search.py`) that constantly searches the internet for new scholarships.
- **Intelligent Searching**: It integrates with DuckDuckGo's Search API (`DDGS`) to query for new scholarships dynamically, avoiding aggressive rate limits. 
- **Fallback Mechanisms**: If dynamic search yields few results, the system possesses a heuristic fallback repository of known government portals (e.g., `scholarships.gov.in`, `buddy4study`) to ensure a constant influx of data.
- **HTML Parsing**: `src/downloader.py` asynchronously fetches web pages to be processed and inserted into the system's SQLite database.

## 3. System Architecture & Technical Stack
The platform is built using modern, scalable technologies designed for high performance:
- **Backend Framework:** FastAPI (Python) – Provides a lightning-fast, asynchronous REST API with automatic Swagger UI documentation built-in.
- **Database:** SQLite (`scholarships.db`) – Lightweight, fast relational database storing user profiles, scholarship data, and configuration weights.
- **AI/ML Libraries:** `pytesseract` (Python wrapper for Google's Tesseract-OCR Engine), `Pillow` (Image Processing), `re` (Regex/NLP basic parsing).
- **Web Scraping:** `requests`, `duckduckgo-search` (`DDGS`).

## 4. Deployment & Automation
The project is designed with production-readiness in mind. It supports robust deployment pipelines:
- **Containerization (Docker)**: The entire application is containerized using a `Dockerfile` based on `python:3.11-slim`. This ensures the system runs identically across all environments and automatically installs critical system dependencies like `tesseract-ocr` and `libgl1`.
- **Local Automation (`start.bat`)**: For development and demonstration, a Windows batch script orchestrates the entire system. It simultaneously launches the FastAPI Web Server and the Background Automation Scheduler (`scheduler.py`) in independent console interfaces, enabling instant one-click startup.

## 5. Conclusion
This project demonstrates a practical, high-impact application of Artificial Intelligence and intelligent web automation. By combining OCR for document intelligence, weighted algorithms for recommendation, and web scraping for data ingestion, the system successfully solves the real-world problem of bridging the gap between available financial aid and eligible students.
