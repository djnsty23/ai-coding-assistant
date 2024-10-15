# AI Coding Assistant

This tool combines YouTube transcript downloading and AI-assisted coding workflow analysis. It fetches transcripts from YouTube videos and analyzes them to extract detailed information about AI coding practices.

## Setup

1. Ensure you have Python 3.7+ installed.
2. Install the required packages:   ```
   pip install -r requirements.txt   ```
3. Create a `.env.local` file in the project directory with your OpenAI API key:   ```
   OPENAI_API_KEY=your_api_key_here   ```

## Usage

Run the script from the command line, providing the YouTube video ID:
python ai_coding_assistant.py VIDEO-ID