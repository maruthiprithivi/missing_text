"""

This module contains functions for splitting text into chunks. Inspired by `text-splitter` from the Langchain Team ❤️.

Chunking is the process of splitting text into smaller units, such as sentences or paragraphs.

The following chunking methods are implemented:
- regex_splitter: Splits text based on a specified regular expression pattern.
- character_splitter: Splits text into chunks of specified character size with optional overlap.
- sentence_splitter: Splits text into individual sentences with optional overlap.
- paragraph_splitter: Splits text into paragraphs.
- markdown_header_splitter: Splits markdown text based on headers of a specified level.
- json_key_splitter: Extracts and splits data from a specified key in nested JSON data.
- html_tag_attribute_splitter: Extracts and splits content within specified HTML tags or their attributes.
- python_code_splitter: Splits Python code into sections based on a specified delimiter (e.g., function definitions).
- nltk_sentence_tokenizer: Tokenizes text into sentences using NLTK's sentence tokenizer.
- spacy_sentence_tokenizer: Tokenizes text into sentences using spaCy's sentence tokenizer.
- latex_section_splitter: Splits LaTeX text by specified sectioning commands (e.g., sections, subsections).

"""


def regex_splitter(text: str, pattern: str) -> list[str]:
    """
    Splits the text based on a specified regular expression pattern.

    Args:
        text (str): The text to be split.
        pattern (str): The regular expression pattern to use as the delimiter.

    Returns:
        list of str: A list of text segments split by the specified pattern.

    Example:
        >>> text = "apple;banana;cherry"
        >>> regex_splitter(text, r";")
        ['apple', 'banana', 'cherry']
    """
    import re

    # Use the regular expression to split the text
    segments = re.split(pattern, text)

    # Filter out any empty segments
    return [segment.strip() for segment in segments if segment.strip()]


def character_splitter(text: str, chunk_size: int = 100, overlap: int = 0) -> list[str]:
    """
    Splits the given text into chunks of specified character size with optional overlap.

    Args:
        text (str): The text to be split into chunks.
        chunk_size (int): The number of characters each chunk should contain.
        overlap (int, optional): The number of characters to overlap between chunks. Defaults to 0.

    Returns:
        list of str: A list containing text chunks.
    """
    # Ensure chunk_size and overlap are positive integers, and overlap is less than chunk_size
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0")
    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be between 0 and chunk_size - 1")

    # Split text into chunks with overlap
    return [text[i : i + chunk_size] for i in range(0, len(text), chunk_size - overlap)]


def sentence_splitter(text: str) -> list[str]:  # Removed overlap argument
    """
    Splits the given text into individual sentences with optional overlap.

    Args:
        text (str): The text to be split into sentences.

    Returns:
        list of str: A list of sentence chunks, each with the specified overlap.

    Example:
        >>> text = "This is a sentence. This is another sentence. This is a third sentence."
        >>> sentence_splitter(text)
        ['This is a sentence. This is another sentence.', 'This is another sentence. This is a third sentence.']
    """
    import re

    # Regular expression to split text by sentence-ending punctuation
    sentence_endings = re.compile(r"(?<=[.!?])\s+")

    # Split text into sentences
    sentences = sentence_endings.split(text)

    # Filter out any empty sentences
    return [sentence.strip() for sentence in sentences if sentence.strip()]


def paragraph_splitter(text: str) -> list[str]:
    """
    Splits the given text into paragraphs.

    Args:
        text (str): The text to be split into paragraphs.

    Returns:
        list of str: A list containing paragraphs from the text.

    Example:
        >>> text = "Paragraph 1\n\nParagraph 2\n\nParagraph 3"
        >>> paragraph_splitter(text)
        ['Paragraph 1\n\nParagraph 2', 'Paragraph 2\n\nParagraph 3']
    """
    # Split text by line breaks to identify paragraphs
    paragraphs = text.split("\n\n")

    # Filter out any empty paragraphs
    return [paragraph.strip() for paragraph in paragraphs if paragraph.strip()]


def markdown_header_splitter(text: str, level: int = 1) -> list[str]:
    """
    Splits the given markdown text based on headers of a specified level.

    Args:
        text (str): The markdown text to be split.
        level (int, optional): The header level to split by. Defaults to 1.
            Available levels:
            - 1: Header level '#'
            - 2: Header level '##'
            - 3: Header level '###'
            - 4: Header level '####'
            - 5: Header level '#####'
            - 6: Header level '######'

    Returns:
        list of str: A list containing markdown sections with the specified overlap.

    Example:
        >>> text = "# Section 1\n\n## Subsection 1.1\n\n# Section 2\n\n## Subsection 2.1"
        >>> markdown_header_splitter(text, level=1)
        ['# Section 1\n\n## Subsection 1.1', '# Section 2\n\n## Subsection 2.1']
    """
    import re

    # Compile a regex pattern that looks for headers of the specified level
    pattern = re.compile(rf'(?=^{"#" * level}\s+)', re.MULTILINE)
    # Split the text at each header
    sections = pattern.split(text)
    # Strip whitespace and filter out any empty sections
    return [section.strip() for section in sections if section.strip()]


def json_key_splitter(json_data: dict, key: str) -> list[str]:
    """
    Extracts and splits data from a specified key in nested JSON data.

    Args:
        json_data (dict): The JSON data to be processed.
        key (str): The key to retrieve data from in the JSON structure.

    Returns:
        list: A list containing the data found under the specified key in the JSON structure.

    Example:
        >>> json_data = {
        ...     "name": "Document",
        ...     "sections": [
        ...         {"title": "Introduction", "content": "Welcome to the introduction."},
        ...         {"title": "Body", "content": "This is the main content."},
        ...         {"title": "Conclusion", "content": "Thank you for reading."}
        ...     ]
        ... }
        >>> json_key_splitter(json_data, "content")
        ['Welcome to the introduction.', 'This is the main content.', 'Thank you for reading.']
        >>> json_key_splitter(json_data, "title")
        ['Introduction', 'Body', 'Conclusion']
    """
    values = []

    if isinstance(json_data, dict):
        for k, v in json_data.items():
            if k == key:
                values.append(v)
            elif isinstance(v, (dict, list)):
                values.extend(json_key_splitter(v, key))
    elif isinstance(json_data, list):
        for item in json_data:
            values.extend(json_key_splitter(item, key))

    return values


def html_tag_attribute_splitter(
    html_content: str, tag: str, attribute: str = None
) -> list[str]:
    """
    Extracts and splits content within specified HTML tags.

    Args:
        html_content (str): The HTML content to be processed.
        tag (str): The HTML tag to retrieve content from (e.g., 'p', 'div', 'span').

    Returns:
        list of str: A list containing the content found within the specified HTML tags.

    Example:
        >>> html_content = "<div>Hello</div><p>World</p><div>Example</div>"
        >>> html_tag_splitter(html_content, "div")
        ['Hello', 'Example']
        >>> html_tag_attribute_splitter(html_content, "img", "src")
        ['image1.jpg', 'image2.jpg']
    """
    from bs4 import BeautifulSoup

    # Parse the HTML content
    soup = BeautifulSoup(html_content, "html.parser")

    # Find and extract all content within the specified tags
    return [element.get_text(strip=True) for element in soup.find_all(tag)]


def html_element_attribute_splitter(
    html_content: str, tag: str, attribute: str
) -> list[str]:
    """
    Extracts and returns the values of a specified attribute from all instances of a given HTML tag.

    Args:
        html_content (str): The HTML content to be processed.
        tag (str): The HTML tag to search for (e.g., 'img', 'a').
        attribute (str): The attribute whose values need to be extracted (e.g., 'src', 'href').

    Returns:
        list of str: A list of attribute values for each instance of the specified tag in the HTML.

    Example:
        >>> html_content = '<img src="image1.jpg"><img src="image2.jpg">'
        >>> html_element_attribute_splitter(html_content, "img", "src")
        ['image1.jpg', 'image2.jpg']
    """
    from bs4 import BeautifulSoup

    # Parse the HTML content
    soup = BeautifulSoup(html_content, "html.parser")

    # Find all elements with the specified tag and extract the attribute values
    return [
        element.get(attribute)
        for element in soup.find_all(tag)
        if element.get(attribute)
    ]


def python_code_splitter(code: str, delimiter: str = "def") -> list[str]:
    """
    Splits Python code into sections based on a specified delimiter (e.g., function definitions).

    Args:
        code (str): The Python code to be split.
        delimiter (str, optional): The delimiter to split by. Defaults to "def" for functions.

    Returns:
        list of str: A list containing code sections split by the specified delimiter.

    Example:
        >>> code = "def func1(): pass\ndef func2(): pass"
        >>> python_code_splitter(code, "def")
        ['def func1(): pass', 'def func2(): pass']
    """
    import re

    # Use regular expression to split code based on the specified delimiter
    sections = re.split(rf"(?=\b{delimiter}\b)", code)

    # Filter out any empty sections
    return [section.strip() for section in sections if section.strip()]


def nltk_sentence_tokenizer(text: str) -> list[str]:
    """
    Tokenizes the given text into sentences using NLTK's sentence tokenizer.

    Args:
        text (str): The text to be tokenized into sentences.

    Returns:
        list of str: A list containing sentences from the text.

    Example:
        >>> text = "Hello world! How are you?"
        >>> nltk_sentence_tokenizer(text)
        ['Hello world!', 'How are you?']
    """
    import nltk

    nltk.download("punkt", quiet=True)

    # Use NLTK's sentence tokenizer
    from nltk.tokenize import sent_tokenize

    return sent_tokenize(text)


def spacy_sentence_tokenizer(text: str, model: str = "en_core_web_sm") -> list[str]:
    """
    Tokenizes the given text into sentences using spaCy's sentence tokenizer.

    Args:
        text (str): The text to be tokenized into sentences.
        model (str, optional): The spaCy language model to use. Defaults to "en_core_web_sm".

    Returns:
        list of str: A list containing sentences from the text.

    Example:
        >>> text = "Hello world! How are you?"
        >>> spacy_sentence_tokenizer(text)
        ['Hello world!', 'How are you?']
    """
    import spacy

    # Load the specified spaCy model
    nlp = spacy.load(model)

    # Use spaCy to tokenize sentences
    doc = nlp(text)
    return [sent.text.strip() for sent in doc.sents]


def latex_section_splitter(text: str, section: str = "section") -> list[str]:
    """
    Splits LaTeX text by specified sectioning commands (e.g., sections, subsections).

    Args:
        text (str): The LaTeX text to be split.
        section (str, optional): The section command to split by (e.g., 'section', 'subsection'). Defaults to "section".
            Available section commands:
            - "part": Splits by \part
            - "chapter": Splits by \chapter (useful in book documents)
            - "section": Splits by \section
            - "subsection": Splits by \subsection
            - "subsubsection": Splits by \subsubsection

    Returns:
        list of str: A list of LaTeX sections split by the specified section command.

    Example:
        >>> text = "\\section{Introduction} Text here. \\section{Conclusion} More text here."
        >>> latex_section_splitter(text, "section")
        ['\\section{Introduction} Text here.', '\\section{Conclusion} More text here.']
    """
    import re

    # Compile a regex pattern that captures the section command and its content
    pattern = re.compile(rf"(\\{section}{{[^}}]*}})", re.MULTILINE)
    parts = pattern.split(text)

    sections = []
    current_section = ""

    for part in parts:
        if pattern.match(part):
            if current_section:
                sections.append(current_section.strip())
            current_section = part  # Start with the section command
        else:
            current_section += part  # Append the content to the current section

    if current_section:
        sections.append(current_section.strip())

    return sections


# TODO: Removing this in the upcoming release as it's not used anywhere
# from typing import Union


# def recursive_splitter(
#     text: str, delimiters: list[str] = ["\n\n", "[.!?]"]
# ) -> Union[str, list]:
#     """
#     Recursively splits text based on a list of delimiters, supporting complex hierarchical splitting.

#     Args:
#         text (str): The text to be split.
#         delimiters (list of str, optional): A list of delimiters for splitting, in order of precedence from outermost to innermost.
#             Defaults to a set of common hierarchical delimiters.

#             Suggested Delimiters by Source Type:
#             - General Text (e.g., blogs, articles): ["\\n\\n", "[.!?]"] for paragraphs and sentences
#             - Books: ["\\n\\n", "Chapter", "Section", "Subsection", "[.!?]"] for chapters, sections, paragraphs, and sentences
#             - LaTeX: ["\\\\section", "\\\\subsection", "\\\\subsubsection", "\\n\\n", "[.!?]"] for sections, subsections, paragraphs, and sentences
#             - Markdown: ["^# ", "^## ", "^### ", "\\n\\n", "[.!?]"] for headers, subheaders, paragraphs, and sentences

#     Returns:
#         Union[str, list]: A nested structure of lists representing the text split at each level of delimiter,
#                           or a string if no further splitting is possible.

#     Example:
#         >>> text = "Chapter 1: Introduction\n\nThis is an intro. Chapter 2: Details\n\nBackground details here."
#         >>> recursive_splitter(text, ["Chapter", "\\n\\n", "[.!?]"])
#         [
#             ['1: Introduction', ['This is an intro']],
#             ['2: Details', ['Background details here']]
#         ]
#     """
#     import re

#     if not delimiters:
#         return text.strip()

#     delimiter = delimiters[0]
#     # Use capturing groups to retain delimiters
#     pattern = re.compile(f"({delimiter})", re.MULTILINE)
#     parts = pattern.split(text)

#     # Reassemble the parts to include the delimiter with the preceding segment
#     segments = []
#     current = ""
#     for i in range(0, len(parts), 2):
#         segment = parts[i].strip()
#         if i + 1 < len(parts):
#             segment += parts[i + 1]
#         if segment:
#             segments.append(segment)

#     if len(delimiters) == 1:
#         return segments

#     # Recursively split each segment with the remaining delimiters
#     return [recursive_splitter(seg, delimiters[1:]) for seg in segments]


def recursive_character_splitter_with_overlap(
    text: str,
    character_size: int = 800,
    overlap: int = 0,
    delimiters: list[str] = ["\n\n", "\n", "[.!?]", ",", " ", ""],
):
    import re

    def split_recursive(text, delimiters, max_size):
        if not delimiters:
            # Base case: split by character size
            if len(text) > max_size:
                chunks = []
                start = 0
                while start < len(text):
                    end = start + max_size
                    chunks.append(text[start:end])
                    start = end
                return chunks
            return [text]

        delimiter = delimiters[0]
        pattern = re.compile(delimiter)
        parts = pattern.split(text)
        chunks = []
        current_chunk = ""

        for part in parts:
            part = part.strip()
            if not part:
                continue

            # If adding this part exceeds max_size, process current_chunk
            if len(current_chunk) + len(part) > max_size:
                if current_chunk:
                    chunks.append(current_chunk)
                # Process the part with remaining delimiters
                if len(part) > max_size:
                    sub_chunks = split_recursive(part, delimiters[1:], max_size)
                    chunks.extend(sub_chunks)
                else:
                    current_chunk = part
            else:
                current_chunk = (
                    (current_chunk + " " + part).strip() if current_chunk else part
                )

        if current_chunk:
            chunks.append(current_chunk)

        return chunks

    chunks = split_recursive(text, delimiters, character_size)

    # Add overlap between chunks
    if overlap <= 0:
        return chunks

    final_chunks = []
    for i, chunk in enumerate(chunks):
        if i == 0:
            final_chunks.append(chunk)
            continue

        # Add overlap from previous chunk
        overlap_text = final_chunks[-1]
        while len(overlap_text) > overlap:
            overlap_text = " ".join(overlap_text.split(" ")[1:])
        final_chunks.append(overlap_text.lstrip() + " " + chunk.lstrip())

    return final_chunks
