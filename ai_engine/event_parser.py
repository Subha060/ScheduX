import json
from datetime import date
from .base import generate, clean_json

def parse_event(text, api_key=None, model_name=None):
    today_str = date.today().strftime('%Y-%m-%d')
    prompt = f"""Parse this text into a specific calendar event JSON object.
Today's date is {today_str}.
The JSON object must contain:
- title: (string)
- date: (string, YYYY-MM-DD format)
- start_time: (string, HH:MM 24h format)
- end_time: (string, HH:MM 24h format)
- description: (string, empty if none)

Guidelines:
1. If the user says "tomorrow", "next Friday", etc., calculate the exact YYYY-MM-DD.
2. If the user says "at 6pm", use "18:00".
3. If no end time is specified, default to 1 hour after the start time.
4. Input Text: {text}

Return ONLY the valid JSON object."""
    
    raw = generate(prompt, api_key=api_key, model_name=model_name)
    cleaned = clean_json(raw)
    try:
        event_data = json.loads(cleaned)
    except Exception as e:
        import re
        found_time = re.search(r'(\d{1,2})(?::(\d{2}))?\s*(am|pm)?', text.lower())
        fallback_start = "09:00"
        if found_time:
            hour = int(found_time.group(1))
            minute = found_time.group(2) or "00"
            ampm = found_time.group(3)
            
            if ampm == 'pm' and hour < 12: hour += 12
            elif ampm == 'am' and hour == 12: hour = 0
            fallback_start = f"{hour:02d}:{minute}"
        
        h, m = map(int, fallback_start.split(':'))
        fallback_end = f"{(h+1)%24:02d}:{m:02d}"

        event_data = {
            'title': text, 
            'date': today_str, 
            'start_time': fallback_start, 
            'end_time': fallback_end,
            'description': ''
        }
    return event_data
