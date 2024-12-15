import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QLabel, QFileDialog, QLineEdit, QVBoxLayout, QWidget, QMessageBox, QCheckBox, QHBoxLayout, QFrame)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import hashlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

class FileEncryptionTool(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("File Encryption and Sharing Tool")
        self.setGeometry(100, 100, 600, 400)

        # Main layout
        self.layout = QVBoxLayout()

        # Title label
        self.title_label = QLabel("File Encryption and Sharing Tool")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setFont(QFont("Helvetica", 18, QFont.Bold))
        self.layout.addWidget(self.title_label)

        # Key input section
        key_layout = QVBoxLayout()
        self.key_label = QLabel("Encryption key:")
        self.key_label.setFont(QFont("Helvetica", 10))
        key_layout.addWidget(self.key_label)

        self.key_input = QLineEdit()
        self.key_input.setEchoMode(QLineEdit.Password)
        key_layout.addWidget(self.key_input)

        self.show_key_checkbox = QCheckBox("Show Key")
        self.show_key_checkbox.stateChanged.connect(self.toggle_key_visibility)
        key_layout.addWidget(self.show_key_checkbox)

        self.layout.addLayout(key_layout)

        # Drag-and-drop file area
        self.drag_drop_label = QLabel("Drag and drop a file here or use the 'Select File' button")
        self.drag_drop_label.setAlignment(Qt.AlignCenter)
        self.drag_drop_label.setFrameStyle(QFrame.StyledPanel | QFrame.Sunken)
        self.drag_drop_label.setFont(QFont("Helvetica", 10))
        self.drag_drop_label.setStyleSheet("background-color: #f0f0f0; border: 2px dashed #ccc; padding: 20px;")
        self.drag_drop_label.setAcceptDrops(True)
        self.drag_drop_label.installEventFilter(self)
        self.layout.addWidget(self.drag_drop_label)

        # Buttons
        button_layout = QHBoxLayout()

        self.generate_key_button = QPushButton("Generate Key")
        self.generate_key_button.clicked.connect(self.generate_key)
        self.generate_key_button.setFixedWidth(150)
        self.generate_key_button.setStyleSheet("background: lightgrey; border: 2px solid #ccc; border-radius: 5px;")
        button_layout.addWidget(self.generate_key_button)

        self.select_file_button = QPushButton("Select File")
        self.select_file_button.clicked.connect(self.select_file)
        self.select_file_button.setFixedWidth(150)
        self.select_file_button.setStyleSheet("background: lightgrey; border: 2px solid #ccc; border-radius: 5px;")
        button_layout.addWidget(self.select_file_button)

        self.layout.addLayout(button_layout)

        # Encryption and decryption buttons
        action_button_layout = QHBoxLayout()

        self.encrypt_button = QPushButton("Encrypt File")
        self.encrypt_button.clicked.connect(self.encrypt_file)
        self.encrypt_button.setFixedWidth(150)
        self.encrypt_button.setStyleSheet("background: lightgrey; border: 2px solid #ccc; border-radius: 5px;")
        action_button_layout.addWidget(self.encrypt_button)

        self.decrypt_button = QPushButton("Decrypt File")
        self.decrypt_button.clicked.connect(self.decrypt_file)
        self.decrypt_button.setFixedWidth(150)
        self.decrypt_button.setStyleSheet("background: lightgrey; border: 2px solid #ccc; border-radius: 5px;")
        action_button_layout.addWidget(self.decrypt_button)

        self.layout.addLayout(action_button_layout)

        # Status label
        self.status_label = QLabel("Status: Ready")
        self.layout.addWidget(self.status_label)

        # Set central widget
        container = QWidget()
        container.setLayout(self.layout)
        self.setCentralWidget(container)

        self.file_path = None

    def eventFilter(self, source, event):
        if source == self.drag_drop_label:
            if event.type() == event.DragEnter:
                if event.mimeData().hasUrls():
                    event.accept()
                    return True
            elif event.type() == event.Drop:
                if event.mimeData().hasUrls():
                    file_urls = event.mimeData().urls()
                    self.file_path = file_urls[0].toLocalFile()
                    self.status_label.setText(f"Selected File: {self.file_path}")
                    return True
        return super().eventFilter(source, event)

    def toggle_key_visibility(self):
        if self.show_key_checkbox.isChecked():
            self.key_input.setEchoMode(QLineEdit.Normal)
        else:
            self.key_input.setEchoMode(QLineEdit.Password)

    def generate_key(self):
        key = os.urandom(32)  # 256-bit key
        self.key_input.setText(key.hex())
        QMessageBox.information(self, "Key Generated", "A new encryption key has been generated.")

    def select_file(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File to Encrypt/Decrypt", "", "All Files (*)", options=options)
        if file_path:
            self.file_path = file_path
            self.status_label.setText(f"Selected File: {file_path}")

    def encrypt_file(self):
        if not self.file_path:
            QMessageBox.warning(self, "Error", "Please select a file first.")
            return

        key = self.key_input.text()
        if not key:
            QMessageBox.warning(self, "Error", "Please provide a valid encryption key.")
            return

        try:
            hashed_key = hashlib.sha256(bytes.fromhex(key)).digest()
            cipher = AES.new(hashed_key, AES.MODE_ECB)

            with open(self.file_path, 'rb') as file:
                file_data = file.read()

            encrypted_data = cipher.encrypt(pad(file_data, AES.block_size))

            encrypted_file_path = self.file_path + ".enc"
            with open(encrypted_file_path, 'wb') as encrypted_file:
                encrypted_file.write(encrypted_data)

            QMessageBox.information(self, "Success", f"File encrypted and saved as {encrypted_file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to encrypt file: {str(e)}")

    def decrypt_file(self):
        if not self.file_path:
            QMessageBox.warning(self, "Error", "Please select a file first.")
            return

        key = self.key_input.text()
        if not key:
            QMessageBox.warning(self, "Error", "Please provide a valid decryption key.")
            return

        try:
            hashed_key = hashlib.sha256(bytes.fromhex(key)).digest()
            cipher = AES.new(hashed_key, AES.MODE_ECB)

            with open(self.file_path, 'rb') as file:
                encrypted_data = file.read()

            decrypted_data = unpad(cipher.decrypt(encrypted_data), AES.block_size)

            decrypted_file_path = self.file_path.replace(".enc", "")
            with open(decrypted_file_path, 'wb') as decrypted_file:
                decrypted_file.write(decrypted_data)

            QMessageBox.information(self, "Success", f"File decrypted and saved as {decrypted_file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to decrypt file: {str(e)}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = FileEncryptionTool()
    main_window.show()
    sys.exit(app.exec_())
