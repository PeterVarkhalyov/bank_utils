# Учебный проект по Python

## Вступление

Учебный Python-проект для маскировки номеров банковских карт и счетов, а
также для преобразования даты из ISO-формата в привычный формат
`ДД.ММ.ГГГГ`.

## Возможности

- маскировка номера банковской карты;
- маскировка номера банковского счёта;
- автоматическое распознавание карты или счёта по входной строке;
- преобразование даты;
- фильтрация операций по статусу;
- фильтрация операций по коду валюты;
- сортировка операций по дате;
- последовательная обработка транзакций с помощью генераторов;
- генерация номеров банковских карт в заданном диапазоне;
- логирование результатов выполнения функций в консоль или файл;
- обработка JSON-файлов или ответов от API в формате JSON;
- обработка CSV и Excel файлов;
- конвертация суммы транзакции в целевую валюту с помощью Exchange Rates Data API;
- логированние;
- выбирает банковские операции по строке в описании `description`;
- производит расчет количества банковских операций по категориям `description`;
- настройка полей различных источников данных через конфигурационный файл;
- интерактивная обработка и вывод транзакций через консольное меню;
- проверка кода с помощью Flake8, Black, isort и mypy.

- ## Структура проекта

```text
.
├── config/
│   └── field_aliases.json
├── data/
│   ├── operations.json
│   ├── transactions.csv
│   └── transactions_excel.xlsx
├── htmlcov/
├── logs/
├── src/
│   ├── __init__.py
│   ├── decorators.py
│   ├── external_api.py
│   ├── fields.py
│   ├── generators.py
│   ├── masks.py
│   ├── processing.py
│   ├── readers.py
│   ├── utils.py
│   └── widget.py
├── tests/
│   ├── __init__.py
│   ├── test_decorators.py
│   ├── test_external_api.py
│   ├── test_fields.py
│   ├── test_generators.py
│   ├── test_logging.py
│   ├── test_main.py
│   ├── test_masks.py
│   ├── test_processing.py
│   ├── test_readers.py
│   ├── test_utils.py
│   └── test_widget.py
├── .coverage
├── .env
├── .env.example
├── .flake8
├── .gitignore
├── main.py
├── pyproject.toml
├── poetry.lock
└── README.md
```

## Требования

- Python 3.12 или новее;
- Poetry 2.x;
- Git — для клонирования проекта с GitHub.

Проверить установленные версии можно командами:

```shell
python --version
poetry --version
git --version
```

## Установка проекта с GitHub

1. На странице репозитория GitHub нажмите **Code** и скопируйте HTTPS-адрес.
2. Клонируйте репозиторий, заменив `USERNAME/REPOSITORY` на данные проекта:

   ```shell
   git clone https://github.com/USERNAME/REPOSITORY.git
   ```

3. Перейдите в каталог проекта:

   ```shell
   cd REPOSITORY
   ```

4. Установите зависимости из `poetry.lock`:

   ```shell
   poetry install
   ```

5. Проверьте, что проект работает:

   ```shell
   poetry run python -m unittest discover -v
   ```

Поскольку GitHub-адрес ещё не привязан к текущему локальному репозиторию,
`USERNAME/REPOSITORY` в примерах необходимо заменить на реальный адрес после
публикации проекта.

## Использование

Функции можно импортировать и вызвать из Python-консоли:

```shell
poetry run python
```

```python
from src.generators import filter_by_currency, transaction_descriptions, card_number_generator
from src.masks import get_mask_account, get_mask_card_number
from src.processing import filter_by_state, sort_by_date
from src.widget import get_date, mask_account_card

transactions = [{'id': 41428829, 'state': 'EXECUTED', 'date': '2019-07-03T18:35:29.512364'},
                {'id': 939719570, 'state': 'EXECUTED', 'date': '2018-06-30T02:08:58.425572'},
                {'id': 594226727, 'state': 'CANCELED', 'date': '2018-09-12T21:27:25.241689'},
                {'id': 615064591, 'state': 'CANCELED', 'date': '2018-10-14T08:21:33.419441'}]

print(get_mask_card_number("7000792289606361"))
print(get_mask_account("73654108430135874305"))
print(mask_account_card("Visa Platinum 7000792289606361"))
print(get_date("2024-03-11T02:26:18.671407"))
print(filter_by_state(transactions))
print(sort_by_date(transactions))
```

Результат:

```text
7000 79** **** 6361
**4305
Visa Platinum 7000 79** **** 6361
11.03.2024
[{'id': 41428829, 'state': 'EXECUTED', 'date': '2019-07-03T18:35:29.512364'}, {'id': 939719570, 'state': 'EXECUTED', 'date': '2018-06-30T02:08:58.425572'}]
[{'id': 41428829, 'state': 'EXECUTED', 'date': '2019-07-03T18:35:29.512364'}, {'id': 615064591, 'state': 'CANCELED', 'date': '2018-10-14T08:21:33.419441'}, {'id': 594226727, 'state': 'CANCELED', 'date': '2018-09-12T21:27:25.241689'}, {'id': 939719570, 'state': 'EXECUTED', 'date': '2018-06-30T02:08:58.425572'}]
```

## Модуль `main`

Файл `main.py` является точкой входа в приложение и связывает функции чтения,
фильтрации, сортировки и форматирования банковских операций.

Запуск консольной программы:

```shell
poetry run python main.py
```

Во время работы программа последовательно предлагает:

1. выбрать источник данных: JSON, CSV или XLSX;
2. отфильтровать операции по статусу;
3. при необходимости отсортировать операции по дате;
4. оставить только рублёвые операции;
5. выполнить поиск по слову в описании;
6. вывести найденные операции с замаскированными реквизитами.

При вводе неподдерживаемого значения соответствующий вопрос задаётся повторно.
Каждая найденная операция выводится в формате:

```text
11.03.2024 Перевод организации
Visa Platinum 7000 79** **** 6361 -> Счет **4305
100.00 RUB (руб.)
```

Если операции, соответствующие выбранным условиям, отсутствуют, программа
выводит сообщение и завершает работу без ошибки.

## Модуль `masks`

Модуль `src.masks` содержит базовые функции маскировки банковских данных.

### `get_mask_card_number`

```python
get_mask_card_number(card_number: str) -> str | None
```

Принимает номер банковской карты в виде строки. Корректный номер должен
содержать ровно 16 цифр. Функция оставляет видимыми первые шесть и последние
четыре цифры, а остальные заменяет звёздочками.

```python
get_mask_card_number("7000792289606361")
# "7000 79** **** 6361"
```

Если длина номера не равна 16 или строка содержит не только цифры, функция
возвращает `None`:

```python
get_mask_card_number("700079228960636a")
# None
```

### `get_mask_account`

```python
get_mask_account(account_number: str) -> str | None
```

Принимает номер банковского счёта длиной не менее четырёх символов. Функция
оставляет видимыми последние четыре символа и добавляет перед ними две
звёздочки.

```python
get_mask_account("73654108430135874305")
# "**4305"
```

Если номер короче четырёх символов, функция возвращает `None`.

## Модуль `widget`

Модуль `src.widget` объединяет функции маскировки и содержит преобразование
даты.

### `mask_account_card`

```python
mask_account_card(account_card: str) -> str
```

Принимает строку, состоящую из типа карты или счёта и номера. Последнее слово
считается номером, поэтому тип карты может состоять из нескольких слов.

```python
mask_account_card("Visa Platinum 7000792289606361")
# "Visa Platinum 7000 79** **** 6361"
```

Значения `Счет`, `Счёт` и `Account` распознаются как банковский счёт без учёта
регистра:

```python
mask_account_card("Счёт 73654108430135874305")
# "Счёт **4305"

mask_account_card("ACCOUNT 73654108430135874305")
# "ACCOUNT **4305"
```

При некорректном номере функция возвращает сообщение:

```python
mask_account_card("Visa 1234")
# "Некорректный номер карты или счёта"
```

Если строка не содержит одновременно тип и номер, возвращается сообщение
`"Укажите тип и номер карты или счёта"`.

### `get_date`

```python
get_date(date_string: str) -> str
```

Принимает дату в ISO-формате и возвращает её в формате `ДД.ММ.ГГГГ`:

```python
get_date("2024-03-11T02:26:18.671407")
# "11.03.2024"
```

Если дата или её формат некорректны, функция создаёт исключение `ValueError`.

## Модуль `processing`

Модуль `src.processing` содержит функции фильтрации и сортировки списков

### `filter_by_state`

```python
filter_by_state(transactions: list[Transaction], state: str = "EXECUTED") -> list[Transaction]
```

Принимает список словарей с данными банковских операций и статус для фильтрации. По умолчанию ``EXECUTED``.

```python
filter_by_state([{'id': 41428829, 'state': 'EXECUTED', 'date': '2019-07-03T18:35:29.512364'},
                 {'id': 939719570, 'state': 'EXECUTED', 'date': '2018-06-30T02:08:58.425572'},
                 {'id': 594226727, 'state': 'CANCELED', 'date': '2018-09-12T21:27:25.241689'},
                 {'id': 615064591, 'state': 'CANCELED', 'date': '2018-10-14T08:21:33.419441'}])
[{'id': 41428829, 'state': 'EXECUTED', 'date': '2019-07-03T18:35:29.512364'}, {'id': 939719570, 'state': 'EXECUTED', 'date': '2018-06-30T02:08:58.425572'}]
```

### `filter_by_currency_code`

```python
filter_by_currency_code(transactions: list[Transaction], currency_code: str = "RUB",) -> list[Transaction]
```

Функция возвращает банковские операции с указанным кодом валюты.
Код валюты извлекается из вложенного поля ``operationAmount.currency.code``. 
Операции с отсутствующей или некорректной структурой этого поля пропускаются.

Функция принимает:
- список словарей с данными банковских операций;
- Код валюты для фильтрации. По умолчанию ``RUB``.

Функция возвращает:
- новый список операций с указанным кодом валюты.

### `sort_by_date`

```python
sort_by_date(transactions: list[Transaction], descending: bool = True) -> list[Transaction]
```

Принимает список словарей и необязательный параметр, задающий порядок сортировки (по умолчанию — убывание). Возвращает новый список, отсортированный по дате (date).

```python
sort_by_date([{"id": 41428829, "state": "EXECUTED", "date": "2019-07-03T18:35:29.512364"},
              {"id": 939719570, "state": "EXECUTED", "date": "2018-06-30T02:08:58.425572"},
              {"id": 594226727, "state": "CANCELED", "date": "2018-09-12T21:27:25.241689"},
              {"id": 615064591, "state": "CANCELED", "date": "2018-10-14T08:21:33.419441"}])
[{'id': 41428829, 'state': 'EXECUTED', 'date': '2019-07-03T18:35:29.512364'}, {'id': 615064591, 'state': 'CANCELED', 'date': '2018-10-14T08:21:33.419441'}, {'id': 594226727, 'state': 'CANCELED', 'date': '2018-09-12T21:27:25.241689'}, {'id': 939719570, 'state': 'EXECUTED', 'date': '2018-06-30T02:08:58.425572'}]
```

### `process_bank_search`

```python
process_bank_search(transactions: list[Transaction], search_string: str) -> list[Transaction]
```

Функция выбирает банковские операции по строке в описании.
Поиск выполняется без учёта регистра. Строка поиска обрабатывается как 
обычный текст, поэтому специальные символы регулярных выражений не изменяют 
её смысл. Операции без строкового поля ``description``  пропускаются.

Функция принимает:
- список банковских операций;
- строка, которую нужно найти в описании операции.

Функция возвращает:
- новый список операций, описания которых содержат строку поиска; 
- для пустой строки поиска возвращается пустой список.

### `process_bank_operations`

```python
process_bank_operations(transactions: list[Transaction], categories: list[str]) -> dict[str, int]
```

Функция производит расчет количества банковских операций по категориям.
Название категории сравнивается с полем ``description`` операции.
Категории, для которых операции не найдены, остаются в результате
со значением ``0``.

Функция принимает:
- список банковских операций;
- список названий категорий операций.

Функция возвращает:
- словарь с количеством операций в каждой категории.

## Модуль `generators`

Модуль `src.generators` содержит ленивые генераторы. Они возвращают значения
по одному и не создают полный результат в памяти.

Примеры ниже используют следующий список транзакций:

```python
transactions = [
    {
        "id": 1,
        "description": "Перевод организации",
        "operationAmount": {
            "amount": "100.00",
            "currency": {"name": "Доллар США", "code": "USD"},
        },
    },
    {
        "id": 2,
        "description": "Перевод со счета на счет",
        "operationAmount": {
            "amount": "250.00",
            "currency": {"name": "Российский рубль", "code": "RUB"},
        },
    },
]
```

### `filter_by_currency`

```python
filter_by_currency(transactions: list[Transaction], currency: str,) -> Iterator[Transaction]
```

Возвращает итератор по транзакциям с заданным кодом валюты. Порядок исходного
списка сохраняется.

```python
from src.generators import filter_by_currency

usd_transactions = filter_by_currency(transactions, "USD")

print(next(usd_transactions))
# Транзакция с id=1
```

Получить все подходящие транзакции можно с помощью `list`, если набор данных
не слишком большой:

```python
list(filter_by_currency(transactions, "USD"))
```

### `transaction_descriptions`

```python
transaction_descriptions(transactions: list[Transaction],) -> Iterator[str]
```

Поочерёдно возвращает значения ключа `description`:

```python
from src.generators import transaction_descriptions

descriptions = transaction_descriptions(transactions)

print(next(descriptions))
# Перевод организации

print(next(descriptions))
# Перевод со счета на счет
```

### `card_number_generator`

```python
card_number_generator(start: int, stop: int) -> Iterator[str]
```

Генерирует номера карт в диапазоне от `start` до `stop` включительно. Каждый
номер дополняется нулями до 16 цифр и разбивается на четыре блока.

```python
from src.generators import card_number_generator

for card_number in card_number_generator(1, 3):
    print(card_number)
```

Результат:

```text
0000 0000 0000 0001
0000 0000 0000 0002
0000 0000 0000 0003
```

Допустимые значения находятся в диапазоне от `1` до `9999999999999999`.
Некорректные границы вызывают `ValueError` при начале обхода генератора.

## Модуль `decorators`

Модуль `src.decorators` содержит типизированный декоратор `log`, который
записывает итог выполнения функции. Декоратор сохраняет исходную сигнатуру,
возвращаемый тип, имя и документацию функции.

### `log`

```python
log(filename: str | None = None)
```

Без аргумента `filename` сообщение выводится в консоль:

```python
from src.decorators import log


@log()
def add(x: int, y: int) -> int:
    return x + y


result = add(1, 2)
# В консоли: add ok
# result == 3
```

Если передать имя файла, сообщения добавляются в конец этого файла:

```python
@log(filename="mylog.txt")
def multiply(x: int, y: int) -> int:
    return x * y


multiply(2, 3)
# Содержимое mylog.txt: multiply ok
```

При ошибке записываются имя функции, текст исключения и входные параметры:

```python
@log()
def divide(x: int, y: int) -> float:
    return x / y


divide(1, 0)
# divide error: division by zero. Inputs: (1, 0), {}
```

После логирования исходное исключение выбрасывается повторно. Вызывающий код
может обработать его конструкцией `try/except`.

## Модуль `utils`

Модуль `src.utils` объединяет функции JSON-файла, содержащего транзакции. Файл, 
содержащий транзакции находится в `data/operations.json`.

### Структура данных

Структура транзакции из `data/operations.json`:

```python
{
    "id": int,
    "state": string,
    "date": datetime,
    "operationAmount": {
      "amount": string,
      "currency": {
        "name": string,
        "code": string
      }
    },
    "description": string,
    "from": string,
    "to": string"
}
```
Значение ключей:

| Key                           | Type     | Required | Descript                     |
|-------------------------------|----------|----------|------------------------------|
| id                            | integer  | Yes      | Идентификатор транзакции     |
| state                         | string   | Yes      | Статус транзакции            |
| date                          | datetime | Yes      | Дата и время транзакции      |
| operationAmount.amount        | string   | Yes      | Сумма транзакции             |
| operationAmount.currency.name | string   | No       | Название валюты транзакции   |
| operationAmount.currency.code | string   | Yes      | Код валюты транзакции в ISO  |
| description                   | string   | No       | Описание транзакции          |
| from                          | string   | Yes      | Отправитель (счет или карта) |
| to                            | string   | Yes      | Получатель (счет или карта)  |

### `get_transactions_from_json`

```python
get_transactions_from_json(file_path: str | Path) -> list[Transaction]
```

Принимает путь к JSON-файлу, который содержит транзакции. Возвращает новый список словарей с транзакциями.

```python
from src.utils import get_transactions_from_json


get_transactions_from_json("data/operations.json")
[{'id': 441945886, 'state': 'EXECUTED', 'date': '2019-08-26T10:50:58.294041', 'operationAmount': {'amount': '31957.58', 'currency': {'name': 'руб.', 'code': 'RUB'}}, 'description': 'Перевод организации', 'from': 'Maestro 1596837868705199', 'to': 'Счет 64686473678894779589'}]
```

## Модуль `external_api`

Модуль `src.external_api` объединяет функции обработки методов API.
Использует файл `.env` для хранения критически важной информации.

### API

Для обработки транзакции используется сервис **Exchange Rates Data API**. 
[Документация](https://marketplace.apilayer.com/exchangerates_data-api#documentation)  

Насройка `.env`:
```.env
# Exchange Rates Data API.
EXCHANGE_RATES_API_KEY=API_KEY
```
API_KEY - получаем при регистрации аккаунта **Exchange Rates Data API**

### `get_api_key`

```python
load_dotenv()

get_api_key() -> str
```

Функция возвращает API ключ от сервиса **EXCHANGE_RATES_API_KEY** из файла `.env`

### `get_response`

```python
ApiResponse = dict[str, Any]

API_TIMEOUT_SECONDS = 10

get_response(url: str, params: dict[str, str | float]) -> ApiResponse
```
Функция получает `url` - URL метода API и `params` - параметры запроса. Возвращает ответ API в виде словаря.

### `_raise_api_error`

```python
ApiResponse = dict[str, Any]

_raise_api_error(api_response: ApiResponse) -> None
```

Функция возвращает исключения с кодом и сообщением об ошибке API.

### `_normalize_target_currency`

```python
_normalize_target_currency(to_currency: str) -> str
```

Функция возвращает нормализированный код целевой валюты.

Получает: `to_currency` - код целевой валюты.
Возвращает: Код целевой валюты без пробелов и в верхнем регистре. Если целевая валюта передана пустой - возвращает RUB.

### `_extract_amount`

```python
ApiResponse = dict[str, Any]

_extract_amount(operation_amount: ApiResponse) -> float
```
Функция проверяет тип данных суммы транзакции.

### `_extract_currency_code`

```python
ApiResponse = dict[str, Any]

_extract_currency_code(operation_amount: ApiResponse) -> str
```

Функция проверяет тип данных кода валюты транзакции.

### `_extract_transaction_date`

```python
Transaction = dict[str, Any]

DATE_FORMATS = {
    "YYYY-MM-DD HH:MM:SS": "%Y-%m-%d %H:%M:%S",
    "YYYY-MM-DD": "%Y-%m-%d",
}

_extract_transaction_date(transaction: Transaction, date_format: str = "YYYY-MM-DD",) -> str
```

Функция преобразует дату транзакции в переданный формат.
Допустимые форматы дат задаются через **DATE_FORMATS**.

### `_extract_transaction_data`

```python
Transaction = dict[str, Any]

_extract_transaction_data(transaction: Transaction) -> tuple[float, str, str]
```
Функция извлекает и осуществляет проверку суммы, кода валюты и даты транзакции.

### `_extract_conversion_result`

```python
ApiResponse = dict[str, Any]

_extract_conversion_result(api_response: ApiResponse) -> float
```

Функция извлекает и проверяет результат конвертации из ответа API.

### `transaction_amount_convert`

```python
Transaction = dict[str, Any]

EXCHANGE_RATES_URL = "https://api.apilayer.com/exchangerates_data/convert"

transaction_amount_convert(transaction: Transaction, to_currency: str = "RUB") -> float
```

Функция возвращает сумму транзакции в целевой валюте `to_currency`.
Для транзакций в целевой валюте возвращается исходная сумма. 
Суммы для валют, отличных от целевой валюты, конвертируются через метод `convert` **Exchange Rates Data API**.

Передаваемая информацмя: 
- transaction - транзакция с суммой и кодом валюты в `operationAmount`;
- to_currency - целевая валюта.

Выходящая информация:
- сумма транзакции в целевой валюте `to_currency`, округлённая до двух знаков после запятой. 

## Модуль `readers`

Модуль `src.readers` объединяет функции обработки CSV и Excel файлов, содержащих транзакции.

### `get_transactions_from_csv`

Функция обрабатывает CSV-файлы, которые содержат информацию о финансовых транзакциях.
Файл находится в `data/transactions.csv`.

Структура файла:
```text
id;state;date;amount;currency_name;currency_code;from;to;description
650703;EXECUTED;2023-09-05T11:30:32Z;16210;Sol;PEN;Счет 58803664561298323391;Счет 39745660563456619397;Перевод организации
3598919;EXECUTED;2020-12-06T23:00:58Z;29740;Peso;COP;Discover 3172601889670065;Discover 0720428384694643;Перевод с карты на карту
```
Вызов функции:
```python
Transaction = dict[str, Any]

get_transactions_from_csv(file_path: str | Path) -> list[Transaction]
```
Функция:
- принимает путь к CSV-файлу, который содержит финансовые транзакции; 
- возвращает список словарей с транзакциями. Если файл отсутствует,
недоступен, пуст или содержит некорректные данные, возвращается пустой список.

### `get_transactions_from_xls`

Функция обрабатывает Excel файлы, которые содержат информацию о финансовых транзакциях.
Файл находится в `data/transactions_excel.xlsx`.

Структура файла:

| field | type    | descript                 |
|-------|---------|--------------------------|
| id    | int     | Идентификатор транзакции |
| state | string  | Статус транзакции        |
| date | datetime | Дата и время             |
| amount | float   | Сумма транзакции         |
| currency_name | string  | Наименование валюты      |
| currency_code | string  | Код валюты ISO           |
| from      | string | Реквизиты отправителя    |
| to | string | Реквизиты получателя |
| description | string | Описание транзакции |

```python
Transaction = dict[str, Any]

get_transactions_from_xls(file_path: str | Path) -> list[Transaction]
```

Функция:
- принимает путь к Excel файлу, который содержит финансовые транзакции; 
- возвращает список словарей с транзакциями. Если файл отсутствует,
недоступен, пуст или содержит некорректные данные, возвращается пустой список.

## Модуль `fields`

Модуль `src.fields` содержит функции обработки конфигурационного файла 
`config/field_aliases.json`, который содержит пути полей для различных структур 
данных используемых в проекта источников.

### Структура `field_aliases.json`

Структура данных:
```JSON
{
  "id": [
    "id"
  ],
  "state": [
    "state"
  ],
  "date": [
    "date"
  ],
  "amount": [
    "amount",
    "operationAmount.amount"
  ],
  "currency_name": [
    "currency_name",
    "operationAmount.currency.name"
  ],
  "currency_code": [
    "currency_code",
    "operationAmount.currency.code"
  ],
  "from": [
    "from"
  ],
  "to": [
    "to"
  ],
  "description": [
    "description"
  ]
}
```

### `load_fields`

```python
load_fields(file_path: str | Path) -> Any
```

Функция принимает:
- Путь к файлу `config/field_aliases.json`.

Функция возвращает
- Словарь путей к полям.

### `get_by_path`

```python
get_by_path(item: Mapping[str, Any], path: str) -> Any
```
Буквальный ключ имеет приоритет: для пути ``currency.code`` сначала
проверяется ключ с таким полным именем, а затем вложенная структура
``{"currency": {"code": ...}}``.

### `get_field_value`

```python
get_field_value(transaction: Mapping[str, Any], field_name: str, field_aliases: Mapping[str, list[str]],) -> Any
```

Функция осуществляет поиск значения поля транзакции по первому доступному `aliase`.
Возвращает значение первого найденного поля или пустой список, если поле
отсутствует в справочнике либо транзакции.

## Логирование

Логирование проекта осуществлены с помощью библиотеки `logging`. Логи помещены 
в папку `logs`. Логируются успешные и ошибочные случаи.

### Модуль `masks`
Логуруются в `logs/masks.log`

Структура логирования:
```
2026-09-15 14:52:41,023 - masks - DEBUG - Начало маскирования номера банковской карты
2026-09-15 14:52:41,023 - masks - DEBUG - Начало маскирования номера банковской карты
2026-09-15 14:52:41,045 - masks - DEBUG - Начало маскирования номера банковской карты
2026-09-15 14:52:41,045 - masks - INFO - Номер карты успешно замаскирован: 7000 79** **** 6361
2026-09-15 14:52:41,047 - masks - DEBUG - Начало маскирования номера банковской карты
2026-09-15 14:52:41,047 - masks - INFO - Номер карты успешно замаскирован: 1234 56** **** 3456
2026-09-15 14:52:41,047 - masks - DEBUG - Начало маскирования номера банковской карты
```

### Модуль `utils`
Логуруются в `logs/utils.log`

Структура логирования:
```
2026-09-15 19:52:43,282 - utils - DEBUG - Начало загрузки транзакций из файла: operations.json
2026-09-15 19:52:43,290 - utils - DEBUG - Начало загрузки транзакций из файла: missing.json
2026-09-15 19:52:43,589 - utils - DEBUG - Начало загрузки транзакций из файла: data/operations.json
2026-09-15 19:52:43,592 - utils - INFO - Успешно загружено транзакций из файла data/operations.json: 2
```

### Модуль `readers`
Логуруются в `logs/readers.log`

Структура логирования:
```
2026-09-15 19:52:43,477 - readers - get_transactions_from_csv - DEBUG - Начало загрузки транзакций из файла: data\transactions.csv
2026-09-15 19:52:43,478 - readers - get_transactions_from_csv - INFO - Успешно загружено транзакций из файла data\transactions.csv: 2
2026-09-15 19:52:43,486 - readers - get_transactions_from_csv - DEBUG - Начало загрузки транзакций из файла: empty.csv
2026-09-15 19:52:43,487 - readers - get_transactions_from_csv - ERROR - Некорректная структура файла empty.csv: отсутствует строка наименования столбцов.
```

### Модуль `processing`

Логируется в `logs/processing.log`

Структура логирования:
```
2026-09-22 04:15:31,537 - processing - filter_by_state - DEBUG - Начало фильтрации для 6 зваписей по статусу EXECUTED.
2026-09-22 04:15:31,539 - processing - filter_by_state - INFO - Получено записей 2 со статусом EXECUTED.
2026-09-22 04:15:31,539 - processing - filter_by_state - DEBUG - Начало фильтрации для 6 зваписей по статусу EXECUTED.
2026-09-22 04:15:31,541 - processing - filter_by_state - INFO - Получено записей 2 со статусом EXECUTED.
2026-09-22 04:15:31,543 - processing - filter_by_state - DEBUG - Начало фильтрации для 6 зваписей по статусу CANCELED.
```

### Модуль `fields`

Логируется в `logs/fields.log`

Структура лргирования:
```
2026-09-22 04:15:29,938 - fields - load_fields - DEBUG - Начало загрузки структур из файла: config/field_aliases.json
2026-09-22 04:15:29,951 - fields - load_fields - INFO - Успешно загружено транзакций из файла config/field_aliases.json: 9
2026-09-22 04:15:31,365 - fields - load_fields - DEBUG - Начало загрузки структур из файла: config\field_aliases.json
2026-09-22 04:15:31,366 - fields - load_fields - INFO - Успешно загружено транзакций из файла config\field_aliases.json: 1
2026-09-22 04:15:31,368 - fields - load_fields - DEBUG - Начало загрузки структур из файла: aliases.json
2026-09-22 04:15:31,369 - fields - load_fields - ERROR - Не удалось загрузить справочник aliases.json: Файл не найден
```

## Тестирование

Тесты проекта написаны с помощью `pytest`. Для измерения покрытия используется
плагин `pytest-cov`. Оба инструмента устанавливаются вместе с зависимостями
проекта:

```shell
poetry install
```

### Организация тестов

- `tests/conftest.py` — общие фикстуры с наборами банковских операций;
- `tests/test_decorators.py` — тесты вывода логов в консоль и файл;
- `tests/test_external_api.py` — тесты обработки методов API;
- `tests/test_fields.py` — тесты обработки файла настройки путей полей для различных источников данных;
- `tests/test_generators.py` — тесты фильтрации, описаний и номеров карт;
- `tests/test_logging.py` — тесты логирования;
- `tests/test_main.py` — тесты консольного меню и основной последовательности обработки;
- `tests/test_masks.py` — тесты маскирования карт и счетов;
- `tests/test_processing.py` — тесты фильтрации и сортировки операций;
- `tests/test_readers.py` — тесты обработки CSV и Excel файлов;
- `tests/test_utils.py` — тесты обработки JSON-файлов;
- `tests/test_widget.py` — тесты распознавания карт/счетов и обработки дат.

Для проверки нескольких вариантов входных данных применяется
`pytest.mark.parametrize`. Фикстуры предоставляют тестам готовые списки
операций с разными статусами и датами, в том числе ошибочными и граничными
значениями.

Для проверки API, обработки CSV и Excel файлов используются Mock и patch.
В `tests/test_main.py` с помощью `patch` имитируются ответы пользователя,
загрузка каждого формата файла и результаты последовательных фильтров.

Проверяются:
- корректные номера карт и счетов;
- пустые строки, неверная длина и недопустимые символы;
- различные названия и регистры типов карт и счетов;
- корректные, граничные и ошибочные даты;
- фильтрация по различным статусам;
- фильтрация по различным кодам валюты;
- сортировка по возрастанию и убыванию;
- одинаковые и нестандартные даты;
- пустой или повреждённый JSON;
- отсутствующий файл;
- ошибка декодирования файла;
- отсутствующий или пустой API-ключ в `.env`;
- JSON с ошибкой;
- невалидный JSON при успешном HTTP-ответе;
- HTTPError;
- ошибка API;
- пустая целевая валюта;
- неправильная структура транзакции;
- некорректная сумма транзакции;
- разные форматы ошибки API;
- нечисловая строка result ответ API;
- некорректная ISO-дата;
- неизвестный формат даты;
- отсутствие обязательных полей в транзакции;
- варианты логирования;
- исключения `ValueError`, `KeyError` и `TypeError`.

### Запуск тестов

Запустить все тесты:

```shell
poetry run pytest
```

Запустить тесты конкретного модуля:

```shell
poetry run pytest tests/test_decorators.py
poetry run pytest tests/test_external_api.py
poetry run pytest tests/test_fields.py
poetry run pytest tests/test_generators.py
poetry run pytest tests/test_logging.py
poetry run pytest tests/test_main.py
poetry run pytest tests/test_masks.py
poetry run pytest tests/test_processing.py
poetry run pytest tests/test_readers.py
poetry run pytest tests/test_utils.py
poetry run pytest tests/test_widget.py
```

Запустить один тест:

```shell
poetry run pytest tests/test_widget.py::test_get_date
```

Выбрать тесты по части имени:

```shell
poetry run pytest -k "mask_account_card"
```

Показать список доступных фикстур:

```shell
poetry run pytest --fixtures
```

### Покрытие кода

Плагин pytest-cov автоматически измеряет покрытие исходного кода и выводит в
консоль строки, которые не были выполнены. Минимально допустимое покрытие
установлено на уровне 80%. Если покрытие окажется ниже, команда завершится с
ошибкой.

Настройки находятся в `pyproject.toml`:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-v --cov=src --cov-branch --cov-report=term-missing --cov-fail-under=80"
```

Создать подробный HTML-отчёт о покрытии:

```shell
poetry run pytest --cov-report=html
```

После выполнения отчёт будет доступен в каталоге `htmlcov`.

## Проверка качества кода

Запустить Flake8:

```shell
poetry run flake8 src tests
```

Проверить форматирование Black без изменения файлов:

```shell
poetry run black --check src tests
```

Отформатировать файлы Black:

```shell
poetry run black src tests
```

Проверить сортировку импортов isort:

```shell
poetry run isort --check-only src tests
```

Исправить порядок импортов:

```shell
poetry run isort src tests
```

Проверить аннотации типов с помощью mypy:

```shell
poetry run mypy
```
