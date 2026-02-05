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
Perform a deep-scan of the web for the last 24 hours and identify the single most impactful headline for each of these 5 categories. 
For each, provide a 'headline', 'url', and a 'reason' (summary of why it matters).

Categories & Logic:
1. Automated Driving Tech: Technical L4/L5 milestones, sensor fusion, or AI architecture shifts. No stock fluff.
2. Longevity Lab: Human-centric research on healthspan/longevity. Focus on actionable protocols (nutrition, sleep, supplements) based on latest human studies.
3. Finance & Business: Top trending startup/business ideas OR significant macro stock market shifts with a brief analysis of the 'why'.
4. AI & Robotics: Breakthroughs in model behavior (LLMs) or robotics features (human-robot interaction, dexterity, deployment).
5. Global Progress: High-impact 'good news' regarding climate, poverty, or geopolitical de-escalation.

Return the result ONLY as a JSON array of objects. Example format:
[
  {"category": "Automated Driving Tech", "headline": "...", "url": "...", "reason": "..."},
  ...
]
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
        
        # 1. Validation: Check if the AI actually returned text
        if not response or not response.text:
            print("CRITICAL: AI returned an empty response. Possible API throttling or Search timeout.")
            return

        raw_text = response.text
        
        # 2. Cleanup: Extract JSON block more aggressively
        if "```json" in raw_text:
            raw_text = raw_text.split("```json")[1].split("```")[0].strip()
        elif "```" in raw_text:
            raw_text = raw_text.split("```")[1].split("```")[0].strip()
        
        # 3. Final Parse Check
        try:
            data = json.loads(raw_text)
        except json.JSONDecodeError:
            print(f"DEBUG: AI returned non-JSON text: {raw_text[:100]}...")
            return

        print(f"\n[TOP SIGNALS DETECTED: {len(data)} Categories]")
        
        for item in data:
            print(f"-> {item.get('category')}: {item.get('headline')[:50]}...")
        
        with open('top_news.json', 'w') as f:
            json.dump(data, f, indent=4)
        print("\nSuccess: top_news.json updated.")

    except Exception as e:
        print(f"Agent Encountered Error: {e}")

if __name__ == "__main__":
    scout()