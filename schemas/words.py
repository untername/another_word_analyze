from enum import Enum


class Choices(str, Enum):

    """
    Класс, созданный для создания вариантов выбора анализа текста.
    """

    translate = 'translate'
    emocolor = 'emocolor'
    count_words = 'count-words'
    synonyms = 'synonyms'
    antonyms = 'antonyms'
    definitions = 'definitions'
    correct = 'correct'
