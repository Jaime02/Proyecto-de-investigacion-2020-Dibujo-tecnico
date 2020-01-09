# -*- coding: utf-8 -*-

from itertools import cycle
from math import sin, cos, radians, atan2

from OpenGL.GL import glClear, GL_COLOR_BUFFER_BIT, glEnable, glMatrixMode, GL_PROJECTION, glLoadIdentity, glOrtho, \
    glClearColor, GL_DEPTH_BUFFER_BIT, GL_MODELVIEW, glLineWidth, glBegin, glColor, glVertex, glEnd, glPointSize, \
    GL_POINT_SMOOTH, GL_POINTS, GL_BLEND, glBlendFunc, GL_SRC_ALPHA, GL_QUADS, GL_LINES, GL_LINE_LOOP, \
    GL_ONE_MINUS_SRC_ALPHA, GL_TRIANGLE_FAN, glLoadMatrixf
from OpenGL.GLU import gluLookAt
from PyQt5.QtCore import Qt, pyqtSlot, QSize, QPoint
from PyQt5.QtGui import QPainter, QPen, QCursor, QTransform, QFont, QColor
from PyQt5.QtWidgets import QOpenGLWidget, QWidget, QCheckBox, QPushButton, QHBoxLayout, QMainWindow, QLabel, QMenu, \
    QApplication, QVBoxLayout, QSpinBox, QPlainTextEdit, QComboBox, QMessageBox, QGraphicsScene, QGraphicsView, \
    QListWidgetItem, QListWidget, QAction, QColorDialog, QDockWidget, QFrame
from sympy import Line, intersection, Point3D, Plane, Line3D, Segment3D


class EntidadGeometrica(QWidget):
    def __init__(self, internal_id: int, nombre: QLabel):
        QWidget.__init__(self)
        self.id = internal_id
        self.customContextMenuRequested.connect(self.context_menu)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.menu = QMenu()
        self.borrar = QAction("Borrar")
        self.render = QAction("Ver")
        self.render.setCheckable(True)
        self.render.setChecked(True)
        self.menu.addAction(self.borrar)
        self.menu.addAction(self.render)

        hbox = QHBoxLayout()
        hbox.addWidget(nombre)
        self.setLayout(hbox)

        self.editar_color = QAction("Color")
        self.menu.addAction(self.editar_color)
        self.editar_color.triggered.connect(self.cambiar_color)

        # Por defecto tienen color negro
        self.color = (0, 0, 0, 1)

        # Vértices del cubo
        self.vertices = (Point3D(500, 500, 500), Point3D(-500, 500, 500), Point3D(-500, -500, 500),
                         Point3D(500, -500, 500), Point3D(500, 500, -500), Point3D(-500, 500, -500),
                         Point3D(-500, -500, -500), Point3D(500, -500, -500))

        # Aristas del cubo
        self.aristas = (Segment3D(self.vertices[0], self.vertices[1]), Segment3D(self.vertices[1], self.vertices[2]),
                        Segment3D(self.vertices[2], self.vertices[3]), Segment3D(self.vertices[3], self.vertices[0]),
                        Segment3D(self.vertices[0], self.vertices[4]), Segment3D(self.vertices[1], self.vertices[5]),
                        Segment3D(self.vertices[2], self.vertices[6]), Segment3D(self.vertices[3], self.vertices[7]),
                        Segment3D(self.vertices[4], self.vertices[5]), Segment3D(self.vertices[5], self.vertices[6]),
                        Segment3D(self.vertices[6], self.vertices[7]), Segment3D(self.vertices[7], self.vertices[4]))

        # Caras del cubo
        self.planos = (Plane(self.vertices[0], self.vertices[1], self.vertices[2]),
                       Plane(self.vertices[0], self.vertices[1], self.vertices[5]),
                       Plane(self.vertices[0], self.vertices[4], self.vertices[7]),
                       Plane(self.vertices[4], self.vertices[5], self.vertices[7]),
                       Plane(self.vertices[2], self.vertices[3], self.vertices[7]),
                       Plane(self.vertices[1], self.vertices[2], self.vertices[5]))

        self.plano_vertical = Plane(Point3D(0, 0, 1), Point3D(0, 0, 0), Point3D(1, 0, 0))
        self.plano_horizontal = Plane(Point3D(0, 1, 0), Point3D(0, 0, 0), Point3D(1, 0, 0))

        self.plano_vertical_bordes = (Segment3D(Point3D(500, 0, 500), Point3D(-500, 0, 500)),
                                      Segment3D(Point3D(-500, 0, 500), Point3D(-500, 0, -500)),
                                      Segment3D(Point3D(-500, 0, -500), Point3D(500, 0, -500)),
                                      Segment3D(Point3D(500, 0, -500), Point3D(500, 0, 500)))

        self.plano_horizontal_bordes = (Segment3D(Point3D(500, 500, 0), Point3D(-500, 500, 0)),
                                        Segment3D(Point3D(-500, 500, 0), Point3D(-500, -500, 0)),
                                        Segment3D(Point3D(-500, -500, 0), Point3D(500, -500, 0)),
                                        Segment3D(Point3D(500, -500, 0), Point3D(500, 500, 0)))

    def cambiar_color(self):
        color_dialog = QColorDialog()
        color = color_dialog.getColor(options=QColorDialog.ShowAlphaChannel)
        if color.isValid():
            color = color.getRgb()
            self.color = tuple([i / 255 for i in color])

    def context_menu(self):
        self.menu.exec(QCursor.pos())


class Punto(EntidadGeometrica):
    def __init__(self,
                 internal_id: int,
                 nombre: str,
                 distancia_origen: int,
                 alejamiento: int,
                 cota: int,
                 interseccion):

        if interseccion is None:
            EntidadGeometrica.__init__(self, internal_id,
                                       QLabel(f"{nombre}({distancia_origen}, {alejamiento}, {cota})"))
        else:
            EntidadGeometrica.__init__(self, internal_id, QLabel(f"{nombre}({interseccion})"))
        self.borrar.triggered.connect(lambda: programa.borrar_punto(self.id))
        self.x = distancia_origen
        self.y = alejamiento
        self.z = cota
        self.nombre = nombre
        self.coords = (distancia_origen, alejamiento, cota)
        self.sympy = Point3D(self.coords)
        self.cuadrante = self.calcular_cuadrante()
        self.contenido_en_plano = False

    def calcular_cuadrante(self):
        coords = self.coords
        if coords[1] >= 0 and coords[2] >= 0:
            return "I"
        elif coords[1] < 0 and coords[2] >= 0:
            return "II"
        elif coords[1] >= 0 and coords[2] < 0:
            return "IV"
        else:
            return "III"


class Recta(EntidadGeometrica):
    def __init__(self,
                 internal_id: int,
                 nombre: str,
                 entidad_1: EntidadGeometrica,
                 entidad_2: EntidadGeometrica,
                 modo=None,
                 nombre_recta=None):

        if entidad_2 is None:
            # Proviene de intersecciones
            EntidadGeometrica.__init__(self, internal_id, QLabel(nombre))
            self.sympy = entidad_1

        elif isinstance(entidad_1, Punto) and isinstance(entidad_2, Punto):
            EntidadGeometrica.__init__(self, internal_id, QLabel(f"{nombre}({entidad_1.nombre}, {entidad_2.nombre})"))
            self.sympy = Line(Point3D(entidad_1.coords), Point3D(entidad_2.coords))
            self.p1 = entidad_1
            self.p2 = entidad_2

        elif isinstance(entidad_1, Line3D) and isinstance(entidad_2, Plano):
            self.sympy = entidad_1
            EntidadGeometrica.__init__(self, internal_id, QLabel(f"{nombre}⊥{entidad_2.nombre}"))
            # No se pueden crear rectas paralelas a planos que pasen por un punto debido a limitaciones técnicas

        elif isinstance(entidad_1, Punto) and isinstance(entidad_2, Line3D):
            self.sympy = entidad_2
            if modo == "Perpendicular":
                EntidadGeometrica.__init__(self, internal_id, QLabel(f"{nombre}⊥{nombre_recta}"))
            else:
                EntidadGeometrica.__init__(self, internal_id, QLabel(f"{nombre}║{nombre_recta}"))

        self.nombre = nombre
        self.contenida_pv = False
        self.contenida_ph = False

        self.borrar.triggered.connect(lambda: programa.borrar_recta(self.id))

        self.ver_traza_horizontal = QAction("Traza en PH")
        self.ver_traza_horizontal.setCheckable(True)
        self.ver_traza_horizontal.setChecked(True)
        self.menu.addAction(self.ver_traza_horizontal)
        self.ver_traza_vertical = QAction("Traza en PV")
        self.ver_traza_vertical.setCheckable(True)
        self.ver_traza_vertical.setChecked(True)
        self.menu.addAction(self.ver_traza_vertical)

        self.infinita = QAction("Infinita")
        self.menu.addAction(self.infinita)
        self.infinita.setCheckable(True)
        self.infinita.setChecked(True)

        # Solo se pueden utilizar segmentos cuando la recta ha sido definida por dos puntos, podría ser mejorado
        if isinstance(entidad_1, Punto) and isinstance(entidad_2, Punto):
            self.traza_v_entre_puntos = False
            self.traza_h_entre_puntos = False
            self.trazas_entre_puntos()

            if self.traza_h_entre_puntos and self.traza_v_entre_puntos:
                if self.traza_h_entre_puntos == "PH+" and self.traza_v_entre_puntos == "PV+":
                    self.segmento_entre_trazas = "I"
                if self.traza_h_entre_puntos == "PH-" and self.traza_v_entre_puntos == "PV+":
                    self.segmento_entre_trazas = "II"
                if self.traza_h_entre_puntos == "PH-" and self.traza_v_entre_puntos == "PV-":
                    self.segmento_entre_trazas = "III"
                if self.traza_h_entre_puntos == "PH+" and self.traza_v_entre_puntos == "PV-":
                    self.segmento_entre_trazas = "IV"
        else:
            self.infinita.setDisabled(True)

        self.extremos = self.extremos(self.sympy)
        # Extremos de la recta separados por cuadrantes
        self.extremos_I = tuple([i for i in self.extremos if i[1] >= 0 and i[2] >= 0])
        self.extremos_II = tuple([i for i in self.extremos if (i[1] < 0 and i[2] > 0) or (i[1] < 0 and i[2] == 0)])
        self.extremos_III = tuple([i for i in self.extremos if i[1] < 0 and i[2] < 0])
        self.extremos_IV = tuple([i for i in self.extremos if (i[1] > 0 and i[2] < 0) or (i[1] == 0 and i[2] < 0)])

        self.traza_v = self.calcular_traza_v()
        self.traza_h = self.calcular_traza_h()

        # Si la recta no tiene trazas, se desactivan estas opciones
        if not self.traza_v:
            self.ver_traza_vertical.setChecked(False)
            self.ver_traza_vertical.setCheckable(False)
            self.ver_traza_vertical.setDisabled(True)

        if not self.traza_h:
            self.ver_traza_horizontal.setChecked(False)
            self.ver_traza_horizontal.setCheckable(False)
            self.ver_traza_horizontal.setDisabled(True)

        self.partes = self.calcular_partes()

    def extremos(self, recta: Line3D):
        intersecciones = []
        for i in range(6):
            interseccion = intersection(recta, self.planos[i])
            if interseccion:
                interseccion = interseccion[0]
                if all(abs(i) <= 500 for i in interseccion.coordinates):
                    intersecciones.append(interseccion.coordinates)
        return tuple(set(intersecciones))

    def calcular_traza_h(self):
        traza_h = intersection(self.sympy, self.plano_horizontal)
        if traza_h:
            if not isinstance(traza_h[0], Line3D):
                traza_h = tuple(traza_h[0])
                if all(abs(i) <= 500 for i in traza_h):
                    return traza_h
        else:
            return False

    def calcular_traza_v(self):
        traza_v = intersection(self.sympy, self.plano_vertical)
        if traza_v:
            if not isinstance(traza_v[0], Line3D):
                traza_v = tuple(traza_v[0])
                if all(abs(i) <= 500 for i in traza_v):
                    return traza_v
        else:
            return False

    def trazas_entre_puntos(self):
        segmento = Segment3D(Point3D(self.p1.coords), Point3D(self.p2.coords))
        interseccion_pv = intersection(segmento, self.plano_vertical)
        interseccion_ph = intersection(segmento, self.plano_horizontal)
        if interseccion_pv:
            if not isinstance(interseccion_pv[0], Line3D):
                if interseccion_pv[0].z > 0:
                    self.traza_v_entre_puntos = "PV+"
                else:
                    self.traza_v_entre_puntos = "PV-"
        if interseccion_ph:
            if not isinstance(interseccion_ph[0], Line3D):
                if interseccion_ph[0].y > 0:
                    self.traza_h_entre_puntos = "PH+"
                else:
                    self.traza_h_entre_puntos = "PH-"

    def calcular_partes(self):
        extremos_I = self.extremos_I
        extremos_II = self.extremos_II
        extremos_III = self.extremos_III
        extremos_IV = self.extremos_IV

        traza_v = self.traza_v
        traza_h = self.traza_h

        partes = {}

        if len(extremos_I) == 2:
            # La recta no sale del primer cuadrante, puede estar en LT o contenida en los planos de proyección
            partes['I'] = extremos_I
        elif len(extremos_II) == 2:
            partes['II'] = extremos_II
        elif len(extremos_III) == 2:
            partes['III'] = extremos_III
        elif len(extremos_IV) == 2:
            partes['IV'] = extremos_IV
        elif not traza_h and traza_v:
            if traza_v[2] >= 0:
                partes['I'] = traza_v, extremos_I[0]
                partes['II'] = traza_v, extremos_II[0]
            else:
                partes['III'] = traza_v, extremos_III[0]
                partes['IV'] = traza_v, extremos_IV[0]
        elif not traza_v and traza_h:
            if traza_h[1] >= 0:
                partes['I'] = traza_h, extremos_I[0]
                partes['IV'] = traza_h, extremos_IV[0]
            else:
                partes['II'] = traza_h, extremos_II[0]
                partes['III'] = traza_h, extremos_III[0]
        else:
            # Traza V y H
            # LT:
            if traza_v == traza_h:
                if extremos_I or extremos_III:
                    partes['I'] = traza_h, extremos_I[0]
                    partes['III'] = traza_h, extremos_III[0]
                else:
                    partes['II'] = traza_h, extremos_II[0]
                    partes['IV'] = traza_h, extremos_IV[0]
            elif traza_v[2] > 0 and traza_h[1] > 0:
                partes['I'] = traza_v, traza_h
                partes['II'] = traza_h, extremos_II[0]
                partes['IV'] = traza_h, extremos_IV[0]
            elif traza_v[2] < 0 and traza_h[1] < 0:
                partes['II'] = extremos_II[0], traza_h
                partes['III'] = traza_h, traza_v
                partes['IV'] = traza_v, extremos_IV[0]
            elif traza_v[2] > 0 and traza_h[1] < 0:
                partes['I'] = extremos_I[0], traza_v
                partes['II'] = traza_v, traza_h
                partes['III'] = traza_h, extremos_III[0]
            else:
                partes['I'] = extremos_I[0], traza_h
                partes['IV'] = traza_h, traza_v
                partes['III'] = traza_v, extremos_III[0]
        return partes


class Plano(EntidadGeometrica):
    def __init__(self,
                 internal_id: int,
                 nombre: str,
                 entidad_1,
                 entidad_2,
                 entidad_3,
                 modo):

        infinito = True
        if isinstance(entidad_1, Punto) and isinstance(entidad_2, Punto) and isinstance(entidad_3, Punto):
            EntidadGeometrica.__init__(self, internal_id,
                                       QLabel(f"{nombre}({entidad_1.nombre}, {entidad_2.nombre}, {entidad_3.nombre})"))
            self.sympy = Plane(Point3D(entidad_1.coords), Point3D(entidad_2.coords), Point3D(entidad_3.coords))

            self.p1 = entidad_1
            self.p2 = entidad_2
            self.p3 = entidad_3

        elif isinstance(entidad_1, Plane) and isinstance(entidad_2, Plano):
            if modo == "Perpendicular":
                EntidadGeometrica.__init__(self, internal_id, QLabel(f"{nombre}⊥{entidad_2.nombre}"))
            else:
                EntidadGeometrica.__init__(self, internal_id, QLabel(f"{nombre}║{entidad_2.nombre}"))
            self.sympy = entidad_1
            infinito = False

        self.vector_normal = self.sympy.normal_vector
        self.nombre = nombre

        self.infinito = QAction("Infinito")
        self.infinito.setCheckable(True)
        self.infinito.setChecked(True)

        if not infinito:
            self.infinito.setDisabled(True)

        self.menu.addAction(self.infinito)

        self.puntos = self.limites()

        self.borrar.triggered.connect(lambda: programa.borrar_plano(self.id))

        # Color por defecto del plano, azul
        self.color = (0, 0, 200, 0.4)
        self.editar_color = QAction("Color")
        self.menu.addAction(self.editar_color)
        self.editar_color.triggered.connect(self.cambiar_color)

        self.ver_traza_horizontal = QAction("Traza en PH")
        self.ver_traza_horizontal.setCheckable(True)
        self.ver_traza_horizontal.setChecked(True)
        self.menu.addAction(self.ver_traza_horizontal)
        self.ver_traza_vertical = QAction("Traza en PV")
        self.ver_traza_vertical.setCheckable(True)
        self.ver_traza_vertical.setChecked(True)
        self.menu.addAction(self.ver_traza_vertical)

        self.traza_v = self.calcular_traza_v()
        self.traza_h = self.calcular_traza_h()

        # Si el plano no tiene trazas, se desactivan estas opciones
        if not self.traza_v:
            self.ver_traza_vertical.setChecked(False)
            self.ver_traza_vertical.setCheckable(False)
            self.ver_traza_vertical.setDisabled(True)

        if not self.traza_h:
            self.ver_traza_horizontal.setChecked(False)
            self.ver_traza_horizontal.setCheckable(False)
            self.ver_traza_horizontal.setDisabled(True)

        self.partes = self.calcular_partes()

        if self.traza_h and self.traza_v:
            self.punto_en_LT = intersection(self.sympy, Segment3D(Point3D(500, 0, 0), Point3D(-500, 0, 0)))[0]
            if self.traza_h[0][1] < self.traza_h[1][1]:
                self.traza_h[0], self.traza_h[1] = self.traza_h[1], self.traza_h[0]
            if self.traza_v[0][2] < self.traza_v[1][2]:
                self.traza_v[0], self.traza_v[1] = self.traza_v[1], self.traza_v[0]
            self.traza_h.insert(1, self.punto_en_LT)
            self.traza_v.insert(1, self.punto_en_LT)

            self.ver_trazas_negativas = QAction("Ver trazas negativas")
            self.ver_trazas_negativas.setCheckable(True)
            self.ver_trazas_negativas.setChecked(True)
            self.menu.addAction(self.ver_trazas_negativas)

    def ordenar_vertices(self, vertices: list):
        # Si es un triángulo no hace falta ordenar su vértices
        if len(vertices) <= 3:
            return tuple(vertices)
        else:
            vector = self.vector_normal
            proyectados = []
            # Proyectar en:
            # Perfil
            if vector[1] == vector[2] == 0:
                for i in vertices:
                    punto = (i[1], i[2])
                    proyectados.append(punto)
            # Vertical
            elif vector[2] == 0:
                for i in vertices:
                    punto = (i[0], i[2])
                    proyectados.append(punto)
            # Horizontal
            else:
                for i in vertices:
                    punto = (i[0], i[1])
                    proyectados.append(punto)

            centroide = self.centroide(proyectados)

            for index, punto in enumerate(proyectados):
                punto = (punto[0] - centroide[0], punto[1] - centroide[1])
                proyectados[index] = punto

            angulos = []
            for i in proyectados:
                angulos.append(atan2(i[0], i[1]))
            juntados = sorted(zip(angulos, vertices))
            ordenados = [i[1] for i in juntados]

            return tuple(ordenados)

    @staticmethod
    def centroide(puntos):
        x = 0
        y = 0
        for punto in puntos:
            x += punto[0]
            y += punto[1]
        return x / len(puntos), y / len(puntos)

    def limites(self):
        plano = self.sympy
        buenos = []

        for i in range(12):
            inter = intersection(plano, self.aristas[i])
            if inter:
                if not isinstance(inter[0], Segment3D):
                    buenos.append((int(inter[0][0]), int(inter[0][1]), int(inter[0][2])))

        for i in range(8):
            inter = intersection(plano, self.vertices[i])
            if inter:
                buenos.append((int(inter[0][0]), int(inter[0][1]), int(inter[0][2])))

        # Elimina duplicados
        buenos = list(set(buenos))
        return self.ordenar_vertices(buenos)

    def calcular_partes(self):
        puntos = list(self.puntos)
        partes = {'I': [], 'II': [], 'III': [], 'IV': []}
        plano = self.sympy
        for segmento in self.plano_vertical_bordes:
            interseccion = intersection(plano, segmento)
            if interseccion:
                if isinstance(interseccion[0], Segment3D):
                    puntos.append(segmento.points[0].coordinates)
                    puntos.append(segmento.points[1].coordinates)
                else:
                    puntos.append(interseccion[0].coordinates)
        for segmento in self.plano_horizontal_bordes:
            interseccion = intersection(plano, segmento)
            if interseccion:
                if isinstance(interseccion[0], Segment3D):
                    puntos.append(segmento.points[0].coordinates)
                    puntos.append(segmento.points[1].coordinates)
                else:
                    puntos.append(interseccion[0].coordinates)
        interseccion = intersection(Segment3D(Point3D(500, 0, 0), Point3D(-500, 0, 0)), plano)
        if interseccion:
            if isinstance(interseccion[0], Segment3D):
                puntos.append((500, 0, 0))
                puntos.append((-500, 0, 0))
            else:
                puntos.append(interseccion[0].coordinates)
        for punto in puntos:
            if punto[1] >= 0 and punto[2] >= 0:
                partes['I'].append(punto)
            if punto[1] <= 0 and punto[2] >= 0:
                partes['II'].append(punto)
            if punto[1] <= 0 and punto[2] <= 0:
                partes['III'].append(punto)
            if punto[1] >= 0 and punto[2] <= 0:
                partes['IV'].append(punto)

        # partes = dict((k, list(map(self.ordenar_vertices, v))) for k, v in partes.items())
        partes['I'] = self.ordenar_vertices(partes['I'])
        partes['II'] = self.ordenar_vertices(partes['II'])
        partes['III'] = self.ordenar_vertices(partes['III'])
        partes['IV'] = self.ordenar_vertices(partes['IV'])

        return partes

    def calcular_traza_h(self):
        if self.vector_normal[0] == 0 and self.vector_normal[1] == 0:
            return False
        else:
            trazas = []
            for i in range(4):
                if not len(trazas) == 2:
                    interseccion = intersection(self.sympy, self.plano_horizontal_bordes[i])
                    if interseccion and not isinstance(interseccion[0], Segment3D):
                        trazas.append(interseccion[0].coordinates)
            trazas = list(set(trazas))
            if len(trazas) == 1:
                return False
            else:
                return trazas

    def calcular_traza_v(self):
        if self.vector_normal[0] == 0 and self.vector_normal[2] == 0:
            return False
        else:
            trazas = []
            for i in range(4):
                if not len(trazas) == 2:
                    interseccion = intersection(self.sympy, self.plano_vertical_bordes[i])
                    if interseccion and not isinstance(interseccion[0], Segment3D):
                        trazas.append(interseccion[0].coordinates)
            trazas = list(set(trazas))
            if len(trazas) == 1:
                return False
            else:
                return trazas


class Renderizador(QOpenGLWidget):
    phi: int  # Ángulo horizontal
    theta: int  # Ángulo vertical

    def __init__(self):
        QOpenGLWidget.__init__(self)
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

        self.lastPos = QPoint()

        self.m = [[1, 0, 0, 0],
                  [0, 0, 1, 0],
                  [0, 1, 0, 0],
                  [0, 0, 0, 1]]

    def sizeHint(self):
        return QSize(800, 800)

    def resizeEvent(self, event):
        if self.width() > self.height():
            self.resize(self.height(), self.height())
        elif self.height() > self.width():
            self.resize(self.width(), self.width())
        QOpenGLWidget.resizeEvent(self, event)

    def mousePressEvent(self, event):
        self.lastPos = event.pos()

    def mouseMoveEvent(self, event):
        self.update()
        dx = event.x() - self.lastPos.x()
        dy = event.y() - self.lastPos.y()

        if event.buttons() and Qt.LeftButton:
            self.theta += dy
            self.phi -= dx

        self.lastPos = event.pos()

        self.recalcular_posicion()

        programa.actualizar_texto()

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
        programa.actualizar_texto()
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
        if programa.ajustes.ver_plano_vertical.isChecked():
            glBegin(GL_QUADS)
            glColor(programa.ajustes.color_plano_vertical)
            for vertex in range(4):
                glVertex(self.vertices_plano_vertical_arriba[vertex])
            glEnd()

    def plano_vertical_debajo(self):
        if programa.ajustes.ver_plano_vertical.isChecked():
            glBegin(GL_QUADS)
            glColor(programa.ajustes.color_plano_vertical)
            for vertex in range(4):
                glVertex(self.vertices_plano_vertical_debajo[vertex])
            glEnd()

    def plano_horizontal_delante(self):
        if programa.ajustes.ver_plano_horizontal.isChecked():
            glBegin(GL_QUADS)
            glColor(programa.ajustes.color_plano_horizontal)
            for vertex in range(4):
                glVertex(self.vertices_plano_horizontal_delante[vertex])
            glEnd()

    def plano_horizontal_detras(self):
        if programa.ajustes.ver_plano_horizontal.isChecked():
            glBegin(GL_QUADS)
            glColor(programa.ajustes.color_plano_horizontal)
            for vertex in range(4):
                glVertex(self.vertices_plano_horizontal_detras[vertex])
            glEnd()

    def bordes_plano_vertical(self):
        if programa.ajustes.ver_plano_vertical.isChecked():
            glLineWidth(1)
            glColor(programa.ajustes.color_plano_vertical)
            glBegin(GL_LINE_LOOP)
            for vertex in range(4):
                glVertex(self.vertices_borde_plano_vertical[vertex])
            glEnd()

    def bordes_plano_horizontal(self):
        if programa.ajustes.ver_plano_horizontal.isChecked():
            glLineWidth(1)
            glColor(programa.ajustes.color_plano_horizontal)
            glBegin(GL_LINE_LOOP)
            for vertex in range(4):
                glVertex(self.vertices_borde_plano_horizontal[vertex])
            glEnd()

    @staticmethod
    def dibujar_ejes():
        if programa.ajustes.ver_ejes.isChecked():
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

    @staticmethod
    def dibujar_puntos(cuadrante: str):
        for i in range(programa.lista_puntos.count()):
            punto = programa.lista_puntos.itemWidget(programa.lista_puntos.item(i))
            if punto.render.isChecked() and punto.cuadrante == cuadrante:
                glColor(punto.color)
                glPointSize(5)
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

        for i in range(programa.lista_rectas.count()):
            recta = programa.lista_rectas.itemWidget(programa.lista_rectas.item(i))
            if recta.render.isChecked():
                glColor(recta.color)
                glLineWidth(2)
                if recta.infinita.isChecked():
                    if "I" in recta.partes and cuadrante == "I":
                        glBegin(GL_LINES)
                        glVertex(recta.partes["I"][0])
                        glVertex(recta.partes["I"][1])
                        glEnd()
                    if "II" in recta.partes and cuadrante == "II":
                        glBegin(GL_LINES)
                        glVertex(recta.partes["II"][0])
                        glVertex(recta.partes["II"][1])
                        glEnd()
                    elif "III" in recta.partes and cuadrante == "III":
                        glBegin(GL_LINES)
                        glVertex(recta.partes["III"][0])
                        glVertex(recta.partes["III"][1])
                        glEnd()
                    elif "IV" in recta.partes and cuadrante == "IV":
                        glBegin(GL_LINES)
                        glVertex(recta.partes["IV"][0])
                        glVertex(recta.partes["IV"][1])
                        glEnd()
                    self.traza_v_recta(recta)
                    self.traza_h_recta(recta)
                else:
                    if recta.p1.cuadrante == recta.p2.cuadrante == cuadrante == "I":
                        dibujar(recta.p1.coords, recta.p2.coords)
                    elif recta.p1.cuadrante == recta.p2.cuadrante == cuadrante == "II":
                        dibujar(recta.p1.coords, recta.p2.coords)
                    elif recta.p1.cuadrante == recta.p2.cuadrante == cuadrante == "III":
                        dibujar(recta.p1.coords, recta.p2.coords)
                    elif recta.p1.cuadrante == recta.p2.cuadrante == cuadrante == "IV":
                        dibujar(recta.p1.coords, recta.p2.coords)
                    else:
                        if recta.traza_v_entre_puntos and recta.traza_h_entre_puntos:
                            # LT
                            if recta.traza_v == recta.traza_h:
                                if cuadrante == recta.p1.cuadrante:
                                    dibujar(recta.p1.coords, recta.traza_v)
                                if cuadrante == recta.p2.cuadrante:
                                    dibujar(recta.p2.coords, recta.traza_v)
                                self.traza_h_recta(recta)
                            if recta.segmento_entre_trazas == cuadrante:
                                dibujar(recta.traza_v, recta.traza_h)

                        if recta.p1.cuadrante == cuadrante:
                            if recta.traza_h_entre_puntos == "PH+" and (cuadrante == "I" or cuadrante == "IV"):
                                dibujar(recta.p1.coords, recta.traza_h)
                                self.traza_h_recta(recta)
                            if recta.traza_h_entre_puntos == "PH-" and (cuadrante == "II" or cuadrante == "III"):
                                dibujar(recta.p1.coords, recta.traza_h)
                                self.traza_h_recta(recta)

                            if recta.traza_v_entre_puntos == "PV+" and (cuadrante == "I" or cuadrante == "II"):
                                dibujar(recta.p1.coords, recta.traza_v)
                                self.traza_v_recta(recta)
                            if recta.traza_v_entre_puntos == "PV-" and (cuadrante == "III" or cuadrante == "IV"):
                                dibujar(recta.p1.coords, recta.traza_v)
                                self.traza_v_recta(recta)
                        if recta.p2.cuadrante == cuadrante:
                            if recta.traza_h_entre_puntos == "PH+" and (cuadrante == "I" or cuadrante == "IV"):
                                dibujar(recta.p2.coords, recta.traza_h)
                                self.traza_h_recta(recta)
                            if recta.traza_h_entre_puntos == "PH-" and (cuadrante == "II" or cuadrante == "III"):
                                dibujar(recta.p2.coords, recta.traza_h)
                                self.traza_h_recta(recta)

                            if recta.traza_v_entre_puntos == "PV+" and (cuadrante == "I" or cuadrante == "II"):
                                dibujar(recta.p2.coords, recta.traza_v)
                                self.traza_v_recta(recta)
                            if recta.traza_v_entre_puntos == "PV-" and (cuadrante == "III" or cuadrante == "IV"):
                                dibujar(recta.p2.coords, recta.traza_v)
                                self.traza_v_recta(recta)

    @staticmethod
    def traza_v_recta(recta):
        if programa.ajustes.ver_rectas_trazas_verticales.isChecked():
            if recta.traza_v and recta.ver_traza_vertical.isChecked():
                if recta.traza_v[0] < 500 and recta.traza_v[1] < 500:
                    glColor(0, 1, 0, 1)
                    glBegin(GL_POINTS)
                    glVertex(recta.traza_v)
                    glEnd()
                    glColor(recta.color)

    @staticmethod
    def traza_h_recta(recta):
        if programa.ajustes.ver_rectas_trazas_horizontales.isChecked():
            if recta.traza_h and recta.ver_traza_horizontal.isChecked():
                if recta.traza_h[0] < 500 and recta.traza_h[2] < 500:
                    glColor(1, 0, 0, 1)
                    glBegin(GL_POINTS)
                    glVertex(recta.traza_h)
                    glEnd()
                    glColor(recta.color)

    @staticmethod
    def dibujar_planos(cuadrante: str):
        for i in range(programa.lista_planos.count()):
            plano = programa.lista_planos.itemWidget(programa.lista_planos.item(i))
            if plano.render.isChecked():
                glBegin(GL_TRIANGLE_FAN)
                glColor(plano.color)
                if plano.infinito.isChecked():
                    puntos = plano.partes[cuadrante]
                    for j in puntos:
                        glVertex(j)
                    glEnd()
                    glBegin(GL_LINE_LOOP)
                    for j in plano.puntos:
                        glVertex(j)
                    glEnd()
                else:
                    glVertex(plano.p1.coords)
                    glVertex(plano.p2.coords)
                    glVertex(plano.p3.coords)
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
        glClearColor(1, 1, 1, 0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadMatrixf(self.m)

        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        self.dibujar_elementos()
        self.update()

    def dibujar_entidades(self, cuadrante: str):
        if programa.ajustes.ver_puntos.isChecked():
            self.dibujar_puntos(cuadrante)
        if programa.ajustes.ver_rectas.isChecked():
            self.dibujar_rectas(cuadrante)
        if programa.ajustes.ver_planos.isChecked():
            self.dibujar_planos(cuadrante)

    def dibujar_elementos(self):
        self.bordes_plano_horizontal()
        self.bordes_plano_vertical()

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

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_W:
            self.theta -= 1
        elif event.key() == Qt.Key_A:
            self.phi -= 1
        elif event.key() == Qt.Key_S:
            self.theta += 1
        elif event.key() == Qt.Key_D:
            self.phi += 1
        elif event.key() == Qt.Key_Q:
            self.desviacion_z += 1
        elif event.key() == Qt.Key_E:
            self.desviacion_z -= 1
        elif event.key() == Qt.Key_Left:
            self.desviacion_x += 1
        elif event.key() == Qt.Key_Up:
            self.desviacion_y += 1
        elif event.key() == Qt.Key_Right:
            self.desviacion_x -= 1
        elif event.key() == Qt.Key_Down:
            self.desviacion_y -= 1
        elif event.key() == Qt.Key_1:
            self.ver_alzado()
        elif event.key() == Qt.Key_2:
            self.ver_planta()
        elif event.key() == Qt.Key_3:
            self.ver_perfil()
        elif event.key() == Qt.Key_R:
            self.ver_reset()
        elif event.key() == Qt.Key_Minus:
            self.zoom += 10
        elif event.key() == Qt.Key_Plus:
            self.zoom -= 10

        self.recalcular_posicion()

        self.update()
        QOpenGLWidget.keyPressEvent(self, event)


class Diedrico(QWidget):
    def __init__(self):
        QWidget.__init__(self)

        negro = QColor(0, 0, 0)
        rojo = QColor(255, 103, 69)
        verde = QColor(0, 255, 0)
        azul = QColor(50, 100, 255)
        azul_oscuro = QColor(10, 50, 140)

        self.pen_base = QPen(negro)
        self.pen_base.setWidth(1)

        self.pen_punto_prima = QPen(QColor(201, 10, 0), 3)
        self.pen_punto_prima2 = QPen(QColor(8, 207, 41), 3)

        self.pen_recta_prima = QPen(rojo, 3, Qt.DotLine)
        self.pen_recta_prima.setDashPattern([1, 3])
        self.pen_recta_prima2 = QPen(verde, 3, Qt.DotLine)
        self.pen_recta_prima2.setDashPattern([1, 3])

        self.pen_recta_prima_continuo = QPen(rojo, 3)
        self.pen_recta_prima2_continuo = QPen(verde, 3)
        self.pen_trazas = QPen(Qt.black, 3)

        self.pen_prima3 = QPen(Qt.black, 3)

        self.pen_plano_prima = QPen(azul, 4)
        self.pen_plano_prima2 = QPen(azul_oscuro, 4)

        self.pen_plano_prima_discontinuo = QPen(azul, 4)
        self.pen_plano_prima_discontinuo.setDashPattern([1, 3])
        self.pen_plano_prima2_discontinuo = QPen(azul_oscuro, 4)
        self.pen_plano_prima2_discontinuo.setDashPattern([1, 3])

    def paintEvent(self, event):
        qp = QPainter(self)
        qp.setRenderHint(QPainter.Antialiasing)
        self.elementos_estaticos(qp)
        qp.translate(500, 500)
        qp.scale(-1, -1)
        if programa.ver_planos.checkState():
            self.dibujar_planos(qp)
        if programa.ver_rectas.checkState():
            self.dibujar_rectas(qp)
        if programa.ver_puntos.checkState():
            self.dibujar_puntos(qp)
        self.update()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Plus:
            self.zoom_in()
        if event.key() == Qt.Key_Minus:
            self.zoom_out()
        if event.key() == Qt.Key_R:
            # Reset
            programa.vista.setTransform(QTransform())

    @staticmethod
    def zoom_in():
        scale_tr = QTransform()
        scale_tr.scale(1.2, 1.2)
        transformacion = programa.vista.transform() * scale_tr
        programa.vista.setTransform(transformacion)

    @staticmethod
    def zoom_out():
        scale_tr = QTransform()
        scale_tr.scale(1.2, 1.2)
        scale_inverted = scale_tr.inverted()[0]
        transformacion = programa.vista.transform() * scale_inverted
        programa.vista.setTransform(transformacion)

    def elementos_estaticos(self, qp):
        qp.setPen(self.pen_base)
        qp.drawRect(0, 0, 1000, 1000)  # Marco
        qp.drawLine(5, 500, 995, 500)  # LT
        qp.drawLine(5, 505, 15, 505)  # Raya pequeña izquierda
        qp.drawLine(985, 505, 995, 505)  # Raya pequeña derecha
        qp.drawLine(500, 5, 500, 995)  # Raya plano perfil

    def dibujar_puntos(self, qp):
        for i in range(programa.lista_puntos.count()):
            punto = programa.lista_puntos.itemWidget(programa.lista_puntos.item(i))
            if punto.render.isChecked():
                self.punto_prima(qp, punto)
                self.punto_prima2(qp, punto)
                if programa.tercera_proyeccion.checkState():
                    self.punto_prima3(qp, punto)

    def punto_prima(self, qp, punto):
        qp.setPen(self.pen_punto_prima)
        qp.drawPoint(punto.x, -punto.y)

    def punto_prima2(self, qp, punto):
        qp.setPen(self.pen_punto_prima2)
        qp.drawPoint(punto.x, punto.z)

    def punto_prima3(self, qp, punto):
        qp.setPen(self.pen_prima3)
        qp.drawPoint(-punto.y, punto.z)

    def dibujar_rectas(self, qp):
        for i in range(programa.lista_rectas.count()):
            recta = programa.lista_rectas.itemWidget(programa.lista_rectas.item(i))
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
                else:
                    if recta.p1.cuadrante == recta.p2.cuadrante == "I":
                        self.dibujar_continuo(qp, (recta.p1.coords, recta.p2.coords))
                    elif recta.p1.cuadrante != "I" and recta.p2.cuadrante != "I":
                        self.dibujar_discontinuo(qp, (recta.p1.coords, recta.p2.coords))
                    else:
                        if recta.p1.cuadrante == "I":
                            if recta.traza_v:
                                if recta.traza_v[2] >= 0:
                                    self.dibujar_discontinuo(qp, (recta.traza_v, recta.p2.coords))
                                    self.dibujar_continuo(qp, (recta.p1.coords, recta.traza_v))
                            if recta.traza_h:
                                if recta.traza_h[1] >= 0:
                                    self.dibujar_discontinuo(qp, (recta.traza_h, recta.p2.coords))
                                    self.dibujar_continuo(qp, (recta.p1.coords, recta.traza_h))
                        elif recta.p2.cuadrante == "I":
                            if recta.traza_v:
                                if recta.traza_v[2] >= 0:
                                    self.dibujar_discontinuo(qp, (recta.traza_v, recta.p1.coords))
                                    self.dibujar_continuo(qp, (recta.p2.coords, recta.traza_v))
                            if recta.traza_h:
                                if recta.traza_h[1] >= 0:
                                    self.dibujar_discontinuo(qp, (recta.traza_h, recta.p1.coords))
                                    self.dibujar_continuo(qp, (recta.p2.coords, recta.traza_h))
                        if recta.traza_v and recta.traza_h:
                            if recta.traza_v[2] >= 0 and recta.traza_h[1] >= 0:

                                if recta.p1.cuadrante == "II":
                                    self.dibujar_discontinuo(qp, (recta.traza_v, recta.p1.coords))
                                else:
                                    self.dibujar_discontinuo(qp, (recta.traza_v, recta.p2.coords))

                                if recta.p1.cuadrante == "IV":
                                    self.dibujar_discontinuo(qp, (recta.traza_h, recta.p1.coords))
                                else:
                                    self.dibujar_discontinuo(qp, (recta.traza_h, recta.p2.coords))

                                self.dibujar_continuo(qp, (recta.traza_v, recta.traza_h))

                # Tercera proyección
                if programa.tercera_proyeccion.checkState():
                    qp.setPen(self.pen_prima3)
                    self.recta_prima3(qp, recta.extremos)

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
        x0 = int(extremos[0][0])
        x = int(extremos[1][0])
        y0 = int(-extremos[0][1])
        y = int(-extremos[1][1])
        if not (x0 == x and y0 == y):
            qp.drawLine(x0, y0, x, y)

    @staticmethod
    def recta_prima2(qp, extremos):
        x0 = int(extremos[0][0])
        x = int(extremos[1][0])
        y0 = int(extremos[0][2])
        y = int(extremos[1][2])
        if not (x0 == x and y0 == y):
            qp.drawLine(x0, y0, x, y)

    @staticmethod
    def recta_prima3(qp, extremos):
        x0 = int(-extremos[0][1])
        x = int(-extremos[1][1])
        y0 = int(extremos[0][2])
        y = int(extremos[1][2])
        qp.drawLine(x0, y0, x, y)

    def dibujar_trazas_recta(self, qp, recta):
        qp.setPen(self.pen_trazas)
        if recta.infinita.isChecked():
            if recta.traza_h and recta.ver_traza_horizontal.isChecked():
                qp.drawPoint(int(recta.traza_h[0]), int(-recta.traza_h[1]))  # V "
                qp.drawPoint(int(recta.traza_h[0]), 0)  # V '
            if recta.traza_v and recta.ver_traza_vertical.isChecked():
                qp.drawPoint(int(recta.traza_v[0]), int(recta.traza_v[2]))  # H '
                qp.drawPoint(int(recta.traza_v[0]), 0)  # H "

    def dibujar_planos(self, qp):
        for i in range(programa.lista_planos.count()):
            plano = programa.lista_planos.itemWidget(programa.lista_planos.item(i))
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


class Ajustes(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.setFixedSize(420, 180)

        self.color_plano_vertical = (0.1, 1, 0.1, 0.5)
        self.color_plano_horizontal = (1, 0.1, 0.1, 0.5)

        fuente = QFont()
        fuente.setPointSize(12)
        widget_central = QWidget(self)

        ajustes = QLabel(widget_central)
        ajustes.setGeometry(10, 10, 40, 16)
        ajustes.setText("Ajustes:")

        puntos = QLabel(widget_central)
        puntos.setText("Puntos:")
        puntos.setGeometry(10, 90, 37, 16)
        rectas = QLabel(widget_central)
        rectas.setText("Rectas")
        rectas.setGeometry(140, 10, 41, 16)
        planos = QLabel(widget_central)
        planos.setText("Planos")
        planos.setGeometry(280, 10, 35, 16)

        self.ver_plano_horizontal = QCheckBox(widget_central)
        self.ver_plano_horizontal.setText("Ver plano horizontal")
        self.ver_plano_horizontal.setChecked(True)
        self.ver_plano_horizontal.setGeometry(10, 70, 118, 17)

        self.ver_plano_vertical = QCheckBox(widget_central)
        self.ver_plano_vertical.setText("Ver plano vertical")
        self.ver_plano_vertical.setChecked(True)
        self.ver_plano_vertical.setGeometry(10, 50, 106, 17)

        self.ver_ejes = QCheckBox(widget_central)
        self.ver_ejes.setText("Ver ejes")
        self.ver_ejes.setChecked(True)
        self.ver_ejes.setGeometry(10, 30, 62, 17)

        self.ver_puntos = QCheckBox(widget_central)
        self.ver_puntos.setText("Ver puntos")
        self.ver_puntos.setChecked(True)
        self.ver_puntos.setGeometry(10, 110, 75, 17)

        self.ver_rectas = QCheckBox(widget_central)
        self.ver_rectas.setText("Ver rectas")
        self.ver_rectas.setChecked(True)
        self.ver_rectas.setGeometry(140, 30, 133, 17)

        self.ver_planos = QCheckBox(widget_central)
        self.ver_planos.setText("Ver planos")
        self.ver_planos.setChecked(True)
        self.ver_planos.setGeometry(280, 30, 73, 17)

        self.ver_rectas_trazas_verticales = QCheckBox(widget_central)
        self.ver_rectas_trazas_verticales.setChecked(True)
        self.ver_rectas_trazas_verticales.setText("Ver trazas verticales")
        self.ver_rectas_trazas_verticales.setGeometry(140, 70, 121, 17)

        self.ver_rectas_trazas_horizontales = QCheckBox(widget_central)
        self.ver_rectas_trazas_horizontales.setChecked(True)
        self.ver_rectas_trazas_horizontales.setGeometry(140, 50, 129, 17)
        self.ver_rectas_trazas_horizontales.setText("Ver trazas horizontales")

        self.ver_planos_trazas_verticales = QCheckBox(widget_central)
        self.ver_planos_trazas_verticales.setChecked(True)
        self.ver_planos_trazas_verticales.setGeometry(280, 70, 121, 17)
        self.ver_planos_trazas_verticales.setText("Ver trazas verticales")
        self.ver_planos_trazas_horizontales = QCheckBox(widget_central)
        self.ver_planos_trazas_horizontales.setChecked(True)
        self.ver_planos_trazas_horizontales.setText("Ver trazas horizontales")
        self.ver_planos_trazas_horizontales.setGeometry(280, 50, 129, 17)

        boton_color_vertical = QPushButton(widget_central)
        boton_color_vertical.setGeometry(10, 130, 101, 41)
        boton_color_vertical.setText("Cambiar el color del\n plano vertical")
        boton_color_vertical.clicked.connect(self.cambiar_color_plano_vertical)
        reset_vertical = QPushButton(widget_central)
        reset_vertical.setGeometry(120, 130, 75, 41)
        reset_vertical.setText("Reestablecer")
        reset_vertical.clicked.connect(self.reset_color_vertical)

        boton_color_horizontal = QPushButton(widget_central)
        boton_color_horizontal.setGeometry(200, 130, 101, 41)
        boton_color_horizontal.setText("Cambiar el color del\n plano horizontal")
        boton_color_horizontal.clicked.connect(self.cambiar_color_plano_horizontal)
        reset_horizontal = QPushButton(widget_central)
        reset_horizontal.setGeometry(310, 130, 75, 41)
        reset_horizontal.setText("Reestablecer")

        self.setWindowTitle("Ajustes")
        self.setCentralWidget(widget_central)

    def reset_color_vertical(self):
        self.color_plano_vertical = (0.1, 1, 0.1, 0.5)

    def reset_color_horizontal(self):
        self.color_plano_horizontal = (1, 0.1, 0.1, 0.5)

    def cambiar_color_plano_vertical(self):
        color_dialog = QColorDialog()
        color = color_dialog.getColor(options=QColorDialog.ShowAlphaChannel)
        if color.isValid():
            color = color.getRgb()
            self.color_plano_vertical = tuple([i / 255 for i in color])

    def cambiar_color_plano_horizontal(self):
        color_dialog = QColorDialog()
        color = color_dialog.getColor(options=QColorDialog.ShowAlphaChannel)
        if color.isValid():
            color = color.getRgb()
            self.color_plano_horizontal = tuple([i / 255 for i in color])


class VentanaBase(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setFixedSize(140, 140)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        font = QFont()
        font.setPointSize(10)
        self.setFont(font)
        self.widget_central = QWidget(self)
        self.setCentralWidget(self.widget_central)

        self.etiqueta_1 = QLabel(self.widget_central)
        self.etiqueta_1.setGeometry(10, 10, 130, 16)

        self.etiqueta_2 = QLabel(self.widget_central)
        self.etiqueta_2.setGeometry(10, 60, 130, 16)

        self.boton_crear = QPushButton(self.widget_central)
        self.boton_crear.setGeometry(10, 110, 61, 23)
        self.boton_crear.setText("Crear")

        self.boton_cerrar = QPushButton(self.widget_central)
        self.boton_cerrar.setGeometry(70, 110, 61, 23)
        self.boton_cerrar.setText("Cancelar")
        self.boton_cerrar.clicked.connect(self.cerrar)

        self.elegir_entidad_1 = QComboBox(self.widget_central)
        self.elegir_entidad_1.setGeometry(10, 30, 121, 21)

        self.elegir_entidad_2 = QComboBox(self.widget_central)
        self.elegir_entidad_2.setGeometry(10, 80, 121, 21)

    @pyqtSlot()
    def cerrar(self):
        self.close()


class VentanaBaseConNombre(VentanaBase):
    def __init__(self):
        VentanaBase.__init__(self)
        self.setFixedSize(140, 190)
        self.etiqueta_nombre = QLabel(self.widget_central)
        self.etiqueta_nombre.setGeometry(10, 110, 51, 20)
        self.etiqueta_nombre.setText("Nombre:")

        self.boton_crear.setGeometry(10, 160, 61, 23)
        self.boton_cerrar.setGeometry(70, 160, 61, 23)

        self.nombre = QPlainTextEdit(self.widget_central)
        self.nombre.setGeometry(10, 130, 121, 28)


class RectaPerpendicularAPlano(VentanaBaseConNombre):
    def __init__(self):
        VentanaBaseConNombre.__init__(self)

        self.etiqueta_1.setText("Punto:")
        self.etiqueta_2.setText("Plano:")

        self.boton_crear.clicked.connect(self.crear_recta)

    def abrir(self):
        self.elegir_entidad_1.clear()
        self.elegir_entidad_2.clear()
        for i in range(programa.lista_puntos.count()):
            self.elegir_entidad_1.addItem(programa.lista_puntos.itemWidget(programa.lista_puntos.item(i)).nombre)

        for i in range(programa.lista_planos.count()):
            self.elegir_entidad_2.addItem(programa.lista_planos.itemWidget(programa.lista_planos.item(i)).nombre)
        self.show()

    def crear_recta(self):
        punto = self.elegir_entidad_1.currentText()
        plano = self.elegir_entidad_2.currentText()
        nombre = programa.asignar_nombre_recta(self.nombre.toPlainText())

        for i in range(programa.lista_puntos.count()):
            if programa.lista_puntos.itemWidget(programa.lista_puntos.item(i)).nombre == punto:
                punto = programa.lista_puntos.itemWidget(programa.lista_puntos.item(i))

        for i in range(programa.lista_planos.count()):
            if programa.lista_planos.itemWidget(programa.lista_planos.item(i)).nombre == plano:
                plano = programa.lista_planos.itemWidget(programa.lista_planos.item(i))

        if punto == "" or plano == "":
            QMessageBox.critical(self, "Error al crear la recta",
                                 "Debes crear al menos un plano y un punto para crear una recta")
        else:
            recta = plano.sympy.perpendicular_line(punto.sympy)
            programa.crear_recta(nombre, recta, plano, modo="Perpendicular")
            self.cerrar()


class PlanoPerpendicularAPlano(VentanaBaseConNombre):
    def __init__(self):
        VentanaBaseConNombre.__init__(self)
        self.setFixedSize(140, 230)

        self.etiqueta_1.setText("Punto:")
        self.etiqueta_2.setText("Plano:")
        self.etiqueta_2.setGeometry(10, 110, 41, 16)
        self.etiqueta_3 = QLabel(self.widget_central)
        self.etiqueta_3.setGeometry(10, 60, 41, 16)
        self.etiqueta_3.setText("Punto:")

        self.elegir_entidad_3 = QComboBox(self.widget_central)
        self.elegir_entidad_3.setGeometry(10, 130, 121, 21)

        self.nombre.setGeometry(10, 170, 121, 28)
        self.etiqueta_nombre.setGeometry(10, 150, 51, 20)

        self.boton_crear.setGeometry(10, 200, 61, 23)
        self.boton_cerrar.setGeometry(70, 200, 61, 23)

        self.boton_crear.clicked.connect(self.crear_plano)

    def abrir(self):
        self.elegir_entidad_1.clear()
        self.elegir_entidad_2.clear()
        self.elegir_entidad_3.clear()
        for i in range(programa.lista_puntos.count()):
            self.elegir_entidad_1.addItem(programa.lista_puntos.itemWidget(programa.lista_puntos.item(i)).nombre)
            self.elegir_entidad_2.addItem(programa.lista_puntos.itemWidget(programa.lista_puntos.item(i)).nombre)
        for i in range(programa.lista_planos.count()):
            self.elegir_entidad_3.addItem(programa.lista_planos.itemWidget(programa.lista_planos.item(i)).nombre)
        self.show()

    def crear_plano(self):
        punto = self.elegir_entidad_1.currentText()
        punto2 = self.elegir_entidad_2.currentText()
        plano = self.elegir_entidad_3.currentText()
        nombre = programa.asignar_nombre_plano(self.nombre.toPlainText())

        for i in range(programa.lista_puntos.count()):
            if programa.lista_puntos.itemWidget(programa.lista_puntos.item(i)).nombre == punto:
                punto = programa.lista_puntos.itemWidget(programa.lista_puntos.item(i))
            if programa.lista_puntos.itemWidget(programa.lista_puntos.item(i)).nombre == punto2:
                punto2 = programa.lista_puntos.itemWidget(programa.lista_puntos.item(i))

        for i in range(programa.lista_planos.count()):
            if programa.lista_planos.itemWidget(programa.lista_planos.item(i)).nombre == plano:
                plano = programa.lista_planos.itemWidget(programa.lista_planos.item(i))

        if punto == "" or plano == "":
            QMessageBox.critical(self, "Error al crear el plano",
                                 "Debes crear al menos un plano y un punto para crear un plano perpendicular a este")
        elif punto.sympy == punto2.sympy:
            QMessageBox.critical(self, "Error al crear el plano", "Los puntos son coincidentes")
        else:
            plano_perpendicular = plano.sympy.perpendicular_plane(punto.sympy, punto2.sympy)
            programa.crear_plano(nombre, plano_perpendicular, plano, modo="Perpendicular")
            self.cerrar()


class PlanoParaleloAPlano(VentanaBaseConNombre):
    def __init__(self):
        VentanaBaseConNombre.__init__(self)

        self.etiqueta_1.setText("Punto:")
        self.etiqueta_2.setText("Plano:")

        self.boton_crear.clicked.connect(self.crear_plano)

    def abrir(self):
        self.elegir_entidad_1.clear()
        self.elegir_entidad_2.clear()
        for i in range(programa.lista_puntos.count()):
            self.elegir_entidad_1.addItem(programa.lista_puntos.itemWidget(programa.lista_puntos.item(i)).nombre)
        for i in range(programa.lista_planos.count()):
            self.elegir_entidad_2.addItem(programa.lista_planos.itemWidget(programa.lista_planos.item(i)).nombre)
        self.show()

    def crear_plano(self):
        punto = self.elegir_entidad_1.currentText()
        plano = self.elegir_entidad_2.currentText()
        nombre = programa.asignar_nombre_plano(self.nombre.toPlainText())

        for i in range(programa.lista_puntos.count()):
            if programa.lista_puntos.itemWidget(programa.lista_puntos.item(i)).nombre == punto:
                punto = programa.lista_puntos.itemWidget(programa.lista_puntos.item(i))

        for i in range(programa.lista_planos.count()):
            if programa.lista_planos.itemWidget(programa.lista_planos.item(i)).nombre == plano:
                plano = programa.lista_planos.itemWidget(programa.lista_planos.item(i))

        if punto == "" or plano == "":
            QMessageBox.critical(self, "Error al crear el plano",
                                 "Debes crear al menos un plano y un punto para crear un plano paralelo a este")
        else:
            plano_paralelo = plano.sympy.parallel_plane(punto.sympy)
            programa.crear_plano(nombre, plano_paralelo, plano, modo="Paralelo")
            self.cerrar()


class RectaPerpendicularARecta(VentanaBaseConNombre):
    def __init__(self):
        VentanaBaseConNombre.__init__(self)
        self.etiqueta_1.setText("Punto:")
        self.etiqueta_2.setText("Recta:")

        self.boton_crear.clicked.connect(self.crear_recta)

    def abrir(self):
        self.elegir_entidad_1.clear()
        self.elegir_entidad_2.clear()
        for i in range(programa.lista_puntos.count()):
            self.elegir_entidad_1.addItem(programa.lista_puntos.itemWidget(programa.lista_puntos.item(i)).nombre)
        for i in range(programa.lista_rectas.count()):
            self.elegir_entidad_2.addItem(programa.lista_rectas.itemWidget(programa.lista_rectas.item(i)).nombre)
        self.show()

    def crear_recta(self):
        punto = self.elegir_entidad_1.currentText()
        recta = self.elegir_entidad_2.currentText()
        nombre = programa.asignar_nombre_recta(self.nombre.toPlainText())

        for i in range(programa.lista_puntos.count()):
            if programa.lista_puntos.itemWidget(programa.lista_puntos.item(i)).nombre == punto:
                punto = programa.lista_puntos.itemWidget(programa.lista_puntos.item(i))

        for i in range(programa.lista_rectas.count()):
            if programa.lista_rectas.itemWidget(programa.lista_rectas.item(i)).nombre == recta:
                recta = programa.lista_rectas.itemWidget(programa.lista_rectas.item(i))
        if punto == "" or recta == "":
            QMessageBox.critical(self, "Error al crear la recta",
                                 "Debes crear al menos una recta y un punto para crear una recta")
        else:
            recta_perpendicular = recta.sympy.perpendicular_line(punto.sympy)
            programa.crear_recta(nombre, punto, recta_perpendicular, modo="Perpendicular", nombre_recta=recta.nombre)
            self.cerrar()


class RectaParalelaARecta(VentanaBaseConNombre):
    def __init__(self):
        VentanaBaseConNombre.__init__(self)

        self.etiqueta_1.setText("Punto:")
        self.etiqueta_2.setText("Recta:")

        self.boton_crear.clicked.connect(self.crear_recta)

    def abrir(self):
        self.elegir_entidad_1.clear()
        self.elegir_entidad_2.clear()
        for i in range(programa.lista_puntos.count()):
            self.elegir_entidad_1.addItem(programa.lista_puntos.itemWidget(programa.lista_puntos.item(i)).nombre)

        for i in range(programa.lista_rectas.count()):
            self.elegir_entidad_2.addItem(programa.lista_rectas.itemWidget(programa.lista_rectas.item(i)).nombre)
        self.show()

    def crear_recta(self):
        punto = self.elegir_entidad_1.currentText()
        recta = self.elegir_entidad_2.currentText()
        nombre = programa.asignar_nombre_recta(self.nombre.toPlainText())
        for i in range(programa.lista_puntos.count()):
            if programa.lista_puntos.itemWidget(programa.lista_puntos.item(i)).nombre == punto:
                punto = programa.lista_puntos.itemWidget(programa.lista_puntos.item(i))

        for i in range(programa.lista_rectas.count()):
            if programa.lista_rectas.itemWidget(programa.lista_rectas.item(i)).nombre == recta:
                recta = programa.lista_rectas.itemWidget(programa.lista_rectas.item(i))

        if punto == "" or recta == "":
            QMessageBox.critical(self, "Error al crear la recta",
                                 "Debes crear al menos una recta y un punto para crear una recta")
        else:
            recta_paralela = recta.sympy.parallel_line(punto.sympy)
            programa.crear_recta(nombre, punto, recta_paralela, modo="Paralela", nombre_recta=recta.nombre)
            self.cerrar()


class Distancia(VentanaBase):
    def __init__(self):
        VentanaBase.__init__(self)

        self.etiqueta_1.setText("Entidad geométrica 1:")
        self.etiqueta_2.setText("Entidad geométrica 2:")

        self.boton_crear.clicked.connect(self.calcular_distancia)

    def abrir(self):
        self.elegir_entidad_1.clear()
        self.elegir_entidad_2.clear()

        for i in range(programa.lista_puntos.count()):
            self.elegir_entidad_1.addItem(programa.lista_puntos.itemWidget(programa.lista_puntos.item(i)).nombre)
            self.elegir_entidad_2.addItem(programa.lista_puntos.itemWidget(programa.lista_puntos.item(i)).nombre)

        for i in range(programa.lista_planos.count()):
            self.elegir_entidad_1.addItem(programa.lista_planos.itemWidget(programa.lista_planos.item(i)).nombre)
            self.elegir_entidad_2.addItem(programa.lista_planos.itemWidget(programa.lista_planos.item(i)).nombre)

        for i in range(programa.lista_rectas.count()):
            self.elegir_entidad_1.addItem(programa.lista_rectas.itemWidget(programa.lista_rectas.item(i)).nombre)
            self.elegir_entidad_2.addItem(programa.lista_rectas.itemWidget(programa.lista_rectas.item(i)).nombre)

        self.show()

    def calcular_distancia(self):
        entidad_1 = self.elegir_entidad_1.currentText()
        entidad_2 = self.elegir_entidad_2.currentText()

        for i in range(programa.lista_puntos.count()):
            if programa.lista_puntos.itemWidget(programa.lista_puntos.item(i)).nombre == entidad_1:
                entidad_1 = programa.lista_puntos.itemWidget(programa.lista_puntos.item(i))
            if programa.lista_puntos.itemWidget(programa.lista_puntos.item(i)).nombre == entidad_2:
                entidad_2 = programa.lista_puntos.itemWidget(programa.lista_puntos.item(i))

        for i in range(programa.lista_rectas.count()):
            if programa.lista_rectas.itemWidget(programa.lista_rectas.item(i)).nombre == entidad_1:
                entidad_1 = programa.lista_rectas.itemWidget(programa.lista_rectas.item(i))
            if programa.lista_rectas.itemWidget(programa.lista_rectas.item(i)).nombre == entidad_2:
                entidad_2 = programa.lista_rectas.itemWidget(programa.lista_rectas.item(i))

        for i in range(programa.lista_planos.count()):
            if programa.lista_planos.itemWidget(programa.lista_planos.item(i)).nombre == entidad_1:
                entidad_1 = programa.lista_planos.itemWidget(programa.lista_planos.item(i))
            if programa.lista_planos.itemWidget(programa.lista_planos.item(i)).nombre == entidad_2:
                entidad_2 = programa.lista_planos.itemWidget(programa.lista_planos.item(i))

        if entidad_1 == "" or entidad_2 == "":
            QMessageBox.critical(self, "Error al calcular la distancia",
                                 "Debes crear almenos dos elementos para calcular su distancia")
        elif entidad_1 == entidad_2:
            QMessageBox.critical(self, "Error al calcular la distancia",
                                 "Los elementos seleccionados son el mismo")
        else:
            distancia = round(entidad_1.sympy.distance(entidad_2.sympy), 2)
            QMessageBox.about(self, "Resultado",
                              f"La distancia entre estos dos elementos es de {distancia} mm")


class Interseccion(VentanaBase):
    def __init__(self):
        VentanaBase.__init__(self)

        self.etiqueta_1.setText("Entidad geométrica 1:")
        self.etiqueta_2.setText("Entidad geométrica 2:")

        self.boton_crear.clicked.connect(self.calcular_interseccion)

    def abrir(self):
        self.elegir_entidad_1.clear()
        self.elegir_entidad_2.clear()

        for i in range(programa.lista_planos.count()):
            self.elegir_entidad_1.addItem(programa.lista_planos.itemWidget(programa.lista_planos.item(i)).nombre)
            self.elegir_entidad_2.addItem(programa.lista_planos.itemWidget(programa.lista_planos.item(i)).nombre)

        for i in range(programa.lista_rectas.count()):
            self.elegir_entidad_1.addItem(programa.lista_rectas.itemWidget(programa.lista_rectas.item(i)).nombre)
            self.elegir_entidad_2.addItem(programa.lista_rectas.itemWidget(programa.lista_rectas.item(i)).nombre)

        self.show()

    def calcular_interseccion(self):
        entidad_1 = self.elegir_entidad_1.currentText()
        entidad_2 = self.elegir_entidad_2.currentText()

        for i in range(programa.lista_rectas.count()):
            if programa.lista_rectas.itemWidget(programa.lista_rectas.item(i)).nombre == entidad_1:
                entidad_1 = programa.lista_rectas.itemWidget(programa.lista_rectas.item(i))
            elif programa.lista_rectas.itemWidget(programa.lista_rectas.item(i)).nombre == entidad_2:
                entidad_2 = programa.lista_rectas.itemWidget(programa.lista_rectas.item(i))

        for i in range(programa.lista_planos.count()):
            if programa.lista_planos.itemWidget(programa.lista_planos.item(i)).nombre == entidad_1:
                entidad_1 = programa.lista_planos.itemWidget(programa.lista_planos.item(i))
            elif programa.lista_planos.itemWidget(programa.lista_planos.item(i)).nombre == entidad_2:
                entidad_2 = programa.lista_planos.itemWidget(programa.lista_planos.item(i))

        if entidad_1 == "" or entidad_2 == "":
            QMessageBox.critical(self, "Error al calcular la intersección",
                                 "Debes crear al dos elementos para calcular su intersección")
        elif entidad_1 == entidad_2:
            QMessageBox.critical(self, "Error al calcular la intersección",
                                 "Los elementos seleccionados son el mismo")
        else:
            interseccion = intersection(entidad_1.sympy, entidad_2.sympy)
            if interseccion:
                interseccion = interseccion[0]

            if isinstance(entidad_1, Recta) and isinstance(entidad_2, Recta):
                """
                Intersección recta-recta. Tres opciones: 
                Ambas son coincidentes -> Se crea una recta idéntica a ambas
                Secantes -> Se crea un punto de intersección
                Paralelas -> No tienen ningún punto en común
                """

                if isinstance(interseccion, Point3D):
                    if any(abs(i) > 499 for i in interseccion.coordinates):
                        QMessageBox.critical(self, "Error al calcular la intersección",
                                             "Las rectas se cortan en un punto fuera de los límites establecidos en "
                                             "el programa")
                    else:
                        texto = f"{entidad_1.nombre}∩{entidad_2.nombre}"
                        programa.crear_punto("", interseccion.x, interseccion.y, interseccion.z, interseccion=texto)
                elif isinstance(interseccion, Line3D):
                    QMessageBox.critical(self, "Error al calcular la intersección",
                                         "Las rectas son coincidentes")
                else:
                    QMessageBox.critical(self, "Error al calcular la intersección",
                                         "Las rectas son paralelas")

            elif isinstance(entidad_1, Plano) and isinstance(entidad_2, Plano):
                # lo mismo, 3 casos: Planos paralelos, secantes o coincidentes

                if isinstance(interseccion, Line3D):
                    try:
                        nombre = f"{entidad_1.nombre}∩{entidad_2.nombre}"
                        extremos = Recta.extremos(interseccion)
                        if len(extremos) < 2:
                            QMessageBox.critical(self, "Error al crear la intersección",
                                                 "La recta está fuera de los límites del programa")
                        else:
                            programa.crear_recta(nombre, interseccion)
                    except Exception:
                        QMessageBox.critical(self, "Error al crear la intersección",
                                             "Se ha producido un grave error debido a limitaciones del programa")
            else:
                if isinstance(interseccion, Point3D):
                    if any(abs(i) > 499 for i in interseccion.coordinates):
                        QMessageBox.critical(self, "Error al calcular la intersección",
                                             "Las intersección se encuentra en un punto fuera de los límites "
                                             "establecidos en el programa")
                    else:
                        texto = f"{entidad_1.nombre}∩{entidad_2.nombre}"
                        programa.crear_punto("", interseccion.x, interseccion.y, interseccion.z, interseccion=texto)
                else:
                    QMessageBox.critical(self, "Error al calcular la intersección",
                                         "La recta se encuentra en el plano")


class Ventana(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)

        # Pantalla completa
        self.showMaximized()
        widget_central = QWidget()

        self.renderizador = Renderizador()
        self.renderizador.setFocusPolicy(Qt.ClickFocus)
        dock_renderizador = QDockWidget("Renderizador")
        dock_renderizador.setWidget(self.renderizador)
        dock_renderizador.setFeatures(QDockWidget.DockWidgetMovable)
        self.addDockWidget(Qt.LeftDockWidgetArea, dock_renderizador)

        scene = QGraphicsScene()
        self.vista = QGraphicsView(scene)
        self.diedrico = Diedrico()
        self.diedrico.setFocusPolicy(Qt.ClickFocus)
        self.diedrico.setFixedSize(1000, 1000)
        scene.addWidget(self.diedrico)

        dock_diedrico = QDockWidget("Diédrico")
        dock_diedrico.setFeatures(QDockWidget.DockWidgetMovable)
        self.addDockWidget(Qt.RightDockWidgetArea, dock_diedrico)
        dock_diedrico.setWidget(self.vista)

        fuente = QFont("Arial")
        fuente.setPointSize(10)

        frame = QFrame(widget_central)
        frame.setLineWidth(3)

        informacion = QLabel(frame)
        informacion.setGeometry(0, 10, 91, 16)
        informacion.setFont(fuente)
        informacion.setText("Información:")

        posicion = QLabel(frame)
        posicion.setGeometry(0, 30, 71, 16)
        posicion.setFont(fuente)
        posicion.setText("Posición:")

        self.posicion = QLabel(frame)
        self.posicion.setGeometry(60, 30, 151, 16)
        self.posicion.setFont(fuente)
        self.posicion.setText("Primer cuadrante")

        self.angulo_vertical = QLabel(frame)
        self.angulo_vertical.setGeometry(0, 50, 121, 16)
        self.angulo_vertical.setFont(fuente)

        self.angulo_horizontal = QLabel(frame)
        self.angulo_horizontal.setGeometry(120, 50, 130, 16)
        self.angulo_horizontal.setFont(fuente)

        vista = QLabel(frame)
        vista.setGeometry(0, 70, 91, 16)
        vista.setFont(fuente)
        vista.setText("Vista:")

        crear_puntos = QLabel(frame)
        crear_puntos.setGeometry(0, 120, 91, 16)
        crear_puntos.setFont(fuente)
        crear_puntos.setText("Crear puntos:")

        nombre_punto = QLabel(frame)
        nombre_punto.setGeometry(0, 200, 91, 16)
        nombre_punto.setText("Nombre:")

        distancia_al_origen = QLabel(frame)
        distancia_al_origen.setGeometry(0, 140, 91, 16)
        distancia_al_origen.setText("Distancia al origen:")

        alejamiento = QLabel(frame)
        alejamiento.setGeometry(0, 160, 91, 16)
        alejamiento.setText("Alejamiento:")

        cota = QLabel(frame)
        cota.setGeometry(0, 180, 91, 16)
        cota.setText("Cota:")

        nombre_recta = QLabel(frame)
        nombre_recta.setGeometry(160, 180, 91, 21)
        nombre_recta.setText("Nombre:")

        crear_rectas = QLabel(frame)
        crear_rectas.setGeometry(160, 120, 91, 16)
        crear_rectas.setFont(fuente)
        crear_rectas.setText("Crear rectas:")

        punto_1_recta = QLabel(frame)
        punto_1_recta.setGeometry(160, 140, 51, 16)
        punto_1_recta.setText("Punto 1:")

        punto_2_recta = QLabel(frame)
        punto_2_recta.setGeometry(160, 160, 51, 16)
        punto_2_recta.setText("Punto 2:")

        nombre_plano = QLabel(frame)
        nombre_plano.setGeometry(320, 200, 91, 21)
        nombre_plano.setText("Nombre:")

        comprobar_planos = QLabel(frame)
        comprobar_planos.setGeometry(320, 120, 91, 16)
        comprobar_planos.setFont(fuente)
        comprobar_planos.setText("Crear planos:")

        punto_1_plano = QLabel(frame)
        punto_1_plano.setGeometry(320, 140, 51, 16)
        punto_1_plano.setText("Punto 1:")

        punto_2_plano = QLabel(frame)
        punto_2_plano.setGeometry(320, 160, 51, 16)
        punto_2_plano.setText("Punto 2:")

        punto_3_plano = QLabel(frame)
        punto_3_plano.setGeometry(320, 180, 51, 16)
        punto_3_plano.setText("Punto 3:")

        boton_reset = QPushButton(frame)
        boton_reset.setGeometry(0, 90, 81, 23)
        boton_reset.clicked.connect(self.renderizador.ver_reset)
        boton_reset.setText("Reset (R)")

        boton_alzado = QPushButton(frame)
        boton_alzado.setGeometry(90, 90, 81, 23)
        boton_alzado.clicked.connect(self.renderizador.ver_alzado)
        boton_alzado.setText("Alzado (1) ''")

        boton_planta = QPushButton(frame)
        boton_planta.setGeometry(180, 90, 81, 23)
        boton_planta.clicked.connect(self.renderizador.ver_planta)
        boton_planta.setText("Planta (2) '")

        boton_perfil = QPushButton(frame)
        boton_perfil.setGeometry(270, 90, 81, 23)
        boton_perfil.clicked.connect(self.renderizador.ver_perfil)
        boton_perfil.setText("Perfil (3) '''")

        boton_punto = QPushButton(frame)
        boton_punto.setGeometry(0, 250, 151, 21)
        boton_punto.clicked.connect(self.comprobar_punto)
        boton_punto.setText("Crear")

        boton_recta = QPushButton(frame)
        boton_recta.setGeometry(160, 229, 151, 21)
        boton_recta.clicked.connect(self.comprobar_recta)
        boton_recta.setText("Crear")

        boton_plano = QPushButton(frame)
        boton_plano.setGeometry(320, 250, 151, 21)
        boton_plano.clicked.connect(self.comprobar_plano)
        boton_plano.setText("Crear")

        self.valor_distancia_origen = QSpinBox(frame)
        self.valor_distancia_origen.setGeometry(100, 140, 51, 20)
        self.valor_distancia_origen.setRange(-499, 499)

        self.valor_alejamiento = QSpinBox(frame)
        self.valor_alejamiento.setGeometry(100, 160, 51, 20)
        self.valor_alejamiento.setRange(-499, 499)

        self.valor_cota = QSpinBox(frame)
        self.valor_cota.setGeometry(100, 180, 51, 20)
        self.valor_cota.setRange(-499, 499)

        self.punto_recta_1 = QComboBox(frame)
        self.punto_recta_1.setGeometry(220, 140, 91, 22)
        self.punto_recta_2 = QComboBox(frame)
        self.punto_recta_2.setGeometry(220, 160, 91, 21)
        self.punto_plano_1 = QComboBox(frame)
        self.punto_plano_1.setGeometry(370, 140, 91, 22)
        self.punto_plano_2 = QComboBox(frame)
        self.punto_plano_2.setGeometry(370, 160, 91, 22)
        self.punto_plano_3 = QComboBox(frame)
        self.punto_plano_3.setGeometry(370, 180, 91, 22)

        self.punto_nombre = QPlainTextEdit(frame)
        self.punto_nombre.setGeometry(0, 220, 151, 25)
        self.recta_nombre = QPlainTextEdit(frame)
        self.recta_nombre.setGeometry(160, 200, 151, 25)
        self.plano_nombre = QPlainTextEdit(frame)
        self.plano_nombre.setGeometry(320, 220, 151, 25)

        self.tercera_proyeccion = QCheckBox(dock_diedrico)
        self.tercera_proyeccion.setGeometry(58, 3, 111, 17)
        self.tercera_proyeccion.setText("Tercera proyección")

        self.ver_puntos = QCheckBox(dock_diedrico)
        self.ver_puntos.setGeometry(172, 3, 61, 17)
        self.ver_puntos.setChecked(True)
        self.ver_puntos.setText("Puntos")

        self.ver_rectas = QCheckBox(dock_diedrico)
        self.ver_rectas.setGeometry(230, 3, 61, 17)
        self.ver_rectas.setChecked(True)
        self.ver_rectas.setText("Rectas")

        self.ver_planos = QCheckBox(dock_diedrico)
        self.ver_planos.setGeometry(288, 3, 70, 17)
        self.ver_planos.setChecked(True)
        self.ver_planos.setText("Planos")

        ajustes = QPushButton(frame)
        ajustes.setGeometry(290, 550, 181, 30)
        ajustes.setText("Ajustes")
        self.ajustes = Ajustes()
        ajustes.clicked.connect(self.ajustes.show)

        widget_punto = QWidget(frame)
        widget_punto.setGeometry(0, 270, 150, 210)
        vertical_punto = QVBoxLayout(widget_punto)
        vertical_punto.setContentsMargins(0, 0, 0, 0)
        self.lista_puntos = QListWidget(widget_punto)
        vertical_punto.addWidget(self.lista_puntos)

        widget_recta = QWidget(frame)
        widget_recta.setGeometry(160, 250, 150, 230)
        vertical_recta = QVBoxLayout(widget_recta)
        vertical_recta.setContentsMargins(0, 0, 0, 0)
        self.lista_rectas = QListWidget(widget_recta)
        vertical_recta.addWidget(self.lista_rectas)

        widget_planos = QWidget(frame)
        widget_planos.setGeometry(320, 270, 151, 210)
        vertical_planos = QVBoxLayout(widget_planos)
        vertical_planos.setContentsMargins(0, 0, 0, 0)
        self.lista_planos = QListWidget(widget_planos)
        vertical_planos.addWidget(self.lista_planos)

        recta_perpendicular_plano = QPushButton(frame)
        recta_perpendicular_plano.setGeometry(160, 480, 151, 71)
        self.recta_perpendicular_plano = RectaPerpendicularAPlano()
        recta_perpendicular_plano.clicked.connect(self.recta_perpendicular_plano.abrir)
        recta_perpendicular_plano.setText("Crear recta \nperpendicular a plano")

        plano_perpendicular_plano = QPushButton(frame)
        plano_perpendicular_plano.setGeometry(320, 480, 151, 40)
        self.plano_perpendicular_plano = PlanoPerpendicularAPlano()
        plano_perpendicular_plano.clicked.connect(self.plano_perpendicular_plano.abrir)
        plano_perpendicular_plano.setText("Crear plano\nperpendicular a plano")

        plano_paralelo_plano = QPushButton(frame)
        plano_paralelo_plano.setGeometry(320, 520, 151, 30)
        self.plano_paralelo_plano = PlanoParaleloAPlano()
        plano_paralelo_plano.clicked.connect(self.plano_paralelo_plano.abrir)
        plano_paralelo_plano.setText("Crear plano paralelo a plano")

        recta_perpendicular_recta = QPushButton(frame)
        recta_perpendicular_recta.setGeometry(0, 480, 151, 40)
        self.recta_perpendicular_recta = RectaPerpendicularARecta()
        recta_perpendicular_recta.clicked.connect(self.recta_perpendicular_recta.abrir)
        recta_perpendicular_recta.setText("Crear recta \nperpendicular a recta")

        recta_paralela_recta = QPushButton(frame)
        recta_paralela_recta.setGeometry(0, 520, 151, 30)
        self.recta_paralela_recta = RectaParalelaARecta()
        recta_paralela_recta.clicked.connect(self.recta_paralela_recta.abrir)
        recta_paralela_recta.setText("Crear recta paralela a recta")

        distancia = QPushButton(frame)
        distancia.setGeometry(0, 550, 181, 30)
        self.distancia = Distancia()
        distancia.clicked.connect(self.distancia.abrir)
        distancia.setText("Calcular distancia entre elementos")

        interseccion = QPushButton(frame)
        interseccion.setGeometry(180, 550, 111, 30)
        self.interseccion = Interseccion()
        interseccion.clicked.connect(self.interseccion.abrir)
        interseccion.setText("Crear intersección")

        self.id_punto = 1
        self.id_recta = 1
        self.id_plano = 1

        self.mayusculas = cycle("PQRSTUVWXYZABCDEFGHIJKLMNO")
        self.minusculas = cycle("rstuvwxyzabcdefghijklmnopq")

        alfabeto_griego = (u'\u03B1', u'\u03B2', u'\u03B3', u'\u03B4', u'\u03B5', u'\u03B6', u'\u03B7', u'\u03B8',
                           u'\u03B9', u'\u03BA', u'\u03BB', u'\u03BC', u'\u03BD', u'\u03BE', u'\u03BF', u'\u03C0',
                           u'\u03C1', u'\u03C3', u'\u03C4', u'\u03C5', u'\u03C6', u'\u03C7', u'\u03C8', u'\u03C9')
        self.alfabeto_griego = cycle(alfabeto_griego)

        self.actualizar_texto()
        self.setWindowTitle("Dibujo técnico")
        self.setCentralWidget(frame)

    def sizeHint(self):
        return QSize(1200, 800)

    def elegir_puntos_recta(self):
        self.punto_recta_1.clear()
        self.punto_recta_2.clear()
        for i in range(self.lista_puntos.count()):
            self.punto_recta_1.addItem(self.lista_puntos.itemWidget(self.lista_puntos.item(i)).nombre)
            self.punto_recta_2.addItem(self.lista_puntos.itemWidget(self.lista_puntos.item(i)).nombre)

    def elegir_puntos_plano(self):
        self.punto_plano_1.clear()
        self.punto_plano_2.clear()
        self.punto_plano_3.clear()
        for i in range(self.lista_puntos.count()):
            self.punto_plano_1.addItem(self.lista_puntos.itemWidget(self.lista_puntos.item(i)).nombre)
            self.punto_plano_2.addItem(self.lista_puntos.itemWidget(self.lista_puntos.item(i)).nombre)
            self.punto_plano_3.addItem(self.lista_puntos.itemWidget(self.lista_puntos.item(i)).nombre)

    def actualizar_texto(self):
        self.angulo_vertical.setText("Ángulo vertical: " + str(self.renderizador.theta - 360))
        self.angulo_horizontal.setText("Ángulo horizontal: " + str(self.renderizador.phi))

        y = round(self.renderizador.y, 2)
        z = round(self.renderizador.z, 2)

        if z == 0 and y == 0:
            self.posicion.setText("Línea de tierra")
        elif z == 0:
            if y > 0:
                self.posicion.setText("Plano vertical positivo")
            else:
                self.posicion.setText("Plano vertical negativo")
        elif y == 0:
            if z > 0:
                self.posicion.setText("Plano horizontal positivo")
            else:
                self.posicion.setText("Plano horizontal negativo")
        elif z > 0:
            if y > 0:
                self.posicion.setText("Primer cuadrante")
            else:
                self.posicion.setText("Cuarto cuadrante")
        else:
            if y > 0:
                self.posicion.setText("Segundo cuadrante")
            else:
                self.posicion.setText("Tercer cuadrante")

    def asignar_nombre_punto(self, nombre):
        # Genera nombres genéricos si no se provee uno
        if nombre == "":
            nombre = self.mayusculas.__next__()
        # Evita nombres duplicados
        for i in range(self.lista_puntos.count()):
            if self.lista_puntos.itemWidget(self.lista_puntos.item(i)).nombre == nombre:
                nombre = self.minusculas.__next__()
                break
        return nombre

    def asignar_nombre_recta(self, nombre):
        # Genera nombres genéricos si no se provee uno
        if nombre == "":
            nombre = self.minusculas.__next__()
        # Evita nombres duplicados
        for i in range(self.lista_rectas.count()):
            if self.lista_rectas.itemWidget(self.lista_rectas.item(i)).nombre == nombre:
                nombre = self.minusculas.__next__()
                break
        return nombre

    def asignar_nombre_plano(self, nombre):
        # Genera nombres genéricos si no se provee uno
        if nombre == "":
            nombre = self.alfabeto_griego.__next__()
        # Evita nombres duplicados
        for i in range(self.lista_planos.count()):
            if self.lista_planos.itemWidget(self.lista_planos.item(i)).nombre == nombre:
                nombre = self.alfabeto_griego.__next__()
                break
        return nombre

    def comprobar_punto(self):
        nombre = self.punto_nombre.toPlainText()
        do = self.valor_distancia_origen.value()
        alejamiento = self.valor_alejamiento.value()
        cota = self.valor_cota.value()
        self.crear_punto(nombre, do, alejamiento, cota)

    def crear_punto(self, nombre, do, alejamiento, cota, interseccion=None):
        nombre = self.asignar_nombre_punto(nombre)
        item = QListWidgetItem()
        self.lista_puntos.addItem(item)
        punto = Punto(self.id_punto, nombre, do, alejamiento, cota, interseccion)
        item.setSizeHint(punto.minimumSizeHint())
        self.lista_puntos.setItemWidget(item, punto)
        self.id_punto += 1
        self.elegir_puntos_recta()
        self.elegir_puntos_plano()

    def comprobar_recta(self):
        punto1 = self.punto_recta_1.currentText()
        punto2 = self.punto_recta_2.currentText()
        for i in range(self.lista_puntos.count()):
            if self.lista_puntos.itemWidget(self.lista_puntos.item(i)).nombre == punto1:
                punto1 = self.lista_puntos.itemWidget(self.lista_puntos.item(i))
            if self.lista_puntos.itemWidget(self.lista_puntos.item(i)).nombre == punto2:
                punto2 = self.lista_puntos.itemWidget(self.lista_puntos.item(i))
        if not punto1 and not punto2:
            QMessageBox.critical(self, "Error al crear la recta",
                                 "Debes crear al menos dos puntos y seleccionarlos para crear la recta")
        elif punto1.coords == punto2.coords:
            QMessageBox.critical(self, "Error al crear la recta",
                                 "La recta debe ser creada a partir de dos puntos no coincidentes")
        else:
            nombre = self.asignar_nombre_recta(self.recta_nombre.toPlainText())
            self.crear_recta(nombre, punto1, punto2)

    def crear_recta(self, nombre, entidad_1=None, entidad_2=None, modo=None, nombre_recta=None):
        recta = Recta(self.id_recta, nombre, entidad_1, entidad_2, modo, nombre_recta)
        item = QListWidgetItem()
        self.lista_rectas.addItem(item)
        item.setSizeHint(recta.minimumSizeHint())
        self.lista_rectas.setItemWidget(item, recta)
        self.id_recta += 1

    def comprobar_plano(self):
        punto1 = self.punto_plano_1.currentText()
        punto2 = self.punto_plano_2.currentText()
        punto3 = self.punto_plano_3.currentText()

        for i in range(self.lista_puntos.count()):
            if self.lista_puntos.itemWidget(self.lista_puntos.item(i)).nombre == punto1:
                punto1 = self.lista_puntos.itemWidget(self.lista_puntos.item(i))
            if self.lista_puntos.itemWidget(self.lista_puntos.item(i)).nombre == punto2:
                punto2 = self.lista_puntos.itemWidget(self.lista_puntos.item(i))
            if self.lista_puntos.itemWidget(self.lista_puntos.item(i)).nombre == punto3:
                punto3 = self.lista_puntos.itemWidget(self.lista_puntos.item(i))

        if not punto1 and not punto2 and not punto3:
            QMessageBox.critical(self, "Error al crear el plano",
                                 "Debes crear al menos tres puntos y seleccionarlos para crear el plano")

        elif len({punto1.coords, punto2.coords, punto3.coords}) < 3:
            QMessageBox.critical(self, "Error al crear el plano",
                                 "Dos de los puntos proporcionados son coincidentes")
        elif Point3D.is_collinear(Point3D(punto1.coords), Point3D(punto2.coords), Point3D(punto3.coords)):
            QMessageBox.critical(self, "Error al crear el plano",
                                 "El plano debe ser creado por tres puntos no alineados")

        else:
            nombre = self.asignar_nombre_plano(self.plano_nombre.toPlainText())
            self.crear_plano(nombre, punto1, punto2, punto3)

    def crear_plano(self, nombre, entidad_1, entidad_2, entidad_3=None, modo=None):
        plano = Plano(self.id_plano, nombre, entidad_1, entidad_2, entidad_3, modo)
        item = QListWidgetItem()
        self.lista_planos.addItem(item)
        item.setSizeHint(plano.minimumSizeHint())
        self.lista_planos.setItemWidget(item, plano)
        self.id_plano += 1

    def borrar_punto(self, borrar_id):
        for indice in range(self.lista_puntos.count()):
            item = self.lista_puntos.item(indice)
            widget = self.lista_puntos.itemWidget(item)
            if widget.id == borrar_id:
                self.lista_puntos.takeItem(self.lista_puntos.row(item))
                break
        self.elegir_puntos_recta()
        self.elegir_puntos_plano()

    def borrar_recta(self, borrar_id):
        for indice in range(self.lista_rectas.count()):
            item = self.lista_rectas.item(indice)
            widget = self.lista_rectas.itemWidget(item)
            if widget.id == borrar_id:
                self.lista_rectas.takeItem(self.lista_rectas.row(item))
                break

    def borrar_plano(self, borrar_id):
        for indice in range(self.lista_planos.count()):
            item = self.lista_planos.item(indice)
            widget = self.lista_planos.itemWidget(item)
            if widget.id == borrar_id:
                self.lista_planos.takeItem(self.lista_planos.row(item))
                break


if __name__ == "__main__":
    evento_principal = QApplication([])
    programa = Ventana()

    # Zoom out para que quepa mejor
    programa.diedrico.zoom_out()
    programa.diedrico.zoom_out()

    programa.show()
    evento_principal.exec()
