import sys
import json
from PyQt6 import QtCore, QtGui, QtWidgets, uic
from PyQt6.QtCore import Qt, QModelIndex

# --- UI ---
qt_creator_file = "mainwindow.ui"
Ui_MainWindow, QtBaseClass = uic.loadUiType(qt_creator_file)

# --- App must exist before any Pixmap/Icon ---
app = QtWidgets.QApplication(sys.argv)

# --- Icon (optional) ---
_tick_img = QtGui.QImage("tick.png")
TICK_ICON = QtGui.QIcon(QtGui.QPixmap.fromImage(_tick_img)) if not _tick_img.isNull() else None


class TodoModel(QtCore.QAbstractListModel):
    def __init__(self, *args, todos=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.todos = list(todos or [])  # list of (bool, str)

    def data(self, index: QtCore.QModelIndex, role: int):
        if not index.isValid():
            return None
        status, text = self.todos[index.row()]
        if role == Qt.ItemDataRole.DisplayRole:
            return text
        if role == Qt.ItemDataRole.DecorationRole and status and TICK_ICON is not None:
            return TICK_ICON
        return None

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        if parent.isValid():
            return 0
        return len(self.todos)

    # Helpers to mutate with proper signals
    def add_item(self, text: str):
        row = len(self.todos)
        self.beginInsertRows(QModelIndex(), row, row)
        self.todos.append((False, text))
        self.endInsertRows()

    def remove_row(self, row: int):
        if 0 <= row < len(self.todos):
            self.beginRemoveRows(QModelIndex(), row, row)
            del self.todos[row]
            self.endRemoveRows()

    def complete_row(self, row: int):
        if 0 <= row < len(self.todos):
            self.todos[row] = (True, self.todos[row][1])
            idx = self.index(row, 0)
            self.dataChanged.emit(idx, idx, [Qt.ItemDataRole.DecorationRole])


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.model = TodoModel()
        self.load()                     # populate model before setting it on the view
        self.todoView.setModel(self.model)

        self.addButton.pressed.connect(self.add)
        self.deleteButton.pressed.connect(self.delete)
        self.completeButton.pressed.connect(self.complete)

    def add(self):
        text = self.todoEdit.text().strip()
        if text:
            self.model.add_item(text)
            self.todoEdit.clear()
            self.save()

    def delete(self):
        indexes = self.todoView.selectedIndexes()
        if indexes:
            row = indexes[0].row()
            self.model.remove_row(row)
            self.todoView.clearSelection()
            self.save()

    def complete(self):
        indexes = self.todoView.selectedIndexes()
        if indexes:
            row = indexes[0].row()
            self.model.complete_row(row)
            self.todoView.clearSelection()
            self.save()

    def load(self):
        try:
            with open("data.db", "r", encoding="utf-8") as f:
                items = json.load(f)  # expect [[bool, str], ...] or [(bool, str), ...]
                # normalize to list of tuples (bool, str)
                norm = []
                for it in items:
                    if isinstance(it, (list, tuple)) and len(it) == 2:
                        norm.append((bool(it[0]), str(it[1])))
                self.model.beginResetModel()
                self.model.todos = norm
                self.model.endResetModel()
        except FileNotFoundError:
            pass  # first run – no data yet
        except Exception as e:
            print(f"Load error: {e}")

    def save(self):
        try:
            with open("data.db", "w", encoding="utf-8") as f:
                json.dump(self.model.todos, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Save error: {e}")


if __name__ == "__main__":
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
