
import os
import validators
import streamlit as st

from dotenv import load_dotenv
from urllib.parse import urlparse, parse_qs

from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.document_loaders import UnstructuredURLLoader
from youtube_transcript_api import YouTubeTranscriptApi


# --------------------------------------------------
# Load Environment Variables
# --------------------------------------------------
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()


# --------------------------------------------------
# Streamlit Configuration
# --------------------------------------------------
st.set_page_config(
    page_title="LangChain: Text Summarizer",
    page_icon="🦜",
    layout="wide"
)

st.title("🦜 LangChain: Text Summarizer")
st.subheader("Summarize YouTube Videos or Website Content")


# --------------------------------------------------
# Sidebar Settings
# --------------------------------------------------
with st.sidebar:
    st.header("Settings")

    if GEMINI_API_KEY:
        st.success("Gemini API key detected")
    else:
        st.warning(
            "GEMINI_API_KEY not found. "
            "Check your .env file or environment variables."
        )

    st.caption("Powered by Google Gemini")


# --------------------------------------------------
# URL Input
# --------------------------------------------------
generic_url = st.text_input(
    "Enter YouTube or Website URL",
    placeholder="https://youtu.be/BQ3BwE7kSLI"
)


# --------------------------------------------------
# Prompt Template
# --------------------------------------------------
prompt_template = """
You are an expert content summarizer.

Summarize the following content in approximately 300 words.

Instructions:
- Focus on the most important information.
- Remove unnecessary details and repetition.
- Use simple and clear language.
- Organize information logically using headings and bullet points.
- Do not add facts that are not present in the source.
- If the source is short, provide a shorter summary.

Content:
{text}

Summary:
"""

prompt = PromptTemplate(
    template=prompt_template,
    input_variables=["text"]
)


# --------------------------------------------------
# Extract YouTube Video ID
# --------------------------------------------------
def extract_youtube_video_id(url):
    parsed_url = urlparse(url)
    hostname = (parsed_url.hostname or "").lower()

    if hostname == "youtu.be":
        return parsed_url.path.strip("/").split("/")[0] or None

    youtube_hosts = [
        "youtube.com",
        "www.youtube.com",
        "m.youtube.com",
        "music.youtube.com"
    ]

    if hostname in youtube_hosts:
        query_params = parse_qs(parsed_url.query)

        # Standard YouTube video
        if query_params.get("v"):
            return query_params["v"][0]

        # Shorts, embedded videos, and live videos
        path_parts = parsed_url.path.strip("/").split("/")

        if (
            len(path_parts) >= 2
            and path_parts[0] in ["shorts", "embed", "live"]
        ):
            return path_parts[1]

    return None


# --------------------------------------------------
# Check YouTube URL
# --------------------------------------------------
def is_youtube_url(url):
    hostname = (urlparse(url).hostname or "").lower()

    return hostname in [
        "youtube.com",
        "www.youtube.com",
        "m.youtube.com",
        "music.youtube.com",
        "youtu.be"
    ]


# --------------------------------------------------
# Get YouTube Transcript
# --------------------------------------------------
def get_youtube_transcript(url):
    video_id = extract_youtube_video_id(url)

    if not video_id:
        raise ValueError(
            "Could not extract the YouTube video ID. "
            "Please check the URL."
        )

    api = YouTubeTranscriptApi()

    try:
        transcript_list = api.list(video_id)
        transcripts = list(transcript_list)

    except Exception as exc:
        raise ValueError(
            "Unable to retrieve the YouTube transcript. "
            "Check whether captions are available for this video. "
            "YouTube may also be blocking transcript access."
        ) from exc

    if not transcripts:
        raise ValueError("No transcript is available for this video.")

    preferred_languages = ["en", "en-US", "en-GB", "ta", "hi"]
    selected_transcript = None

    # Select a preferred language when available
    for language in preferred_languages:
        for transcript in transcripts:
            if transcript.language_code.lower() == language.lower():
                selected_transcript = transcript
                break

        if selected_transcript:
            break

    # Otherwise, use the first available transcript
    if selected_transcript is None:
        selected_transcript = transcripts[0]

    try:
        fetched_transcript = selected_transcript.fetch()

    except Exception as exc:
        raise ValueError(
            "The transcript was found but could not be downloaded."
        ) from exc

    text = " ".join(
        snippet.text for snippet in fetched_transcript
    )

    if not text.strip():
        raise ValueError("The YouTube transcript is empty.")

    return text, selected_transcript.language_code


# --------------------------------------------------
# Get Website Content
# --------------------------------------------------
def get_website_content(url):
    loader = UnstructuredURLLoader(
        urls=[url],
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        }
    )

    docs = loader.load()

    if not docs:
        raise ValueError(
            "Could not extract content from the website."
        )

    text = "\n\n".join(
        doc.page_content
        for doc in docs
        if doc.page_content
    )

    if not text.strip():
        raise ValueError(
            "The website does not contain readable text."
        )

    return text


# --------------------------------------------------
# Summarize Content Using Gemini
# --------------------------------------------------
def summarize_text(text, llm):
    max_characters = 30000
    text = text[:max_characters]

    formatted_prompt = prompt.format(text=text)
    response = llm.invoke(formatted_prompt)

    if isinstance(response.content, str):
        return response.content

    if isinstance(response.content, list):
        return "\n".join(
            str(block.get("text", ""))
            if isinstance(block, dict)
            else str(block)
            for block in response.content
        )

    return str(response.content)


# --------------------------------------------------
# Main Application
# --------------------------------------------------
if st.button("Summarize the Content", type="primary"):

    # Validate API key
    if not GEMINI_API_KEY:
        st.error(
            "GEMINI_API_KEY was not found. "
            "Add it to your .env file or Windows environment variables."
        )
        st.stop()

    # Validate URL
    if not generic_url.strip():
        st.error("Please enter a YouTube or website URL.")
        st.stop()

    if not validators.url(generic_url):
        st.error("Please enter a valid URL.")
        st.stop()

    parsed_url = urlparse(generic_url)

    if parsed_url.scheme not in ["http", "https"]:
        st.error("Only HTTP and HTTPS URLs are supported.")
        st.stop()

    try:
        with st.spinner(
            "Loading content and generating your summary..."
        ):

            # Initialize Google Gemini
            llm = ChatGoogleGenerativeAI(
                model="gemini-3.1-flash-lite",
                google_api_key=GEMINI_API_KEY,
                temperature=0
            )

            # Extract YouTube transcript
            if is_youtube_url(generic_url):
                st.info("Fetching YouTube transcript...")

                text, language = get_youtube_transcript(
                    generic_url
                )

                st.success(
                    f"Transcript retrieved. Language: {language}"
                )

            # Extract website content
            else:
                st.info("Extracting website content...")

                text = get_website_content(generic_url)

            if not text.strip():
                st.error("No readable content was found.")
                st.stop()

            st.write(
                f"**Extracted content:** {len(text):,} characters"
            )

            # Generate summary
            output_summary = summarize_text(text, llm)

        # Display summary
        st.success("Summary generated successfully!")

        st.subheader("📝 Summary")
        st.markdown(output_summary)

        # Download summary
        st.download_button(
            label="Download Summary",
            data=output_summary,
            file_name="summary.txt",
            mime="text/plain"
        )

    except Exception as exc:
        st.error("Unable to process the provided URL.")

        error_message = str(exc)

        if "API_KEY_INVALID" in error_message or (
            "API key not valid" in error_message
        ):
            st.error(
                "Your Gemini API key was rejected. "
                "Check or regenerate it in Google AI Studio."
            )

        elif "404" in error_message or "NOT_FOUND" in error_message:
            st.error(
                "The Gemini model may be unavailable. "
                "Check the model ID and API access."
            )

        with st.expander("View technical error"):
            st.exception(exc)