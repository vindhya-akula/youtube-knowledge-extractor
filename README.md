# YouTube Knowledge Extractor

An AI-powered application that transforms YouTube videos into structured, category-specific learning materials using Python, Google Gemini AI, and Streamlit.

Instead of generating the same generic summary for every video, this application automatically identifies the video's content category and generates relevant notes based on its subject.

## Features

- **YouTube Transcript Extraction:** Extracts video transcripts and supports available captions.
- **Automatic Content Classification:** Uses Gemini AI to identify the type of video.
- **Category-Specific Knowledge Extraction:** Generates structured content tailored to different video categories.
- **AI-Powered Processing:** Uses Google Gemini to analyze transcripts and generate meaningful insights.
- **Structured AI Responses:** Uses Pydantic models to validate and organize generated content.
- **Transcript Caching:** Stores previously fetched transcripts to reduce repeated requests.
- **SQLite Database:** Saves extracted knowledge and maintains a personal video library.
- **Retry Handling:** Handles temporary Gemini API errors with retry logic and model fallback support.
- **Streamlit Interface:** Provides a simple interface to extract, view, and manage video notes.

## Supported Video Categories

The application automatically classifies videos into the following categories:

| Category | Generated Content |
|---|---|
| Education | Learning objectives, topic-wise notes, definitions, examples, revision points, and practice questions |
| Entertainment | Storyline, characters, relationships, important scenes, twists, emotional moments, and ending |
| Technical Tutorials | Skills, tools, prerequisites, step-by-step instructions, code examples, tips, and exercises |
| Podcasts & Interviews | Speaker information, discussion topics, viewpoints, insights, and conclusions |
| News & Current Affairs | Event summaries, people involved, timelines, background, impacts, and claims to verify |
| Documentaries | Main subject, themes, chronology, evidence, people, findings, and conclusions |
| General | Overview, key points, takeaways, and relevant questions |

## Technology Stack

- **Programming Language:** Python
- **Frontend:** Streamlit
- **AI Model:** Google Gemini
- **Data Validation:** Pydantic
- **Database:** SQLite
- **Transcript Extraction:** YouTube Transcript API
- **Environment Management:** Python dotenv
- **Version Control:** Git and GitHub

## Project Structure

```text
youtube-knowledge-extractor/
│
├── main.py                  # Streamlit application
├── transcript_fetcher.py    # YouTube transcript extraction
├── ai_summarizer.py         # Gemini AI classification and generation
├── content_templates.py     # Category-specific schemas and prompts
├── database.py              # SQLite database operations
│
├── requirements.txt         # Project dependencies
├── README.md                # Project documentation
├── .env.example             # Environment variable template
├── .gitignore               # Git ignored files
│
└── youtube_knowledge.db     # Local SQLite database (generated)
```

## Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/vindhya-akula/youtube-knowledge-extractor.git
cd youtube-knowledge-extractor
```

Replace `YOUR_USERNAME` with your GitHub username.

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

Activate it on Windows:

```powershell
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Gemini API Key

Create a `.env` file in the project root directory.

Add the following configuration:

```env
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=your_primary_model
GEMINI_FALLBACK_MODEL=your_fallback_model
```

Replace the placeholder values with your actual Gemini API key and supported model IDs.

You can obtain a Gemini API key from [Google AI Studio](https://aistudio.google.com/).

**Important:** Never upload your `.env` file or expose your API key on GitHub.

### 5. Run the Application

```bash
streamlit run main.py
```

The application will open in your browser.

## How It Works

1. Enter a YouTube video URL.
2. Select the available transcript language.
3. The application fetches the transcript or retrieves a cached transcript from SQLite.
4. Gemini AI automatically identifies the video category.
5. A category-specific Pydantic schema and prompt are selected.
6. Gemini generates structured knowledge from the transcript.
7. The generated notes and category are saved in SQLite.
8. Access previously processed videos through the personal library.

## Database Design

The application uses SQLite to maintain two main data tables:

- **transcripts:** Stores video transcripts, language information, and transcript metadata.
- **summaries:** Stores generated structured notes, video details, category, and creation timestamp.

This allows previously fetched transcripts and generated notes to be reused.

## Error Handling

- Retries temporary Gemini API failures.
- Supports a fallback Gemini model when configured.
- Preserves pending transcripts when AI generation fails.
- Reuses the detected category during retry attempts when available.
- Uses transcript caching to avoid unnecessary repeated extraction.

## Future Enhancements

- Add multilingual output generation.
- Support exporting notes to PDF and Markdown.
- Add keyword-based search and filtering in the personal library.
- Introduce user authentication and cloud database support.
- Add downloadable study materials and flashcards.
- Improve long-video processing through transcript chunking.

## Learning Outcomes

Through this project, I gained practical experience in:

- Building AI-powered applications using Python.
- Integrating Google Gemini APIs.
- Designing structured AI outputs using Pydantic.
- Extracting and processing YouTube transcripts.
- Implementing database operations using SQLite.
- Handling API failures, retries, and fallback mechanisms.
- Developing interactive applications using Streamlit.
- Managing project versions using Git and GitHub.

## Author

**Vindhya Akula**

GitHub: [vindhya-akula](https://github.com/vindhya-akula)