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
- сортировка операций по дате;
- последовательная обработка транзакций с помощью генераторов;
- генерация номеров банковских карт в заданном диапазоне;
- логирование результатов выполнения функций в консоль или файл;
- проверка кода с помощью Flake8, Black, isort и mypy.

- ## Структура проекта

```text
.
├── htmlcov/
├── src/
│   ├── __init__.py
│   ├── decorators.py
│   ├── generators.py
│   ├── masks.py
│   ├── processing.py
│   └── widget.py
├── tests/
│   ├── __init__.py
│   ├── test_decorators.py
│   ├── test_generators.py
│   ├── test_main.py
│   ├── test_masks.py
│   ├── test_processing.py
│   └── test_widget.py
├── .coverage
├── .flake8
├── .gitignore
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

## Модуль `test_main`

Модуль `tests.test_main` предназначен для тестировния функционала модулей из пакета `src`

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
- `tests/test_generators.py` — тесты фильтрации, описаний и номеров карт;
- `tests/test_masks.py` — тесты маскирования карт и счетов;
- `tests/test_widget.py` — тесты распознавания карт/счетов и обработки дат;
- `tests/test_processing.py` — тесты фильтрации и сортировки операций.

Для проверки нескольких вариантов входных данных применяется
`pytest.mark.parametrize`. Фикстуры предоставляют тестам готовые списки
операций с разными статусами и датами, в том числе ошибочными и граничными
значениями.

Проверяются:

- корректные номера карт и счетов;
- пустые строки, неверная длина и недопустимые символы;
- различные названия и регистры типов карт и счетов;
- корректные, граничные и ошибочные даты;
- фильтрация по различным статусам;
- сортировка по возрастанию и убыванию;
- одинаковые и нестандартные даты;
- исключения `ValueError`, `KeyError` и `TypeError`.

### Запуск тестов

Запустить все тесты:

```shell
poetry run pytest
```

Запустить тесты конкретного модуля:

```shell
poetry run pytest tests/test_decorators.py
poetry run pytest tests/test_generators.py
poetry run pytest tests/test_masks.py
poetry run pytest tests/test_widget.py
poetry run pytest tests/test_processing.py
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
