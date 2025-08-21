# imports - ui.py, by Mc_Snurtle
from PyQt6.QtWidgets import QApplication, QWidget
import sys

# ========== Variables ==========
theme: str = "auto"


# ========== Classes ==========
class UI(QApplication):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # layout
        self.window = QWidget()
        
    def mainloop(self):
        """Mainloop of the application."""
        self.window.show()


# ========== Main ==========
if __name__ == "__main__":
    app = UI(sys.argv)
    app.mainloop()
    app.exec()

