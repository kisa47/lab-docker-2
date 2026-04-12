# SSH

## Оглавление
- [Подключение к удалённому серверу](#подключение-к-удалённому-серверу)
- [Копирование файлов через SCP и RSYNC](#копирование-файлов-через-scp-и-rsync)
- [Запуск команд и скриптов на удалённом сервере](#запуск-команд-и-скриптов-на-удалённом-сервере)
- [SSH-ключи и агенты](#ssh-ключи-и-агенты)
- [Полезные опции SSH](#полезные-опции-ssh)
    - [Пример: проброс порта и запуск команды в фоне](#пример-проброс-порта-и-запуск-команды-в-фоне)

## Подключение к удалённому серверу

```bash
# Стандартное подключение
ssh user@hostname

# С указанием порта (если не 22)
ssh -p 2222 user@hostname

# Использование нестандартного ключа
ssh -i ~/.ssh/custom_key user@hostname

# Запуск команды сразу после подключения
ssh user@hostname "uptime"
```

## Копирование файлов через SCP и RSYNC

```bash
# Копирование файла с локальной машины на сервер
scp file.txt user@hostname:/home/user/
rsync file.txt user@hostname:/home/user/

# Копирование файла с сервера на локальную машину
scp user@hostname:/home/user/file.txt ./file.txt
rsync user@hostname:/home/user/file.txt ./file.txt

# Рекурсивное копирование директроии (со вложенными файлами и директориями)
scp -r directory/ user@hostname:/home/user/
rsync -a directory/ user@hostname:/home/user/
# Копирование с указанием порта
scp -P 2222 file.txt user@hostname:/home/user/
```

## Запуск команд и скриптов на удалённом сервере

```bash
# Запуск одной команды
ssh user@hostname "ls -la /var/log"

# Передача переменных окружения
VAR="value" ssh user@hostname "echo $VAR"

# Запуск локального скрипта на удалённом сервере
ssh user@hostname "bash -s" < script.sh

# Альтернативно — скопировать скрипт и запустить
scp script.sh user@hostname:/tmp/script.sh
ssh user@hostname "bash /tmp/script.sh"
```

## SSH-ключи и агенты

```bash
# Генерация нового ключа (RSA, 4096 бит)
ssh-keygen -t rsa -b 4096 -C "email@example.com"

# Добавление ключа в ssh-agent
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_rsa

# Копирование открытого ключа на сервер
ssh-copy-id user@hostname

# Просмотр активных ключей в агенте
ssh-add -l
```

## Полезные опции SSH

| **Опция** | **Описание** |
|-----------|-------------|
| `-v` | Подробный вывод (отладка) |
| `-C` | Сжатие данных (полезно для медленных соединений) |
| `-L` | Перенаправление портов (локальный проброс) |
| `-N` | Не выполнять команды, только пробросить порт |
| `-f` | Перейти в фон после аутентификации |
| `-t` | Принудительно выделить терминал (для sudo, screen и т.д.) |

### Пример: проброс порта и запуск команды в фоне

```bash
# Проброс локального порта 8080 на 80 порт сервера
ssh -L 8080:localhost:80 user@hostname -N -f

# Запуск команды с sudo на удалённом сервере
ssh -t user@hostname "sudo bash -c 'apt update && apt upgrade'"
```
