from unittest import TestLoader


def get_tests():
    return TestLoader().discover('tests/')
