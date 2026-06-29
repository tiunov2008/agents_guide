# Как создавать простых AI-агентов на Python

Этот репозиторий показывает путь от обычного запроса к модели до простого агента, который умеет вызывать инструменты.

Агент здесь - это программа, которая:

1. получает сообщение пользователя;
2. отправляет его модели;
3. дает модели инструкции через системный промпт;
4. описывает доступные инструменты;
5. выполняет инструмент, если модель решила его вызвать;
6. возвращает пользователю результат.

## Что есть в проекте

```text
example1/
  main.py              простой запрос к модели

example2/
  client.py            настройка клиента Anthropic
  tools.py             пример tool runner с инструментом погоды
  tools_pretty.py      более подробный вывод сообщений

example3/
  agent.py             агент-калькулятор
  client.py            настройка клиента Anthropic
  prompts/
    agent.md           системный промпт агента
    math_tool.md       описание математического инструмента
  tools/
    math_tool.py       код инструмента
```

## Установка

Нужен Python 3.11 или новее.

Создай виртуальное окружение:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Установи зависимости:

```powershell
python -m pip install anthropic>=0.112.0 httpx python-dotenv
```

Или из папки конкретного примера:

```powershell
python -m pip install -r example2/requirements.txt
```

## API-ключ

В `example2` и `example3` используется файл `.env`.

Создай файл:

```powershell
copy example3/.env.example example3/.env
```

Внутри должно быть:

```env
ANTHROPIC_API_KEY=твой_ключ
```

В `example1/main.py` ключ сейчас прописан прямо в коде:

```python
API_KEY = "API_TOKEN"
```

Для учебного примера это понятно, но в реальных проектах ключи лучше хранить в `.env`, а не в коде.

## Пример 1: обычный запрос к модели

Файл: `example1/main.py`

Это самый простой вариант:

```python
message = client.messages.create(
    max_tokens=1024,
    messages=[
        {
            "role": "user",
            "content": user_input,
        }
    ],
    model="claude-opus-4-8",
)
```

Здесь нет агента и инструментов. Программа просто берет текст пользователя, отправляет его модели и печатает ответ.

Запуск:

```powershell
python example1/main.py
```

## Пример 2: модель вызывает tool

Файл: `example2/tools.py`

Tool - это обычная Python-функция, которую модель может попросить вызвать.

```python
@beta_tool
def get_weather(location: str) -> str:
    return json.dumps(
        {
            "location": location,
            "temperature": "68°F",
            "condition": "Sunny",
        }
    )
```

Дальше инструмент передается в `tool_runner`:

```python
runner = client.beta.messages.tool_runner(
    max_tokens=1024,
    model="claude-opus-4-8",
    tools=[get_weather],
    messages=[
        {"role": "user", "content": "What is the weather in SF?"},
    ],
)
```

`tool_runner` сам делает цикл:

1. отправляет вопрос модели;
2. получает запрос на вызов инструмента;
3. вызывает Python-функцию;
4. отправляет результат обратно модели;
5. получает финальный ответ.

Запуск:

```powershell
python example2/tools.py
```

## Пример 3: агент с системным промптом и своим инструментом

Файл: `example3/agent.py`

Это уже ближе к настоящему агенту.

Главные части:

```python
SYSTEM_PROMPT = (
    Path(__file__).with_name("prompts") / "agent.md"
).read_text(encoding="utf-8").strip()
```

Системный промпт объясняет модели роль агента. В этом примере агент должен быть калькулятором и всегда вызывать `math_tool`.

Инструмент регистрируется так:

```python
registered_math_tool = beta_tool(
    name=math_tool_desc["name"],
    description=math_tool_desc["description"].strip(),
    input_schema=math_tool_desc["input_schema"],
)(run_math_tool)
```

Описание инструмента лежит в `example3/tools/math_tool.py`:

```python
math_tool_desc = {
    "name": "math_tool",
    "description": MATH_TOOL_PROMPT,
    "input_schema": {
        "type": "object",
        "properties": {
            "expression": {
                "type": "string",
                "description": "Математическое выражение для вычисления",
            }
        },
        "required": ["expression"],
        "additionalProperties": False,
    },
}
```

`input_schema` говорит модели, какие аргументы нужны инструменту.

Запуск:

```powershell
python example3/agent.py
```

Пример запроса:

```text
Сколько будет (25 + 17) * 3?
```

Модель должна не считать сама, а вызвать `math_tool` с выражением:

```text
(25 + 17) * 3
```

## Как создать своего агента

Минимальный план:

1. Создай функцию-инструмент.
2. Опиши, что она делает.
3. Опиши входные параметры через `input_schema`.
4. Напиши системный промпт.
5. Передай промпт и список инструментов в `client.messages.create`.
6. Проверь, вызывает ли модель нужный tool.

Например, агент для заметок может иметь инструменты:

```text
create_note(title, text)
find_note(query)
delete_note(title)
```

Агент для файлов:

```text
read_file(path)
write_file(path, content)
list_files(folder)
```

Агент для таблиц:

```text
read_excel(path)
sum_column(column_name)
filter_rows(condition)
```

## Хороший системный промпт

Системный промпт должен отвечать на вопросы:

```text
Кто ты?
Что ты должен делать?
Какие инструменты использовать?
Когда инструмент обязателен?
Что нельзя делать?
В каком формате отвечать?
```

Пример:

```text
Ты - агент для работы с заметками.
Если пользователь просит сохранить информацию, вызови create_note.
Если пользователь ищет информацию, вызови find_note.
Не выдумывай содержимое заметок. Если данных нет, честно скажи об этом.
```

## Как описывать tool

У хорошего инструмента есть:

```text
name            короткое имя, например get_weather
description     понятное описание для модели
input_schema    JSON Schema с аргументами
function        Python-код, который реально выполняет действие
```

Важно: модель не выполняет Python сама. Она только просит вызвать инструмент. Выполняет инструмент твоя программа.

## Частые ошибки новичков

### ImportError: cannot import name beta_tool

Нужна свежая версия SDK:

```powershell
python -m pip install --upgrade anthropic
```

Проверь версию:

```powershell
python -c "import anthropic; print(anthropic.__version__)"
```

Для этих примеров нужна версия `0.112.0` или новее.

### ANTHROPIC_API_KEY is not set

Проверь, что файл `.env` создан в папке примера и внутри есть:

```env
ANTHROPIC_API_KEY=твой_ключ
```

### UnicodeEncodeError на Windows

Если в консоли ломается вывод русских букв или emoji, добавь в начало `main()`:

```python
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
```

В `example2/tools.py` и `example3/agent.py` это уже используется.

## Безопасность

В `example3/tools/math_tool.py` используется:

```python
return eval(exp)
```

Это удобно для учебного калькулятора, но небезопасно для реального приложения. `eval` может выполнить опасный Python-код, если туда попадет вредный ввод.

Для настоящего проекта лучше:

1. использовать безопасный парсер выражений;
2. разрешать только нужные операции;
3. проверять аргументы инструмента;
4. логировать вызовы tools;
5. не давать агенту доступ к файлам, сети или системе без ограничений.

## Главная идея

Модель хорошо понимает текст и решает, что нужно сделать.

Python-код реально выполняет действия.

Агент получается там, где модель и код работают вместе:

```text
пользователь -> модель -> выбор tool -> Python-функция -> результат -> модель -> ответ
```

Начни с простого инструмента, например калькулятора или погоды. Когда поймешь цикл вызова tools, можно добавлять память, файлы, базу данных, поиск, браузер или работу с API.
