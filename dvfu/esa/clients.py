from httpx import Client, AsyncClient


class EsaClient(Client):
    """
    Синхронный клиент
    """
    BASE_URL = 'https://esa.dvfu.ru/'

    def __init__(self, login: str, password: str, basic_code: str) -> None:
        """
        Инициализация синхронного клиента

        :param login: логин пользователя
        :param password: пароль пользователя
        :param basic_code: код приложения в Base64
        """

        super().__init__(base_url=self.BASE_URL)
        self._login = login
        self._password = password
        self.headers.update(
            {
                'user-agent': 'Dart/3.3 (dart:io)',
                'accept': 'application/json',
                'cache-control': 'no-cache',
                'authorization': f'Basic {basic_code}',
                'host': 'esa.dvfu.ru',
                'content-type': 'application/json'
            }
        )
        self._token = self._create_token()

    def _create_token(self) -> str | None:
        """
        Запрос на получение токена
        :return: токен
        """

        response = self.post(
            url='oauth/token/create/',
            json={
                'grant_type': 'password',
                'username': self._login,
                'password': self._password,
            }
        )
        return response.json().get('access_token')

    def get_token(self) -> str | None:
        return self._token


class AsyncEsaClient(AsyncClient):
    """
    Асинхронный клиент
    """

    BASE_URL = 'https://esa.dvfu.ru/'

    def __init__(self, login: str, password: str, basic_code: str) -> None:
        """
        Инициализация асинхронного клиента

        :param login: логин пользователя
        :param password: пароль пользователя
        :param basic_code: код приложения в Base64
        """

        super().__init__(base_url=self.BASE_URL)
        self._login = login
        self._password = password
        self.headers.update(
            {
                'user-agent': 'Dart/3.3 (dart:io)',
                'accept': 'application/json',
                'cache-control': 'no-cache',
                'authorization': f'Basic {basic_code}',
                'host': 'esa.dvfu.ru',
                'content-type': 'application/json'
            }
        )
        self._token = self._create_token()

    async def _create_token(self) -> str | None:
        """
        Запрос на получение токена
        :return: токен
        """

        response = await self.post(
            'oauth/token/create/',
            json={
                'grant_type': 'password',
                'username': self._login,
                'password': self._password,
            }
        )
        return response.json().get('access_token')

    async def get_token(self) -> str | None:
        return await self._token
