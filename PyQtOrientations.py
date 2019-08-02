<< << << < Updated
upstream
# -*- coding: utf-8 -*-

import sys

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QOpenGLWidget


def ver_alzado():
    pass


def ver_planta():
    pass


def ver_perfil():
    pass


class Renderizador(QOpenGLWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self._x = -0.1
        self._y = -0.1
        self._z = -0.1
        self._rx = 45
        self._ry = 45
        self._rz = 90
        self.vertices_vertical = [[10, 10, 0], [10, -10, 0],
                                  [-10, -10, 0], [-10, 10, 0]]
        self.vertices_horizontal = [[10, 0, -10], [10, 0, 10],
                                    [-10, 0, 10], [-10, 0, -10]]

    def initializeGL(self):
        glClear(GL_COLOR_BUFFER_BIT)
        glEnable(GL_DEPTH_TEST)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(-10, 10, 10, -10, -150, 150)
        glTranslate(self._x, self._y, self._z)
        glRotate(self._rx, 1, 0, 0)
        glRotate(self._ry, 0, 1, 0)
        glRotate(self._rz, 0, 0, 1)

    def paintGL(self):
        glClearColor(1, 1, 1, 1)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        glTranslate(self._x, self._y, self._z)
        glRotate(self._rx, 1, 0, 0)
        glRotate(self._ry, 0, 1, 0)
        glRotate(self._rz, 0, 0, 1)

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
        # glDepthMask(GL_FALSE)
        glBlendFunc(GL_SRC_ALPHA, GL_SRC_ALPHA)
        glBlendColor(0, 1, 0, 0.6)
        glBegin(GL_QUADS)
        glColor((0, 1, 0, 0.6))
        for vertex in range(4):
            glVertex(self.vertices_vertical[vertex])
        glColor((1, 0, 0, 0.6))
        for vertex in range(4):
            glVertex(self.vertices_horizontal[vertex])
        glEnd()
        glDisable(GL_BLEND)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Left:
            self._y += 0.2
        elif event.key() == QtCore.Qt.Key_Up:
            self._x += 0.2
        elif event.key() == QtCore.Qt.Key_Right:
            self._y -= 0.2
        elif event.key() == QtCore.Qt.Key_Down:
            self._x -= 0.2
        elif event.key() == QtCore.Qt.Key_W:
            self._rz += 45
        elif event.key() == QtCore.Qt.Key_A:
            self._ry += 45
        elif event.key() == QtCore.Qt.Key_S:
            self._rz -= 45
        elif event.key() == QtCore.Qt.Key_D:
            self._ry -= 45
        elif event.key() == QtCore.Qt.Key_E:
            self._rx -= 45
        elif event.key() == QtCore.Qt.Key_Q:
            self._rx += 45
        global p_x
        p_x = self._x
        global p_y
        p_y = self._y
        global p_z
        p_z = self._z
        global p_rx
        p_rx = self._rx
        global p_ry
        p_ry = self._ry
        global p_rz
        p_rz = self._rz
        self.update()
        super().keyPressEvent(event)


class UiVentana:
    def __init__(self):
        ventana.resize(1500, 750)
        ventana.setLayoutDirection(QtCore.Qt.LeftToRight)
        ventana.setToolButtonStyle(QtCore.Qt.ToolButtonIconOnly)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.widget_central = QtWidgets.QWidget(ventana)
        self.gridLayoutWidget = QtWidgets.QWidget(self.widget_central)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(1000, 0, 251, 55))
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
        self.boton_planta.setMaximumSize(QtCore.QSize(50, 16777215))
        self.boton_planta.setText("Planta")
        self.Vistas.addWidget(self.boton_planta, 1, 1, 1, 1)
        self.boton_perfil = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.boton_perfil.setText("Perfil")
        self.boton_perfil.setMaximumSize(QtCore.QSize(50, 16777215))
        self.Vistas.addWidget(self.boton_perfil, 1, 2, 1, 1)
        self.boton_alzado = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.boton_alzado.setMaximumSize(QtCore.QSize(50, 16777215))
        self.boton_alzado.setText("Alzado")
        self.Vistas.addWidget(self.boton_alzado, 1, 0, 1, 1)

        self.boton_debug = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.boton_debug.setText("Debug")
        self.boton_debug.setMaximumSize(QtCore.QSize(50, 16777215))
        self.Vistas.addWidget(self.boton_perfil, 1, 3, 1, 1)
        self.boton_debug.clicked.connect(lambda: imprimir())

        self.Visor = Renderizador(self.widget_central)
        self.Visor.setGeometry(QtCore.QRect(0, 0, 1000, 750))
        self.Visor.setFocusPolicy(QtCore.Qt.StrongFocus)

        self.gridLayoutWidget_2 = QtWidgets.QWidget(self.widget_central)
        self.gridLayoutWidget_2.setGeometry(QtCore.QRect(1000, 50, 251, 178))
        self.Punto = QtWidgets.QGridLayout(self.gridLayoutWidget_2)
        self.Punto.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.Punto.setContentsMargins(5, 5, 5, 5)
        self.Punto.setVerticalSpacing(4)
        self.texto_nombre = QtWidgets.QLabel(self.gridLayoutWidget_2)
        self.texto_nombre.setMaximumSize(QtCore.QSize(70, 16777215))
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
        self.texto_do.setMinimumSize(QtCore.QSize(70, 0))
        self.texto_do.setMaximumSize(QtCore.QSize(70, 16777215))
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
        ventana.setCentralWidget(self.widget_central)
        QtCore.QMetaObject.connectSlotsByName(ventana)
        ventana.setWindowTitle("Dibujo técnico")
        ventana.show()


def imprimir():
    # print(p_x)
    # print(p_y)
    # print(p_z)
    print("X: " + str(p_rx))
    print("Y: " + str(p_ry))
    print("Z: " + str(p_rz))


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    ventana = QtWidgets.QMainWindow()
    ui = UiVentana()
    sys.exit(app.exec_())
== == == =
# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QOpenGLWidget
from OpenGL.GL import *
import sys


def ver_alzado():
    pass


def ver_planta():
    pass


def ver_perfil():
    pass


class Renderizador(QOpenGLWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self._x = -0.1
        self._y = -0.1
        self._z = -0.1
        self._rx = 45
        self._ry = 45
        self._rz = 90
        self.vertices_vertical = [[10, 10, 0], [10, -10, 0],
                                  [-10, -10, 0], [-10, 10, 0]]
        self.vertices_horizontal = [[10, 0, -10], [10, 0, 10],
                                    [-10, 0, 10], [-10, 0, -10]]

    def initializeGL(self):
        glClear(GL_COLOR_BUFFER_BIT)
        glEnable(GL_DEPTH_TEST)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(-10, 10, 10, -10, -150, 150)
        glTranslate(self._x, self._y, self._z)
        glRotate(self._rx, 1, 0, 0)
        glRotate(self._ry, 0, 1, 0)
        glRotate(self._rz, 0, 0, 1)

    def paintGL(self):
        glClearColor(1, 1, 1, 1)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        glTranslate(self._x, self._y, self._z)
        glRotate(self._rx, 1, 0, 0)
        glRotate(self._ry, 0, 1, 0)
        glRotate(self._rz, 0, 0, 1)

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
        # glDepthMask(GL_FALSE)
        glBlendFunc(GL_SRC_ALPHA, GL_SRC_ALPHA)
        glBlendColor(0, 1, 0, 0.6)
        glBegin(GL_QUADS)
        glColor((0, 1, 0, 0.6))
        for vertex in range(4):
            glVertex(self.vertices_vertical[vertex])
        glColor((1, 0, 0, 0.6))
        for vertex in range(4):
            glVertex(self.vertices_horizontal[vertex])
        glEnd()
        glDisable(GL_BLEND)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Left:
            self._y += 0.2
        elif event.key() == QtCore.Qt.Key_Up:
            self._x += 0.2
        elif event.key() == QtCore.Qt.Key_Right:
            self._y -= 0.2
        elif event.key() == QtCore.Qt.Key_Down:
            self._x -= 0.2
        elif event.key() == QtCore.Qt.Key_W:
            self._rz += 45
        elif event.key() == QtCore.Qt.Key_A:
            self._ry += 45
        elif event.key() == QtCore.Qt.Key_S:
            self._rz -= 45
        elif event.key() == QtCore.Qt.Key_D:
            self._ry -= 45
        elif event.key() == QtCore.Qt.Key_E:
            self._rx -= 45
        elif event.key() == QtCore.Qt.Key_Q:
            self._rx += 45
        global p_x
        p_x = self._x
        global p_y
        p_y = self._y
        global p_z
        p_z = self._z
        global p_rx
        p_rx = self._rx
        global p_ry
        p_ry = self._ry
        global p_rz
        p_rz = self._rz
        self.update()
        super().keyPressEvent(event)


class UiVentana:
    def __init__(self):
        ventana.resize(1500, 750)
        ventana.setLayoutDirection(QtCore.Qt.LeftToRight)
        ventana.setToolButtonStyle(QtCore.Qt.ToolButtonIconOnly)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.widget_central = QtWidgets.QWidget(ventana)
        self.gridLayoutWidget = QtWidgets.QWidget(self.widget_central)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(1000, 0, 251, 55))
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
        self.boton_planta.setMaximumSize(QtCore.QSize(50, 16777215))
        self.boton_planta.setText("Planta")
        self.Vistas.addWidget(self.boton_planta, 1, 1, 1, 1)
        self.boton_perfil = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.boton_perfil.setText("Perfil")
        self.boton_perfil.setMaximumSize(QtCore.QSize(50, 16777215))
        self.Vistas.addWidget(self.boton_perfil, 1, 2, 1, 1)
        self.boton_alzado = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.boton_alzado.setMaximumSize(QtCore.QSize(50, 16777215))
        self.boton_alzado.setText("Alzado")
        self.Vistas.addWidget(self.boton_alzado, 1, 0, 1, 1)

        self.boton_debug = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.boton_debug.setText("Debug")
        self.boton_debug.setMaximumSize(QtCore.QSize(50, 16777215))
        self.Vistas.addWidget(self.boton_perfil, 1, 3, 1, 1)
        self.boton_debug.clicked.connect(lambda: imprimir())

        self.Visor = Renderizador(self.widget_central)
        self.Visor.setGeometry(QtCore.QRect(0, 0, 1000, 750))
        self.Visor.setFocusPolicy(QtCore.Qt.StrongFocus)

        self.gridLayoutWidget_2 = QtWidgets.QWidget(self.widget_central)
        self.gridLayoutWidget_2.setGeometry(QtCore.QRect(1000, 50, 251, 178))
        self.Punto = QtWidgets.QGridLayout(self.gridLayoutWidget_2)
        self.Punto.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.Punto.setContentsMargins(5, 5, 5, 5)
        self.Punto.setVerticalSpacing(4)
        self.texto_nombre = QtWidgets.QLabel(self.gridLayoutWidget_2)
        self.texto_nombre.setMaximumSize(QtCore.QSize(70, 16777215))
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
        self.texto_do.setMinimumSize(QtCore.QSize(70, 0))
        self.texto_do.setMaximumSize(QtCore.QSize(70, 16777215))
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
        ventana.setCentralWidget(self.widget_central)
        QtCore.QMetaObject.connectSlotsByName(ventana)
        ventana.setWindowTitle("Dibujo técnico")
        ventana.show()


def imprimir():
    # print(p_x)
    # print(p_y)
    # print(p_z)
    print("X: " + str(p_rx))
    print("Y: " + str(p_ry))
    print("Z: " + str(p_rz))


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    ventana = QtWidgets.QMainWindow()
    ui = UiVentana()
    sys.exit(app.exec_())
>> >> >> > Stashed
changes
