from __future__ import annotations

import json
import os
import threading
from dataclasses import asdict, dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import List, Optional
from urllib.parse import urlparse


@dataclass
class Task:
    id: int
    title: str
    priority: str
    isDone: bool


class TaskStorage:
    def __init__(self, path: str) -> None:
        self._path = path
        self._tasks: List[Task] = []
        self._next_id = 1
        self._lock = threading.Lock()
        self._load()

    def create(self, title: str, priority: str) -> Task:
        with self._lock:
            task = Task(id=self._next_id, title=title, priority=priority, isDone=False)
            self._next_id += 1
            self._tasks.append(task)
            self._save()
            return task

    def list_all(self) -> List[Task]:
        with self._lock:
            return list(self._tasks)

    def complete(self, task_id: int) -> bool:
        with self._lock:
            for task in self._tasks:
                if task.id == task_id:
                    task.isDone = True
                    self._save()
                    return True
        return False

    def _load(self) -> None:
        if not os.path.exists(self._path):
            return
        try:
            with open(self._path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError):
            return

        if not isinstance(data, list):
            return

        tasks: List[Task] = []
        for item in data:
            if not isinstance(item, dict):
                continue
            try:
                id_value = item.get("id")
                title_value = item.get("title")
                priority_value = item.get("priority")
                is_done_value = item.get("isDone")
                if id_value is None or title_value is None or priority_value is None:
                    continue
                task_id = int(id_value)
                title = str(title_value)
                priority = str(priority_value)
                is_done = bool(is_done_value) if is_done_value is not None else False
            except (TypeError, ValueError):
                continue
            tasks.append(Task(id=task_id, title=title, priority=priority, isDone=is_done))

        if tasks:
            self._tasks = tasks
            self._next_id = max(task.id for task in tasks) + 1

    def _save(self) -> None:
        data = [asdict(task) for task in self._tasks]
        try:
            with open(self._path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except OSError:
            pass


class TaskAPIHandler(BaseHTTPRequestHandler):
    storage: TaskStorage
    protocol_version = "HTTP/1.1"

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/tasks":
            tasks = [asdict(task) for task in self.storage.list_all()]
            self._send_json(tasks, status=200)
            return
        self._send_empty(status=404)

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/tasks":
            self._handle_create_task()
            return

        parts = parsed.path.strip("/").split("/")
        if len(parts) == 3 and parts[0] == "tasks" and parts[2] == "complete":
            try:
                task_id = int(parts[1])
            except ValueError:
                self._send_empty(status=404)
                return
            self._handle_complete_task(task_id)
            return

        self._send_empty(status=404)

    def _handle_create_task(self) -> None:
        data = self._read_json_body()
        if data is None or not isinstance(data, dict):
            self._send_json_error("Invalid JSON payload", status=400)
            return

        title = data.get("title")
        priority = data.get("priority")

        if not isinstance(title, str) or not title.strip():
            self._send_json_error("Title must be a non-empty string", status=400)
            return
        if priority not in {"low", "normal", "high"}:
            self._send_json_error("Priority must be one of low, normal, high", status=400)
            return

        task = self.storage.create(title.strip(), priority)
        self._send_json(asdict(task), status=200)

    def _handle_complete_task(self, task_id: int) -> None:
        completed = self.storage.complete(task_id)
        if completed:
            self._send_empty(status=200)
        else:
            self._send_empty(status=404)

    def _read_json_body(self) -> Optional[object]:
        length_header = self.headers.get("Content-Length")
        if length_header is None:
            return None
        try:
            length = int(length_header)
        except (TypeError, ValueError):
            return None

        try:
            raw = self.rfile.read(length)
        except (OSError, ValueError):
            return None
        try:
            return json.loads(raw.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return None

    def _send_json(self, data: object, status: int = 200) -> None:
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_json_error(self, message: str, status: int) -> None:
        self._send_json({"error": message}, status=status)

    def _send_empty(self, status: int) -> None:
        self.send_response(status)
        self.send_header("Content-Length", "0")
        self.end_headers()

    def log_message(self, format: str, *args: object) -> None:
        # Use default logging to stderr; override to keep standard format.
        super().log_message(format, *args)


def run_server(host: str = "127.0.0.1", port: int = 8000) -> None:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    storage_path = os.path.join(base_dir, "tasks.txt")
    storage = TaskStorage(storage_path)

    TaskAPIHandler.storage = storage
    server = ThreadingHTTPServer((host, port), TaskAPIHandler)

    print(f"Task server running at http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    run_server()
