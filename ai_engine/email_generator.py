
from .base import generate


TONE_DESCRIPTIONS = {
    'professional': 'formal and professional, suitable for workplace communication',
    'friendly':     'warm and friendly, yet still appropriate for work',
    'formal':       'highly formal with proper salutations, suitable for official correspondence',
    'assertive':    'confident and direct, clearly stating requirements without being rude',
    'apologetic':   'empathetic and apologetic in tone, taking responsibility where needed',
    'persuasive':   'compelling and persuasive, designed to convince the reader',
}


def draft_email(
    brief: str,
    recipient: str = '',
    tone: str = 'professional',
    context: str = '',
    sender_name: str = '',
) -> str:
   
    tone_desc = TONE_DESCRIPTIONS.get(tone, TONE_DESCRIPTIONS['professional'])

    recipient_line = f"To: {recipient}" if recipient else "To: appropriate recipient (infer from context)"
    context_line   = f"Additional context: {context}" if context else ""
    sender_line    = f"Sign off with the name: {sender_name}" if sender_name else "Use a generic sign-off"

    prompt = f"""You are an expert business email writer. Write a complete email based on the following brief.

BRIEF: {brief}
{recipient_line}
TONE: {tone_desc}
{context_line}
{sender_line}

Requirements:
1. Start with: Subject: [your subject line here]
2. Leave a blank line
3. Write a proper greeting
4. Well-structured body paragraphs
5. Professional closing and sign-off

Output ONLY the email. No explanations, no preamble:"""

    return generate(prompt)


def extract_subject(email_text: str) -> str:
    # Pull out just the Subject line from a generated email
    for line in email_text.split('\n'):
        stripped = line.strip()
        if stripped.lower().startswith('subject:'):
            return stripped.replace('Subject:', '').replace('subject:', '').strip()
    return 'Email Draft'