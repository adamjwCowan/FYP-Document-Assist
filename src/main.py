from PyQt5.QtWidgets import QApplication
from ui import ChatApp
import sys

def main():
    app = QApplication(sys.argv)
    window = ChatApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()