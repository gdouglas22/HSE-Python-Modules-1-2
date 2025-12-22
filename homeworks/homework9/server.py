import json
import re
from dataclasses import asdict, dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import List
from urllib.parse import urlparse


@dataclass
class Task:
    title: str
    priority: str
    isDone: bool
    id: int


class TaskStorage:
    def __init__(self, path: str = "tasks.txt") -> None:
        self.path = path
        self.tasks: List[Task] = []
        self._next_id = 1
        self._load()

    def create(self, title: str, priority: str) -> Task:
        task = Task(title=title, priority=priority, isDone=False, id=self._next_id)
        self._next_id += 1
        self.tasks.append(task)
        self._save()
        return task

    def list_all(self) -> List[Task]:
        return list(self.tasks)

    def complete(self, task_id: int) -> bool:
        for task in self.tasks:
            if task.id == task_id:
                task.isDone = True
                self._save()
                return True
        return False

    def _save(self) -> None:
        data = [asdict(task) for task in self.tasks]
        with open(self.path, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False)

    def _load(self) -> None:
        try:
            with open(self.path, "r", encoding="utf-8") as file:
                content = file.read()
            if not content.strip():
                return
            data = json.loads(content)
            if not isinstance(data, list):
                self.tasks = []
                self._next_id = 1
                return
            loaded: List[Task] = []
            max_id = 0
            for item in data:
                if not isinstance(item, dict):
                    loaded = []
                    break
                if not {"title", "priority", "isDone", "id"}.issubset(item.keys()):
                    loaded = []
                    break
                title = item.get("title")
                priority = item.get("priority")
                is_done = item.get("isDone")
                task_id = item.get("id")
                if not isinstance(title, str) or not isinstance(priority, str) or not isinstance(is_done, bool) or not isinstance(task_id, int):
                    loaded = []
                    break
                loaded.append(Task(title=title, priority=priority, isDone=is_done, id=task_id))
                if task_id > max_id:
                    max_id = task_id
            self.tasks = loaded
            self._next_id = max_id + 1 if loaded else 1
        except (OSError, json.JSONDecodeError):
            self.tasks = []
            self._next_id = 1


class TaskHandler(BaseHTTPRequestHandler):
    storage: TaskStorage

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/tasks":
            tasks = [asdict(task) for task in self.storage.list_all()]
            self._send_json(200, tasks)
        else:
            self._send_not_found()

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/tasks":
            self._handle_create()
            return
        match = re.fullmatch(r"/tasks/(\d+)/complete", parsed.path)
        if match:
            task_id = int(match.group(1))
            self._handle_complete(task_id)
            return
        self._send_not_found()

    def _handle_create(self) -> None:
        try:
            content_length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self._send_error_json("Некорректная длина тела запроса")
            return
        body = self.rfile.read(content_length).decode("utf-8") if content_length > 0 else ""
        try:
            data = json.loads(body) if body else {}
        except json.JSONDecodeError:
            self._send_error_json("Некорректный JSON")
            return
        if not isinstance(data, dict):
            self._send_error_json("Некорректные данные запроса")
            return
        title = data.get("title")
        priority = data.get("priority")
        if not isinstance(title, str) or not title.strip():
            self._send_error_json("Поле title должно быть непустой строкой")
            return
        if priority not in ("low", "normal", "high"):
            self._send_error_json("Поле priority должно быть одним из: low, normal, high")
            return
        task = self.storage.create(title=title.strip(), priority=priority)
        self._send_json(200, asdict(task))

    def _handle_complete(self, task_id: int) -> None:
        found = self.storage.complete(task_id)
        if found:
            self._send_empty(200)
        else:
            self._send_empty(404, "Не найдено")

    def _send_json(self, status: int, data: object, message: str | None = None) -> None:
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        if message:
            self.send_response(status, message)
        else:
            self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_error_json(self, error_message: str) -> None:
        self._send_json(400, {"error": error_message}, "Некорректный запрос")

    def _send_empty(self, status: int, message: str | None = None) -> None:
        if message:
            self.send_response(status, message)
        else:
            self.send_response(status)
        self.send_header("Content-Length", "0")
        self.end_headers()

    def _send_not_found(self) -> None:
        self._send_empty(404, "Не найдено")

    def log_message(self, format: str, *args: object) -> None:
        return


def run_server(host: str = "0.0.0.0", port: int = 8000) -> None:
    storage = TaskStorage("tasks.txt")
    TaskHandler.storage = storage
    with ThreadingHTTPServer((host, port), TaskHandler) as httpd:
        print(f"Сервер запущен на http://{host}:{port}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    run_server()
