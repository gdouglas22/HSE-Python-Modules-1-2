import os
import tempfile
import unittest

from server import TaskStorage


class TaskStorageTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.temp_dir.name, "tasks.txt")

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_save_and_load(self) -> None:
        storage = TaskStorage(self.path)
        first = storage.create("Первая", "low")
        second = storage.create("Вторая", "high")
        new_storage = TaskStorage(self.path)
        tasks = new_storage.list_all()
        self.assertEqual(len(tasks), 2)
        self.assertEqual(tasks[0].id, first.id)
        self.assertEqual(tasks[1].priority, "high")
        new_task = new_storage.create("Третья", "normal")
        self.assertEqual(new_task.id, second.id + 1)
        self.assertTrue(os.path.exists(self.path))

    def test_corrupted_file(self) -> None:
        with open(self.path, "w", encoding="utf-8") as file:
            file.write("повреждено")
        storage = TaskStorage(self.path)
        self.assertEqual(storage.list_all(), [])
        task = storage.create("После сбоя", "low")
        self.assertEqual(task.id, 1)
        storage_again = TaskStorage(self.path)
        self.assertEqual(len(storage_again.list_all()), 1)

    def test_complete_and_persist(self) -> None:
        storage = TaskStorage(self.path)
        task = storage.create("Завершить", "normal")
        self.assertFalse(task.isDone)
        self.assertTrue(storage.complete(task.id))
        self.assertFalse(storage.complete(task.id + 1))
        reloaded = TaskStorage(self.path)
        tasks = reloaded.list_all()
        self.assertEqual(len(tasks), 1)
        self.assertTrue(tasks[0].isDone)

    def test_empty_file(self) -> None:
        with open(self.path, "w", encoding="utf-8") as file:
            file.write("")
        storage = TaskStorage(self.path)
        self.assertEqual(storage.list_all(), [])
        new_task = storage.create("Старт", "high")
        self.assertEqual(new_task.id, 1)
        again = TaskStorage(self.path)
        self.assertEqual(again.list_all()[0].id, 1)


if __name__ == "__main__":
    unittest.main()
