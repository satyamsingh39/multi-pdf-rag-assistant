from __future__ import annotations

import unittest

from multipdf_chat.text_utils import (
    extract_requested_page_numbers,
    normalize_text,
    response_content_to_text,
    select_best_sentences,
)


class TextUtilsTests(unittest.TestCase):
    def test_normalize_text_collapses_whitespace(self):
        self.assertEqual(normalize_text("Hello   world\n\nagain"), "Hello world again")

    def test_extract_requested_page_numbers_finds_multiple_pages(self):
        question = "Compare page 2 with page 10 and mention page 2 again."
        self.assertEqual(extract_requested_page_numbers(question), {2, 10})

    def test_response_content_to_text_handles_mixed_list_content(self):
        content = ["first", {"text": "second"}, 3]
        self.assertEqual(response_content_to_text(content), "first\nsecond\n3")

    def test_select_best_sentences_prefers_question_overlap(self):
        text = "Cats sleep often. Dogs bark loudly. Dogs like walks."
        selected = select_best_sentences("Why do dogs bark?", text, limit=1)
        self.assertEqual(selected, ["Dogs bark loudly."])


if __name__ == "__main__":
    unittest.main()
