import re

def sanitize_payload(text: str) -> str:
    """
    Redacts common API key formats and prompt injection attempts from text inputs.
    """
    if not isinstance(text, str):
        return text

    # Redact common API keys
    # Matches typical keys starting with sk- followed by alphanumeric chars
    text = re.sub(r'\bsk-[a-zA-Z0-9]{20,}\b', '[REDACTED API KEY]', text)
    # Google API keys typically start with AIza
    text = re.sub(r'\bAIza[0-9A-Za-z-_]{35}\b', '[REDACTED API KEY]', text)
    # Generic bearer tokens
    text = re.sub(r'\bBearer\s+[a-zA-Z0-9\-\._~+/]+=*\b', 'Bearer [REDACTED TOKEN]', text)

    # Redact common prompt injection patterns
    injection_patterns = [
        r'(?i)\bignore\s+(all\s+)?previous\s+(instructions|prompts|directions)\b',
        r'(?i)\bforget\s+(all\s+)?previous\s+(instructions|prompts|directions)\b',
        r'(?i)\bdisregard\s+(all\s+)?previous\s+(instructions|prompts|directions)\b',
        r'(?i)\byou\s+are\s+now\b',
        r'(?i)\bprint\s+(all\s+)?previous\s+(instructions|prompts)\b'
    ]
    
    for pattern in injection_patterns:
        text = re.sub(pattern, '[REDACTED INJECTION ATTEMPT]', text)

    return text
