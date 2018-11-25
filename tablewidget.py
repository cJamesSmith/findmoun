from PyQt5.QtWidgets import (QWidget, QTableWidget, QHBoxLayout, QApplication, QDesktopWidget, QTableWidgetItem, QHeaderView)


class table(QWidget):

    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):

        self.resize(400, 400)
        self.setWindowTitle('TableWidget')

        self.table = QTableWidget(2, 2)
        self.table.setHorizontalHeaderLabels(['FileName', 'Muon?'])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        number = QTableWidgetItem('1.txt')
        name = QTableWidgetItem('Yes')
        self.table.setItem(0, 0, number)
        self.table.setItem(0, 1, name)
        layout = QHBoxLayout()

        layout.addWidget(self.table)
        self.setLayout(layout)
 #       self.center()
        self.show()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    exp = table()
    sys.exit(app.exec_())
