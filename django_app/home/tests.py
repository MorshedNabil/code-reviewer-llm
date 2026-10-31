from django.test import SimpleTestCase
from django_app.home.review_engine.github.github import extract_changed_lines


class ExtractChangedLinesTests(SimpleTestCase):
    def test_extracts_added_and_deleted_lines_with_file_line_numbers(self):
        patch = """@@ -2,4 +2,5 @@
 context
-old line
+new line
 another context line
+last addition
"""

        self.assertEqual(
            extract_changed_lines(patch),
            "\n".join(
                [
                    "- [old line 3] old line",
                    "+ [new line 3] new line",
                    "+ [new line 5] last addition",
                ]
            ),
        )

    def test_returns_empty_string_when_patch_has_no_changes(self):
        self.assertEqual(extract_changed_lines("@@ -1,1 +1,1 @@\n unchanged"), "")
