def truncate_content(content: str, max_length: int = 50000) -> str:
    if len(content) <= max_length:
        return content

    truncated = content[:max_length]
    last_space = truncated.rfind(' ')
    if last_space > max_length * 0.8:
        return truncated[:last_space] + '...'
    else:
        return truncated + '...'
