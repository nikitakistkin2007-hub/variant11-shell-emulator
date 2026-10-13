# Variant 11 — Shell Emulator (этапы 1–2)

Эмулятор командной оболочки UNIX-подобной ОС (вариант №11 практической
работы). Консольное приложение на Python 3.10+ без внешних зависимостей.
В репозитории реализованы два этапа: **REPL** и **конфигурация**.

## 1. Общее описание

- интерфейс — CLI: интерактивный REPL или выполнение стартового скрипта;
- приглашение содержит имя VFS: `my_vfs:/$ `. Имя — последний компонент
  пути из параметра `--vfs`;
- парсер делит ввод на команду и аргументы по пробелам; кавычки
  позволяют передать аргумент с пробелами, всё после `#` — комментарий;
- команды `ls` и `cd` — заглушки: выводят своё имя и аргументы;
- ошибки (неизвестная команда, неверные аргументы, ошибка разбора)
  выводятся в stderr в виде `error: ...`, эмулятор продолжает работу;
- Ctrl+C сбрасывает введённую строку, Ctrl+D завершает работу.

## 2. Команды

| Команда | Описание |
|---|---|
| `ls [ARGS...]` | заглушка: выводит `ls: args=[...]` |
| `cd [ARGS...]` | заглушка: выводит `cd: args=[...]` |
| `exit` | завершить эмулятор (аргументы недопустимы) |

## 3. Параметры командной строки

| Параметр | Обязательный | Описание |
|---|---|---|
| `--vfs PATH` | да | путь к физическому расположению VFS |
| `--script PATH` | нет | путь к стартовому скрипту; без него запускается REPL |

При запуске выводятся все заданные параметры (`[debug] ...`).

Коды выхода: `0` — успех; `1` — не найден или не читается файл скрипта;
`2` — ошибка параметров командной строки (например, не указан `--vfs`).

## 4. Стартовый скрипт

Текстовый файл, одна команда на строку. Пустые строки и строки,
начинающиеся с `#`, пропускаются; `#` после команды тоже начинает
комментарий. При выполнении на экране показываются приглашение, команда и
результат, как при живом диалоге. Ошибка команды не прерывает скрипт,
`exit` завершает его. Пример — `scripts/startup.txt`.

## 5. Запуск и тесты

Сборка не нужна. Нужен Python 3.10 или новее.

```bash
make test        # unittest
make run         # интерактивный режим
make demo        # скрипт ОС для Linux/macOS (scripts/demo.sh)
```

Без make:

```bash
python3 -m unittest discover -s tests -v
python3 src/main.py --vfs vfs_demo
python3 src/main.py --vfs vfs_demo --script scripts/startup.txt
```

Windows (cmd, двойной щелчок или командная строка):

```bat
scripts\run.bat                      :: интерактивный режим
scripts\run.bat scripts\startup.txt   :: выполнить стартовый скрипт
scripts\test.bat                     :: тесты
scripts\demo.bat                     :: вызовы со всеми параметрами
```

Скрипты `.bat` сами находят Python (`py`, затем `python`); нужный
интерпретатор можно задать вручную: `set PYTHON=C:\path\to\python.exe`.
Запускайте их из терминала (cmd или PowerShell, в PowerShell с `.\`),
чтобы окно не закрывалось после завершения.

Windows PowerShell: `.\scripts\demo.ps1`

Скрипты ОС `scripts/demo.bat`, `scripts/demo.ps1` и `scripts/demo.sh` вызывают эмулятор со
всеми параметрами: `--help`, только `--vfs` (интерактивный режим), `--vfs`
со `--script`, а также с ошибочными параметрами (нет `--vfs`, нет файла
скрипта, неизвестный параметр). Для каждого вызова печатается код выхода.

## 6. Примеры использования

Интерактивный режим:

```text
$ python3 src/main.py --vfs vfs_demo
[debug] parameters:
[debug]   --vfs    = vfs_demo
[debug]   --script = <interactive>
vfs_demo:/$ ls -l /home
ls: args=['-l', '/home']
vfs_demo:/$ cd "my dir"
cd: args=['my dir']
vfs_demo:/$ rm file
error: unknown command: rm
vfs_demo:/$ exit
```

Стартовый скрипт:

```text
$ python3 src/main.py --vfs vfs_demo --script scripts/startup.txt
[debug] parameters:
[debug]   --vfs    = vfs_demo
[debug]   --script = scripts/startup.txt
vfs_demo:/$ ls                       # no arguments
ls: args=[]
vfs_demo:/$ ls -l /home docs         # several arguments
ls: args=['-l', '/home', 'docs']
vfs_demo:/$ exit now                 # error: exit takes no arguments
error: usage: exit
vfs_demo:/$ exit
```

Ошибки параметров:

```text
$ python3 src/main.py
usage: main.py [-h] --vfs VFS [--script SCRIPT]
main.py: error: the following arguments are required: --vfs
```

## 7. Структура

```text
src/main.py      исходный код эмулятора
tests/           unittest: модульные и сквозные (запуск процесса) тесты
scripts/         стартовый скрипт и скрипты ОС (*.bat, demo.ps1, demo.sh;
                 _env.bat - вспомогательный, ищет Python)
vfs_demo/        каталог-заготовка для параметра --vfs
Makefile         test / run / demo
```

## 8. История Git

Каждый этап — отдельный коммит по Conventional Commits:

```text
feat(repl): add interactive prompt with ls and cd stubs and exit
feat(config): add --vfs and --script parameters with debug output
```
