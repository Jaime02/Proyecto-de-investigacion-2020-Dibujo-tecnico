from math import sin, cos, radians

from OpenGL.GL import (glClear, GL_COLOR_BUFFER_BIT, glEnable, glMatrixMode, GL_PROJECTION, glLoadIdentity, glOrtho,
                       glClearColor, GL_DEPTH_BUFFER_BIT, GL_MODELVIEW, glLineWidth, glBegin, glColor, glVertex, glEnd,
                       glPointSize, GL_POINT_SMOOTH, GL_POINTS, GL_BLEND, glBlendFunc, GL_SRC_ALPHA, GL_QUADS, GL_LINES,
                       GL_LINE_LOOP, GL_ONE_MINUS_SRC_ALPHA, GL_TRIANGLE_FAN, glLoadMatrixf)
from OpenGL.GLU import gluLookAt
from PySide6.QtCore import Qt, QSize, QPoint, QPointF
from PySide6.QtGui import QPainter, QPen, QTransform, QColor
from PySide6.QtWidgets import QWidget
from PySide6.QtOpenGLWidgets import QOpenGLWidget


class Renderizador(QOpenGLWidget):
    phi: int  # Ángulo horizontal
    theta: int  # Ángulo vertical

    def __init__(self, programa):
        QOpenGLWidget.__init__(self)
        self.programa = programa
        self.desviacion_x = 0
        self.desviacion_y = 0
        self.desviacion_z = 0
        self.theta = 405
        self.phi = 45
        self.zoom = 150
        self.x = sin(radians(self.theta)) * cos(radians(self.phi)) + self.desviacion_x
        self.z = sin(radians(self.theta)) * sin(radians(self.phi)) + self.desviacion_z
        self.y = cos(radians(self.theta)) + self.desviacion_y

        # Vértices de los planos
        self.vertices_plano_vertical_arriba = ((500, 0, 500), (500, 0, 0), (-500, 0, 0), (-500, 0, 500))
        self.vertices_plano_vertical_debajo = ((500, 0, 0), (-500, 0, 0), (-500, 0, -500), (500, 0, -500))
        self.vertices_plano_horizontal_delante = ((500, 0, 0), (500, 500, 0), (-500, 500, 0), (-500, 0, 0))
        self.vertices_plano_horizontal_detras = ((500, 0, 0), (500, -500, 0), (-500, -500, 0), (-500, 0, 0))
        self.vertices_borde_plano_vertical = ((500, 0, 500), (-500, 0, 500), (-500, 0, -500), (500, 0, -500))
        self.vertices_borde_plano_horizontal = ((500, 500, 0), (500, -500, 0), (-500, -500, 0), (-500, 500, 0))

        self.ultima_posicion = QPoint()

        self.m = [[1, 0, 0, 0],
                  [0, 0, 1, 0],
                  [0, 1, 0, 0],
                  [0, 0, 0, 1]]

    def sizeHint(self):
        return QSize(700, 700)

    def resizeEvent(self, evento):
        # Mantiene una relación de aspecto cuadrada
        if self.width() > self.height():
            self.resize(self.height(), self.height())
        elif self.height() > self.width():
            self.resize(self.width(), self.width())
        QOpenGLWidget.resizeEvent(self, evento)

    def mousePressEvent(self, evento):
        self.ultima_posicion = evento.pos()

    def mouseMoveEvent(self, evento):
        # Permite rotar la cámara arrastrando el ratón
        dx = evento.x() - self.ultima_posicion.x()
        dy = evento.y() - self.ultima_posicion.y()

        if evento.buttons() and Qt.LeftButton:
            self.theta -= dy
            self.phi -= dx

        self.ultima_posicion = evento.pos()
        self.recalcular_posicion()
        self.programa.actualizar_texto()

    def recalcular_posicion(self):
        if self.theta < 360:
            self.theta = 360
        if self.theta > 540:
            self.theta = 540
        if self.phi >= 360:
            self.phi -= 360
        if self.phi < 0:
            self.phi += 360

        if self.zoom < 10:
            self.zoom = 10

        self.x = sin(radians(self.theta)) * cos(radians(self.phi)) + self.desviacion_x
        self.z = sin(radians(self.theta)) * sin(radians(self.phi)) + self.desviacion_z
        self.y = cos(radians(self.theta)) + self.desviacion_y
        gluLookAt(self.x, self.y, self.z, self.desviacion_x, self.desviacion_y, self.desviacion_z, 0, 1, 0)
        self.programa.actualizar_texto()
        self.update()

    def ver_alzado(self):
        self.phi = 90
        self.theta = 450
        self.recalcular_posicion()

    def ver_planta(self):
        self.phi = 90
        self.theta = 360
        self.recalcular_posicion()

    def ver_perfil(self):
        self.phi = 0
        self.theta = 450
        self.recalcular_posicion()

    def ver_reset(self):
        self.theta = 405
        self.phi = 45
        self.zoom = 150
        self.desviacion_x = 0
        self.desviacion_y = 0
        self.desviacion_z = 0
        self.recalcular_posicion()

    def plano_vertical_arriba(self):
        if self.programa.ajustes.ver_plano_vertical.isChecked():
            glBegin(GL_QUADS)
            glColor(self.programa.ajustes.color_plano_vertical)
            for vertex in range(4):
                glVertex(self.vertices_plano_vertical_arriba[vertex])
            glEnd()

    def plano_vertical_debajo(self):
        if self.programa.ajustes.ver_plano_vertical.isChecked():
            glBegin(GL_QUADS)
            glColor(self.programa.ajustes.color_plano_vertical)
            for vertex in range(4):
                glVertex(self.vertices_plano_vertical_debajo[vertex])
            glEnd()

    def plano_horizontal_delante(self):
        if self.programa.ajustes.ver_plano_horizontal.isChecked():
            glBegin(GL_QUADS)
            glColor(self.programa.ajustes.color_plano_horizontal)
            for vertex in range(4):
                glVertex(self.vertices_plano_horizontal_delante[vertex])
            glEnd()

    def plano_horizontal_detras(self):
        if self.programa.ajustes.ver_plano_horizontal.isChecked():
            glBegin(GL_QUADS)
            glColor(self.programa.ajustes.color_plano_horizontal)
            for vertex in range(4):
                glVertex(self.vertices_plano_horizontal_detras[vertex])
            glEnd()

    def bordes_plano_vertical(self):
        if self.programa.ajustes.ver_plano_vertical.isChecked():
            glLineWidth(1)
            glColor(self.programa.ajustes.color_plano_vertical)
            glBegin(GL_LINE_LOOP)
            for vertex in range(4):
                glVertex(self.vertices_borde_plano_vertical[vertex])
            glEnd()

    def bordes_plano_horizontal(self):
        if self.programa.ajustes.ver_plano_horizontal.isChecked():
            glLineWidth(1)
            glColor(self.programa.ajustes.color_plano_horizontal)
            glBegin(GL_LINE_LOOP)
            for vertex in range(4):
                glVertex(self.vertices_borde_plano_horizontal[vertex])
            glEnd()

    def dibujar_ejes(self):
        if self.programa.ajustes.ver_ejes.isChecked():
            glLineWidth(3)
            glBegin(GL_LINES)
            # Eje X, color rojo
            glColor(1, 0, 0)
            glVertex(0, 0, 0)
            glVertex(10, 0, 0)
            # Eje Y, color verde
            glColor(0, 1, 0)
            glVertex(0, 0, 0)
            glVertex(0, 10, 0)
            # Eje Z, color azul
            glColor(0, 0, 1)
            glVertex(0, 0, 0)
            glVertex(0, 0, 10)
            glEnd()

    def dibujar_puntos(self, cuadrante: str):
        for i in range(self.programa.lista_puntos.count()):
            punto = self.programa.lista_puntos.itemWidget(self.programa.lista_puntos.item(i))
            if punto.render.isChecked() and punto.cuadrante == cuadrante:
                glColor(punto.color)
                glPointSize(punto.grosor)
                glEnable(GL_POINT_SMOOTH)
                glBegin(GL_POINTS)
                glVertex(punto.x, punto.y, punto.z)
                glEnd()

    def dibujar_rectas(self, cuadrante: str):
        def dibujar(inicio, fin):
            glBegin(GL_LINES)
            glVertex(inicio)
            glVertex(fin)
            glEnd()

        for i in range(self.programa.lista_rectas.count()):
            recta = self.programa.lista_rectas.itemWidget(self.programa.lista_rectas.item(i))
            if recta.render.isChecked():
                glColor(recta.color)
                glLineWidth(recta.grosor)
                if recta.infinita.isChecked():
                    if "I" in recta.partes and cuadrante == "I":
                        glBegin(GL_LINES)
                        glVertex(recta.partes["I"][0].coords)
                        glVertex(recta.partes["I"][1].coords)
                        glEnd()
                    if "II" in recta.partes and cuadrante == "II":
                        glBegin(GL_LINES)
                        glVertex(recta.partes["II"][0].coords)
                        glVertex(recta.partes["II"][1].coords)
                        glEnd()
                    elif "III" in recta.partes and cuadrante == "III":
                        glBegin(GL_LINES)
                        glVertex(recta.partes["III"][0].coords)
                        glVertex(recta.partes["III"][1].coords)
                        glEnd()
                    elif "IV" in recta.partes and cuadrante == "IV":
                        glBegin(GL_LINES)
                        glVertex(recta.partes["IV"][0].coords)
                        glVertex(recta.partes["IV"][1].coords)
                        glEnd()
                    self.traza_v_recta(recta)
                    self.traza_h_recta(recta)
                else:
                    if recta.traza_v == "Contenida en PV" and recta.traza_h == "Contenida en PH":
                        if cuadrante == "I":
                            dibujar(recta.punto_1.coords, recta.punto_2.coords)
                    if recta.traza_v == "Contenida en PV":
                        if recta.traza_h_entre_puntos:
                            if cuadrante == recta.cuadrante_punto_1:
                                dibujar(recta.punto_1.coords, recta.traza_h.coords)
                            if cuadrante == recta.cuadrante_punto_2:
                                dibujar(recta.punto_2.coords, recta.traza_h.coords)
                            self.traza_h_recta(recta)
                        else:
                            if cuadrante == recta.cuadrante_punto_1:
                                dibujar(recta.punto_1.coords, recta.punto_2.coords)
                    elif recta.traza_h == "Contenida en PH":
                        if recta.traza_v_entre_puntos:
                            if cuadrante == recta.cuadrante_punto_1:
                                dibujar(recta.punto_1.coords, recta.traza_v.coords)
                            if cuadrante == recta.cuadrante_punto_2:
                                dibujar(recta.punto_2.coords, recta.traza_v.coords)
                            self.traza_v_recta(recta)
                        else:
                            if cuadrante == recta.cuadrante_punto_1:
                                dibujar(recta.punto_1.coords, recta.punto_2.coords)
                    elif recta.cuadrante_punto_1 == recta.cuadrante_punto_2 == cuadrante == "I":
                        dibujar(recta.punto_1.coords, recta.punto_2.coords)
                    elif recta.cuadrante_punto_1 == recta.cuadrante_punto_2 == cuadrante == "II":
                        dibujar(recta.punto_1.coords, recta.punto_2.coords)
                    elif recta.cuadrante_punto_1 == recta.cuadrante_punto_2 == cuadrante == "III":
                        dibujar(recta.punto_1.coords, recta.punto_2.coords)
                    elif recta.cuadrante_punto_1 == recta.cuadrante_punto_2 == cuadrante == "IV":
                        dibujar(recta.punto_1.coords, recta.punto_2.coords)
                    else:
                        if recta.traza_v_entre_puntos and recta.traza_h_entre_puntos:
                            if recta.segmento_entre_trazas == cuadrante:
                                dibujar(recta.traza_v.coords, recta.traza_h.coords)
                            elif recta.traza_v_entre_puntos == recta.traza_h_entre_puntos == "LT":
                                if recta.cuadrante_punto_1 == cuadrante:
                                    dibujar(recta.punto_1.coords, recta.traza_h.coords)
                                if recta.cuadrante_punto_2 == cuadrante:
                                    dibujar(recta.punto_2.coords, recta.traza_h.coords)
                                self.traza_h_recta(recta)
                        if recta.cuadrante_punto_1 == cuadrante:
                            if recta.traza_h_entre_puntos == "PH+" and (cuadrante == "I" or cuadrante == "IV"):
                                dibujar(recta.punto_1.coords, recta.traza_h.coords)
                                self.traza_h_recta(recta)
                            if recta.traza_h_entre_puntos == "PH-" and (cuadrante == "II" or cuadrante == "III"):
                                dibujar(recta.punto_1.coords, recta.traza_h.coords)
                                self.traza_h_recta(recta)

                            if recta.traza_v_entre_puntos == "PV+" and (cuadrante == "I" or cuadrante == "II"):
                                dibujar(recta.punto_1.coords, recta.traza_v.coords)
                                self.traza_v_recta(recta)
                            if recta.traza_v_entre_puntos == "PV-" and (cuadrante == "III" or cuadrante == "IV"):
                                dibujar(recta.punto_1.coords, recta.traza_v.coords)
                                self.traza_v_recta(recta)
                        if recta.cuadrante_punto_2 == cuadrante:
                            if recta.traza_h_entre_puntos == "PH+" and (cuadrante == "I" or cuadrante == "IV"):
                                dibujar(recta.punto_2.coords, recta.traza_h.coords)
                                self.traza_h_recta(recta)
                            if recta.traza_h_entre_puntos == "PH-" and (cuadrante == "II" or cuadrante == "III"):
                                dibujar(recta.punto_2.coords, recta.traza_h.coords)
                                self.traza_h_recta(recta)

                            if recta.traza_v_entre_puntos == "PV+" and (cuadrante == "I" or cuadrante == "II"):
                                dibujar(recta.punto_2.coords, recta.traza_v.coords)
                                self.traza_v_recta(recta)
                            if recta.traza_v_entre_puntos == "PV-" and (cuadrante == "III" or cuadrante == "IV"):
                                dibujar(recta.punto_2.coords, recta.traza_v.coords)
                                self.traza_v_recta(recta)

    def traza_v_recta(self, recta):
        if self.programa.ajustes.rectas_trazas_v.isChecked():
            if recta.traza_v != "Contenida en PV" and recta.ver_traza_vertical.isChecked():
                if recta.traza_v.x < 500 and recta.traza_v.y < 500:
                    glColor(0, 1, 0, 1)
                    glBegin(GL_POINTS)
                    glVertex(recta.traza_v.coords)
                    glEnd()
                    glColor(recta.color)

    def traza_h_recta(self, recta):
        if self.programa.ajustes.rectas_trazas_h.isChecked():
            if recta.traza_h != "Contenida en PH" and recta.ver_traza_horizontal.isChecked():
                if recta.traza_h.x < 500 and recta.traza_h.z < 500:
                    glColor(1, 0, 0, 1)
                    glBegin(GL_POINTS)
                    glVertex(recta.traza_h.coords)
                    glEnd()
                    glColor(recta.color)

    def dibujar_planos(self, cuadrante: str):
        for i in range(self.programa.lista_planos.count()):
            plano = self.programa.lista_planos.itemWidget(self.programa.lista_planos.item(i))
            if plano.render.isChecked():
                glBegin(GL_TRIANGLE_FAN)
                glColor(plano.color)
                if plano.infinito.isChecked():
                    puntos = plano.partes[cuadrante]
                    for j in puntos:
                        glVertex(j.coords)
                    glEnd()
                    glLineWidth(2)
                    glBegin(GL_LINE_LOOP)
                    for j in plano.limites:
                        glVertex(j.coords)
                elif cuadrante == "I":
                    glVertex(plano.puntos[0])
                    glVertex(plano.puntos[1])
                    glVertex(plano.puntos[2])
                glEnd()

    def paintGL(self):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(self.zoom, -self.zoom, -self.zoom, self.zoom, -5000, 5000)
        arriba = 1
        if self.theta == 360:
            arriba = -1
        gluLookAt(self.x, self.y, self.z, self.desviacion_x, self.desviacion_y, self.desviacion_z, 0, arriba, 0)

        glMatrixMode(GL_MODELVIEW)
        if self.programa.modo_oscuro:
            glClearColor(0.3, 0.3, 0.3, 0)
        else:
            glClearColor(1, 1, 1, 0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadMatrixf(self.m)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        self.ordenar_elementos()
        self.update()

    def dibujar_entidades(self, cuadrante: str):
        if self.programa.ajustes.ver_planos.isChecked():
            self.dibujar_planos(cuadrante)
        if self.programa.ajustes.ver_rectas.isChecked():
            self.dibujar_rectas(cuadrante)
        if self.programa.ajustes.ver_puntos.isChecked():
            self.dibujar_puntos(cuadrante)

    def ordenar_elementos(self):
        self.bordes_plano_horizontal()
        self.bordes_plano_vertical()

        # TODO: fixea esta wea
        self.dibujar_circunferencias()
        self.dibujar_poligonos()

        # Observador en:
        # Línea de tierra:
        if (self.phi == 0 or self.phi == 180) and self.theta == 0:
            self.dibujar_ejes()
            self.dibujar_entidades("I")
            self.dibujar_entidades("II")
            self.dibujar_entidades("III")
            self.dibujar_entidades("IV")

        # Plano horizontal:
        elif self.theta == 450:
            # PH positivo
            if 0 <= self.phi <= 180:
                self.dibujar_entidades("II")
                self.dibujar_entidades("III")
                self.plano_vertical_arriba()
                self.plano_vertical_debajo()
                self.dibujar_ejes()
                self.dibujar_entidades("I")
                self.dibujar_entidades("IV")
            else:
                # PH negativo
                self.dibujar_entidades("I")
                self.dibujar_entidades("IV")
                self.plano_vertical_arriba()
                self.plano_vertical_debajo()
                self.dibujar_ejes()
                self.dibujar_entidades("II")
                self.dibujar_entidades("III")

        # Plano vertical:
        elif self.phi == 0 or self.phi == 180 or self.theta == 360 or self.theta == 540:
            # PV positivo
            if self.theta < 450:
                self.dibujar_entidades("III")
                self.dibujar_entidades("IV")
                self.plano_horizontal_delante()
                self.plano_horizontal_detras()
                self.dibujar_ejes()
                self.dibujar_entidades("I")
                self.dibujar_entidades("II")
            else:
                # PV negativo
                self.dibujar_entidades("I")
                self.dibujar_entidades("II")
                self.plano_horizontal_delante()
                self.plano_horizontal_detras()
                self.dibujar_ejes()
                self.dibujar_entidades("III")
                self.dibujar_entidades("IV")

        # Primer cuadrante:
        elif self.theta < 450 and self.phi < 180:
            self.dibujar_entidades("III")
            self.plano_vertical_debajo()
            self.plano_horizontal_detras()
            self.dibujar_entidades("II")
            self.dibujar_entidades("IV")
            self.plano_vertical_arriba()
            self.plano_horizontal_delante()
            self.dibujar_ejes()
            self.dibujar_entidades("I")

        # Segundo cuadrante:
        elif self.theta < 450 and self.phi > 180:
            self.dibujar_entidades("IV")
            self.plano_vertical_debajo()
            self.plano_horizontal_delante()
            self.dibujar_entidades("III")
            self.dibujar_entidades("I")
            self.plano_vertical_arriba()
            self.plano_horizontal_detras()
            self.dibujar_ejes()
            self.dibujar_entidades("II")

        # Tercer cuadrante:
        elif self.theta > 450 and self.phi > 180:
            self.dibujar_entidades("I")
            self.plano_vertical_arriba()
            self.plano_horizontal_delante()
            self.dibujar_entidades("II")
            self.dibujar_entidades("IV")
            self.plano_vertical_debajo()
            self.plano_horizontal_detras()
            self.dibujar_ejes()
            self.dibujar_entidades("III")

        # Cuarto cuadrante:
        else:
            self.dibujar_entidades("II")
            self.plano_vertical_arriba()
            self.plano_horizontal_detras()
            self.dibujar_entidades("I")
            self.dibujar_entidades("III")
            self.plano_horizontal_delante()
            self.plano_vertical_debajo()
            self.dibujar_ejes()
            self.dibujar_entidades("IV")

    def dibujar_circunferencias(self):
        for i in range(self.programa.lista_circunferencias.count()):
            circ = self.programa.lista_circunferencias.itemWidget(self.programa.lista_circunferencias.item(i))
            if circ.render.isChecked():
                glColor(circ.color)
                glBegin(GL_LINE_LOOP)
                for punto in circ.puntos:
                    glVertex(*punto.coords)
                glEnd()

    def dibujar_poligonos(self):
        for i in range(self.programa.lista_poligonos.count()):
            poligono = self.programa.lista_poligonos.itemWidget(self.programa.lista_poligonos.item(i))
            if poligono.render.isChecked():
                glColor(poligono.color)
                glBegin(GL_LINE_LOOP)
                for punto in poligono.puntos:
                    glVertex(*punto.coords)
                glEnd()

    def keyPressEvent(self, evento):
        if evento.key() == Qt.Key_W:
            self.theta -= 1
        elif evento.key() == Qt.Key_A:
            self.phi -= 1
        elif evento.key() == Qt.Key_S:
            self.theta += 1
        elif evento.key() == Qt.Key_D:
            self.phi += 1
        elif evento.key() == Qt.Key_Q:
            self.desviacion_z += 1
        elif evento.key() == Qt.Key_E:
            self.desviacion_z -= 1
        elif evento.key() == Qt.Key_Left:
            self.desviacion_x += 1
        elif evento.key() == Qt.Key_Up:
            self.desviacion_y += 1
        elif evento.key() == Qt.Key_Right:
            self.desviacion_x -= 1
        elif evento.key() == Qt.Key_Down:
            self.desviacion_y -= 1
        elif evento.key() == Qt.Key_1:
            self.ver_alzado()
        elif evento.key() == Qt.Key_2:
            self.ver_planta()
        elif evento.key() == Qt.Key_3:
            self.ver_perfil()
        elif evento.key() == Qt.Key_R:
            self.ver_reset()
        elif evento.key() == Qt.Key_Minus:
            self.zoom += 10
        elif evento.key() == Qt.Key_Plus:
            self.zoom -= 10

        self.recalcular_posicion()

        self.update()
        QOpenGLWidget.keyPressEvent(self, evento)

    def wheelEvent(self, evento):
        angulo = evento.angleDelta().y()
        if angulo < 0:
            self.zoom += 10
        elif angulo > 0:
            self.zoom -= 10

        if self.zoom < 10:
            self.zoom = 10

        QOpenGLWidget.wheelEvent(self, evento)


class Diedrico(QWidget):
    def __init__(self, programa):
        QWidget.__init__(self)
        self.programa = programa

        negro = QColor(0, 0, 0)
        rojo = QColor(255, 103, 69)
        verde = QColor(0, 255, 0)
        azul = QColor(50, 100, 255)
        azul_oscuro = QColor(10, 50, 140)

        self.pen_base = QPen(negro, 2)
        self.pen_base.setCosmetic(True)

        self.pen_punto_prima = QPen(QColor(201, 10, 0), 6)
        self.pen_punto_prima.setCosmetic(True)
        self.pen_punto_prima2 = QPen(QColor(8, 207, 41), 6)
        self.pen_punto_prima2.setCosmetic(True)

        self.pen_recta_prima = QPen(rojo, 5, Qt.DotLine)
        self.pen_recta_prima.setDashPattern([1, 3])
        self.pen_recta_prima.setCosmetic(True)
        self.pen_recta_prima2 = QPen(verde, 5, Qt.DotLine)
        self.pen_recta_prima2.setDashPattern([1, 3])
        self.pen_recta_prima2.setCosmetic(True)

        self.pen_recta_prima_continuo = QPen(rojo, 5)
        self.pen_recta_prima_continuo.setCosmetic(True)
        self.pen_recta_prima2_continuo = QPen(verde, 5)
        self.pen_recta_prima2_continuo.setCosmetic(True)
        self.pen_trazas = QPen(Qt.black, 6)
        self.pen_trazas.setCosmetic(True)

        self.pen_prima3 = QPen(Qt.black, 5)
        self.pen_prima3.setCosmetic(True)

        self.pen_plano_prima = QPen(azul, 8)
        self.pen_plano_prima.setCosmetic(True)
        self.pen_plano_prima2 = QPen(azul_oscuro, 8)
        self.pen_plano_prima2.setCosmetic(True)

        self.pen_plano_prima_discontinuo = QPen(azul, 8)
        self.pen_plano_prima_discontinuo.setDashPattern([1, 3])
        self.pen_plano_prima_discontinuo.setCosmetic(True)
        self.pen_plano_prima2_discontinuo = QPen(azul_oscuro, 8)
        self.pen_plano_prima2_discontinuo.setDashPattern([1, 3])
        self.pen_plano_prima2_discontinuo.setCosmetic(True)

    def paintEvent(self, evento):
        qp = QPainter(self)
        qp.setRenderHint(QPainter.Antialiasing)
        self.elementos_estaticos(qp)
        qp.translate(500, 500)
        qp.scale(-1, -1)
        if self.programa.ver_planos.checkState():
            self.dibujar_planos(qp)
        if self.programa.ver_rectas.checkState():
            self.dibujar_rectas(qp)
        if self.programa.ver_puntos.checkState():
            self.dibujar_puntos(qp)
        self.dibujar_circunferencias(qp)
        self.dibujar_poligonos(qp)
        self.update()

    def keyPressEvent(self, evento):
        if evento.key() == Qt.Key_Plus:
            self.zoom_in()
        if evento.key() == Qt.Key_Minus:
            self.zoom_out()
        if evento.key() == Qt.Key_R:
            # Reset
            self.programa.vista.setTransform(QTransform())

    def zoom_in(self):
        scale_tr = QTransform()
        scale_tr.scale(1.2, 1.2)
        transformacion = self.programa.vista.transform() * scale_tr
        self.programa.vista.setTransform(transformacion)

    def zoom_out(self):
        scale_tr = QTransform()
        scale_tr.scale(1.2, 1.2)
        scale_inverted = scale_tr.inverted()[0]
        transformacion = self.programa.vista.transform() * scale_inverted
        self.programa.vista.setTransform(transformacion)

    def elementos_estaticos(self, qp):
        qp.setPen(self.pen_base)
        qp.drawRect(0, 0, 1000, 1000)  # Marco
        qp.drawLine(5, 500, 995, 500)  # LT
        qp.drawLine(5, 505, 15, 505)  # Raya pequeña izquierda
        qp.drawLine(985, 505, 995, 505)  # Raya pequeña derecha
        qp.drawLine(500, 5, 500, 995)  # Raya plano perfil

    def dibujar_puntos(self, qp):
        for i in range(self.programa.lista_puntos.count()):
            punto = self.programa.lista_puntos.itemWidget(self.programa.lista_puntos.item(i))
            if punto.render.isChecked():
                # Dibuja la proyección ' del punto
                qp.setPen(self.pen_punto_prima)
                qp.drawPoint(QPointF(punto.x, -punto.y))

                # Dibuja la proyección " del punto
                qp.setPen(self.pen_punto_prima2)
                qp.drawPoint(QPointF(punto.x, punto.z))

                # Si la tercera proyección del punto está activada, la dibuja
                if self.programa.tercera_proyeccion.checkState():
                    if self.programa.modo_oscuro:
                        self.pen_prima3.setColor(QColor(200, 200, 200))
                    else:
                        self.pen_prima3.setColor(QColor(0, 0, 0))
                    qp.setPen(self.pen_prima3)
                    qp.drawPoint(QPointF(-punto.y, punto.z))

    def dibujar_rectas(self, qp):
        for i in range(self.programa.lista_rectas.count()):
            recta = self.programa.lista_rectas.itemWidget(self.programa.lista_rectas.item(i))
            partes = recta.partes
            if recta.render.isChecked():
                if recta.infinita.isChecked():
                    if 'I' in partes:
                        self.dibujar_continuo(qp, partes['I'])
                    if 'II' in partes:
                        self.dibujar_discontinuo(qp, partes['II'])
                    if 'III' in partes:
                        self.dibujar_discontinuo(qp, partes['III'])
                    if 'IV' in partes:
                        self.dibujar_discontinuo(qp, partes['IV'])
                    self.recta_prima3(qp, recta.extremos)
                else:
                    if recta.cuadrante_punto_1 == recta.cuadrante_punto_2 == "I":
                        self.dibujar_continuo(qp, (recta.punto_1, recta.punto_2))
                    elif recta.cuadrante_punto_1 != "I" and recta.cuadrante_punto_2 != "I":
                        self.dibujar_discontinuo(qp, (recta.punto_1, recta.punto_2))
                    else:
                        if recta.cuadrante_punto_1 == "I":
                            if recta.traza_v != "Contenida en PV" and recta.traza_v:
                                if recta.traza_v.z >= 0:
                                    self.dibujar_discontinuo(qp, (recta.traza_v, recta.punto_2))
                                    self.dibujar_continuo(qp, (recta.punto_1, recta.traza_v))
                            if recta.traza_h != "Contenida en PH" and recta.traza_h:
                                if recta.traza_h.y >= 0:
                                    self.dibujar_discontinuo(qp, (recta.traza_h, recta.punto_2))
                                    self.dibujar_continuo(qp, (recta.punto_1, recta.traza_h))
                        elif recta.cuadrante_punto_2 == "I":
                            if recta.traza_v != "Contenida en PV" and recta.traza_v:
                                if recta.traza_v.z >= 0:
                                    self.dibujar_discontinuo(qp, (recta.traza_v, recta.punto_1))
                                    self.dibujar_continuo(qp, (recta.punto_2, recta.traza_v))
                            if recta.traza_h != "Contenida en PH" and recta.traza_h:
                                if recta.traza_h.y >= 0:
                                    self.dibujar_discontinuo(qp, (recta.traza_h, recta.punto_1))
                                    self.dibujar_continuo(qp, (recta.punto_2, recta.traza_h))
                        if recta.traza_v != "Contenida en PV" and recta.traza_v \
                                and recta.traza_h and recta.traza_h != "Contenida en PH":
                            if recta.traza_v.z >= 0 and recta.traza_h.y >= 0:
                                if recta.cuadrante_punto_1 == "II":
                                    self.dibujar_discontinuo(qp, (recta.traza_v, recta.punto_1))
                                else:
                                    self.dibujar_discontinuo(qp, (recta.traza_v, recta.punto_2))

                                if recta.cuadrante_punto_1 == "IV":
                                    self.dibujar_discontinuo(qp, (recta.traza_h, recta.punto_1))
                                else:
                                    self.dibujar_discontinuo(qp, (recta.traza_h, recta.punto_2))

                                self.dibujar_continuo(qp, (recta.traza_v, recta.traza_h))
                    self.recta_prima3(qp, recta.puntos)

                self.dibujar_trazas_recta(qp, recta)

    def dibujar_continuo(self, qp, extremos):
        qp.setPen(self.pen_recta_prima_continuo)
        self.recta_prima(qp, extremos)
        qp.setPen(self.pen_recta_prima2_continuo)
        self.recta_prima2(qp, extremos)

    def dibujar_discontinuo(self, qp, extremos):
        qp.setPen(self.pen_recta_prima)
        self.recta_prima(qp, extremos)
        qp.setPen(self.pen_recta_prima2)
        self.recta_prima2(qp, extremos)

    @staticmethod
    def recta_prima(qp, extremos):
        x0 = extremos[0].x
        x = extremos[1].x
        y0 = -extremos[0].y
        y = -extremos[1].y
        if not (round(x0, 1) == round(x, 1) and round(y0, 1) == round(y, 1)):
            qp.drawLine(QPointF(x0, y0), QPointF(x, y))

    @staticmethod
    def recta_prima2(qp, extremos):
        x0 = extremos[0].x
        x = extremos[1].x
        y0 = extremos[0].z
        y = extremos[1].z
        if not (round(x0, 1) == round(x, 1) and round(y0, 1) == round(y, 1)):
            qp.drawLine(QPointF(x0, y0), QPointF(x, y))

    def recta_prima3(self, qp, extremos):
        # Tercera proyección
        if self.programa.tercera_proyeccion.checkState():
            if self.programa.modo_oscuro:
                self.pen_prima3.setColor(QColor(200, 200, 200))
            else:
                self.pen_prima3.setColor(QColor(0, 0, 0))
            qp.setPen(self.pen_prima3)
            x0 = -extremos[0].y
            x = -extremos[1].y
            y0 = extremos[0].z
            y = extremos[1].z
            if not (round(x0, 1) == round(x, 1) and round(y0, 1) == round(y, 1)):
                qp.drawLine(QPointF(x0, y0), QPointF(x, y))

    def dibujar_trazas_recta(self, qp, recta):
        qp.setPen(self.pen_trazas)
        if recta.infinita.isChecked():
            if recta.traza_h != "Contenida en PH" and recta.traza_h and recta.ver_traza_horizontal.isChecked():
                qp.drawPoint(round(recta.traza_h.x), round(-recta.traza_h.y))  # H "
                qp.drawPoint(round(recta.traza_h.x), 0)  # H '
            if recta.traza_v != "Contenida en PV" and recta.traza_v and recta.ver_traza_vertical.isChecked():
                qp.drawPoint(round(recta.traza_v.x), round(recta.traza_v.z))  # V '
                qp.drawPoint(round(recta.traza_v.x), 0)  # V "
        else:
            if recta.traza_v_entre_puntos and recta.traza_v:
                qp.drawPoint(round(recta.traza_v.x), round(recta.traza_v.z))  # H '
                qp.drawPoint(round(recta.traza_v.x), 0)  # H "
            if recta.traza_h_entre_puntos and recta.traza_h:
                qp.drawPoint(round(recta.traza_h.x), round(-recta.traza_h.y))  # H "
                qp.drawPoint(round(recta.traza_h.x), 0)  # H '

    def dibujar_planos(self, qp):
        for i in range(self.programa.lista_planos.count()):
            plano = self.programa.lista_planos.itemWidget(self.programa.lista_planos.item(i))
            if plano.render.isChecked() and plano.infinito.isChecked():
                if plano.ver_traza_horizontal.isChecked():
                    qp.setPen(self.pen_plano_prima)
                    if len(plano.traza_h) == 2:
                        self.recta_prima(qp, plano.traza_h)
                    else:
                        self.recta_prima(qp, (plano.traza_h[0], plano.traza_h[1]))
                        if plano.ver_trazas_negativas.isChecked():
                            qp.setPen(self.pen_plano_prima_discontinuo)
                            self.recta_prima(qp, (plano.traza_h[1], plano.traza_h[2]))

                if plano.ver_traza_vertical.isChecked():
                    qp.setPen(self.pen_plano_prima2)
                    if len(plano.traza_v) == 2:
                        self.recta_prima2(qp, plano.traza_v)
                    else:
                        self.recta_prima2(qp, (plano.traza_v[0], plano.traza_v[1]))
                        if plano.ver_trazas_negativas.isChecked():
                            qp.setPen(self.pen_plano_prima2_discontinuo)
                            self.recta_prima2(qp, (plano.traza_v[1], plano.traza_v[2]))

    def dibujar_circunferencias(self, qp):
        for i in range(self.programa.lista_circunferencias.count()):
            circ = self.programa.lista_circunferencias.itemWidget(self.programa.lista_circunferencias.item(i))
            if circ.render.isChecked():
                segmentos = circ.puntos
                # Cambia el color del trazo en modo oscuro
                if self.programa.tercera_proyeccion.checkState():
                    if self.programa.modo_oscuro:
                        self.pen_prima3.setColor(QColor(200, 200, 200))
                    else:
                        self.pen_prima3.setColor(QColor(0, 0, 0))

                for j in range(len(segmentos)):
                    segmento = segmentos[j-1], segmentos[j]
                    if segmento[0].y >= 0 and segmento[0].z >= 0 and segmento[1].y >= 0 and segmento[1].z >= 0:
                        qp.setPen(self.pen_recta_prima_continuo)
                        self.recta_prima(qp, segmento)
                        qp.setPen(self.pen_recta_prima2_continuo)
                        self.recta_prima2(qp, segmento)
                    else:
                        qp.setPen(self.pen_recta_prima)
                        self.recta_prima(qp, segmento)
                        qp.setPen(self.pen_recta_prima2)
                        self.recta_prima2(qp, segmento)

                    self.recta_prima3(qp, segmento)

    def dibujar_poligonos(self, qp):
        for i in range(self.programa.lista_poligonos.count()):
            poligono = self.programa.lista_poligonos.itemWidget(self.programa.lista_poligonos.item(i))
            if poligono.render.isChecked():
                segmentos = poligono.puntos

                # Cambia el color del trazo en modo oscuro
                if self.programa.tercera_proyeccion.checkState():
                    if self.programa.modo_oscuro:
                        self.pen_prima3.setColor(QColor(200, 200, 200))
                    else:
                        self.pen_prima3.setColor(QColor(0, 0, 0))

                for j in range(len(segmentos)):
                    segmento = segmentos[j - 1], segmentos[j]
                    if segmento[0].y >= 0 and segmento[0].z >= 0 and segmento[1].y >= 0 and segmento[1].z >= 0:
                        qp.setPen(self.pen_recta_prima_continuo)
                        self.recta_prima(qp, segmento)
                        qp.setPen(self.pen_recta_prima2_continuo)
                        self.recta_prima2(qp, segmento)
                    else:
                        qp.setPen(self.pen_recta_prima)
                        self.recta_prima(qp, segmento)
                        qp.setPen(self.pen_recta_prima2)
                        self.recta_prima2(qp, segmento)

                    self.recta_prima3(qp, segmento)