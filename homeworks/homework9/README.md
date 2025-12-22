# Сервер задач

HTTP-сервис на стандартной библиотеке Python для создания и завершения задач. Запуск: `python server.py`.

- Приложение использует `http.server` и работает без сторонних зависимостей: “stdlib only, no third-party libs; data stored in tasks.txt”.
- Данные сохраняются после каждого изменения в файл `tasks.txt` в корне проекта.
- По умолчанию сервер стартует на `http://0.0.0.0:8000`.

## Эндпоинты

- Создать задачу: `POST /tasks`
  - Тело: `{"title":"Купить хлеб","priority":"normal"}`
  - Ответ 200 (JSON задачи): `{"title":"Купить хлеб","priority":"normal","isDone":false,"id":1}`
- Список задач: `GET /tasks`
  - Ответ 200: массив всех задач.
- Завершить задачу: `POST /tasks/<id>/complete`
  - Без тела.
  - Ответ 200 с пустым телом при успехе, 404 при отсутствии задачи.

## Примеры curl

Создать задачу:
```bash
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"Позвонить","priority":"high"}'
```

Получить список задач:
```bash
curl http://localhost:8000/tasks
```

Отметить задачу выполненной:
```bash
curl -X POST http://localhost:8000/tasks/1/complete
```
