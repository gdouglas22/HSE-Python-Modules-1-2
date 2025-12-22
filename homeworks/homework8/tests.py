import json
import os
import tempfile
import unittest

from server import TaskStorage


class TaskStorageTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.temp_dir.name, "tasks.txt")
        self.storage = TaskStorage(self.path)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_create_and_list_tasks(self) -> None:
        first = self.storage.create("Buy milk", "normal")
        second = self.storage.create("Clean room", "high")

        tasks = self.storage.list_all()
        self.assertEqual(len(tasks), 2)
        self.assertEqual(first.id, 1)
        self.assertEqual(second.id, 2)
        self.assertTrue(all(not task.isDone for task in tasks))
        self.assertEqual(tasks[1].priority, "high")

    def test_complete_existing_task(self) -> None:
        task = self.storage.create("Read book", "low")
        result = self.storage.complete(task.id)
        self.assertTrue(result)

        tasks = self.storage.list_all()
        self.assertTrue(tasks[0].isDone)

        with open(self.path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertTrue(data[0]["isDone"])

    def test_complete_missing_task(self) -> None:
        self.assertFalse(self.storage.complete(123))
        self.assertEqual(self.storage.list_all(), [])

    def test_persistence_across_instances(self) -> None:
        created = self.storage.create("Write tests", "normal")

        reloaded = TaskStorage(self.path)
        tasks = reloaded.list_all()
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0].title, created.title)
        self.assertEqual(tasks[0].id, created.id)

        new_task = reloaded.create("Second task", "low")
        self.assertEqual(new_task.id, created.id + 1)


if __name__ == "__main__":
    unittest.main()
