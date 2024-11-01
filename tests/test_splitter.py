import pytest
from missing_text.splitter.util import (
    regex_splitter,
    character_splitter,
    sentence_splitter,
    paragraph_splitter,
    markdown_header_splitter,
    json_key_splitter,
    html_tag_attribute_splitter,
    python_code_splitter,
    nltk_sentence_tokenizer,
    spacy_sentence_tokenizer,
    latex_section_splitter,
    # recursive_splitter,
    recursive_character_splitter_with_overlap,
)


def test_regex_splitter():
    text = "apple;banana;cherry"
    assert regex_splitter(text, r";") == ["apple", "banana", "cherry"]


def test_character_splitter():
    text = "This is a test sentence for character splitting."
    assert character_splitter(text, chunk_size=10, overlap=2) == [
        "This is a ",
        "a test sen",
        "entence fo",
        "for charac",
        "acter spli",
        "litting.",
    ]


def test_sentence_splitter():
    text = "This is a sentence. This is another sentence. This is a third sentence."
    assert sentence_splitter(text) == [
        "This is a sentence.",
        "This is another sentence.",
        "This is a third sentence.",
    ]


def test_paragraph_splitter():
    text = "Paragraph 1\n\nParagraph 2\n\nParagraph 3"
    assert paragraph_splitter(text) == ["Paragraph 1", "Paragraph 2", "Paragraph 3"]


def test_markdown_header_splitter():
    text = "# Section 1\n\n## Subsection 1.1\n\n# Section 2\n\n## Subsection 2.1"
    assert markdown_header_splitter(text, level=1) == [
        "# Section 1\n\n## Subsection 1.1",
        "# Section 2\n\n## Subsection 2.1",
    ]


def test_json_key_splitter():
    json_data = {
        "name": "Document",
        "sections": [
            {"title": "Introduction", "content": "Welcome to the introduction."},
            {"title": "Body", "content": "This is the main content."},
            {"title": "Conclusion", "content": "Thank you for reading."},
        ],
    }
    assert json_key_splitter(json_data, "content") == [
        "Welcome to the introduction.",
        "This is the main content.",
        "Thank you for reading.",
    ]


def test_html_tag_attribute_splitter():
    html_content = "<div>Hello</div><p>World</p><div>Example</div>"
    assert html_tag_attribute_splitter(html_content, "div") == ["Hello", "Example"]


def test_python_code_splitter():
    code = "def func1(): pass\ndef func2(): pass"
    assert python_code_splitter(code, "def") == [
        "def func1(): pass",
        "def func2(): pass",
    ]


@pytest.mark.skip(reason="Requires NLTK download, consider mocking")
def test_nltk_sentence_tokenizer():
    text = "Hello world! How are you?"
    assert nltk_sentence_tokenizer(text) == ["Hello world!", "How are you?"]


@pytest.mark.skip(reason="Requires spaCy model, consider mocking")
def test_spacy_sentence_tokenizer():
    text = "Hello world! How are you?"
    assert spacy_sentence_tokenizer(text) == ["Hello world!", "How are you?"]


def test_latex_section_splitter():
    text = "\\section{Introduction} Text here. \\section{Conclusion} More text here."
    assert latex_section_splitter(text, "section") == [
        "\\section{Introduction} Text here.",
        "\\section{Conclusion} More text here.",
    ]


# def test_recursive_splitter():
#     text = "Chapter 1: Introduction\n\nThis is an intro. Chapter 2: Details\n\nBackground details here."
#     expected = [
#         ["Chapter 1: Introduction", ["This is an intro."]],
#         ["Chapter 2: Details", ["Background details here."]],
#     ]
#     assert recursive_splitter(text, ["Chapter", "\n\n", "[.!?]"]) == expected


def test_recursive_character_splitter_with_overlap():
    text = """
One of the most important things I didn't understand about the world when I was a child is the degree to which the returns for performance are superlinear.

Teachers and coaches implicitly told us the returns were linear. "You get out," I heard a thousand times, "what you put in." They meant well, but this is rarely true. If your product is only half as good as your competitor's, you don't get half as many customers. You get no customers, and you go out of business.
"""
    chunks = recursive_character_splitter_with_overlap(
        text, character_size=100, overlap=50
    )

    assert chunks == [
        "One of the most important things I didn't understand about the world when I was a child is the degree",
        "about the world when I was a child is the degree to which the returns for performance are superlinear",
        "which the returns for performance are superlinear Teachers and coaches implicitly told us the returns were linear",
        'coaches implicitly told us the returns were linear "You get out," I heard a thousand times, "what you put in " They meant well, but this is rarely true',
        "put in \" They meant well, but this is rarely true If your product is only half as good as your competitor's, you don't get half as many customers",
        "competitor's, you don't get half as many customers You get no customers, and you go out of business",
    ]

    # Test with no overlap
    chunks_no_overlap = recursive_character_splitter_with_overlap(
        text, character_size=200, overlap=0
    )

    assert chunks_no_overlap == [
        "One of the most important things I didn't understand about the world when I was a child is the degree to which the returns for performance are superlinear.",
        'Teachers and coaches implicitly told us the returns were linear "You get out," I heard a thousand times, "what you put in " They meant well, but this is rarely true',
        "If your product is only half as good as your competitor's, you don't get half as many customers You get no customers, and you go out of business",
        "One of the most important things I didn't understand about the world when I was a child is the degree to which the returns for performance are superlinear.",
    ]
