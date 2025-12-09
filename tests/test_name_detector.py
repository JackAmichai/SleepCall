import pytest
from name_detector import NameDetector

class TestNameDetector:
    def test_exact_match(self):
        detector = NameDetector(target_names=["Jack", "Amichai"])
        assert detector.is_name_mentioned("Hello Jack, how are you?")
        assert detector.is_name_mentioned("Is Amichai there?")
        assert not detector.is_name_mentioned("Hello world")

    def test_case_insensitive(self):
        detector = NameDetector(target_names=["Jack"])
        assert detector.is_name_mentioned("hello jack")
        assert detector.is_name_mentioned("JACK!")

    def test_fuzzy_match(self):
        detector = NameDetector(target_names=["Amichai"], fuzz_threshold=80)
        # Typo
        assert detector.is_name_mentioned("Hello Amicha, how are you?")

    def test_find_mentioned_names(self):
        detector = NameDetector(target_names=["Jack", "Amichai"])
        names = detector.find_mentioned_names("Jack and Amichai are here")
        assert "Jack" in names
        assert "Amichai" in names
        assert len(names) == 2

    def test_empty_input(self):
        detector = NameDetector(target_names=["Jack"])
        assert not detector.is_name_mentioned("")
        assert not detector.is_name_mentioned(None)
