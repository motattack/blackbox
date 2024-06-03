# Неофициальная библиотека для работы с esa и blackbox

- **WARNING:** Используйте на свой страх и риск, нет никаких гарантий работоспособности

Библиотека работает в синхронном и асинхронном режиме:
```py
from dvfu.esa import EsaClient, AsyncEsaClient
from dvfu.blackbox import BlackBoxClient, AsyncBlackBoxClient
```

## Установка
```bash
pip install poetry
poetry install
```

## Пример использования синхронного клиента:
```py
from dvfu.esa import EsaClient

client = EsaClient(
    login='',
    password='',
    basic_code='YnJpY3M6MTIzMzIx'
)

token = client.get_token()
print(token)
```

```py
from dvfu.blackbox import BlackBoxClient
bb = BlackBoxClient(
    login='',
    password='',
    token=token
)
```
Получить новости:
```py
print(bb.get_news())
```
Получить информацию о профиле
```py
print(bb.profile())
```