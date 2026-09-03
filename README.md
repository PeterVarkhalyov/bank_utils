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
- проверка кода с помощью Flake8, Black, isort и mypy.

- ## Структура проекта

```text
.
├── htmlcov/
├── src/
│   ├── __init__.py
│   ├── masks.py
│   └── widget.py
├── tests/
│   ├── __init__.py
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
from src.masks import get_mask_account, get_mask_card_number
from src.widget import get_date, mask_account_card
from src.processing import filter_by_state

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


## Тестирование

Тесты проекта написаны с помощью `pytest`. Для измерения покрытия используется
плагин `pytest-cov`. Оба инструмента устанавливаются вместе с зависимостями
проекта:

```shell
poetry install
```

### Организация тестов

- `tests/conftest.py` — общие фикстуры с наборами банковских операций;
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
