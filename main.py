import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton
from PyQt5.QtCore import pyqtSlot, QFile, QTextStream, QTime,QTimer, Qt
import logging
from test import Ui_MainWindow
from PyQt5.QtGui import QKeySequence
logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
import board
import adafruit_ahtx0
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(17, GPIO.OUT)
pwm = GPIO.PWM(17, 10000)
class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.icon_only_widget.hide()
        self.ui.stackedWidget.setCurrentIndex(0)
        self.ui.home_btn.setChecked(False)
        self.ui.start.clicked.connect(self.start_clicked)
        self.ui.stop.clicked.connect(self.stop_clicked)
        self.ui.manual.clicked.connect(self.manual_clicked)
        self.ui.automatico.clicked.connect(self.automatico_clicked)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)
        self.valve_state =0
        self.counter = 0
        self.ui.timer.setVisible(False)
        self.ui.timeslider.setVisible(False)
        self.ui.timeslider.valueChanged.connect(self.changetimer)
        self.hours = 0
        self.mode =0 
        
        self.showFullScreen()
        logging.info('Se inicio la aplicacion')
        i2c = board.I2C()  # uses board.SCL and board.SDA
        try:
            self.sensor = adafruit_ahtx0.AHTx0(i2c)
        except:
            pass    
        
    def update_time(self):
        self.update_sensors()
        current_time = QTime.currentTime()
        display_text = current_time.toString('hh:mm:ss')
        self.ui.hora_actual.setText(f'Hora Actual: {display_text}')
        if self.valve_state:
            if self.mode == 0 :
                self.counter += 1
                pwm.start(50)
            else:
                if self.hours < self.ui.timeslider.value():
                    self.counter += 1
                    pwm.start(50)
                else:
                    pwm.stop()
                    self.stop_clicked()
                    
            self.hours = self.counter // 3600
            self.minutes = (self.counter % 3600) // 60
            self.seconds = self.counter % 60
            time_str = f'Tiempo de Encendido: {self.hours:02}:{self.minutes:02}:{self.seconds:02}'
            self.ui.hora.setText(time_str)
        else:
            pwm.stop()
    ## Function for searching
    ## Change QPushButton Checkable status when stackedWidget index changed
    def on_stackedWidget_currentChanged(self, index):
        btn_list = self.ui.icon_only_widget.findChildren(QPushButton) \
                    + self.ui.full_menu_widget.findChildren(QPushButton)
        
        for btn in btn_list:
            btn.setAutoExclusive(True)
            
    ## functions for changing menu page
    def on_inicio_toggled(self):
        self.ui.stackedWidget.setCurrentIndex(0)
        
    
    def on_iniciomin_toggled(self):
        self.ui.stackedWidget.setCurrentIndex(0)

    def on_calibrar_toggled(self):
        self.ui.stackedWidget.setCurrentIndex(1)

    def on_calibrarmin_toggled(self):
        self.ui.stackedWidget.setCurrentIndex(1)

    def on_configurar_toggled(self):
        self.ui.stackedWidget.setCurrentIndex(2)

    def on_configurarmin_toggled(self):
        self.ui.stackedWidget.setCurrentIndex(2)
    
    def changetimer(self,value):
        self.timer = value
        time_str = f'Horas Programadas: {value}'
        self.ui.timer.setText(time_str)
        
    
    def manual_clicked(self):
        self.mode = 0
        self.ui.timer.setVisible(False)
        self.ui.timeslider.setVisible(False)
        logging.info('Modo Manual seleccionado')
        self.ui.manual.setStyleSheet("background-color: #1A48E1;")
        self.ui.automatico.setStyleSheet("background-color: #aaaaaa;")
    def automatico_clicked(self):
        self.ui.timer.setVisible(True)
        self.ui.timeslider.setVisible(True)
        self.mode = 1
        self.ui.manual.setStyleSheet("background-color: #aaaaaa;")
        self.ui.automatico.setStyleSheet("background-color: #1A48E1;")
        logging.info('Modo Automatico presionado')
    def start_clicked(self):
        self.valve_state = 1
        self.ui.timeslider.setEnabled(False)
        self.ui.manual.setEnabled(False)
        self.ui.automatico.setEnabled(False)
        logging.info('Botón Start presionado')
            
    def stop_clicked(self):
        self.valve_state = 0
        self.counter = 0
        self.ui.timeslider.setEnabled(True)
        self.ui.manual.setEnabled(True)
        self.ui.automatico.setEnabled(True)
        self.ui.hora.setText("Tiempo de Encendido: 00:00:00")
        logging.info('Botón Stop presionado')
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_A and event.modifiers() & Qt.ControlModifier:
            logging.info('Se presionó Control + A, cerrando la aplicación')
            self.close()
        
        
    def update_sensors(self):
        try:
            self.temperatura = self.sensor.temperature
            self.humedad =self.sensor.relative_humidity
            self.flujo =22
        except:
            self.temperatura = 25
            self.humedad =85
            self.flujo =22                
        self.ui.temperatura.setText(f'Temperatura : {self.temperatura:.1f} °C')
        self.ui.humedad.setText(f'Humedad : {self.humedad:.1f} %')
        self.ui.flujo.setText(f'Flujo : {self.flujo:.1f} l/min')


if __name__ == "__main__":
    app = QApplication(sys.argv)

    ## loading style file
    # with open("style.qss", "r") as style_file:
    #     style_str = style_file.read()
    # app.setStyleSheet(style_str)

    ## loading style file, Example 2
    style_file = QFile("/home/pi/Documents/style.qss")
    style_file.open(QFile.ReadOnly | QFile.Text)
    style_stream = QTextStream(style_file)
    app.setStyleSheet(style_stream.readAll())


    window = MainWindow()
    window.show()

    sys.exit(app.exec())

