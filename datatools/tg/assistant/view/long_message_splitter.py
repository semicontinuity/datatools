import re


def split_text_into_lines0(text: str, max_line_length=120):
    lines = text.splitlines()
    ans = []
    for line in lines:
        if len(line) == 0:
            ans += ['']
        else:
            ans += split_text_into_lines(line, max_line_length)
    return ans


def split_text_into_lines(text: str, max_line_length=120):
    # Define regex patterns for sentence and sub-sentence boundaries
    sentence_endings = r'(?<=[.!?])\s+'
    sub_sentence_endings = r'([;,])\s*'  # Capture the delimiter (, or ;) for retention

    # Step 1: Split the text into sentences
    sentences = re.split(sentence_endings, text.strip())

    # Initialize the result list to store lines
    lines = []
    current_line = ""

    def add_to_line(segment):
        """Helper function to add a segment to the current line or create a new line if necessary."""
        nonlocal current_line
        if len(current_line) + len(segment) + (1 if current_line else 0) <= max_line_length:
            current_line += (" " + segment if current_line else segment)
        else:
            if current_line:
                lines.append(current_line)
            current_line = segment

    def split_segment(segment, delimiter_pattern):
        """Recursively split a segment by delimiters until it fits within the line length."""
        if len(segment) <= max_line_length:
            return [segment]

        # Attempt to split by the given delimiter pattern while retaining the delimiter
        parts = re.split(delimiter_pattern, segment)
        result = []
        current_part = ""

        for i in range(0, len(parts), 2):  # Process text parts and delimiters alternately
            part = parts[i]  # Text part
            delimiter = parts[i + 1] if i + 1 < len(parts) else ""  # Delimiter part

            combined = part + delimiter  # Combine text and delimiter
            if len(current_part) + len(combined) <= max_line_length:
                current_part += (", " + combined if current_part else combined)  # Retain delimiter
            else:
                if current_part:
                    result.append(current_part)
                current_part = combined

        if current_part:
            result.append(current_part)

        # If any part is still too long, split further on word boundaries
        final_result = []
        for part in result:
            if len(part) > max_line_length:
                words = part.split()
                temp_line = ""
                for word in words:
                    if len(temp_line) + len(word) + 1 <= max_line_length:
                        temp_line += (" " + word if temp_line else word)
                    else:
                        final_result.append(temp_line)
                        temp_line = word
                if temp_line:
                    final_result.append(temp_line)
            else:
                final_result.append(part)

        return final_result

    # Step 2: Process each sentence
    for sentence in sentences:
        segments = split_segment(sentence, sub_sentence_endings)
        for segment in segments:
            add_to_line(segment)

    # Add the last line if it's not empty
    if current_line:
        lines.append(current_line)

    return lines

