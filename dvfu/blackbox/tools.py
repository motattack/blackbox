import os


def load_query_from_folder(folder_path: str = 'queries', end_format: str = '.gql'):
    """
    Загрузка GraphQl файлов из папки folder_path
    :param folder_path: папка, где лежат файлы
    :param end_format: окончания у имен файлов
    :return: именованный (именами файлов без окончания) список со значениями (содержимым файлов).
    """

    queries = {}
    current_dir = os.path.dirname(__file__)
    folder_path = os.path.join(current_dir, folder_path)
    gql_files = [file for file in os.listdir(folder_path) if file.endswith(end_format)]
    for file_name in gql_files:
        with open(os.path.join(folder_path, file_name), 'r', encoding='utf-8') as file:
            queries[file_name[:-len(end_format)]] = file.read()
    return queries


def replace_lesson_feedback_placeholders(query: str, lesson_guid: str, interest: int, usefulness: int,
                                         clarity: int, violation_id: int, comment: str) -> str:
    """
    Функция для подстановки значений в query
    :param query: UpdateLessonFeedback
    :param lesson_guid: Уникальный идентификатор лекции (GUID).
    :param interest: Оценка интересности лекции. Допустимые значения: [-2, -1, 0, 1, 2].
    :param usefulness: Оценка полезности лекции. Допустимые значения: [-2, -1, 0, 1, 2].
    :param clarity: Оценка понятности лекции. Допустимые значения: [-2, -1, 0, 1, 2].
    :param violation_id: Идентификатор возникшей проблемы:
        - 0: Проблем не возникло
        - 1: Конфликт между преподавателем и обучающимся
        - 2: Неисправность оборудования
        - 3: Некомфортные условия
        - 4: Преподаватель не явился на пару
    :param comment: Ваш комментарий
    :return: query UpdateLessonFeedback с подставленными значениями
    """

    query = query.replace('#LESSON_GUID#', f'{lesson_guid}', 1)
    query = query.replace('#LESSON_INTEREST#', f'{interest}', 1)
    query = query.replace('#LESSON_USEFULNESS#', f'{usefulness}', 1)
    query = query.replace('#LESSON_CLARITY#', f'{clarity}', 1)
    query = query.replace('#LESSON_VIOLATION_ID#', f'{violation_id}', 1)
    query = query.replace('#LESSON_COMMENT#', f'{comment}', 1)
    return query
