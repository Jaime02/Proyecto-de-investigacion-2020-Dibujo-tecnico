# -*- coding: utf-8 -*-

from functools import partial
from math import sin, cos, radians
from string import ascii_uppercase, ascii_lowercase

from OpenGL.GL import glClear, GL_COLOR_BUFFER_BIT, glEnable, GL_DEPTH_TEST, glMatrixMode, GL_PROJECTION, \
    glLoadIdentity, glOrtho, glClearColor, GL_DEPTH_BUFFER_BIT, GL_MODELVIEW, glLineWidth, glBegin, glColor, glVertex, \
    glEnd, glPointSize, GL_POINT_SMOOTH, GL_POINTS, GL_BLEND, glBlendFunc, GL_SRC_ALPHA, \
    GL_QUADS, glDisable, GL_LINES, GL_LINE_LOOP, glDepthMask, GL_FALSE, GL_TRUE, GL_ONE_MINUS_SRC_ALPHA
from OpenGL.GLU import gluLookAt
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QPainter, QPen, QColor
from PyQt5.QtWidgets import QOpenGLWidget, QWidget
from sympy import Line, intersection, Point3D, Plane, Line3D


class Renderizador(QOpenGLWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.dx = 0
        self.dy = 0
        self.dz = 0
        self.theta = 405
        self.phi = 45
        self.z1 = 150
        self.z2 = -150
        self.x = sin(radians(self.theta)) * cos(radians(self.phi)) + self.dx
        self.z = sin(radians(self.theta)) * sin(radians(self.phi)) + self.dz
        self.y = cos(radians(self.theta)) + self.dy
        self.vertices_vertical = ((500, 500, 0), (-500, 500, 0), (-500, 0, 0), (500, 0, 0))
        self.vertices_vertical_debajo = ((500, 0, 0), (-500, 0, 0), (-500, -500, 0), (500, -500, 0))
        self.vertices_horizontal = ((500, 0, 0), (500, 0, 500), (-500, 0, 500), (-500, 0, 0))
        self.vertices_horizontal_detras = ((500, 0, 0), (500, 0, -500), (-500, 0, -500), (-500, 0, 0))
        self.vertices_borde_v = ((500, 500, 0), (500, -500, 0), (-500, -500, 0), (-500, 500, 0))
        self.vertices_borde_h = ((500, 0, 500), (-500, 0, 500), (-500, 0, -500), (500, 0, -500))
        self.puntos = []
        self.rectas = []

    def recalcular(self):
        self.x = sin(radians(self.theta)) * cos(radians(self.phi)) + self.dx
        self.z = sin(radians(self.theta)) * sin(radians(self.phi)) + self.dz
        self.y = cos(radians(self.theta)) + self.dy
        gluLookAt(self.x, self.y, self.z, self.dx, self.dy, self.dz, 0, 1, 0)
        ui.actualizar()
        self.update()

    def ver_alzado(self):
        self.phi = 90
        self.theta = 450
        self.recalcular()

    def ver_planta(self):
        self.phi = 90
        self.theta = 360
        self.recalcular()

    def ver_perfil(self):
        self.phi = 0
        self.theta = 450
        self.recalcular()

    def ver_reset(self):
        self.theta = 405
        self.phi = 45
        self.z1 = 150
        self.z2 = -150
        self.dx = 0
        self.dy = 0
        self.dz = 0
        self.recalcular()

    def dibujar_planos(self):
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glDepthMask(GL_FALSE)
        glBegin(GL_QUADS)
        glColor(1, 0, 0, 0.5)
        for vertex in range(4):
            glVertex(self.vertices_horizontal_detras[vertex])
        glColor(0, 1, 0, 0.5)
        for vertex in range(4):
            glVertex(self.vertices_vertical_debajo[vertex])
        glColor(0, 1, 0, 0.5)
        for vertex in range(4):
            glVertex(self.vertices_vertical[vertex])
        glColor(1, 0, 0, 0.5)
        for vertex in range(4):
            glVertex(self.vertices_horizontal[vertex])
        glEnd()
        glDepthMask(GL_TRUE)
        glDisable(GL_BLEND)
        glLineWidth(1)
        glColor(0.2, 1, 0.2, 0.5)
        glBegin(GL_LINE_LOOP)
        for vertex in range(4):
            glVertex(self.vertices_borde_v[vertex])
        glColor(1, 0.2, 0.2, 0.5)
        glEnd()
        glBegin(GL_LINE_LOOP)
        for vertex in range(4):
            glVertex(self.vertices_borde_h[vertex])
        glEnd()

    @staticmethod
    def dibujar_ejes():
        glLineWidth(3)
        glBegin(GL_LINES)
        # X ROJO
        glColor(1, 0, 0)
        glVertex(0, 0, 0)
        glVertex(10, 0, 0)
        # Y VERDE
        glColor(0, 1, 0)
        glVertex(0, 0, 0)
        glVertex(0, 10, 0)
        # Z AZUL
        glColor(0, 0, 1)
        glVertex(0, 0, 0)
        glVertex(0, 0, 10)
        glEnd()

    def dibujar_punto(self):
        glColor(0, 0, 0, 0)
        glPointSize(4)
        glEnable(GL_POINT_SMOOTH)
        glBegin(GL_POINTS)
        for i in range(len(self.puntos)):
            glVertex(self.puntos[i][1], self.puntos[i][3], self.puntos[i][2])
        glEnd()
        self.update()

    def dibujar_rectas(self):
        glColor(0, 0, 0, 0)
        glLineWidth(2)
        glBegin(GL_LINES)
        for i in range(len(self.rectas)):
            glVertex(self.rectas[i][3][0], self.rectas[i][3][2], self.rectas[i][3][1])
            glVertex(self.rectas[i][4][0], self.rectas[i][4][2], self.rectas[i][4][1])
        glEnd()
        for i in range(len(self.rectas)):
            if self.rectas[i][5]:  # H
                glColor(0, 1, 0, 0)
                glBegin(GL_POINTS)
                x = self.rectas[i][5][0]
                y = self.rectas[i][5][2]
                z = self.rectas[i][5][1]
                glVertex(x, y, z)
                glEnd()
            if self.rectas[i][6]:  # V
                glColor(1, 0, 0, 0)
                glBegin(GL_POINTS)
                x = self.rectas[i][6][0]
                y = self.rectas[i][6][2]
                z = self.rectas[i][6][1]
                glVertex(x, y, z)
                glEnd()

    def initializeGL(self):
        glEnable(GL_DEPTH_TEST)

    def paintGL(self):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(self.z1, self.z2, self.z2, self.z1, -5000, 5000)
        glMatrixMode(GL_MODELVIEW)
        glClearColor(1, 1, 1, 0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        up = 1
        if self.theta == 0 or self.theta == 360:
            self.theta = 360
            up = -1
        gluLookAt(self.x, self.y, self.z, self.dx, self.dy, self.dz, 0, up, 0)
        if self.puntos:
            self.dibujar_punto()
        if self.rectas:
            self.dibujar_rectas()
        self.dibujar_planos()
        self.dibujar_ejes()
        self.update()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_W:
            self.theta -= 5
        elif event.key() == QtCore.Qt.Key_A:
            self.phi -= 5
        elif event.key() == QtCore.Qt.Key_S:
            self.theta += 5
        elif event.key() == QtCore.Qt.Key_D:
            self.phi += 5
        elif event.key() == QtCore.Qt.Key_Q:
            self.dz += 1
        elif event.key() == QtCore.Qt.Key_E:
            self.dz -= 1
        elif event.key() == QtCore.Qt.Key_Left:
            self.dx += 1
        elif event.key() == QtCore.Qt.Key_Up:
            self.dy += 1
        elif event.key() == QtCore.Qt.Key_Right:
            self.dx -= 1
        elif event.key() == QtCore.Qt.Key_Down:
            self.dy -= 1
        elif event.key() == QtCore.Qt.Key_1:
            self.ver_alzado()
        elif event.key() == QtCore.Qt.Key_2:
            self.ver_planta()
        elif event.key() == QtCore.Qt.Key_3:
            self.ver_perfil()
        elif event.key() == QtCore.Qt.Key_R:
            self.ver_reset()
        elif event.key() == QtCore.Qt.Key_Minus:
            self.z1 += 10
            self.z2 -= 10
        elif event.key() == QtCore.Qt.Key_Plus:
            self.z1 -= 10
            self.z2 += 10
        if self.theta < 360:
            self.theta = 360
        if self.theta > 540:
            self.theta = 540
        if self.phi >= 360:
            self.phi -= 360
        if self.phi < 0:
            self.phi += 360
        if self.z1 < 10:
            self.z1 = 10
        if self.z2 > -10:
            self.z2 = -10
        self.x = sin(radians(self.theta)) * cos(radians(self.phi)) + self.dx
        self.z = sin(radians(self.theta)) * sin(radians(self.phi)) + self.dz
        self.y = cos(radians(self.theta)) + self.dy

        ui.actualizar()
        self.update()
        super().keyPressEvent(event)


class Diedrico(QWidget):
    def __init__(self, parent=None):
        super(Diedrico, self).__init__(parent)

        negro = QColor(0, 0, 0)
        rojo = QColor(255, 103, 69)
        verde = QColor(0, 255, 0)

        self.pen_lt = QPen(negro)
        self.pen_lt.setWidth(1)

        self.pen_pprima = QPen(QColor(201, 10, 0), 4)
        self.pen_pprima2 = QPen(QColor(8, 207, 41), 4)

        self.pen_rprima = QPen(rojo, 3, Qt.DotLine)
        self.pen_rprima.setDashPattern([1, 3])
        self.pen_rprima2 = QPen(verde, 3, Qt.DotLine)
        self.pen_rprima2.setDashPattern([1, 3])

        self.pen_rprimaC = QPen(rojo, 4)
        self.pen_rprima2C = QPen(verde, 4)
        self.pen_trazas = QPen(Qt.black, 4)
        self.pen_prima3 = QPen(Qt.black, 4)

        self.plano_v = Plane(Point3D(0, 0, 1), Point3D(0, 0, 0), Point3D(1, 0, 0))
        self.plano_h = Plane(Point3D(0, 1, 0), Point3D(0, 0, 0), Point3D(1, 0, 0))

    def minimumSizeHint(self):
        return QtCore.QSize(2000, 2000)

    def paintEvent(self, event):
        qp = QPainter(self)
        qp.setRenderHint(QPainter.Antialiasing)
        self.elementos_estaticos(qp)
        qp.translate(500, 500)
        qp.scale(-1, -1)
        if ui.Renderizador.rectas and ui.ver_rectas.checkState():
            self.dibujar_rectas(qp)
        if ui.Renderizador.puntos and ui.ver_puntos.checkState():
            self.puntos(qp)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Plus:
            ui.zoom_in()
        if event.key() == QtCore.Qt.Key_Minus:
            ui.zoom_out()
        if event.key() == QtCore.Qt.Key_R:
            ui.vista.setTransform(QtGui.QTransform())

    def elementos_estaticos(self, qp):
        qp.setPen(self.pen_lt)
        qp.drawRect(0, 0, 1000, 1000)  # Marco

        qp.drawLine(5, 500, 995, 500)  # LT

        qp.drawLine(5, 505, 15, 505)  # Raya 1
        qp.drawLine(985, 505, 995, 505)  # Raya 2
        qp.drawLine(500, 5, 500, 995)  # Raya PP

    def puntos(self, qp):
        for i in range(len(ui.Renderizador.puntos)):
            self.punto_prima(qp, i)
            self.punto_prima2(qp, i)
            if ui.tercera_proyeccion.checkState():
                self.punto_prima3(qp, i)

    def punto_prima(self, qp, i):
        qp.setPen(self.pen_pprima)
        qp.drawPoint(ui.Renderizador.puntos[i][1], -ui.Renderizador.puntos[i][2])

    def punto_prima2(self, qp, i):
        qp.setPen(self.pen_pprima2)
        qp.drawPoint(ui.Renderizador.puntos[i][1], ui.Renderizador.puntos[i][3])

    def punto_prima3(self, qp, i):
        qp.setPen(self.pen_prima3)
        qp.drawPoint(-ui.Renderizador.puntos[i][2], ui.Renderizador.puntos[i][3])

    def dibujar_rectas(self, qp):
        for i in range(len(ui.Renderizador.rectas)):
            recta = ui.Renderizador.rectas[i]
            inicio = recta[3]
            fin = recta[4]

            qp.setPen(self.pen_rprima)
            self.recta_prima(qp, inicio, fin)

            qp.setPen(self.pen_rprima2)
            self.recta_prima2(qp, inicio, fin)

            if ui.tercera_proyeccion.checkState():  # Tercera proyección
                qp.setPen(self.pen_prima3)
                self.recta_prima3(qp, inicio, fin)

            # Ninguna traza
            if not recta[5] and not recta[6] and recta[3][1] > 0 and recta[3][2] > 0 and recta[4][1] > 0 \
                    and recta[4][2] > 0:
                inicio = recta[3]
                fin = recta[4]
                self.dibujar_continuo(qp, inicio, fin)
            # Una traza en PH
            if recta[5] and not recta[6]:
                if recta[5][2] > 0:
                    inicio = recta[5]
                    fin = recta[3]
                    self.dibujar_continuo(qp, inicio, fin)
            # Una traza en PV
            if not recta[5] and recta[6]:
                if recta[6][1] > 0:
                    inicio = recta[6]
                    fin = recta[3]
                    self.dibujar_continuo(qp, inicio, fin)

            # Dos trazas
            if recta[5] and recta[6]:
                # Continua 010
                if recta[5][2] > 0 and recta[6][1] > 0:
                    inicio = recta[5]
                    fin = recta[6]
                    self.dibujar_continuo(qp, inicio, fin)

                elif recta[5][2] < 0 < recta[6][1]:
                    inicio = recta[6]
                    if recta[4][1] > 0:
                        fin = recta[4]
                    else:
                        fin = recta[3]
                    self.dibujar_continuo(qp, inicio, fin)

                elif recta[5][2] > 0 > recta[6][1]:
                    inicio = recta[5]
                    if recta[4][1] > 0:
                        fin = recta[4]
                    else:
                        fin = recta[3]
                    self.dibujar_continuo(qp, inicio, fin)

            # Trazas en LT
            if recta[5] == recta[6] and recta[5] != ():
                if recta[3][1] > 0 and recta[3][2] > 0:
                    inicio = recta[3]
                    fin = recta[5]
                    self.dibujar_continuo(qp, inicio, fin)
                elif recta[4][1] > 0 and recta[4][2] > 0:
                    inicio = recta[4]
                    fin = recta[5]
                    self.dibujar_continuo(qp, inicio, fin)
            # Trazas en PH
            if recta[3][1] == 0 and recta[4][1] == 0:
                if not recta[6]:
                    inicio = recta[4]
                    fin = recta[3]
                    self.dibujar_continuo(qp, inicio, fin)
                else:
                    inicio = recta[3]
                    fin = recta[6]
                    self.dibujar_continuo(qp, inicio, fin)
            # Trazas en PV
            if recta[3][2] == 0 and recta[4][2] == 0:
                if not recta[5]:
                    inicio = recta[3]
                    fin = recta[4]
                    self.dibujar_continuo(qp, inicio, fin)
                else:
                    inicio = recta[3]
                    fin = recta[5]
                    self.dibujar_continuo(qp, inicio, fin)

            if len(ui.Renderizador.rectas[i]) >= 6:  # Trazas
                self.dibujar_trazas(qp, recta)

    def dibujar_continuo(self, qp, inicio, fin):
        qp.setPen(self.pen_rprimaC)
        self.recta_prima(qp, inicio, fin)
        qp.setPen(self.pen_rprima2C)
        self.recta_prima2(qp, inicio, fin)

    @staticmethod
    def recta_prima(qp, inicio, fin):
        x0 = inicio[0]
        x = fin[0]
        y0 = -inicio[1]
        y = -fin[1]
        qp.drawLine(x0, y0, x, y)

    @staticmethod
    def recta_prima2(qp, inicio, fin):
        x0 = inicio[0]
        x = fin[0]
        y0 = inicio[2]
        y = fin[2]
        qp.drawLine(x0, y0, x, y)

    @staticmethod
    def recta_prima3(qp, inicio, fin):
        x0 = -inicio[1]
        x = -fin[1]
        y0 = inicio[2]
        y = fin[2]
        qp.drawLine(x0, y0, x, y)

    def dibujar_trazas(self, qp, recta):
        qp.setPen(self.pen_trazas)
        if recta[5]:
            qp.drawPoint(recta[5][0], recta[5][2])  # V "
            qp.drawPoint(recta[5][0], 0)  # V '
        if recta[6]:
            qp.drawPoint(recta[6][0], -recta[6][1])  # H '
            qp.drawPoint(recta[6][0], 0)  # H "


class UiVentana(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(1500, 1015)

        widget_central = QtWidgets.QWidget(self)
        self.Renderizador = Renderizador(widget_central)
        self.Renderizador.setGeometry(QRect(0, 0, 1000, 1000))
        self.Renderizador.setFocusPolicy(QtCore.Qt.ClickFocus)
        fuente = QtGui.QFont()
        fuente.setPointSize(10)

        label = QtWidgets.QLabel(widget_central)
        label.setGeometry(QRect(1010, 10, 91, 16))
        label.setFont(fuente)
        label_2 = QtWidgets.QLabel(widget_central)
        label_2.setGeometry(QRect(1010, 30, 71, 16))
        label_2.setFont(fuente)
        self.label_3 = QtWidgets.QLabel(widget_central)
        self.label_3.setGeometry(QRect(1110, 30, 141, 20))
        self.label_3.setFont(fuente)
        label_4 = QtWidgets.QLabel(widget_central)
        label_4.setGeometry(QRect(1008, 50, 110, 16))
        label_4.setFont(fuente)
        self.label_5 = QtWidgets.QLabel(widget_central)
        self.label_5.setGeometry(QRect(1110, 49, 200, 20))
        self.label_5.setFont(fuente)
        self.label_6 = QtWidgets.QLabel(widget_central)
        self.label_6.setGeometry(QRect(1010, 70, 111, 16))
        self.label_6.setFont(fuente)
        self.label_7 = QtWidgets.QLabel(widget_central)
        self.label_7.setGeometry(QRect(1130, 70, 130, 16))
        self.label_7.setFont(fuente)
        label_8 = QtWidgets.QLabel(widget_central)
        label_8.setGeometry(QRect(1010, 90, 91, 16))
        label_8.setFont(fuente)
        label_9 = QtWidgets.QLabel(widget_central)
        label_9.setGeometry(QRect(1010, 140, 91, 16))
        label_9.setFont(fuente)
        label_10 = QtWidgets.QLabel(widget_central)
        label_10.setGeometry(QRect(1170, 140, 91, 16))
        label_10.setFont(fuente)
        label_11 = QtWidgets.QLabel(widget_central)
        label_11.setGeometry(QRect(1330, 140, 91, 16))
        label_11.setFont(fuente)
        label_12 = QtWidgets.QLabel(widget_central)
        label_12.setGeometry(QRect(1010, 160, 91, 16))
        label_13 = QtWidgets.QLabel(widget_central)
        label_13.setGeometry(QRect(1010, 180, 91, 16))
        label_14 = QtWidgets.QLabel(widget_central)
        label_14.setGeometry(QRect(1010, 200, 91, 16))
        label_15 = QtWidgets.QLabel(widget_central)
        label_15.setGeometry(QRect(1010, 220, 91, 16))
        label_16 = QtWidgets.QLabel(widget_central)
        label_16.setGeometry(QRect(1170, 160, 51, 16))
        label_17 = QtWidgets.QLabel(widget_central)
        label_17.setGeometry(QRect(1170, 180, 51, 16))
        label_18 = QtWidgets.QLabel(widget_central)
        label_18.setGeometry(QRect(1170, 200, 91, 21))
        label_19 = QtWidgets.QLabel(widget_central)
        label_19.setGeometry(QRect(1330, 160, 51, 16))
        label_20 = QtWidgets.QLabel(widget_central)
        label_20.setGeometry(QRect(1330, 180, 51, 16))
        label_21 = QtWidgets.QLabel(widget_central)
        label_21.setGeometry(QRect(1330, 220, 91, 21))
        label_22 = QtWidgets.QLabel(widget_central)
        label_22.setGeometry(QRect(1330, 200, 51, 16))
        label_23 = QtWidgets.QLabel(widget_central)
        label_23.setGeometry(QRect(1020, 982, 21, 16))

        boton_r = QtWidgets.QPushButton(widget_central)
        boton_r.setGeometry(QRect(1010, 110, 81, 23))
        boton_r.clicked.connect(self.Renderizador.ver_reset)
        boton_alzado = QtWidgets.QPushButton(widget_central)
        boton_alzado.setGeometry(QRect(1100, 110, 81, 23))
        boton_alzado.clicked.connect(self.Renderizador.ver_alzado)
        boton_planta = QtWidgets.QPushButton(widget_central)
        boton_planta.setGeometry(QRect(1190, 110, 81, 23))
        boton_planta.clicked.connect(self.Renderizador.ver_planta)
        boton_perfil = QtWidgets.QPushButton(widget_central)
        boton_perfil.setGeometry(QRect(1280, 110, 81, 23))
        boton_perfil.clicked.connect(self.Renderizador.ver_perfil)
        boton_recta = QtWidgets.QPushButton(widget_central)
        boton_recta.setGeometry(QRect(1170, 249, 151, 21))
        boton_recta.clicked.connect(self.crear_recta)
        boton_plano = QtWidgets.QPushButton(widget_central)
        boton_plano.setGeometry(QRect(1330, 270, 151, 21))

        widget = QtWidgets.QWidget(widget_central)
        widget.setFocusPolicy(QtCore.Qt.ClickFocus)
        wrapper = QtWidgets.QHBoxLayout(widget)
        widget.setGeometry(QRect(1000, 500, 500, 490))

        scene = QtWidgets.QGraphicsScene(self)
        self.vista = QtWidgets.QGraphicsView(scene)

        wrapper.addWidget(self.vista)

        self.diedrico = Diedrico()
        self.diedrico.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.diedrico.setFixedSize(1000, 1000)
        scene.addWidget(self.diedrico)
        QtCore.QTimer.singleShot(0, self.mover)

        boton_punto = QtWidgets.QPushButton(widget_central)
        boton_punto.setGeometry(QRect(1010, 270, 151, 21))
        boton_punto.clicked.connect(self.crear_punto)
        self.valor_do = QtWidgets.QSpinBox(widget_central)
        self.valor_do.setGeometry(QRect(1110, 160, 51, 20))
        self.valor_do.setRange(-500, 500)
        self.valor_a = QtWidgets.QSpinBox(widget_central)
        self.valor_a.setGeometry(QRect(1110, 180, 51, 20))
        self.valor_a.setRange(-500, 500)
        self.valor_c = QtWidgets.QSpinBox(widget_central)
        self.valor_c.setGeometry(QRect(1110, 200, 51, 20))
        self.valor_c.setRange(-500, 500)

        self.punto_nombre = QtWidgets.QPlainTextEdit(widget_central)
        self.punto_nombre.setGeometry(QRect(1010, 240, 151, 25))
        self.recta_nombre = QtWidgets.QPlainTextEdit(widget_central)
        self.recta_nombre.setGeometry(QRect(1170, 220, 151, 25))
        self.plano_nombre = QtWidgets.QPlainTextEdit(widget_central)
        self.plano_nombre.setGeometry(QRect(1330, 240, 151, 25))
        self.punto_1 = QtWidgets.QComboBox(widget_central)
        self.punto_1.setGeometry(QRect(1230, 160, 91, 22))
        self.punto_2 = QtWidgets.QComboBox(widget_central)
        self.punto_2.setGeometry(QRect(1230, 180, 91, 21))
        self.pplano1 = QtWidgets.QComboBox(widget_central)
        self.pplano1.setGeometry(QRect(1380, 160, 91, 22))
        self.pplano2 = QtWidgets.QComboBox(widget_central)
        self.pplano2.setGeometry(QRect(1380, 180, 91, 22))
        self.pplano3 = QtWidgets.QComboBox(widget_central)
        self.pplano3.setGeometry(QRect(1380, 200, 91, 22))

        self.tercera_proyeccion = QtWidgets.QCheckBox(widget_central)
        self.tercera_proyeccion.setGeometry(QRect(1050, 982, 111, 17))
        self.tercera_proyeccion.clicked.connect(self.diedrico.update)
        self.ver_puntos = QtWidgets.QCheckBox(widget_central)
        self.ver_puntos.setGeometry(QRect(1170, 982, 61, 17))
        self.ver_puntos.setChecked(True)
        self.ver_puntos.clicked.connect(self.diedrico.update)
        self.ver_rectas = QtWidgets.QCheckBox(widget_central)
        self.ver_rectas.setGeometry(QRect(1232, 982, 61, 17))
        self.ver_rectas.setChecked(True)
        self.ver_rectas.clicked.connect(self.diedrico.update)
        self.ver_planos = QtWidgets.QCheckBox(widget_central)
        self.ver_planos.setGeometry(QRect(1292, 982, 70, 17))
        self.ver_planos.setChecked(True)
        self.ver_planos.clicked.connect(self.diedrico.update)

        label.setText("Información:")
        label_2.setText("Posición:")
        self.label_3.setText("Primer cuadrante")
        label_4.setText("Coordenadas:")
        self.label_5.setText("X: Y: Z:")
        self.label_6.setText("Ángulo vertical:")
        self.label_7.setText("Ángulo horizontal:")
        label_8.setText("Vista:")
        boton_r.setText("Reset (R)")
        boton_alzado.setText("Alzado (1) ''")
        boton_planta.setText("Planta (2) '")
        boton_perfil.setText("Perfil (3) '''")
        label_9.setText("Crear puntos:")
        label_10.setText("Crear rectas:")
        label_11.setText("Crear planos:")
        label_12.setText("Distancia al origen:")
        label_13.setText("Alejamiento:")
        label_14.setText("Cota:")
        label_15.setText("Nombre:")
        boton_punto.setText("Crear")
        boton_recta.setText("Crear")
        boton_plano.setText("Crear")
        label_16.setText("Punto 1:")
        label_17.setText("Punto 2:")
        label_18.setText("Nombre:")
        label_19.setText("Punto 1:")
        label_20.setText("Punto 2:")
        label_21.setText("Nombre:")
        label_22.setText("Punto 3:")
        self.tercera_proyeccion.setText("Tercera proyección")
        self.ver_puntos.setText("Puntos")
        self.ver_rectas.setText("Rectas")
        self.ver_planos.setText("Planos")
        label_23.setText("Ver:")

        elementos_widget = QtWidgets.QWidget(widget_central)
        scroll_widget = QtWidgets.QWidget()
        scroll = QtWidgets.QScrollArea(widget_central)
        scroll.setGeometry(QRect(1010, 291, 151, 211))
        scroll.setWidgetResizable(True)
        scroll.setWidget(scroll_widget)
        vbox = QtWidgets.QVBoxLayout(scroll_widget)
        vbox.addWidget(elementos_widget)
        vbox.addStretch()
        self.elementos = QtWidgets.QGridLayout(elementos_widget)

        elementos_widget2 = QtWidgets.QWidget(widget_central)
        scroll_widget2 = QtWidgets.QWidget()
        scroll2 = QtWidgets.QScrollArea(widget_central)
        scroll2.setGeometry(QRect(1170, 270, 151, 231))
        scroll2.setWidgetResizable(True)
        scroll2.setWidget(scroll_widget2)
        vbox2 = QtWidgets.QVBoxLayout(scroll_widget2)
        vbox2.addWidget(elementos_widget2)
        vbox2.addStretch()
        self.elementos2 = QtWidgets.QGridLayout(elementos_widget2)

        self.puntero_puntos = 15
        self.puntero_rectas = 17
        self.opciones = []
        self.v = (Point3D(500, 500, 500), Point3D(-500, 500, 500), Point3D(-500, -500, 500), Point3D(500, -500, 500),
                  Point3D(500, 500, -500), Point3D(-500, 500, -500), Point3D(500, -500, -500))

        self.p = (Plane(self.v[0], self.v[1], self.v[2]), Plane(self.v[0], self.v[1], self.v[5]), Plane(self.v[0],
                                                                                                        self.v[4],
                                                                                                        self.v[6]),
                  Plane(self.v[5], self.v[4], self.v[6]), Plane(self.v[2], self.v[3], self.v[6]),
                  Plane(self.v[2], self.v[1], self.v[5]))

        self.actualizar()
        self.setWindowTitle("Dibujo técnico")
        self.setCentralWidget(widget_central)

    def zoom_in(self):
        scale_tr = QtGui.QTransform()
        scale_tr.scale(1.2, 1.2)
        tr = self.vista.transform() * scale_tr
        self.vista.setTransform(tr)

    def zoom_out(self):
        scale_tr = QtGui.QTransform()
        scale_tr.scale(1.2, 1.2)
        scale_inverted, invertible = scale_tr.inverted()
        if invertible:
            tr = self.vista.transform() * scale_inverted
            self.vista.setTransform(tr)

    def mover(self):
        self.vista.verticalScrollBar().setValue(int(self.vista.verticalScrollBar().maximum() / 2))
        self.vista.horizontalScrollBar().setValue(int(self.vista.verticalScrollBar().maximum() / 2))

    def crear_punto(self):
        do = self.valor_do.value()
        cota = self.valor_c.value()
        alejamiento = self.valor_a.value()
        nombre = self.punto_nombre.toPlainText()

        if self.puntero_puntos == len(ascii_uppercase):  # Evita que el puntero supere la longitud de la lista
            self.puntero_puntos = 0

        if nombre == "":  # Genera nombres genéricos si no se provee uno
            nombre = ascii_uppercase[self.puntero_puntos]
            self.puntero_puntos += 1

        for i in range(len(self.Renderizador.puntos)):  # Evita nombres duplicados
            if self.Renderizador.puntos[i][0] == nombre:
                nombre = ascii_uppercase[self.puntero_puntos]
                self.puntero_puntos += 1

        name = QtWidgets.QLabel("{}({}, {}, {})".format(nombre, do, alejamiento, cota))

        punto = (nombre, do, alejamiento, cota)

        borrar = QtWidgets.QPushButton("X")
        borrar.setMaximumWidth(20)

        wrapper = partial(self.borrar_punto, (name, borrar), punto)
        borrar.clicked.connect(wrapper)

        row = self.elementos.rowCount()

        self.elementos.addWidget(name, row, 0)
        self.elementos.addWidget(borrar, row, 1)
        self.Renderizador.puntos.append(punto)

        self.opciones.append(nombre)
        self.actualizar_combo()
        self.Renderizador.update()
        self.diedrico.update()

    def actualizar_combo(self):
        self.punto_1.clear()
        self.punto_2.clear()
        for i in range(len(self.opciones)):
            self.punto_1.addItem(self.opciones[i])
            self.punto_2.addItem(self.opciones[i])

    def borrar_punto(self, widgets, punto):
        if self.Renderizador.puntos:
            name, borrar = widgets
            name.deleteLater()
            borrar.deleteLater()
            self.opciones.remove(punto[0])
            self.actualizar_combo()
            self.Renderizador.puntos.remove(punto)
            self.diedrico.update()

    def actualizar(self):
        x = round(500 * (sin(radians(self.Renderizador.theta)) * cos(radians(self.Renderizador.phi)))
                  + self.Renderizador.dx, 2)
        z = round(500 * (sin(radians(self.Renderizador.theta)) * sin(radians(self.Renderizador.phi)))
                  + self.Renderizador.dz, 2)
        y = round(500 * (cos(radians(self.Renderizador.theta))) + self.Renderizador.dy, 2)
        theta = self.Renderizador.theta - 360
        phi = self.Renderizador.phi
        if x == -0:
            x = 0
        if y == -0:
            y = 0
        if z == -0:
            z = 0
        self.label_5.setText("X: {} Y: {} Z: {}".format(x, z, y))
        self.label_6.setText("Ángulo vertical: " + str(theta))
        self.label_7.setText("Ángulo horizontal: " + str(phi))
        if z == 0 and y == 0:
            self.label_3.setText("Línea de tierra")
        elif z == 0:
            if y > 0:
                self.label_3.setText("Plano vertical positivo")
            else:
                self.label_3.setText("Plano vertical negativo")
        elif y == 0:
            if z > 0:
                self.label_3.setText("Plano horizontal positivo")
            else:
                self.label_3.setText("Plano horizontal negativo")
        elif z > 0:
            if y > 0:
                self.label_3.setText("Primer cuadrante")
            else:
                self.label_3.setText("Cuarto cuadrante")
        else:
            if y > 0:
                self.label_3.setText("Segundo cuadrante")
            else:
                self.label_3.setText("Tercer cuadrante")

    def crear_recta(self):
        punto1 = self.punto_1.currentText()
        punto2 = self.punto_2.currentText()
        nombre = self.recta_nombre.toPlainText()
        for i in range(len(self.Renderizador.puntos)):
            if self.Renderizador.puntos[i][0] == punto1:
                punto1 = self.Renderizador.puntos[i]
            if self.Renderizador.puntos[i][0] == punto2:
                punto2 = self.Renderizador.puntos[i]
        if not punto1 and not punto2:
            QtWidgets.QMessageBox.about(self, "Error al crear la recta",
                                        "Debes crear al menos dos puntos y seleccionarlos para crear la recta")
        elif punto1[-3:] == punto2[-3:]:
            QtWidgets.QMessageBox.about(self, "Error al crear la recta",
                                        "La recta debe ser creada a partir de dos puntos no coincidentes")
        else:
            if self.puntero_rectas == len(ascii_lowercase):  # Evita que el puntero supere la longitud de la lista
                self.puntero_rectas = 0

            if nombre == "":  # Genera nombres genéricos si no se provee uno
                nombre = ascii_lowercase[self.puntero_rectas]
                self.puntero_rectas += 1

            for i in range(len(self.Renderizador.rectas)):  # Evita nombres duplicados
                if self.Renderizador.rectas[i][0] == nombre:
                    nombre = ascii_lowercase[self.puntero_rectas]
                    self.puntero_puntos += 1

            name = QtWidgets.QLabel("{}({}, {})".format(nombre, punto1[0], punto2[0]))
            extremos = self.recta_limites(punto1, punto2)
            a, b = [], []
            for i in range(3):
                a.append(extremos[0][i])
            for i in range(3):
                b.append(extremos[1][i])
            recta = [nombre, punto1, punto2, tuple(a), tuple(b)]

            borrar = QtWidgets.QPushButton("X")
            borrar.setMaximumWidth(20)

            wrapper = partial(self.borrar_recta, (name, borrar), recta)
            borrar.clicked.connect(wrapper)
            row = self.elementos2.rowCount()

            self.elementos2.addWidget(name, row, 0)
            self.elementos2.addWidget(borrar, row, 1)
            self.Renderizador.rectas.append(recta)
            self.recta_trazas(recta)
            self.Renderizador.update()
            self.diedrico.update()

    def recta_trazas(self, recta):
        p1 = Point3D(recta[1][-3:])
        p2 = Point3D(recta[2][-3:])
        recta = Line(p1, p2)
        v = intersection(recta, self.diedrico.plano_v)
        h = intersection(recta, self.diedrico.plano_h)

        if v:
            if isinstance(v[0], Line3D):
                self.Renderizador.rectas[len(self.Renderizador.rectas) - 1].append(())
            else:
                self.Renderizador.rectas[len(self.Renderizador.rectas) - 1].append(tuple(v[0]))
        else:
            self.Renderizador.rectas[len(self.Renderizador.rectas) - 1].append(())

        if h:
            if isinstance(h[0], Line3D):
                self.Renderizador.rectas[len(self.Renderizador.rectas) - 1].append(())
            else:
                self.Renderizador.rectas[len(self.Renderizador.rectas) - 1].append(tuple(h[0]))
        else:
            self.Renderizador.rectas[len(self.Renderizador.rectas) - 1].append(())

    def recta_limites(self, punto1, punto2):
        r = Line3D(Point3D(punto1[-3:]), Point3D(punto2[-3:]))
        inter = []
        for i in range(6):
            a = intersection(r, self.p[i])
            if a and not isinstance(a[0], Line3D):
                inter.append(a[0])
            else:
                inter.append((210, 210, 210))
        buenos = []
        if -500 < inter[1][0] < 500 and -500 < inter[1][2] < 500:
            buenos.append(inter[1])
        if -500 < inter[4][0] < 500 and -500 < inter[4][2] < 500:
            buenos.append(inter[4])
        if -500 <= inter[0][0] <= 500 and -500 <= inter[0][1] <= 500:
            buenos.append(inter[0])
        if -500 < inter[2][1] < 500 and -500 < inter[2][2] < 500:
            buenos.append(inter[2])
        if -500 <= inter[3][0] <= 500 and -500 <= inter[3][1] <= 500:
            buenos.append(inter[3])
        if -500 < inter[5][1] < 500 and -500 < inter[5][2] < 500:
            buenos.append(inter[5])
        if 500 == abs(inter[2][1]):
            buenos.append(inter[2])
        if 500 == abs(inter[5][1]):
            buenos.append(inter[5])
        return buenos

    def borrar_recta(self, widgets, recta):
        name, borrar = widgets
        name.deleteLater()
        borrar.deleteLater()
        self.Renderizador.rectas.remove(recta)
        self.Renderizador.update()
        self.diedrico.update()


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication([])
    ui = UiVentana()
    ui.show()
    sys.exit(app.exec_())
