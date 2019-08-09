# -*- coding: utf-8 -*-

from sys import argv, exit

from OpenGL.GL import *
from OpenGL.GLU import gluLookAt
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QOpenGLWidget
from math import sin, cos, radians


def ver_alzado():
    pass


def ver_planta():
    pass


def ver_perfil():
    pass


class Renderizador(QOpenGLWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self._z = 0
        self._y = 0
        self.at = 45
        self.ap = 45
        self.x = 0
        self.y = 0
        self.z = 0
        self.vertices_vertical = ((10, 10, 0), (-10, 10, 0), (-10, 0, 0), (10, 0, 0))
        self.vertices_vertical_debajo = ((10, 0, 0), (-10, 0, 0), (-10, -10, 0), (10, -10, 0))
        self.vertices_horizontal = ((10, 0, 0), (10, 0, 10), (-10, 0, 10), (-10, 0, 0))
        self.vertices_horizontal_detras = ((10, 0, 0), (10, 0, -10), (-10, 0, -10), (-10, 0, 0))
        self.vertices_borde_v = ((10, 10, 0), (10, -10, 0), (-10, -10, 0), (-10, 10, 0))
        self.vertices_borde_h = ((10, 0, 10), (-10, 0, 10), (-10, 0, -10), (10, 0, -10))

    def initializeGL(self):
        glClear(GL_COLOR_BUFFER_BIT)
        glEnable(GL_DEPTH_TEST)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(-10, 10, -10, 10, -150, 150)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    def paintGL(self):
        glClearColor(1, 1, 1, 1)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        if self.at == 0:
            self.at = 360
        self.x = sin(radians(self.at)) * cos(radians(self.ap))
        self.z = sin(radians(self.at)) * sin(radians(self.ap)) + self._z
        self.y = cos(radians(self.at)) + self._y

        gluLookAt(self.x, self.y, self.z, 0, self._y, self._z, 0, 1, 0)

        glLineWidth(5)
        glBegin(GL_LINES)
        # X ROJO
        glColor(1, 0, 0)
        glVertex(0, 0, 0)
        glVertex(1, 0, 0)
        # Y VERDE
        glColor(0, 1, 0)
        glVertex(0, 0, 0)
        glVertex(0, 1, 0)
        # Z AZUL
        glColor(0, 0, 1)
        glVertex(0, 0, 0)
        glVertex(0, 0, 1)

        glEnd()

        glPointSize(5)
        glEnable(GL_POINT_SMOOTH)
        glBegin(GL_POINTS)
        glVertex(1, 1, 1)
        glEnd()

        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glBlendColor(0, 1, 0, 0.5)
        glDepthMask(GL_FALSE)
        glBegin(GL_QUADS)
        glColor((0, 1, 0, 0.5))
        for vertex in range(4):
            glVertex(self.vertices_vertical[vertex])
        glColor((1, 0, 0, 0.5))
        for vertex in range(4):
            glVertex(self.vertices_horizontal[vertex])
        for vertex in range(4):
            glVertex(self.vertices_horizontal_detras[vertex])
        glColor((0, 1, 0, 0.5))
        for vertex in range(4):
            glVertex(self.vertices_vertical_debajo[vertex])
        glEnd()
        glDepthMask(GL_TRUE)
        glDisable(GL_BLEND)
        glLineWidth(1)
        glBegin(GL_LINE_LOOP)
        for vertex in range(4):
            glVertex(self.vertices_borde_v[vertex])
        glColor((1, 0, 0, 0.5))
        glEnd()
        glBegin(GL_LINE_LOOP)
        for vertex in range(4):
            glVertex(self.vertices_borde_h[vertex])
        glEnd()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_W:
            self.at -= 15
        elif event.key() == QtCore.Qt.Key_A:
            self.ap += 15
        elif event.key() == QtCore.Qt.Key_S:
            self.at += 15
        elif event.key() == QtCore.Qt.Key_D:
            self.ap -= 15
        elif event.key() == QtCore.Qt.Key_Left:
            self._z -= 1
        elif event.key() == QtCore.Qt.Key_Up:
            self._y += 1
        elif event.key() == QtCore.Qt.Key_Right:
            self._z += 1
        elif event.key() == QtCore.Qt.Key_Down:
            self._y -= 1

        global x, y, z, at, ap
        x = round(self.x, 2)
        y = round(self.y, 2)
        z = round(self.z, 2)
        at = self.at
        ap = self.ap

        ui.update()
        self.update()
        super().keyPressEvent(event)


class UiVentana:
    def __init__(self):
        ventana.resize(1500, 750)
        ventana.setLayoutDirection(QtCore.Qt.LeftToRight)
        ventana.setToolButtonStyle(QtCore.Qt.ToolButtonIconOnly)
        ventana.setFixedSize(ventana.size())
        font = QtGui.QFont()
        font.setPointSize(10)
        self.widget_central = QtWidgets.QWidget(ventana)
        self.gridLayoutWidget = QtWidgets.QWidget(self.widget_central)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(1000, 50, 250, 55))
        self.Vistas = QtWidgets.QGridLayout(self.gridLayoutWidget)
        self.Vistas.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.Vistas.setContentsMargins(5, 5, 5, 5)
        self.Vistas.setHorizontalSpacing(6)
        self.Vistas.setVerticalSpacing(4)
        self.texto_vista = QtWidgets.QLabel(self.gridLayoutWidget)
        self.texto_vista.setFont(font)
        self.Vistas.addWidget(self.texto_vista, 0, 0, 1, 4)
        self.texto_vista.setText("Vista:")
        self.boton_planta = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.boton_planta.setText("Planta")
        self.Vistas.addWidget(self.boton_planta, 1, 1, 1, 1)
        self.boton_perfil = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.boton_perfil.setText("Perfil")
        self.Vistas.addWidget(self.boton_perfil, 1, 2, 1, 1)
        self.boton_alzado = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.boton_alzado.setText("Alzado")
        self.Vistas.addWidget(self.boton_alzado, 1, 0, 1, 1)

        self.Visor = Renderizador(self.widget_central)
        self.Visor.setGeometry(QtCore.QRect(0, 0, 1000, 1000))
        self.Visor.setFocusPolicy(QtCore.Qt.StrongFocus)

        self.gridLayoutWidget_2 = QtWidgets.QWidget(self.widget_central)
        self.gridLayoutWidget_2.setGeometry(QtCore.QRect(1000, 100, 250, 178))
        self.Punto = QtWidgets.QGridLayout(self.gridLayoutWidget_2)
        self.Punto.setContentsMargins(5, 5, 5, 5)
        self.Punto.setVerticalSpacing(4)
        self.texto_nombre = QtWidgets.QLabel(self.gridLayoutWidget_2)
        self.texto_nombre.setAlignment(QtCore.Qt.AlignCenter)
        self.texto_nombre.setText("Nombre:")
        self.Punto.addWidget(self.texto_nombre, 3, 0, 1, 1)
        self.crear_punto = QtWidgets.QPushButton(self.gridLayoutWidget_2)
        self.crear_punto.setMaximumSize(QtCore.QSize(65, 16777215))
        self.crear_punto.setText("Crear")
        self.Punto.addWidget(self.crear_punto, 3, 2, 1, 1)
        self.texto_cota = QtWidgets.QLabel(self.gridLayoutWidget_2)
        self.texto_cota.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.texto_cota.setAlignment(QtCore.Qt.AlignCenter)
        self.texto_cota.setText("Cota")
        self.Punto.addWidget(self.texto_cota, 1, 2, 1, 1)
        self.texto_do = QtWidgets.QLabel(self.gridLayoutWidget_2)
        self.texto_do.setAlignment(QtCore.Qt.AlignCenter)
        self.texto_do.setText("D. Origen")
        self.Punto.addWidget(self.texto_do, 1, 0, 1, 1)
        self.texto_alej = QtWidgets.QLabel(self.gridLayoutWidget_2)
        self.texto_alej.setAlignment(QtCore.Qt.AlignCenter)
        self.texto_alej.setText("Alejamiento")
        self.Punto.addWidget(self.texto_alej, 1, 1, 1, 1)
        self.texto_crearpunto = QtWidgets.QLabel(self.gridLayoutWidget_2)
        self.texto_crearpunto.setFont(font)
        self.texto_crearpunto.setText("Crear punto:")
        self.Punto.addWidget(self.texto_crearpunto, 0, 0, 1, 3)
        self.textEdit = QtWidgets.QTextEdit(self.gridLayoutWidget_2)
        self.textEdit.setMaximumSize(QtCore.QSize(100, 24))
        self.Punto.addWidget(self.textEdit, 3, 1, 1, 1)
        self.VerPuntos = QtWidgets.QScrollArea(self.gridLayoutWidget_2)
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 239, 77))
        self.VerPuntos.setWidget(self.scrollAreaWidgetContents)
        self.Punto.addWidget(self.VerPuntos, 4, 0, 1, 3)
        self.valor_do = QtWidgets.QSpinBox(self.gridLayoutWidget_2)
        self.Punto.addWidget(self.valor_do, 2, 0, 1, 1)
        self.valor_alej = QtWidgets.QSpinBox(self.gridLayoutWidget_2)
        self.Punto.addWidget(self.valor_alej, 2, 1, 1, 1)
        self.valor_cota = QtWidgets.QSpinBox(self.gridLayoutWidget_2)
        self.Punto.addWidget(self.valor_cota, 2, 2, 1, 1)

        self.gridLayoutWidget_3 = QtWidgets.QWidget(self.widget_central)
        self.gridLayoutWidget_3.setGeometry(QtCore.QRect(1000, 0, 250, 80))
        self.infocuadro = QtWidgets.QGridLayout(self.gridLayoutWidget_3)
        self.infocuadro.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
        self.infocuadro.setContentsMargins(0, 0, 0, 0)
        self.infocuadro.setVerticalSpacing(6)
        self.label_2 = QtWidgets.QLabel(self.gridLayoutWidget_3)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_2.setFont(font)
        self.infocuadro.addWidget(self.label_2, 0, 0, 1, 1)
        self.cuadrante = QtWidgets.QLabel(self.gridLayoutWidget_3)
        self.infocuadro.addWidget(self.cuadrante, 1, 1, 1, 1)
        self.label_3 = QtWidgets.QLabel(self.gridLayoutWidget_3)
        self.infocuadro.addWidget(self.label_3, 1, 0, 1, 1)
        self.label = QtWidgets.QLabel(self.gridLayoutWidget_3)
        self.infocuadro.addWidget(self.label, 2, 0, 1, 1)
        self.coordenadas = QtWidgets.QLabel(self.gridLayoutWidget_3)
        self.infocuadro.addWidget(self.coordenadas, 2, 1, 1, 1)
        self.label_2.setText("Información:")
        self.cuadrante.setText("Primer cuadrante")
        self.label_3.setText("Cuadrante:")
        self.label.setText("Coordenadas:")

        ventana.setCentralWidget(self.widget_central)
        ventana.setWindowTitle("Dibujo técnico")
        ventana.show()

    def update(self):
        self.coordenadas.setText("X: {} Y: {} Z: {} Ángulo vertical: {} Ángulo horizontal: {}".format(x, y, z, at, ap))
        if z == 0 and y == 0:  # puntoCuadrante en LT
            self.cuadrante.setText("Línea de tierra")
        elif z == 0:
            if y > 0:
                self.cuadrante.setText("Plano vertical positivo")
            else:
                self.cuadrante.setText("Plano vertical negativo")
        elif y == 0:
            if z > 0:
                self.cuadrante.setText("Plano horizontal positivo")
            else:
                self.cuadrante.setText("Plano horizontal negativo")
        elif z > 0:
            if y > 0:
                self.cuadrante.setText("Primer cuadrante")
            else:
                self.cuadrante.setText("Cuarto cuadrante")
        else:
            if y > 0:
                self.cuadrante.setText("Segundo cuadrante")
            else:
                self.cuadrante.setText("Tercer cuadrante")


def imprimir():
    # print(p_x)
    # print(p_y)
    # print(p_z)

    print("X: " + str(x))
    print("Y: " + str(y))
    print("Z: " + str(z))


if __name__ == "__main__":
    app = QtWidgets.QApplication(argv)
    ventana = QtWidgets.QMainWindow()
    ui = UiVentana()
    exit(app.exec_())
