# -*- coding: utf-8 -*-

from math import sin, cos, radians
from string import ascii_uppercase, ascii_lowercase

from OpenGL.GL import glClear, GL_COLOR_BUFFER_BIT, glEnable, GL_DEPTH_TEST, glMatrixMode, GL_PROJECTION, GL_TRUE, \
    glLoadIdentity, glOrtho, glClearColor, GL_DEPTH_BUFFER_BIT, GL_MODELVIEW, glLineWidth, glBegin, glColor, glVertex, \
    glEnd, glPointSize, GL_POINT_SMOOTH, GL_POINTS, GL_BLEND, glBlendFunc, GL_SRC_ALPHA, GL_QUADS, glDisable, GL_LINES, \
    GL_LINE_LOOP, glDepthMask, GL_FALSE, GL_ONE_MINUS_SRC_ALPHA
from OpenGL.GLU import gluLookAt
from PyQt5.QtCore import Qt, QRect, pyqtSlot, QSize, QTimer
from PyQt5.QtGui import QPainter, QPen, QColor, QCursor, QTransform, QFont
from PyQt5.QtWidgets import QOpenGLWidget, QWidget, QCheckBox, QPushButton, QHBoxLayout, QMainWindow, QLabel, QMenu, \
    QApplication, QVBoxLayout, QSpinBox, QPlainTextEdit, QComboBox, QMessageBox, QGraphicsScene, QGraphicsView, \
    QListWidgetItem, QListWidget, QAction
from sympy import Line, intersection, Point3D, Plane, Line3D, Segment3D


class Punto(QWidget):
    def __init__(self, parent, internal_id, name, do, alejamiento, cota):
        QWidget.__init__(self)

        self.render = True

        self.customContextMenuRequested.connect(self.context_menu)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.menu = QMenu()
        self.borrar = QAction("Borrar")
        self.ver = QAction("Ver")
        self.ver.setCheckable(True)
        self.ver.setChecked(True)
        self.menu.addAction(self.borrar)
        self.borrar.triggered.connect(self.delete)
        self.menu.addAction(self.ver)
        self.ver.toggled.connect(self.toggle)

        self.parent = parent
        self.id = internal_id
        self.x = do
        self.y = cota
        self.z = alejamiento
        self.name = name
        self.coords = (self.x, self.z, self.y)

        hbox = QHBoxLayout()
        hbox.addWidget(QLabel(f"{name}({self.x}, {self.z}, {self.y})"))

        self.setLayout(hbox)

    def context_menu(self):
        self.menu.exec_(QCursor.pos())

    @pyqtSlot()
    def toggle(self):
        self.render = self.ver.isChecked()
        main_app.diedrico.update()

    @property
    def itemid(self):
        return self.id

    @pyqtSlot()
    def delete(self):
        self.parent.borrar_punto(self.id)


class Recta(QWidget):
    def __init__(self, parent, internal_id, name, p1, p2):
        QWidget.__init__(self)

        self.id = internal_id
        self.parent = parent
        self.recta = Line(Point3D(p1.coords), Point3D(p2.coords))
        self.p1 = (p1.coords[0], p1.coords[2], p1.coords[1])
        self.p2 = (p2.coords[0], p2.coords[2], p2.coords[1])
        hbox = QHBoxLayout()
        hbox.addWidget(QLabel(f"{name}({p1.name}, {p2.name})"))
        self.setLayout(hbox)
        self.name = name
        self.contenida_pv = False
        self.contenida_ph = False

        self.customContextMenuRequested.connect(self.context_menu)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.menu = QMenu()
        self.borrar = QAction("Borrar")
        self.render = QAction("Ver")
        self.render.setCheckable(True)
        self.render.setChecked(True)
        self.menu.addAction(self.borrar)
        self.borrar.triggered.connect(self.delete)
        self.menu.addAction(self.render)
        self.render.toggled.connect(main_app.diedrico.update)

        self.ver_traza_h = QAction("Traza en PH")
        self.ver_traza_v = QAction("Traza en PV")
        self.ver_traza_h.setCheckable(True)
        self.ver_traza_v.setCheckable(True)
        self.ver_traza_h.setChecked(True)
        self.ver_traza_v.setChecked(True)
        self.menu.addAction(self.ver_traza_h)
        self.menu.addAction(self.ver_traza_v)
        self.ver_traza_h.triggered.connect(main_app.diedrico.update)
        self.ver_traza_v.triggered.connect(main_app.diedrico.update)

        self.infinita = QAction("Infinita")
        self.infinita.setCheckable(True)
        self.infinita.setChecked(True)
        self.infinita.toggled.connect(main_app.diedrico.update)
        self.menu.addAction(self.infinita)

        self.v = (Point3D(500, 500, 500), Point3D(-500, 500, 500), Point3D(-500, -500, 500),
                  Point3D(500, -500, 500), Point3D(500, 500, -500), Point3D(-500, 500, -500),
                  Point3D(-500, -500, -500), Point3D(500, -500, -500))

        self.p = (Plane(self.v[0], self.v[1], self.v[2]), Plane(self.v[0], self.v[1], self.v[5]),
                  Plane(self.v[0], self.v[4], self.v[7]), Plane(self.v[4], self.v[5], self.v[7]),
                  Plane(self.v[2], self.v[3], self.v[7]), Plane(self.v[1], self.v[2], self.v[5]))

        self.plano_v = Plane(Point3D(0, 0, 1), Point3D(0, 0, 0), Point3D(1, 0, 0))
        self.plano_h = Plane(Point3D(0, 1, 0), Point3D(0, 0, 0), Point3D(1, 0, 0))

        self.extremos = self.extremos()
        self.extremos_I = [i for i in self.extremos if i[1] >= 0 and i[2] >= 0]

        self.traza_v = self.calcular_traza_v()
        if self.traza_v:
            self.traza_v = (self.traza_v[0], self.traza_v[2], self.traza_v[1])
            if self.traza_v[0] > 500 or self.traza_v[1] > 500:
                self.ver_traza_v.setCheckable(False)
                self.ver_traza_v.setDisabled(True)
        else:
            self.ver_traza_v.setCheckable(False)
            self.ver_traza_v.setDisabled(True)

        self.traza_h = self.calcular_traza_h()
        if self.traza_h:
            self.traza_h = (self.traza_h[0], self.traza_h[2], self.traza_h[1])
            if self.traza_h[0] > 500 or self.traza_h[2] > 500:
                self.ver_traza_h.setCheckable(False)
                self.ver_traza_h.setDisabled(True)
        else:
            self.ver_traza_h.setCheckable(False)
            self.ver_traza_h.setDisabled(True)

    def extremos(self):
        intersecciones = []
        for i in range(6):
            interseccion = intersection(self.recta, self.p[i])
            if interseccion:
                intersecciones.append(interseccion[0])
            else:
                intersecciones.append((501, 501, 501))  # Valores inventados para que no sirva la interseccion
        buenos = []
        if -500 < intersecciones[1][0] < 500 and -500 < intersecciones[1][2] < 500:
            buenos.append(intersecciones[1])
        if -500 < intersecciones[4][0] < 500 and -500 < intersecciones[4][2] < 500:
            buenos.append(intersecciones[4])
        if -500 <= intersecciones[0][0] <= 500 and -500 <= intersecciones[0][1] <= 500:
            buenos.append(intersecciones[0])
        if -500 < intersecciones[2][1] < 500 and -500 < intersecciones[2][2] < 500:
            buenos.append(intersecciones[2])
        if -500 <= intersecciones[3][0] <= 500 and -500 <= intersecciones[3][1] <= 500:
            buenos.append(intersecciones[3])
        if -500 < intersecciones[5][1] < 500 and -500 < intersecciones[5][2] < 500:
            buenos.append(intersecciones[5])
        if 500 == abs(intersecciones[2][1]):
            buenos.append(intersecciones[2])
        if 500 == abs(intersecciones[5][1]):
            buenos.append(intersecciones[5])
        buenos = [tuple([p.x, p.z, p.y]) for p in buenos]
        return buenos

    def calcular_traza_h(self):
        traza_h = intersection(self.recta, self.plano_h)
        if traza_h:
            if not isinstance(traza_h[0], Line3D) and traza_h[0]:
                traza_h = tuple(traza_h[0])
                return traza_h
            else:
                self.contenida_ph = True
        return False

    def calcular_traza_v(self):
        traza_v = intersection(self.recta, self.plano_v)
        if traza_v:
            if not isinstance(traza_v[0], Line3D) and traza_v[0]:
                traza_v = tuple(traza_v[0])
                return traza_v
            else:
                self.contenida_pv = True
        return False

    def context_menu(self):
        self.menu.exec_(QCursor.pos())

    @property
    def itemid(self):
        return self.id

    @pyqtSlot()
    def delete(self):
        self.parent.borrar_recta(self.id)


class Renderizador(QOpenGLWidget):
    def __init__(self, parent):
        QOpenGLWidget.__init__(self, parent)
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
        self.planos = []

    def recalcular(self):
        self.x = sin(radians(self.theta)) * cos(radians(self.phi)) + self.dx
        self.z = sin(radians(self.theta)) * sin(radians(self.phi)) + self.dz
        self.y = cos(radians(self.theta)) + self.dy
        gluLookAt(self.x, self.y, self.z, self.dx, self.dy, self.dz, 0, 1, 0)
        main_app.actualizar()
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

    def planos_proyectantes(self):
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glDepthMask(GL_FALSE)
        glBegin(GL_QUADS)
        glColor(1, 0.1, 0.1, 0.5)
        for vertex in range(4):
            glVertex(self.vertices_horizontal_detras[vertex])
        glColor(0.1, 1, 0.1, 0.5)
        for vertex in range(4):
            glVertex(self.vertices_vertical_debajo[vertex])
        glColor(0.1, 1, 0.1, 0.5)
        for vertex in range(4):
            glVertex(self.vertices_vertical[vertex])
        glColor(1, 0.1, 0.1, 0.5)
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

    @staticmethod
    def dibujar_puntos():
        glColor(0, 0, 0, 0)
        glPointSize(4)
        glEnable(GL_POINT_SMOOTH)
        glBegin(GL_POINTS)
        for i in range(main_app.lista_puntos.count()):
            punto = main_app.lista_puntos.itemWidget(main_app.lista_puntos.item(i))
            if punto.render:
                glVertex(punto.x, punto.y, punto.z)
        glEnd()

    @staticmethod
    def dibujar_rectas():
        for i in range(main_app.lista_rectas.count()):
            recta = main_app.lista_rectas.itemWidget(main_app.lista_rectas.item(i))
            if recta.render.isChecked():
                glColor(0, 0, 0, 0)
                glLineWidth(2)
                glBegin(GL_LINES)
                if recta.infinita.isChecked():
                    glVertex(recta.extremos[0])
                    glVertex(recta.extremos[1])
                else:
                    glVertex(recta.p1)
                    glVertex(recta.p2)
                glEnd()
                if recta.traza_h and recta.ver_traza_h.isChecked():
                    if recta.traza_h[0] < 500 and recta.traza_h[2] < 500:
                        glColor(1, 0, 0, 0)
                        glBegin(GL_POINTS)
                        glVertex(recta.traza_h)
                        glEnd()
                if recta.traza_v and recta.ver_traza_v.isChecked():
                    if recta.traza_v[0] < 500 and recta.traza_v[1] < 500:
                        glColor(0, 1, 0, 0)
                        glBegin(GL_POINTS)
                        glVertex(recta.traza_v)
                        glEnd()

    def dibujar_planos(self):
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glDepthMask(GL_FALSE)
        glBegin(GL_QUADS)
        glColor(0.6, 0.6, 0.15, 0.5)
        for i in range(len(self.planos)):
            glVertex(self.planos[i][1][0], self.planos[i][1][2], self.planos[i][1][1])
            glVertex(self.planos[i][2][0], self.planos[i][2][2], self.planos[i][2][1])
            glVertex(self.planos[i][3][0], self.planos[i][3][2], self.planos[i][3][1])
            glVertex(self.planos[i][4][0], self.planos[i][4][2], self.planos[i][4][1])
        glEnd()
        glDepthMask(GL_TRUE)
        glDisable(GL_BLEND)
        # TODO traza del plano

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
        self.dibujar_puntos()
        self.dibujar_rectas()
        if self.planos:
            self.dibujar_planos()
        self.planos_proyectantes()
        self.dibujar_ejes()
        self.update()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_W:
            self.theta -= 5
        elif event.key() == Qt.Key_A:
            self.phi -= 5
        elif event.key() == Qt.Key_S:
            self.theta += 5
        elif event.key() == Qt.Key_D:
            self.phi += 5
        elif event.key() == Qt.Key_Q:
            self.dz += 1
        elif event.key() == Qt.Key_E:
            self.dz -= 1
        elif event.key() == Qt.Key_Left:
            self.dx += 1
        elif event.key() == Qt.Key_Up:
            self.dy += 1
        elif event.key() == Qt.Key_Right:
            self.dx -= 1
        elif event.key() == Qt.Key_Down:
            self.dy -= 1
        elif event.key() == Qt.Key_1:
            self.ver_alzado()
        elif event.key() == Qt.Key_2:
            self.ver_planta()
        elif event.key() == Qt.Key_3:
            self.ver_perfil()
        elif event.key() == Qt.Key_R:
            self.ver_reset()
        elif event.key() == Qt.Key_Minus:
            self.z1 += 10
            self.z2 -= 10
        elif event.key() == Qt.Key_Plus:
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

        main_app.actualizar()
        self.update()
        super().keyPressEvent(event)


class Diedrico(QWidget):
    def __init__(self):
        QWidget.__init__(self)

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
        return QSize(2000, 2000)

    def paintEvent(self, event):
        qp = QPainter(self)
        qp.setRenderHint(QPainter.Antialiasing)
        self.elementos_estaticos(qp)
        qp.translate(500, 500)
        qp.scale(-1, -1)
        if main_app.ver_rectas.checkState():
            self.dibujar_rectas(qp)
        if main_app.ver_puntos.checkState():
            self.puntos(qp)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Plus:
            main_app.zoom_in()
        if event.key() == Qt.Key_Minus:
            main_app.zoom_out()
        if event.key() == Qt.Key_R:
            main_app.vista.setTransform(QTransform())

    def elementos_estaticos(self, qp):
        qp.setPen(self.pen_lt)
        qp.drawRect(0, 0, 1000, 1000)  # Marco

        qp.drawLine(5, 500, 995, 500)  # LT

        qp.drawLine(5, 505, 15, 505)  # Raya 1
        qp.drawLine(985, 505, 995, 505)  # Raya 2
        qp.drawLine(500, 5, 500, 995)  # Raya PP

    def puntos(self, qp):
        for i in range(main_app.lista_puntos.count()):
            punto = main_app.lista_puntos.itemWidget(main_app.lista_puntos.item(i))
            if punto.render:
                self.punto_prima(qp, punto)
                self.punto_prima2(qp, punto)
                if main_app.tercera_proyeccion.checkState():
                    self.punto_prima3(qp, punto)

    def punto_prima(self, qp, punto):
        qp.setPen(self.pen_pprima)
        qp.drawPoint(punto.x, -punto.z)

    def punto_prima2(self, qp, punto):
        qp.setPen(self.pen_pprima2)
        qp.drawPoint(punto.x, punto.y)

    def punto_prima3(self, qp, punto):
        qp.setPen(self.pen_prima3)
        qp.drawPoint(-punto.z, punto.y)

    def dibujar_rectas(self, qp):
        for i in range(main_app.lista_rectas.count()):
            recta = main_app.lista_rectas.itemWidget(main_app.lista_rectas.item(i))
            if recta.render.isChecked():

                if recta.infinita.isChecked():
                    extremos = recta.extremos
                    # Ninguna traza
                    if not recta.traza_v and not recta.traza_h and len(recta.extremos_I) == 2:
                        # Recta en PH
                        if recta.contenida_ph and not recta.contenida_pv:
                            self.dibujar_continuo(qp, recta.extremos_I[0], recta.extremos_I[1])

                        # Recta en PV
                        elif not recta.contenida_ph and recta.contenida_pv:
                            self.dibujar_continuo(qp, recta.extremos_I[0], recta.extremos_I[1])

                        # Trazas en LT
                        elif recta.extremos[0][1:] == recta.extremos[1][1:] == (0, 0):
                            self.dibujar_continuo(qp, [500, 0, 0], [-500, 0, 0])

                        # 1er cuadrante
                        else:
                            self.dibujar_continuo(qp, recta.extremos_I[0], recta.extremos_I[1])

                    # Una traza en PH
                    elif recta.traza_h and not recta.traza_v:
                        # Trazas en PH
                        if recta.extremos[0][2] == 0 and recta.extremos[1][2] == 0:
                            inicio = recta.traza_h
                            fin = recta.extremos_I[0]
                            self.dibujar_continuo(qp, inicio, fin)
                        else:
                            inicio = recta.traza_h
                            fin = recta.extremos_I[0]
                            self.dibujar_continuo(qp, inicio, fin)

                    # Una traza en PV
                    elif not recta.traza_h and recta.traza_v:
                        # Trazas en PV
                        if recta.extremos[0][1] == 0 and recta.extremos[1][1] == 0:
                            inicio = recta.traza_v
                            fin = recta.extremos_I[0]
                            self.dibujar_continuo(qp, inicio, fin)
                        # elif recta.traza_v[2] > 0:
                        else:
                            inicio = recta.traza_v
                            fin = recta.extremos_I[0]
                            self.dibujar_continuo(qp, inicio, fin)

                    # Dos trazas
                    elif recta.traza_v and recta.traza_h:
                        # Trazas en LT
                        if recta.traza_h == recta.traza_v:
                            inicio = recta.traza_h
                            fin = recta.extremos_I[0]
                            self.dibujar_continuo(qp, inicio, fin)
                        # 010
                        if recta.traza_h[2] > 0 and recta.traza_v[1] > 0:
                            inicio = recta.traza_v
                            fin = recta.traza_h
                            self.dibujar_continuo(qp, inicio, fin)
                        # 001
                        elif recta.traza_h[2] < 0 < recta.traza_v[1]:
                            inicio = recta.traza_v
                            fin = recta.extremos_I[0]
                            self.dibujar_continuo(qp, inicio, fin)
                        # 100
                        elif recta.traza_h[2] > 0 > recta.traza_v[1]:
                            inicio = recta.traza_h
                            fin = recta.extremos_I[0]
                            self.dibujar_continuo(qp, inicio, fin)
                else:
                    extremos = (recta.p1, recta.p2)

                    extremos_i = []
                    if extremos[0][1] >= 0 and extremos[0][2] >= 0:
                        extremos_i.append(extremos[0])
                    if extremos[1][1] >= 0 and extremos[1][2] >= 0:
                        extremos_i.append(extremos[1])

                    if len(extremos_i) == 2:
                        self.dibujar_continuo(qp, extremos[0], extremos[1])

                    else:
                        if recta.traza_v:
                            if recta.traza_v[2] >= 0:
                                self.dibujar_continuo(qp, extremos[0], recta.traza_v)

                        elif recta.traza_h:
                            if recta.traza_h[1] >= 0:
                                self.dibujar_continuo(qp, extremos[0], recta.traza_h)

                # Dibuja en discontínuo
                qp.setPen(self.pen_rprima)
                self.recta_prima(qp, extremos)
                qp.setPen(self.pen_rprima2)
                self.recta_prima2(qp, extremos)

                # Tercera proyección
                if main_app.tercera_proyeccion.checkState():
                    qp.setPen(self.pen_prima3)
                    self.recta_prima3(qp, extremos)

                self.dibujar_trazas(qp, recta)

    def dibujar_continuo(self, qp, inicio, fin):
        # Intercambio de ejes para arreglar sistema de coordenadas
        qp.setPen(self.pen_rprimaC)
        self.recta_prima(qp, (inicio, fin))
        qp.setPen(self.pen_rprima2C)
        self.recta_prima2(qp, (inicio, fin))

    @staticmethod
    def recta_prima(qp, extremos):
        x0 = int(extremos[0][0])
        x = int(extremos[1][0])
        y0 = int(-extremos[0][2])
        y = int(-extremos[1][2])
        if not (x0 == x and y0 == y):
            qp.drawLine(x0, y0, x, y)

    @staticmethod
    def recta_prima2(qp, extremos):
        x0 = int(extremos[0][0])
        x = int(extremos[1][0])
        y0 = int(extremos[0][1])
        y = int(extremos[1][1])
        if not (x0 == x and y0 == y):
            qp.drawLine(x0, y0, x, y)

    @staticmethod
    def recta_prima3(qp, extremos):
        x0 = int(-extremos[0][2])
        x = int(-extremos[1][2])
        y0 = int(extremos[0][1])
        y = int(extremos[1][1])
        qp.drawLine(x0, y0, x, y)

    def dibujar_trazas(self, qp, recta):
        qp.setPen(self.pen_trazas)
        if recta.infinita.isChecked():
            if recta.traza_h and recta.ver_traza_h.isChecked():
                qp.drawPoint(int(recta.traza_h[0]), int(-recta.traza_h[2]))  # V "
                qp.drawPoint(int(recta.traza_h[0]), 0)  # V '
            if recta.traza_v and recta.ver_traza_v.isChecked():
                qp.drawPoint(int(recta.traza_v[0]), int(recta.traza_v[1]))  # H '
                qp.drawPoint(int(recta.traza_v[0]), 0)  # H "


class Ventana(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setFixedSize(1500, 1015)

        widget_central = QWidget(self)
        self.renderizador = Renderizador(widget_central)
        self.renderizador.setGeometry(QRect(0, 0, 1000, 1000))
        self.renderizador.setFocusPolicy(Qt.ClickFocus)
        fuente = QFont()
        fuente.setPointSize(10)

        label = QLabel(widget_central)
        label.setGeometry(QRect(1010, 10, 91, 16))
        label.setFont(fuente)
        label_2 = QLabel(widget_central)
        label_2.setGeometry(QRect(1010, 30, 71, 16))
        label_2.setFont(fuente)
        self.label_3 = QLabel(widget_central)
        self.label_3.setGeometry(QRect(1110, 30, 141, 20))
        self.label_3.setFont(fuente)
        label_4 = QLabel(widget_central)
        label_4.setGeometry(QRect(1008, 50, 110, 16))
        label_4.setFont(fuente)
        self.label_5 = QLabel(widget_central)
        self.label_5.setGeometry(QRect(1110, 49, 200, 20))
        self.label_5.setFont(fuente)
        self.label_6 = QLabel(widget_central)
        self.label_6.setGeometry(QRect(1010, 70, 111, 16))
        self.label_6.setFont(fuente)
        self.label_7 = QLabel(widget_central)
        self.label_7.setGeometry(QRect(1130, 70, 130, 16))
        self.label_7.setFont(fuente)
        label_8 = QLabel(widget_central)
        label_8.setGeometry(QRect(1010, 90, 91, 16))
        label_8.setFont(fuente)
        label_9 = QLabel(widget_central)
        label_9.setGeometry(QRect(1010, 140, 91, 16))
        label_9.setFont(fuente)
        label_10 = QLabel(widget_central)
        label_10.setGeometry(QRect(1170, 140, 91, 16))
        label_10.setFont(fuente)
        label_11 = QLabel(widget_central)
        label_11.setGeometry(QRect(1330, 140, 91, 16))
        label_11.setFont(fuente)
        label_12 = QLabel(widget_central)
        label_12.setGeometry(QRect(1010, 160, 91, 16))
        label_13 = QLabel(widget_central)
        label_13.setGeometry(QRect(1010, 180, 91, 16))
        label_14 = QLabel(widget_central)
        label_14.setGeometry(QRect(1010, 200, 91, 16))
        label_15 = QLabel(widget_central)
        label_15.setGeometry(QRect(1010, 220, 91, 16))
        label_16 = QLabel(widget_central)
        label_16.setGeometry(QRect(1170, 160, 51, 16))
        label_17 = QLabel(widget_central)
        label_17.setGeometry(QRect(1170, 180, 51, 16))
        label_18 = QLabel(widget_central)
        label_18.setGeometry(QRect(1170, 200, 91, 21))
        label_19 = QLabel(widget_central)
        label_19.setGeometry(QRect(1330, 160, 51, 16))
        label_20 = QLabel(widget_central)
        label_20.setGeometry(QRect(1330, 180, 51, 16))
        label_21 = QLabel(widget_central)
        label_21.setGeometry(QRect(1330, 220, 91, 21))
        label_22 = QLabel(widget_central)
        label_22.setGeometry(QRect(1330, 200, 51, 16))
        label_23 = QLabel(widget_central)
        label_23.setGeometry(QRect(1020, 982, 21, 16))

        boton_r = QPushButton(widget_central)
        boton_r.setGeometry(QRect(1010, 110, 81, 23))
        boton_r.clicked.connect(self.renderizador.ver_reset)
        boton_alzado = QPushButton(widget_central)
        boton_alzado.setGeometry(QRect(1100, 110, 81, 23))
        boton_alzado.clicked.connect(self.renderizador.ver_alzado)
        boton_planta = QPushButton(widget_central)
        boton_planta.setGeometry(QRect(1190, 110, 81, 23))
        boton_planta.clicked.connect(self.renderizador.ver_planta)
        boton_perfil = QPushButton(widget_central)
        boton_perfil.setGeometry(QRect(1280, 110, 81, 23))
        boton_perfil.clicked.connect(self.renderizador.ver_perfil)
        boton_punto = QPushButton(widget_central)
        boton_punto.setGeometry(QRect(1010, 270, 151, 21))
        boton_punto.clicked.connect(self.crear_punto)
        boton_recta = QPushButton(widget_central)
        boton_recta.setGeometry(QRect(1170, 249, 151, 21))
        boton_recta.clicked.connect(self.crear_recta)
        boton_plano = QPushButton(widget_central)
        boton_plano.setGeometry(QRect(1330, 270, 151, 21))
        boton_plano.clicked.connect(self.crear_plano)

        widget = QWidget(widget_central)
        widget.setFocusPolicy(Qt.ClickFocus)
        layout = QHBoxLayout(widget)
        widget.setGeometry(QRect(1000, 500, 500, 490))
        scene = QGraphicsScene(self)
        self.vista = QGraphicsView(scene)
        layout.addWidget(self.vista)
        self.diedrico = Diedrico()
        self.diedrico.setFocusPolicy(Qt.ClickFocus)
        self.diedrico.setFixedSize(1000, 1000)
        scene.addWidget(self.diedrico)
        QTimer.singleShot(0, self.mover)

        self.valor_do = QSpinBox(widget_central)
        self.valor_do.setGeometry(QRect(1110, 160, 51, 20))
        self.valor_do.setRange(-500, 500)
        self.valor_a = QSpinBox(widget_central)
        self.valor_a.setGeometry(QRect(1110, 180, 51, 20))
        self.valor_a.setRange(-500, 500)
        self.valor_c = QSpinBox(widget_central)
        self.valor_c.setGeometry(QRect(1110, 200, 51, 20))
        self.valor_c.setRange(-500, 500)
        self.punto_1 = QComboBox(widget_central)
        self.punto_1.setGeometry(QRect(1230, 160, 91, 22))
        self.punto_2 = QComboBox(widget_central)
        self.punto_2.setGeometry(QRect(1230, 180, 91, 21))
        self.pplano1 = QComboBox(widget_central)
        self.pplano1.setGeometry(QRect(1380, 160, 91, 22))
        self.pplano2 = QComboBox(widget_central)
        self.pplano2.setGeometry(QRect(1380, 180, 91, 22))
        self.pplano3 = QComboBox(widget_central)
        self.pplano3.setGeometry(QRect(1380, 200, 91, 22))

        self.punto_nombre = QPlainTextEdit(widget_central)
        self.punto_nombre.setGeometry(QRect(1010, 240, 151, 25))
        self.recta_nombre = QPlainTextEdit(widget_central)
        self.recta_nombre.setGeometry(QRect(1170, 220, 151, 25))
        self.plano_nombre = QPlainTextEdit(widget_central)
        self.plano_nombre.setGeometry(QRect(1330, 240, 151, 25))

        self.tercera_proyeccion = QCheckBox(widget_central)
        self.tercera_proyeccion.setGeometry(QRect(1050, 982, 111, 17))
        self.tercera_proyeccion.clicked.connect(self.diedrico.update)
        self.ver_puntos = QCheckBox(widget_central)
        self.ver_puntos.setGeometry(QRect(1170, 982, 61, 17))
        self.ver_puntos.setChecked(True)
        self.ver_puntos.clicked.connect(self.diedrico.update)
        self.ver_rectas = QCheckBox(widget_central)
        self.ver_rectas.setGeometry(QRect(1232, 982, 61, 17))
        self.ver_rectas.setChecked(True)
        self.ver_rectas.clicked.connect(self.diedrico.update)
        self.ver_planos = QCheckBox(widget_central)
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

        widget_punto = QWidget(widget_central)
        widget_punto.setGeometry(QRect(1010, 291, 151, 211))
        vertical_punto = QVBoxLayout(widget_punto)
        vertical_punto.setContentsMargins(0, 0, 0, 0)
        self.lista_puntos = QListWidget(widget_punto)

        vertical_punto.addWidget(self.lista_puntos)

        widget_recta = QWidget(widget_central)
        widget_recta.setGeometry(QRect(1170, 270, 151, 231))
        vertical_recta = QVBoxLayout(widget_recta)
        vertical_recta.setContentsMargins(0, 0, 0, 0)
        self.lista_rectas = QListWidget(widget_recta)
        vertical_recta.addWidget(self.lista_rectas)

        widget_planos = QWidget(widget_central)
        widget_planos.setGeometry(QRect(1330, 290, 151, 211))
        vertical_planos = QVBoxLayout(widget_planos)
        vertical_planos.setContentsMargins(0, 0, 0, 0)
        self.lista_planos = QListWidget(widget_planos)
        vertical_planos.addWidget(self.lista_planos)

        self.puntero_puntos = 15
        self.puntero_rectas = 17
        self.puntero_planos = 0
        self.id_punto = 1
        self.id_recta = 1
        self.id_plano = 1

        self.opciones = []
        self.v = (Point3D(500, 500, 500), Point3D(-500, 500, 500), Point3D(-500, -500, 500),
                  Point3D(500, -500, 500), Point3D(500, 500, -500), Point3D(-500, 500, -500),
                  Point3D(-500, -500, -500), Point3D(500, -500, -500))

        self.p = (Plane(self.v[0], self.v[1], self.v[2]), Plane(self.v[0], self.v[1], self.v[5]),
                  Plane(self.v[0], self.v[4], self.v[7]), Plane(self.v[4], self.v[5], self.v[7]),
                  Plane(self.v[2], self.v[3], self.v[7]), Plane(self.v[1], self.v[2], self.v[5]))

        self.a = (Segment3D(self.v[0], self.v[1]), Segment3D(self.v[1], self.v[2]),
                  Segment3D(self.v[2], self.v[3]), Segment3D(self.v[3], self.v[0]),
                  Segment3D(self.v[0], self.v[4]), Segment3D(self.v[1], self.v[5]),
                  Segment3D(self.v[2], self.v[6]), Segment3D(self.v[3], self.v[7]),
                  Segment3D(self.v[4], self.v[5]), Segment3D(self.v[5], self.v[6]),
                  Segment3D(self.v[6], self.v[7]), Segment3D(self.v[7], self.v[4]))
        self.actualizar()
        self.setWindowTitle("Dibujo técnico")
        self.setCentralWidget(widget_central)

    def zoom_in(self):
        scale_tr = QTransform()
        scale_tr.scale(1.2, 1.2)
        tr = self.vista.transform() * scale_tr
        self.vista.setTransform(tr)

    def zoom_out(self):
        scale_tr = QTransform()
        scale_tr.scale(1.2, 1.2)
        scale_inverted, invertible = scale_tr.inverted()
        if invertible:
            tr = self.vista.transform() * scale_inverted
            self.vista.setTransform(tr)

    def mover(self):
        self.vista.verticalScrollBar().setValue(int(self.vista.verticalScrollBar().maximum() / 2))
        self.vista.horizontalScrollBar().setValue(int(self.vista.verticalScrollBar().maximum() / 2))

    def elegir_puntos_recta(self):
        self.punto_1.clear()
        self.punto_2.clear()
        for i in range(self.lista_puntos.count()):
            self.punto_1.addItem(self.lista_puntos.itemWidget(self.lista_puntos.item(i)).name)
            self.punto_2.addItem(self.lista_puntos.itemWidget(self.lista_puntos.item(i)).name)

    def elegir_puntos_plano(self):
        self.pplano1.clear()
        self.pplano2.clear()
        self.pplano3.clear()
        for i in range(len(self.opciones)):
            self.pplano1.addItem(self.opciones[i])
            self.pplano2.addItem(self.opciones[i])
            self.pplano3.addItem(self.opciones[i])

    def actualizar(self):
        x = round(500 * (sin(radians(self.renderizador.theta)) * cos(radians(self.renderizador.phi)))
                  + self.renderizador.dx, 2)
        z = round(500 * (sin(radians(self.renderizador.theta)) * sin(radians(self.renderizador.phi)))
                  + self.renderizador.dz, 2)
        y = round(500 * (cos(radians(self.renderizador.theta))) + self.renderizador.dy, 2)
        theta = self.renderizador.theta - 360
        phi = self.renderizador.phi
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

    def crear_punto(self):
        do = self.valor_do.value()
        cota = self.valor_c.value()
        alejamiento = self.valor_a.value()
        name = self.punto_nombre.toPlainText()

        # Evita que el puntero supere la longitud de la lista
        if self.puntero_puntos == len(ascii_uppercase):
            self.puntero_puntos = 0
        # Genera nombres genéricos si no se provee uno
        if name == "":
            name = ascii_uppercase[self.puntero_puntos]
            self.puntero_puntos += 1
        # Evita nombres duplicados
        for i in range(self.lista_puntos.count()):
            if self.lista_puntos.itemWidget(self.lista_puntos.item(i)).name == name:
                name = ascii_uppercase[self.puntero_puntos]
                self.puntero_puntos += 1
                break

        # Add placeholder item to List
        item = QListWidgetItem()
        self.lista_puntos.addItem(item)
        # Create Custom Widget
        punto = Punto(self, self.id_punto, name, do, alejamiento, cota)
        self.id_punto += 1
        item.setSizeHint(punto.minimumSizeHint())
        # Set the custom_row widget to be displayed within the placeholder Item
        self.lista_puntos.setItemWidget(item, punto)

        self.elegir_puntos_recta()
        # self.elegir_puntos_plano()
        self.diedrico.update()

    def borrar_punto(self, idd):
        for indx in range(self.lista_puntos.count()):
            item = self.lista_puntos.item(indx)
            widget = self.lista_puntos.itemWidget(item)
            if widget.id == idd:
                self.lista_puntos.takeItem(self.lista_puntos.row(item))
                break
        self.diedrico.update()
        self.elegir_puntos_recta()
        self.elegir_puntos_plano()

    def borrar_recta(self, idd):
        for indx in range(self.lista_rectas.count()):
            item = self.lista_rectas.item(indx)
            widget = self.lista_rectas.itemWidget(item)
            if widget.id == idd:
                self.lista_rectas.takeItem(self.lista_rectas.row(item))
                break
        self.diedrico.update()

    def crear_recta(self):
        punto1 = self.punto_1.currentText()
        punto2 = self.punto_2.currentText()
        name = self.recta_nombre.toPlainText()
        for i in range(self.lista_puntos.count()):
            if self.lista_puntos.itemWidget(self.lista_puntos.item(i)).name == punto1:
                punto1 = self.lista_puntos.itemWidget(self.lista_puntos.item(i))
            if self.lista_puntos.itemWidget(self.lista_puntos.item(i)).name == punto2:
                punto2 = self.lista_puntos.itemWidget(self.lista_puntos.item(i))
        if not punto1 and not punto2:
            QMessageBox.about(self, "Error al crear la recta",
                              "Debes crear al menos dos puntos y seleccionarlos para crear la recta")
        elif punto1.coords == punto2.coords:
            QMessageBox.about(self, "Error al crear la recta",
                              "La recta debe ser creada a partir de dos puntos no coincidentes")
        else:
            if self.puntero_rectas == len(ascii_lowercase):  # Evita que el puntero supere la longitud de la lista
                self.puntero_rectas = 0

            if name == "":  # Genera nombres genéricos si no se provee uno
                name = ascii_lowercase[self.puntero_rectas]
                self.puntero_rectas += 1

            for i in range(self.lista_rectas.count()):  # Evita nombres duplicados
                if self.lista_rectas.itemWidget(self.lista_rectas.item(i)).name == name:
                    name = ascii_lowercase[self.puntero_rectas]
                    self.puntero_rectas += 1
                    break

            # Add placeholder item to List
            item = QListWidgetItem()
            self.lista_rectas.addItem(item)
            # Create Custom Widget
            recta = Recta(self, self.id_recta, name, punto1, punto2)
            self.id_recta += 1
            item.setSizeHint(recta.minimumSizeHint())
            # Set the custom_row widget to be displayed within the placeholder Item
            self.lista_rectas.setItemWidget(item, recta)

            self.id_recta += 1

            self.diedrico.update()

    def crear_plano(self):
        punto1 = self.pplano1.currentText()
        punto2 = self.pplano2.currentText()
        punto3 = self.pplano3.currentText()
        nombre = self.plano_nombre.toPlainText()

        for i in range(len(self.renderizador.puntos)):
            if self.renderizador.puntos[i][0] == punto1:
                punto1 = self.renderizador.puntos[i]
            if self.renderizador.puntos[i][0] == punto2:
                punto2 = self.renderizador.puntos[i]
            if self.renderizador.puntos[i][0] == punto3:
                punto3 = self.renderizador.puntos[i]

        if len({punto1[-3:], punto2[-3:], punto3[-3:]}) < 3:
            QMessageBox.about(self, "Error al crear el plano",
                              "Dos de los puntos proporcionados son coincidentes")
        elif Point3D.is_collinear(Point3D(punto1[-3:]), Point3D(punto2[-3:]), Point3D(punto3[-3:])):
            QMessageBox.about(self, "Error al crear el plano",
                              "El plano debe ser creado por tres puntos no alineados")
        # TODO Plano en el límite del mal
        else:
            if self.puntero_planos == len(ascii_uppercase):  # Evita que el puntero supere la longitud de la lista
                self.puntero_planos = 0

            if nombre == "":  # Genera nombres genéricos si no se provee uno
                nombre = ascii_uppercase[self.puntero_planos]
                self.puntero_planos += 1

            for i in range(len(self.renderizador.planos)):  # Evita nombres duplicados
                if self.renderizador.planos[i][0] == nombre:
                    nombre = ascii_uppercase[self.puntero_planos]
                    self.puntero_planos += 1

            name = QLabel("{}({}, {}, {})".format(nombre, punto1[0], punto2[0], punto3[0]))

            vertices = self.plano_limites(punto1, punto2, punto3)
            vertices = [tuple([p.x, p.y, p.z]) for p in vertices]
            plano = (nombre, vertices[0], vertices[1], vertices[2], vertices[3])
            borrar = QPushButton("X")
            borrar.setMaximumWidth(20)

            # wrapper = partial(self.borrar_plano, (name, borrar), plano)
            # borrar.clicked.connect(wrapper)

            row = self.elementos3.rowCount()

            self.elementos3.addWidget(name, row, 0)
            self.elementos3.addWidget(borrar, row, 1)
            self.renderizador.planos.append(plano)

            self.diedrico.update()

    def plano_limites(self, punto1, punto2, punto3):
        plano = Plane(Point3D(punto1[-3:]), Point3D(punto2[-3:]), Point3D(punto3[-3:]))
        buenos = []
        for i in range(12):
            interseccion = intersection(plano, self.a[i])
            if interseccion:
                buenos.append(interseccion[0])
        return buenos

    def borrar_plano(self, widgets, plano):
        name, borrar = widgets
        name.deleteLater()
        borrar.deleteLater()
        self.renderizador.planos.remove(plano)
        self.diedrico.update()


if __name__ == "__main__":
    MainEvent = QApplication([])
    main_app = Ventana()
    main_app.show()
    MainEvent.exec()
