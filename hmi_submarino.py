import sys
import serial
import numpy as np
import pyqtgraph as pg
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLabel
from PyQt5.QtCore import QTimer, Qt

# CONFIGURACIÓN: Escucha por el segundo puerto virtual
PUERTO_SERIAL = 'COM11' 
BAUDIOS = 115200

class HMI_Submarino(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("T.E.R.R.A.M.A.R. - Modo Simulación (VS Code)")
        self.resize(1000, 700)
        
        try:
            self.ser = serial.Serial(PUERTO_SERIAL, BAUDIOS, timeout=0.1)
            print(f"🔌 HMI conectado exitosamente al puerto {PUERTO_SERIAL}.")
        except:
            print(f"❌ No se pudo abrir el puerto {PUERTO_SERIAL}. Recuerda correr primero el simulador.")
            sys.exit()

        centro = QWidget()
        layout_principal = QHBoxLayout(centro)
        self.setCentralWidget(centro)

        panel_izq = QVBoxLayout()
        self.lbl_profundidad = QLabel("Profundidad: 0.00 m")
        self.lbl_profundidad.setStyleSheet("font-size: 24px; color: #00FF00; font-weight: bold;")
        self.lbl_vibracion = QLabel("Fuerza G: 0.00 G")
        self.lbl_vibracion.setStyleSheet("font-size: 24px; color: #FFCC00; font-weight: bold;")
        self.lbl_posicion = QLabel("Pitch: 0° | Roll: 0°")
        self.lbl_posicion.setStyleSheet("font-size: 18px; color: #FFFFFF;")
        
        panel_izq.addWidget(self.lbl_profundidad)
        panel_izq.addWidget(self.lbl_vibracion)
        panel_izq.addWidget(self.lbl_posicion)
        panel_izq.addStretch()
        layout_principal.addLayout(panel_izq, stretch=1)

        panel_der = QVBoxLayout()
        
        self.win_vibracion = pg.PlotWidget(title="Monitoreo Sísmico de Corteza (MPU6050 SIMULADO)")
        self.curve_vibracion = self.win_vibracion.plot(pen='y')
        self.datos_vibracion = list(np.zeros(100))
        panel_der.addWidget(self.win_vibracion)

        self.win_espectro = pg.PlotWidget(title="Espectrograma de Sonido Subacuático (Piezoeléctrico SIMULADO)")
        self.img_espectro = pg.ImageItem()
        self.win_espectro.addItem(self.img_espectro)
        
        self.matriz_espectro = np.zeros((32, 100))
        cmap = pg.colormap.get('thermal')
        self.img_espectro.setLookupTable(cmap.getLookupTable())
        
        panel_der.addWidget(self.win_espectro)
        layout_principal.addLayout(panel_der, stretch=3)

        self.timer = QTimer()
        self.timer.timeout.connect(self.actualizar_hmi)
        self.timer.start(10)

    def actualizar_hmi(self):
        if self.ser.in_waiting > 0:
            try:
                linea = self.ser.readline().decode('utf-8').strip()
                partes = linea.split(',')
                
                if len(partes) == 5:
                    prof = float(partes[0])
                    acel = float(partes[1])
                    pi = float(partes[2])
                    ro = float(partes[3])
                    fft_str = partes[4].split('-')
                    fft_vals = np.array([float(x) for x in fft_str])

                    self.lbl_profundidad.setText(f"Profundidad: {prof:.2f} m")
                    self.lbl_vibracion.setText(f"Fuerza G: {acel:.2f} G")
                    self.lbl_posicion.setText(f"Pitch: {pi:.1f}° | Roll: {ro:.1f}°")

                    self.datos_vibracion.pop(0)
                    self.datos_vibracion.append(acel)
                    self.curve_vibracion.setData(self.datos_vibracion)

                    self.matriz_espectro = np.roll(self.matriz_espectro, -1, axis=1)
                    self.matriz_espectro[:, -1] = fft_vals
                    self.img_espectro.setImage(self.matriz_espectro, autoLevels=True)
                    
            except Exception as e:
                pass

    def closeEvent(self, event):
        self.ser.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    palette = pg.QtGui.QPalette()
    palette.setColor(pg.QtGui.QPalette.Window, pg.QtGui.QColor(25, 25, 25))
    app.setPalette(palette)
    
    hmi = HMI_Submarino()
    hmi.show()
    sys.exit(app.exec_())