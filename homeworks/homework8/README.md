# Task API (stdlib only)

Simple task tracker built with Python's standard library `http.server`. Data is stored in `tasks.txt` (JSON array) in the project root and loaded on startup.

## Run

```bash
python server.py
```

Server listens on `http://127.0.0.1:8000`.

## Example requests

- Create task  
  ```bash
  curl -X POST http://127.0.0.1:8000/tasks \
    -H "Content-Type: application/json" \
    -d '{"title":"Buy milk","priority":"normal"}'
  ```

- List tasks  
  ```bash
  curl http://127.0.0.1:8000/tasks
  ```

- Mark complete  
  ```bash
  curl -X POST http://127.0.0.1:8000/tasks/1/complete
  ```

## Notes

- Uses only the Python standard library.
- All changes are saved immediately to `tasks.txt`.
- State is restored from `tasks.txt` on startup.
- Optional tests for storage logic: `python tests.py`
