import sys

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QLabel,
)

from network import Messenger


STYLE = """
QWidget {
    background-color: #FFF0F5;
    color: #5A2A4A;
    font-family: 'Segoe UI';
    font-size: 14px;
}
QLabel#title {
    color: #C2185B;
    font-size: 22px;
    font-weight: bold;
}
QLineEdit, QTextEdit {
    background-color: #FFFFFF;
    border: 2px solid #FFB6C1;
    border-radius: 12px;
    padding: 6px;
}
QPushButton {
    background-color: #FF8FB1;
    color: white;
    border: none;
    border-radius: 12px;
    padding: 8px 18px;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #FF6F9C;
}
"""


class ChatWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.messenger = None
        self.peer = None

        self.setWindowTitle("Keytie")
        self.setStyleSheet(STYLE)
        self.resize(420, 560)

        title = QLabel("Keytie 💗")
        title.setObjectName("title")

        self.me_input = QLineEdit()
        self.me_input.setPlaceholderText("Моё имя")
        self.peer_input = QLineEdit()
        self.peer_input.setPlaceholderText("Собеседник")
        self.connect_button = QPushButton("Подключиться")
        self.connect_button.clicked.connect(self.start_chat)

        login_row = QHBoxLayout()
        login_row.addWidget(self.me_input)
        login_row.addWidget(self.peer_input)
        login_row.addWidget(self.connect_button)

        self.chat_log = QTextEdit()
        self.chat_log.setReadOnly(True)

        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Сообщение...")
        self.message_input.returnPressed.connect(self.send)
        self.send_button = QPushButton("Отправить")
        self.send_button.clicked.connect(self.send)

        send_row = QHBoxLayout()
        send_row.addWidget(self.message_input)
        send_row.addWidget(self.send_button)

        layout = QVBoxLayout()
        layout.addWidget(title)
        layout.addLayout(login_row)
        layout.addWidget(self.chat_log)
        layout.addLayout(send_row)
        self.setLayout(layout)

        self.timer = QTimer()
        self.timer.timeout.connect(self.poll)

    def start_chat(self):
        self.messenger = Messenger(self.me_input.text())
        self.messenger.register()
        self.peer = self.peer_input.text()
        self.me_input.setEnabled(False)
        self.peer_input.setEnabled(False)
        self.connect_button.setEnabled(False)
        self.chat_log.append(f"<i>Подключено как {self.messenger.username}</i>")
        self.timer.start(1000)

    def send(self):
        text = self.message_input.text()
        if not text or self.messenger is None:
            return
        try:
            self.messenger.send(self.peer, text)
            self.chat_log.append(f"<b style='color:#C2185B'>Я:</b> {text}")
            self.message_input.clear()
        except Exception:
            self.chat_log.append("<i>Собеседник ещё не подключился</i>")

    def poll(self):
        try:
            for sender, text in self.messenger.receive():
                self.chat_log.append(f"<b style='color:#8E24AA'>{sender}:</b> {text}")
        except Exception:
            pass


def main():
    app = QApplication(sys.argv)
    window = ChatWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()