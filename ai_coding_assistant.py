import os
import sys
import json
import argparse
from dotenv import load_dotenv
from openai import OpenAI
from youtube_transcript_api import YouTubeTranscriptApi
from googleapiclient.discovery import build

# Load environment variables
load_dotenv()

# Set up OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Set up YouTube API client
youtube = build('youtube', 'v3', developerKey=os.getenv('YOUTUBE_API_KEY'))

def get_video_info(video_id):
    try:
        # Fetch video details
        video_response = youtube.videos().list(
            part='snippet',
            id=video_id
        ).execute()

        video_title = video_response['items'][0]['snippet']['title']

        # Fetch transcript
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        full_transcript = ' '.join([entry['text'] for entry in transcript])

        return video_title, full_transcript
    except Exception as e:
        print(f"Error fetching video info: {str(e)}")
        return None, None

def analyze_transcript(transcript):
    functions = [
        {
            "name": "extract_ai_workflow_information",
            "description": "Extract detailed information about AI-assisted coding workflow from the transcript",
            "parameters": {
                "type": "object",
                "properties": {
                    "planning_and_specs": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Steps for detailed planning and creating specifications"
                    },
                    "proof_of_concept": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Steps for building proof of concept for core functionalities"
                    },
                    "project_setup": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Steps for setting up the project structure"
                    },
                    "spec_refinement": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Steps for refining and expanding initial specs using AI"
                    },
                    "implementation": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Steps for implementing functionality"
                    },
                    "ui_refinement": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Steps for refining the UI"
                    },
                    "modular_prompts": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Information about using modular, reusable prompts"
                    },
                    "iteration_and_debugging": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Steps for iterating and debugging"
                    },
                    "best_practices": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Best practices mentioned in the transcript"
                    },
                    "tools_and_technologies": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Tools and technologies mentioned in the transcript"
                    },
                    "donts": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Practices or approaches to avoid in AI-assisted coding"
                    }
                },
                "required": ["planning_and_specs", "proof_of_concept", "project_setup", "spec_refinement", 
                             "implementation", "ui_refinement", "modular_prompts", "iteration_and_debugging", 
                             "best_practices", "tools_and_technologies", "donts"]
            }
        }
    ]

    completion = client.chat.completions.create(
        model="gpt-4o-mini",  # Note: This model name might need to be changed to a standard OpenAI model
        messages=[
            {"role": "system", "content": "You are an AI assistant that extracts detailed information about AI-assisted coding workflows from transcripts. You focus on practical steps, best practices, tools used in the process, and practices to avoid."},
            {"role": "user", "content": f"""
            Analyze the following transcript and extract detailed information about the AI-assisted coding workflow described. Focus on the following aspects:

            1. Planning and Specs: Steps for detailed planning and creating specifications.
            2. Proof of Concept: Steps for building proof of concept for core functionalities.
            3. Project Setup: Steps for setting up the project structure.
            4. Spec Refinement: Steps for refining and expanding initial specs using AI.
            5. Implementation: Steps for implementing functionality.
            6. UI Refinement: Steps for refining the UI.
            7. Modular Prompts: Information about using modular, reusable prompts.
            8. Iteration and Debugging: Steps for iterating and debugging.
            9. Best Practices: Best practices mentioned in the transcript.
            10. Tools and Technologies: Tools and technologies mentioned in the transcript.
            11. DON'Ts: Practices or approaches that should be avoided in AI-assisted coding.

            Present the information in a structured, detailed format suitable for developers looking to improve their AI-assisted coding workflow. Include specific steps, techniques, examples, and warnings mentioned in the transcript.

            Transcript: {transcript}
            """}
        ],
        functions=functions,
        function_call={"name": "extract_ai_workflow_information"}
    )

    return json.loads(completion.choices[0].message.function_call.arguments)

def main():
    parser = argparse.ArgumentParser(description="Download YouTube transcript and analyze AI coding workflow.")
    parser.add_argument("video_id", help="YouTube video ID")
    args = parser.parse_args()

    print(f"Fetching video info for video ID: {args.video_id}")
    video_title, transcript = get_video_info(args.video_id)

    if transcript:
        print("Transcript fetched successfully. Saving to file...")
        safe_title = ''.join(c for c in video_title if c.isalnum() or c in (' ', '_')).rstrip()
        safe_title = safe_title[:100]  # Limit title length to 100 characters
        transcript_path = os.path.join('transcripts', f"{safe_title}.txt")
        with open(transcript_path, 'w', encoding='utf-8') as f:
            f.write(transcript)
        print(f"Transcript saved to {transcript_path}")

        print("Analyzing transcript...")
        analysis = analyze_transcript(transcript)

        analysis_path = os.path.join('analyzed_transcripts', f"{safe_title}_analysis.json")
        with open(analysis_path, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2)
        print(f"Analysis saved to {analysis_path}")
    else:
        print("Failed to fetch video info. Exiting.")

if __name__ == "__main__":
    main()
