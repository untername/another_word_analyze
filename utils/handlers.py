from typing import Union, Dict, Tuple, List
from core.analyzers import Analyzer


async def text_handler(method: List, text: str) -> Dict[str, Union[str, Tuple, Dict]]:

    """
    Функция, обрабатывающая текст, введенный в текстовое поле или отправленный в файле.

    Возвращает список результатов анализа, в зависимости от выбора.
    """

    response: Dict = {}
    analyzer = Analyzer(text)

    if 'translate' in method:
        translate_response = await analyzer.ru_translate()
        response['translate'] = translate_response
    if 'definitions' in method:
        define_resp = await analyzer.get_definitions()
        response['definitions'] = define_resp
    if 'correct' in method:
        corr_resp = await analyzer.get_correct()
        response['correct'] = corr_resp
    if 'emocolor' in method:
        emocolor_response = await analyzer.text_polarity()
        response['emotional-color'] = emocolor_response
    if 'count-words' in method:
        count_response = await analyzer.wordcount()
        response['count-words'] = count_response
    if 'synonyms' in method:
        syn_response = await analyzer.get_synonyms()
        response['synonyms'] = syn_response
    if 'antonyms' in method:
        ant_response = await analyzer.get_antonyms()
        response['antonyms'] = ant_response

    return response
