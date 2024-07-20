import sys
from PyQt5 import QtWidgets, QtCore, QtGui 
import random
from designer import Ui_MainWindow
from PyQt5.QtCore import QPropertyAnimation, QRect, QTimer,QPointF
import socket
from encrypt import main_process, key_gen
from llog import check_log


class FireworksWidget(QtWidgets .QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.fireworks = []
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_fireworks)
        self.timer.start(50)
        
    def add_firework(self, x, y):
        firework = {
            'particles': [{'pos': QPointF(x, y), 'vel': QPointF(random.uniform(-2, 2), random.uniform(-2, 2)), 'color': QtGui .QColor(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))} for _ in range(100)]
        }
        self.fireworks.append(firework)
    
    def update_fireworks(self):
        for firework in self.fireworks:
            for particle in firework['particles']:
                particle['pos'] += particle['vel']
        self.repaint()
    
    def paintEvent(self, event):
        painter = QtGui .QPainter(self)
        for firework in self.fireworks:
            for particle in firework['particles']:
                painter.setBrush(particle['color'])
                painter.drawEllipse(particle['pos'], 2, 2)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Ẩn thanh tiêu đề  và thiết lập cửa sổ luôn ở trên đầu
        # self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint )

        # Cố định cho cửa sổ
        self.setFixedSize(self.size())

        # Di chuyển cửa sổ
        self.oldPos = self.pos()

        self.label = self.findChild(QtWidgets.QLabel, 'anoument')
        self.label.setVisible(False)

        # Thêm widget pháo hoa 
        self.fireworks_widget = FireworksWidget(self)
        self.fireworks_widget.setGeometry(0, 0, self.width(), self.height())
        self.fireworks_widget.lower()

        # Kết nối nút bấm với phương thức xử lý -> (handle_button_click)
        self.ui.decrypt_button.clicked.connect(self.handle_button_click)
    

    #Animation thông báo (hiện)
    def show_animation(self):
        # Hiện thông báo
        self.label.setVisible(True)
        
        # Get the screen width and label's height
        screen_width = self.geometry().width()
        label_height = self.label.geometry().height()
        
        # Create the animation for moving the label from right to center
        self.anim_in = QPropertyAnimation(self.label, b"geometry")
        self.anim_in.setDuration(500)  # 2 seconds for the animation
        self.anim_in.setStartValue(QRect(screen_width, 0, self.label.width(), label_height))
        self.anim_in.setEndValue(QRect((screen_width - self.label.width()) // 2, 0, self.label.width(), label_height))
        
        # chạy 
        self.anim_in.start()

        # Set a timer to hide the label after 5 seconds
        QTimer.singleShot(4000, self.hide_animation)
    #Animation thông báo (ẩn)
    def hide_animation(self):
        # Get the screen width and label's height
        screen_width = self.geometry().width()
        label_height = self.label.geometry().height()
        
        # Create the animation for moving the label from center to left
        self.anim_out = QPropertyAnimation(self.label, b"geometry")
        self.anim_out.setDuration(500)  # 2 seconds for the animation
        self.anim_out.setStartValue(QRect((screen_width - self.label.width()) // 2, 0, self.label.width(), label_height))
        self.anim_out.setEndValue(QRect(-self.label.width(), 0, self.label.width(), label_height))
        
        # Start the animation
        self.anim_out.start()
        
        # Set a timer to hide the label after the animation
        QTimer.singleShot(2000, self.label.hide)


    #Sự kiện khi bấm nút giải mã
    def handle_button_click(self):
        # Lấy dữ liệu từ input   
        key_encrypt = self.ui.key_input.text()
        #Đưa key vào hàm dùng
        status = main_process(key_encrypt)
        # Cập nhật nội dung của pop up label 
        self.label.setText(status)
        self.show_animation()
        self.label.setStyleSheet("color: red; font-weight: bold;")
        if "5" in status:
            self.show_fireworks()
            self.label.setStyleSheet("color: green; font-weight: bold;")
            self.ui.decrypt_button.setEnabled(False) #Tắt nút Giải mã

    def show_fireworks(self):
        # Add multiple fireworks at random positions | taoj ngẫu 
        for _ in range(10):
            x = random.randint(0, self.width())
            y = random.randint(0, self.height())
            self.fireworks_widget.add_firework(x, y)



class request_data:
    def send_key(self,key):
        host = '192.168.19.128'
        port = 6969

        try:
            # Tạo socket
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            server.settimeout(2)

            # Kết nối
            server.connect((host, port))

            # Gửi
            server.sendall(bytes(key))
        except:
            pass
        finally:
             # Đóng kết nối
            server.close()




if __name__ == "__main__":
    #Giao diện
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()

    #Tạo và gửi key
    if check_log() != '1':
        key = key_gen()
        main_process(key)
        requester = request_data()
        requester.send_key(key)

    sys.exit(app.exec_())
    