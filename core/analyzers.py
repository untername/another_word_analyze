"""
Модуль с классом для анализа текста.

[Analyzer]
    [wordcount]: Подсчет частотности слов.
    [text polarity]: Анализ эмоционального окраса текста.
    [get correct]: Корректировка ошибок, варианты правильного написания слов.
    [get definitions]: Определения полученных слов.
    [synonyms]: Поиск синонимов.
    [antonyms]: Поиск антонимов.
    [ru translate]: Перевод на русский.

В дальнейшем методы будут добавляться.
"""

from textblob import TextBlob, Word
from textblob.exceptions import NotTranslated
from typing import Dict, Union, List
import operator


class Analyzer:

    """
    Класс, объединяющий методы обработки и анализа текста.
    """

    def __init__(self, text):

        txt = TextBlob(text)
        self.text = txt.translate(to='en') if txt.detect_language() != 'en' else txt

    async def wordcount(self) -> Dict[str, str]:

        """
        Функция, подсчитывающая частотность слов. Отбрасывает ненужные символы и сортирует результат.
        """

        result = sorted(
            {x: [y] for x in self.text.word_counts.items() for y in self.text.word_counts.items()},
            key=operator.itemgetter(1), reverse=True)

        return dict(result)

    async def text_polarity(self) -> Union[str, Dict[str, str]]:

        """
        Метод, анализирующая полярность и субъективность полученного текста.

        Для корректной работы все переводится на английский язык, а уже потом анализируется.
        """

        result = {
            "Polariry": str(self.text.sentiment.polarity),
            "Subjectivity": str(self.text.sentiment.subjectivity)}

        return result

    async def get_correct(self) -> Dict[str, Union[str, Dict]]:

        """
        Метод, возвращающая текст без ошибок и варианты правильного написания слов.
        """

        corrected_word = self.text.correct()
        correctly_vars: Dict = {x: str(Word(x).spellcheck()[0][0]) for x in self.text.words}

        return {
            "corrected": str(corrected_word),
            "correctly words": correctly_vars}

    async def get_definitions(self) -> Dict[str, Union[List, str]]:

        """
        Функция для нахождения определений конкретных слов.
        """

        words: List = []
        definitions: List = []

        for x in self.text.words:
            defins: List = [z for z in Word(x).definitions]

            if len(defins) > 0:
                words.append(x)
                definitions.append(defins)

        couple = dict(zip(words, definitions))
        return couple

    async def get_synonyms(self) -> Dict[str, List[str]]:

        """
        Функция, находящая синонимы каждого слова в полученном тексте.

        Для корректной работы текст изначально переводится на английский.
        """

        words: List = []
        synonims: List = []

        for x in self.text.words:
            syns = set()
            item = Word(x)
            for synset in item.synsets:
                for lem in synset.lemmas():
                    syns.add((lem.name().replace('_', ' ').capitalize()))

            synsy = list(syns)

            if len(synsy) >= 2:
                words.append(x.capitalize())
                synonims.append(synsy)

        result = dict(zip(words, synonims))
        return result

    async def get_antonyms(self) -> Dict[str, str]:

        """
        Функция, возвращающая список антонимов.
        """

        words: List = []
        antonyms: List = []

        for x in self.text.words:

            xword = Word(x)
            x_antonyms: List = []

            for synset in xword.synsets:
                for lemmas in synset.lemmas():
                    try:
                        _ = lemmas.antonyms()[0]
                    except IndexError:
                        continue
                    else:
                        word_ant = lemmas.antonyms()
                        x_antonyms.append((word_ant[0].name().replace('_', ' ').capitalize()))

            if len(x_antonyms) >= 1:
                words.append(x.capitalize())
                antonyms.append(x_antonyms)

        result = dict(zip(words, antonyms))
        return result

    async def ru_translate(self) -> str:

        """
        Ничего необычного. Функция, переводящая с русского на английский или наоборот.
        """

        try:
            response = self.text.translate(to="ru")
        except NotTranslated:
            response = """Unfortunately, the language could not be determined.
            Perhaps the text contains words from several languages. If so, check them separately."""

        return str(response)
