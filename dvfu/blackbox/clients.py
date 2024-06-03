import logging
import uuid

from httpx import Client, AsyncClient

from dvfu.blackbox.tools import load_query_from_folder, replace_lesson_feedback_placeholders


class BlackBoxClient(Client):
    """
    Синхронный клиент
    """

    BASE_URL = 'https://blackbox.dvfu.ru/'

    def __init__(self, login: str, password: str, token: str):
        super().__init__(base_url=self.BASE_URL)
        self._login = login
        self._password = password
        self._token = token
        self._queries = load_query_from_folder()
        self.headers.update(
            {
                'user-agent': 'Dart/3.3 (dart:io)',
                'accept': '*/*',
                'accept-language': 'ru-RU',
                'host': 'blackbox.dvfu.ru',
                'content-type': 'application/json'
            }
        )
        self._short_token = self._create_short_token()

    def _create_short_token(self) -> str | None:
        response = self.post(
            url='v1/token',
            json={
                'username': self._login,
                'password': self._password,
            }
        )

        if response.status_code != 200:
            logging.error(f'Request failed with status code {response.status_code}')
            return None

        data = response.json().get('data')
        if data:
            return data.get('token')
        return None

    def get_short_token(self) -> str | None:
        return self._short_token

    def register_device(self, device_id=str(uuid.uuid4())) -> str | None:
        self.headers['authorization'] = f'Bearer {self._short_token}'
        response = self.post(
            url='v1/device/register',
            json={
                'device_id': f'{device_id}',
                'device_code': 'fcm',
                'device_description': 'flutter;null'
            }
        )

        if response.status_code != 200:
            logging.error(f'Request failed with status code {response.status_code}')
            return None

        data = response.json().get('data')
        if data:
            return data.get('user_id')
        return None

    def _schedule(self, query, variables=None) -> dict | None:
        self.headers['authorization'] = f'Bearer {self._token}'
        if variables is None:
            variables = {}

        response = self.post(
            url='v2/graphql/schedule',
            json={
                'operationName': None,
                'variables': variables,
                'query': query,
            }
        )

        if response.status_code != 200:
            logging.error(f'Request failed with status code {response.status_code}')
            return None

        data = response.json().get('data')
        if data:
            return data
        return None

    def profile(self) -> dict | None:
        query = self._queries['ReadProfile']
        return self._schedule(query)

    def get_news(self) -> dict | None:
        query = self._queries['ReadNews']
        variables = {
            'catalogCodes': ['mobile']
        }
        return self._schedule(query, variables)

    def read_news(self, news_id: int):
        query = self._queries['newsItem']
        variables = {
            'id': f'{news_id}'
        }
        return self._schedule(query, variables)

    def qr_code(self) -> dict | None:
        query = self._queries['userQrPassKey']
        return self._schedule(query)

    def lessons(self, start_time, end_time, group) -> dict | None:
        query = self._queries['ReadLessons']
        query = query.replace('#START_TIME#', f'{start_time}', 1)
        query = query.replace('#END_TIME#', f'{end_time}', 1)
        query = query.replace('"#GROUP#"', f'{group}', 1)

        return self._schedule(query)

    def can_lesson_feedback(self, lesson_guid: str) -> dict | None:
        query = self._queries['ReadLessonFeedback']
        query = query.replace('#LESSON_GUID#', f'{lesson_guid}', 1)
        return self._schedule(query)

    @DeprecationWarning
    def lesson_feedback(self, lesson_guid: str, interest: int = 0, usefulness: int = 0, clarity: int = 0,
                        violation_id: int = 0, comment: str = 'test'):
        # Не работает со стороны сервера

        """
        Оценить лекцию

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
        :return:
        """

        query = self._queries['UpdateLessonFeedback']
        query = replace_lesson_feedback_placeholders(
            query,
            lesson_guid,
            interest,
            usefulness,
            clarity,
            violation_id,
            comment
        )

        return self._schedule(query)

    def mfc_utils(self) -> dict | None:
        self.headers['authorization'] = f'Bearer {self._token}'

        response = self.get(
            url='v2/mfc/units',
        )

        if response.status_code != 200:
            logging.error(f'Request failed with status code {response.status_code}')
            return None

        data = response.json().get('data')
        if data:
            return data
        return None

    def mfc_user_requests(self) -> dict | None:
        self.headers['authorization'] = f'Bearer {self._token}'
        response = self.get(
            url='v2/user-requests',
        )

        if response.status_code != 200:
            logging.error(f'Request failed with status code {response.status_code}')
            return None

        data = response.json().get('data')
        if data:
            return data
        return None


class AsyncBlackBoxClient(AsyncClient):
    """
    Асинхронный клиент
    """

    BASE_URL = 'https://blackbox.dvfu.ru/'

    def __init__(self, login: str, password: str, token: str):
        super().__init__(base_url=self.BASE_URL)
        self._login = login
        self._password = password
        self._token = token
        self._queries = load_query_from_folder()
        self.headers.update(
            {
                'user-agent': 'Dart/3.3 (dart:io)',
                'accept': '*/*',
                'accept-language': 'ru-RU',
                'host': 'blackbox.dvfu.ru',
                'content-type': 'application/json'
            }
        )
        self._short_token = None

    async def _create_short_token(self) -> str | None:
        response = await self.post(
            url='v1/token',
            json={
                'username': self._login,
                'password': self._password,
            }
        )

        if response.status_code != 200:
            logging.error(f'Request failed with status code {response.status_code}')
            return None

        data = response.json().get('data')
        if data:
            return data.get('token')
        return None

    async def get_short_token(self) -> str | None:
        if not self._short_token:
            self._short_token = await self._create_short_token()
        return self._short_token

    async def register_device(self, device_id=str(uuid.uuid4())) -> str | None:
        self.headers['authorization'] = f'Bearer {await self.get_short_token()}'
        response = await self.post(
            url='v1/device/register',
            json={
                'device_id': f'{device_id}',
                'device_code': 'fcm',
                'device_description': 'flutter;null'
            }
        )

        if response.status_code != 200:
            logging.error(f'Request failed with status code {response.status_code}')
            return None

        data = response.json().get('data')
        if data:
            return data.get('user_id')
        return None

    async def _schedule(self, query, variables=None) -> dict | None:
        self.headers['authorization'] = f'Bearer {self._token}'
        if variables is None:
            variables = {}

        response = await self.post(
            url='v2/graphql/schedule',
            json={
                'operationName': None,
                'variables': variables,
                'query': query,
            }
        )

        if response.status_code != 200:
            logging.error(f'Request failed with status code {response.status_code}')
            return None

        data = response.json().get('data')
        if data:
            return data
        return None

    async def profile(self) -> dict | None:
        query = self._queries['ReadProfile']
        return await self._schedule(query)

    async def get_news(self) -> dict | None:
        query = self._queries['ReadNews']
        variables = {
            'catalogCodes': ['mobile']
        }
        return await self._schedule(query, variables)

    async def read_news(self, news_id: int):
        query = self._queries['newsItem']
        variables = {
            'id': f'{news_id}'
        }
        return await self._schedule(query, variables)

    async def qr_code(self) -> dict | None:
        query = self._queries['userQrPassKey']
        return await self._schedule(query)

    async def lessons(self, start_time, end_time, group) -> dict | None:
        query = self._queries['ReadLessons']
        query = query.replace('#START_TIME#', f'{start_time}', 1)
        query = query.replace('#END_TIME#', f'{end_time}', 1)
        query = query.replace('"#GROUP#"', f'{group}', 1)

        return await self._schedule(query)

    async def can_lesson_feedback(self, lesson_guid: str) -> dict | None:
        query = self._queries['ReadLessonFeedback']
        query = query.replace('#LESSON_GUID#', f'{lesson_guid}', 1)
        return await self._schedule(query)

    @DeprecationWarning
    async def lesson_feedback(self, lesson_guid: str, interest: int = 0, usefulness: int = 0, clarity: int = 0,
                              violation_id: int = 0, comment: str = 'test'):
        # Не работает со стороны сервера

        """
        Оценить лекцию

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
        :return:
        """

        query = self._queries['UpdateLessonFeedback']
        query = replace_lesson_feedback_placeholders(
            query,
            lesson_guid,
            interest,
            usefulness,
            clarity,
            violation_id,
            comment
        )

        return await self._schedule(query)

    async def mfc_utils(self) -> dict | None:
        self.headers['authorization'] = f'Bearer {self._token}'

        response = await self.get(
            url='v2/mfc/units',
        )

        if response.status_code != 200:
            logging.error(f'Request failed with status code {response.status_code}')
            return None

        data = response.json().get('data')
        if data:
            return data
        return None

    async def mfc_user_requests(self) -> dict | None:
        self.headers['authorization'] = f'Bearer {self._token}'
        response = await self.get(
            url='v2/user-requests',
        )

        if response.status_code != 200:
            logging.error(f'Request failed with status code {response.status_code}')
            return None

        data = response.json().get('data')
        if data:
            return data
        return None
