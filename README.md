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
├── src/
│   ├── __init__.py
│   ├── masks.py
│   └── widget.py
├── tests/
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

print(get_mask_card_number("7000792289606361"))
print(get_mask_account("73654108430135874305"))
print(mask_account_card("Visa Platinum 7000792289606361"))
print(get_date("2024-03-11T02:26:18.671407"))
```

Результат:

```text
7000 79** **** 6361
**4305
Visa Platinum 7000 79** **** 6361
11.03.2024
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

## Тестирование

Запустить все тесты стандартной библиотеки `unittest`:

```shell
poetry run python -m unittest discover -v
```

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
