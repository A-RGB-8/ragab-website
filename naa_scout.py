from google import genai
from google.genai import types
import json
import os

# 1. Setup
api_key = os.environ.get('GEMINI_API_KEY')
if not api_key:
    print("ERROR: Run 'export GEMINI_API_KEY=your_key' first.")
    exit()

client = genai.Client(api_key=api_key)

# CHANGE: Moving to 2.5 Flash-Lite (the 2026 Free Tier Standard)
model_id = "gemini-2.5-flash-lite" 

prompt = """
Search the live web for the single most significant technical breakthrough or deployment milestone in 
Autonomous Driving (AD) from the last 24 hours. 
Focus on: L4/L5 milestones, sensor fusion, or AI model architecture.
Provide the result ONLY as a JSON object: {"headline": "...", "url": "...", "reason": "..."}
"""

def scout():
    print(f"NAA Agent: Scanning using {model_id} + Search...")
    try:
        response = client.models.generate_content(
            model=model_id,
            contents=prompt,
            config=types.GenerateContentConfig(
                tools=[types.Tool(google_search=types.GoogleSearch())]
            )
        )
        
        raw_text = response.text
        # Logic to extract JSON if AI adds conversational filler
        if "```json" in raw_text:
            raw_text = raw_text.split("```json")[1].split("```")[0].strip()
        elif "```" in raw_text:
            raw_text = raw_text.split("```")[1].split("```")[0].strip()
        
        data = json.loads(raw_text)
        
        print(f"\n[TOP SIGNAL DETECTED]")
        print(f"HEADLINE: {data['headline']}")
        
        with open('top_news.json', 'w') as f:
            json.dump(data, f, indent=4)
        print("\nSuccess: top_news.json updated.")

    except Exception as e:
        if "429" in str(e):
            print("CRITICAL: Still hitting rate limits. The free tier search quota might be exhausted for today.")
            print("Suggestion: Try again in a few minutes or check if billing is enabled for 'Pay-as-you-go' (which has a huge free buffer).")
        else:
            print(f"Agent Encountered Error: {e}")

if __name__ == "__main__":
    scout()