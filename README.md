# LangChain Text Summarizer

A simple AI-powered text summarization application built using Streamlit, LangChain, and Google Gemini. It summarizes YouTube video transcripts and website content in a clear, concise format.

## Features

- Summarize YouTube videos using their transcripts
- Summarize content from website URLs
- Generate summaries using Google Gemini
- Simple and interactive Streamlit interface
- Download generated summaries as text files
- Secure API key management using environment variables

## Tech Stack

- Python
- Streamlit
- LangChain
- Google Gemini API
- YouTube Transcript API
- Unstructured URL Loader
- Python Dotenv

## Project Structure

```text
langchain-text-summarizer/
├── app.py
├── .env
├── .gitignore
├── README.md
└── .venv/
```

Note: `.env` and `.venv/` are local files/folders and should not be committed to GitHub.

## Installation

1. Clone the repository:

```bash
git clone https://github.com/YOUR_USERNAME/langchain-text-summarizer.git
cd langchain-text-summarizer
```

2. Create and activate a virtual environment (optional but recommended):

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

3. Install the required packages:

```bash
pip install streamlit langchain langchain-google-genai python-dotenv youtube-transcript-api langchain-community unstructured
```

Depending on the website loader used in `app.py`, additional packages may be required.

## Configure the API Key

Create a `.env` file in the same directory as `app.py` and add your Google Gemini API key:

```env
GEMINI_API_KEY=your_actual_api_key_here
```

Get an API key from [Google AI Studio](https://aistudio.google.com/apikey).

Never upload your real API key to GitHub.

## Run the Application

```bash
streamlit run app.py
```

Open the local URL displayed in your terminal, usually `http://localhost:8501`.

## How to Use

1. Start the application.
2. Choose a YouTube video URL or website URL, according to the options in the app.
3. Enter the URL.
4. Click the summarize button.
5. Read and download the generated summary.

Note: YouTube videos must have transcripts available, and websites must allow their content to be accessed.

## Security

- Store API keys in `.env` or environment variables.
- Keep `.env` out of version control.
- Never commit credentials or private tokens.

## Future Improvements

- Support multiple languages
- Add summary length controls
- Support PDF and document summarization
- Improve error handling and transcript availability checks

## Author

Kodeeswaran A S

- GitHub: https://github.com/YOUR_USERNAME
- LinkedIn: https://www.linkedin.com/in/kodeeswaran-a-s/

---

If you find this project useful, consider giving the repository a star!