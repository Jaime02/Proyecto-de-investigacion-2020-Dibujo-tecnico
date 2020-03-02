# -*- coding: utf-8 -*-

# Interfaz:
from PyQt5.QtCore import Qt, QSize, QPoint, QPointF
from PyQt5.QtGui import QPainter, QPen, QCursor, QTransform, QFont, QColor, QIcon, QPalette
from PyQt5.QtWidgets import QOpenGLWidget, QWidget, QCheckBox, QPushButton, QHBoxLayout, QMainWindow, QLabel, \
    QApplication, QVBoxLayout, QSpinBox, QPlainTextEdit, QComboBox, QMessageBox, QGraphicsScene, QGraphicsView, \
    QListWidgetItem, QListWidget, QAction, QColorDialog, QDockWidget, QMenu, QMenuBar, QFileDialog

# Herramientas:
from itertools import cycle
from math import sin, cos, radians, atan2
from pickle import dump, loads
from sys import exit
from sympy import intersection, Point3D, Plane, Line3D, Segment3D

# OpenGL:
from OpenGL.GL import glClear, GL_COLOR_BUFFER_BIT, glEnable, glMatrixMode, GL_PROJECTION, glLoadIdentity, glOrtho, \
    glClearColor, GL_DEPTH_BUFFER_BIT, GL_MODELVIEW, glLineWidth, glBegin, glColor, glVertex, glEnd, glPointSize, \
    GL_POINT_SMOOTH, GL_POINTS, GL_BLEND, glBlendFunc, GL_SRC_ALPHA, GL_QUADS, GL_LINES, GL_LINE_LOOP, \
    GL_ONE_MINUS_SRC_ALPHA, GL_TRIANGLE_FAN, glLoadMatrixf
from OpenGL.GLU import gluLookAt


class EntidadGeometrica(QWidget):
    nombre: str

    def __init__(self, internal_id: int, nombre: str):
        QWidget.__init__(self)
        self.id = internal_id
        self.customContextMenuRequested.connect(self.context_menu)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.menu = QMenu()
        self.borrar = QAction("Borrar")
        self.render = QAction("Ver")
        self.render.setCheckable(True)
        self.render.setChecked(True)
        self.actualizar_nombre = QAction("Renombrar")

        self.ventana_cambiar_nombre = VentanaRenombrar()
        self.actualizar_nombre.triggered.connect(self.ventana_cambiar_nombre.show)
        self.ventana_cambiar_nombre.boton_crear.clicked.connect(self.cambiar_nombre)

        self.menu.addAction(self.borrar)
        self.menu.addAction(self.render)
        self.menu.addAction(self.actualizar_nombre)

        hbox = QHBoxLayout()
        self.etiqueta = QLabel(nombre)
        hbox.addWidget(self.etiqueta)
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

    def cambiar_nombre(self):
        self.nombre = self.ventana_cambiar_nombre.widget_texto.toPlainText()
        self.etiqueta.setText(self.ventana_cambiar_nombre.widget_texto.toPlainText())
        programa.elegir_puntos_recta()
        programa.elegir_puntos_plano()


class VentanaRenombrar(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setFixedSize(180, 90)
        self.setWindowFlags(Qt.Tool)
        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowTitle("Renombrar")

        fuente = QFont()
        fuente.setPointSize(10)
        self.setFont(fuente)

        widget_central = QWidget(self)
        self.setCentralWidget(widget_central)

        nombre = QLabel("Nombre:", widget_central)
        nombre.setGeometry(5, 0, 50, 20)

        self.widget_texto = QPlainTextEdit(widget_central)
        self.widget_texto.setGeometry(5, 25, 170, 30)

        self.boton_crear = QPushButton("Crear", widget_central)
        self.boton_crear.setGeometry(5, 58, 85, 23)

        boton_cerrar = QPushButton("Cancelar", widget_central)
        boton_cerrar.setGeometry(90, 58, 85, 23)
        boton_cerrar.clicked.connect(self.close)


class Punto(EntidadGeometrica):
    def __init__(self, internal_id: int, nombre: str, sympy: Point3D):
        EntidadGeometrica.__init__(self, internal_id, nombre)

        self.nombre = nombre
        self.sympy = sympy
        self.coordenadas = self.sympy.coordinates
        self.x = self.sympy.x
        self.y = self.sympy.y
        self.z = self.sympy.z

        self.borrar.triggered.connect(lambda: programa.borrar_punto(self.id))
        self.cuadrante = self.calcular_cuadrante(self.coordenadas)

    @staticmethod
    def calcular_cuadrante(coordenadas) -> str:
        # Se considera que los puntos contenidos en el plano vertical positivo
        # o en el horizontal positivo pertenecen al primer cuadrante

        # Los contenidos en el PH- pertenecen al segundo cuadrante
        # Los contenidos en el PV- pertenecen al cuarto cuadrante

        if coordenadas[1] >= 0 and coordenadas[2] >= 0:
            return "I"
        elif coordenadas[1] < 0 and coordenadas[2] >= 0:
            return "II"
        elif coordenadas[1] >= 0 and coordenadas[2] < 0:
            return "IV"
        else:
            return "III"

    def guardar(self) -> dict:
        return {"Nombre": self.nombre, "Sympy": self.sympy}


class Recta(EntidadGeometrica):
    def __init__(self, internal_id: int, nombre: str, sympy: Line3D, puntos: list = None):
        EntidadGeometrica.__init__(self, internal_id, nombre)

        self.sympy = sympy
        self.nombre = nombre

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

        self.extremos = self.extremos(self.sympy)
        # Extremos de la recta separados por cuadrantes
        self.extremos_I = tuple([i for i in self.extremos if i[1] >= 0 and i[2] >= 0])
        self.extremos_II = tuple([i for i in self.extremos if (i[1] < 0 and i[2] > 0) or (i[1] < 0 and i[2] == 0)])
        self.extremos_III = tuple([i for i in self.extremos if i[1] < 0 and i[2] < 0])
        self.extremos_IV = tuple([i for i in self.extremos if (i[1] > 0 and i[2] < 0) or (i[1] == 0 and i[2] < 0)])

        self.traza_v = self.calcular_traza_v()
        self.traza_h = self.calcular_traza_h()

        # Solo se pueden utilizar segmentos cuando la recta ha sido definida por dos puntos, podría ser mejorado
        if puntos:
            self.puntos = puntos
            self.cuadrante_punto_1 = Punto.calcular_cuadrante(puntos[0])
            self.cuadrante_punto_2 = Punto.calcular_cuadrante(puntos[1])
            self.punto_1, self.punto_2 = puntos[0], puntos[1]
            if self.traza_v == self.traza_h:
                # Pasa por LT
                self.traza_h_entre_puntos = "LT"
                self.traza_v_entre_puntos = "LT"
                self.segmento_entre_trazas = False
            else:
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
            self.puntos = False
            self.infinita.setDisabled(True)

        # Si la recta no tiene trazas, se desactivan estas opciones
        if not self.traza_v or self.traza_v == "Contenida en PV":
            self.ver_traza_vertical.setChecked(False)
            self.ver_traza_vertical.setCheckable(False)
            self.ver_traza_vertical.setDisabled(True)

        if not self.traza_h or self.traza_h == "Contenida en PH":
            self.ver_traza_horizontal.setChecked(False)
            self.ver_traza_horizontal.setCheckable(False)
            self.ver_traza_horizontal.setDisabled(True)

        self.partes = self.calcular_partes()

    def extremos(self, recta: Line3D) -> tuple:
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
                return "Contenida en PH"
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
                return "Contenida en PV"
        else:
            return False

    def trazas_entre_puntos(self):
        segmento = Segment3D(self.punto_1, self.punto_2)
        interseccion_pv = intersection(segmento, self.plano_vertical)
        interseccion_ph = intersection(segmento, self.plano_horizontal)
        if interseccion_pv:
            if not isinstance(interseccion_pv[0], Segment3D):
                if interseccion_pv[0].z > 0:
                    self.traza_v_entre_puntos = "PV+"
                else:
                    self.traza_v_entre_puntos = "PV-"
        if interseccion_ph:
            if not isinstance(interseccion_ph[0], Segment3D):
                if interseccion_ph[0].y >= 0:
                    self.traza_h_entre_puntos = "PH+"
                else:
                    self.traza_h_entre_puntos = "PH-"

    def calcular_partes(self) -> dict:
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
        elif traza_v == "Contenida en PV" and traza_h == "Contenida en PH":
            # LT
            partes['I'] = extremos_I[0], extremos_I[1]
        elif traza_v == "Contenida en PV":
            if traza_h:
                partes['I'] = extremos_I[0], traza_h
                partes['IV'] = traza_h, extremos_IV[0]
        elif traza_h == "Contenida en PH":
            if traza_v:
                partes['I'] = extremos_I[0], traza_v
                partes['II'] = traza_v, extremos_II[0]
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
            if traza_v == traza_h:
                # Pasa por LT
                if len(extremos_I) == 1:
                    partes['I'] = extremos_I[0], traza_v
                    partes['III'] = extremos_III[0], traza_v
                else:
                    partes['II'] = extremos_II[0], traza_v
                    partes['IV'] = extremos_IV[0], traza_v
            elif traza_v[2] > 0 and traza_h[1] > 0:
                partes['I'] = traza_v, traza_h
                partes['II'] = traza_v, extremos_II[0]
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

    def guardar(self):
        if self.puntos:
            return {"Nombre": self.nombre, "Punto_1": self.punto_1, "Punto_2": self.punto_2, "Sympy": self.sympy}
        else:
            return {"Nombre": self.nombre, "Sympy": self.sympy}


class Plano(EntidadGeometrica):
    def __init__(self, internal_id: int, nombre: str, sympy: Plane, puntos: list = None):
        EntidadGeometrica.__init__(self, internal_id, nombre)

        self.sympy = sympy
        self.vector_normal = self.sympy.normal_vector
        self.nombre = nombre

        self.infinito = QAction("Infinito")
        self.infinito.setCheckable(True)
        self.infinito.setChecked(True)
        self.menu.addAction(self.infinito)

        if not puntos:
            self.infinito.setDisabled(True)
            self.puntos = False
        else:
            self.puntos = puntos
            self.punto_1, self.punto_2, self.punto_3 = puntos[0], puntos[1], puntos[2]

        self.limites = self.limites()

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
            punto_en_LT = intersection(self.sympy, Segment3D(Point3D(500, 0, 0), Point3D(-500, 0, 0)))
            if punto_en_LT:
                if not isinstance(punto_en_LT[0], Segment3D):
                    if abs(punto_en_LT[0][0]) < 500:
                        self.punto_en_LT = punto_en_LT[0]

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
        puntos = list(self.limites)
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

    def guardar(self):
        if self.puntos:
            return {"Nombre": self.nombre, "Punto_1": self.punto_1, "Punto_2": self.punto_2,
                    "Punto_3": self.punto_3, "Sympy": self.sympy}
        else:
            return {"Nombre": self.nombre, "Sympy": self.sympy}


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
                    if recta.traza_v == "Contenida en PV" and recta.traza_h == "Contenida en PH":
                        if cuadrante == "I":
                            dibujar(recta.punto_1.coordinates, recta.punto_2.coordinates)
                    if recta.traza_v == "Contenida en PV":
                        if recta.traza_h_entre_puntos:
                            if cuadrante == recta.cuadrante_punto_1:
                                dibujar(recta.punto_1.coordinates, recta.traza_h)
                            if cuadrante == recta.cuadrante_punto_2:
                                dibujar(recta.punto_2.coordinates, recta.traza_h)
                            self.traza_h_recta(recta)
                        else:
                            if cuadrante == recta.cuadrante_punto_1:
                                dibujar(recta.punto_1.coordinates, recta.punto_2.coordinates)

                    elif recta.traza_h == "Contenida en PH":
                        if recta.traza_v_entre_puntos:
                            if cuadrante == recta.cuadrante_punto_1:
                                dibujar(recta.punto_1.coordinates, recta.traza_v)
                            if cuadrante == recta.cuadrante_punto_2:
                                dibujar(recta.punto_2.coordinates, recta.traza_v)
                            self.traza_v_recta(recta)
                        else:
                            if cuadrante == recta.cuadrante_punto_1:
                                dibujar(recta.punto_1.coordinates, recta.punto_2.coordinates)

                    elif recta.cuadrante_punto_1 == recta.cuadrante_punto_2 == cuadrante == "I":
                        dibujar(recta.punto_1.coordinates, recta.punto_2.coordinates)
                    elif recta.cuadrante_punto_1 == recta.cuadrante_punto_2 == cuadrante == "II":
                        dibujar(recta.punto_1.coordinates, recta.punto_2.coordinates)
                    elif recta.cuadrante_punto_1 == recta.cuadrante_punto_2 == cuadrante == "III":
                        dibujar(recta.punto_1.coordinates, recta.punto_2.coordinates)
                    elif recta.cuadrante_punto_1 == recta.cuadrante_punto_2 == cuadrante == "IV":
                        dibujar(recta.punto_1.coordinates, recta.punto_2.coordinates)
                    else:
                        if recta.traza_v_entre_puntos and recta.traza_h_entre_puntos:
                            if recta.segmento_entre_trazas == cuadrante:
                                dibujar(recta.traza_v, recta.traza_h)
                            elif recta.traza_v_entre_puntos == recta.traza_h_entre_puntos == "LT":
                                if recta.cuadrante_punto_1 == cuadrante:
                                    dibujar(recta.punto_1.coordinates, recta.traza_h)
                                if recta.cuadrante_punto_2 == cuadrante:
                                    dibujar(recta.punto_2.coordinates, recta.traza_h)
                                self.traza_h_recta(recta)
                        if recta.cuadrante_punto_1 == cuadrante:
                            if recta.traza_h_entre_puntos == "PH+" and (cuadrante == "I" or cuadrante == "IV"):
                                dibujar(recta.punto_1.coordinates, recta.traza_h)
                                self.traza_h_recta(recta)
                            if recta.traza_h_entre_puntos == "PH-" and (cuadrante == "II" or cuadrante == "III"):
                                dibujar(recta.punto_1.coordinates, recta.traza_h)
                                self.traza_h_recta(recta)

                            if recta.traza_v_entre_puntos == "PV+" and (cuadrante == "I" or cuadrante == "II"):
                                dibujar(recta.punto_1.coordinates, recta.traza_v)
                                self.traza_v_recta(recta)
                            if recta.traza_v_entre_puntos == "PV-" and (cuadrante == "III" or cuadrante == "IV"):
                                dibujar(recta.punto_1.coordinates, recta.traza_v)
                                self.traza_v_recta(recta)
                        if recta.cuadrante_punto_2 == cuadrante:
                            if recta.traza_h_entre_puntos == "PH+" and (cuadrante == "I" or cuadrante == "IV"):
                                dibujar(recta.punto_2.coordinates, recta.traza_h)
                                self.traza_h_recta(recta)
                            if recta.traza_h_entre_puntos == "PH-" and (cuadrante == "II" or cuadrante == "III"):
                                dibujar(recta.punto_2.coordinates, recta.traza_h)
                                self.traza_h_recta(recta)

                            if recta.traza_v_entre_puntos == "PV+" and (cuadrante == "I" or cuadrante == "II"):
                                dibujar(recta.punto_2.coordinates, recta.traza_v)
                                self.traza_v_recta(recta)
                            if recta.traza_v_entre_puntos == "PV-" and (cuadrante == "III" or cuadrante == "IV"):
                                dibujar(recta.punto_2.coordinates, recta.traza_v)
                                self.traza_v_recta(recta)

    @staticmethod
    def traza_v_recta(recta):
        if programa.ajustes.ver_rectas_trazas_verticales.isChecked():
            if recta.traza_v != "Contenida en PV" and recta.ver_traza_vertical.isChecked():
                if recta.traza_v[0] < 500 and recta.traza_v[1] < 500:
                    glColor(0, 1, 0, 1)
                    glBegin(GL_POINTS)
                    glVertex(recta.traza_v)
                    glEnd()
                    glColor(recta.color)

    @staticmethod
    def traza_h_recta(recta):
        if programa.ajustes.ver_rectas_trazas_horizontales.isChecked():
            if recta.traza_h != "Contenida en PH" and recta.ver_traza_horizontal.isChecked():
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
                    for j in plano.limites:
                        glVertex(j)
                    glEnd()
                else:
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
        if programa.modo_oscuro:
            glClearColor(0.3, 0.3, 0.3, 0)
        else:
            glClearColor(1, 1, 1, 0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadMatrixf(self.m)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        self.dibujar_elementos()
        self.update()

    def dibujar_entidades(self, cuadrante: str):
        if programa.ajustes.ver_planos.isChecked():
            self.dibujar_planos(cuadrante)
        if programa.ajustes.ver_rectas.isChecked():
            self.dibujar_rectas(cuadrante)
        if programa.ajustes.ver_puntos.isChecked():
            self.dibujar_puntos(cuadrante)

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
    def __init__(self):
        QWidget.__init__(self)

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
        if programa.ver_planos.checkState():
            self.dibujar_planos(qp)
        if programa.ver_rectas.checkState():
            self.dibujar_rectas(qp)
        if programa.ver_puntos.checkState():
            self.dibujar_puntos(qp)
        self.update()

    def keyPressEvent(self, evento):
        if evento.key() == Qt.Key_Plus:
            self.zoom_in()
        if evento.key() == Qt.Key_Minus:
            self.zoom_out()
        if evento.key() == Qt.Key_R:
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
        qp.drawPoint(QPointF(punto.x, -punto.y))

    def punto_prima2(self, qp, punto):
        qp.setPen(self.pen_punto_prima2)
        qp.drawPoint(QPointF(punto.x, punto.z))

    def punto_prima3(self, qp, punto):
        if programa.modo_oscuro:
            self.pen_prima3.setColor(QColor(200, 200, 200))
        else:
            self.pen_prima3.setColor(QColor(0, 0, 0))
        qp.setPen(self.pen_prima3)
        qp.drawPoint(QPointF(-punto.y, punto.z))

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
                    if recta.cuadrante_punto_1 == recta.cuadrante_punto_2 == "I":
                        self.dibujar_continuo(qp, (recta.punto_1.coordinates, recta.punto_2.coordinates))
                    elif recta.cuadrante_punto_1 != "I" and recta.cuadrante_punto_2 != "I":
                        self.dibujar_discontinuo(qp, (recta.punto_1.coordinates, recta.punto_2.coordinates))
                    else:
                        if recta.cuadrante_punto_1 == "I":
                            if recta.traza_v != "Contenida en PV" and recta.traza_v:
                                if recta.traza_v[2] >= 0:
                                    self.dibujar_discontinuo(qp, (recta.traza_v, recta.punto_2.coordinates))
                                    self.dibujar_continuo(qp, (recta.punto_1.coordinates, recta.traza_v))
                            if recta.traza_h != "Contenida en PH" and recta.traza_h:
                                if recta.traza_h[1] >= 0:
                                    self.dibujar_discontinuo(qp, (recta.traza_h, recta.punto_2.coordinates))
                                    self.dibujar_continuo(qp, (recta.punto_1.coordinates, recta.traza_h))
                        elif recta.cuadrante_punto_2 == "I":
                            if recta.traza_v != "Contenida en PV" and recta.traza_v:
                                if recta.traza_v[2] >= 0:
                                    self.dibujar_discontinuo(qp, (recta.traza_v, recta.punto_1.coordinates))
                                    self.dibujar_continuo(qp, (recta.punto_2.coordinates, recta.traza_v))
                            if recta.traza_h != "Contenida en PH" and recta.traza_h:
                                if recta.traza_h[1] >= 0:
                                    self.dibujar_discontinuo(qp, (recta.traza_h, recta.punto_1.coordinates))
                                    self.dibujar_continuo(qp, (recta.punto_2.coordinates, recta.traza_h))
                        if recta.traza_v != "Contenida en PV" and recta.traza_v \
                                and recta.traza_h and recta.traza_h != "Contenida en PH":
                            if recta.traza_v[2] >= 0 and recta.traza_h[1] >= 0:
                                if recta.cuadrante_punto_1 == "II":
                                    self.dibujar_discontinuo(qp, (recta.traza_v, recta.punto_1.coordinates))
                                else:
                                    self.dibujar_discontinuo(qp, (recta.traza_v, recta.punto_2.coordinates))

                                if recta.cuadrante_punto_1 == "IV":
                                    self.dibujar_discontinuo(qp, (recta.traza_h, recta.punto_1.coordinates))
                                else:
                                    self.dibujar_discontinuo(qp, (recta.traza_h, recta.punto_2.coordinates))

                                self.dibujar_continuo(qp, (recta.traza_v, recta.traza_h))

                # Tercera proyección
                if programa.tercera_proyeccion.checkState():
                    if programa.modo_oscuro:
                        self.pen_prima3.setColor(QColor(200, 200, 200))
                    else:
                        self.pen_prima3.setColor(QColor(0, 0, 0))
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
        x0 = extremos[0][0]
        x = extremos[1][0]
        y0 = -extremos[0][1]
        y = -extremos[1][1]
        if not (x0 == x and y0 == y):
            qp.drawLine(QPointF(x0, y0), QPointF(x, y))

    @staticmethod
    def recta_prima2(qp, extremos):
        x0 = extremos[0][0]
        x = extremos[1][0]
        y0 = extremos[0][2]
        y = extremos[1][2]
        if not (x0 == x and y0 == y):
            qp.drawLine(QPointF(x0, y0), QPointF(x, y))

    @staticmethod
    def recta_prima3(qp, extremos):
        x0 = -extremos[0][1]
        x = -extremos[1][1]
        y0 = extremos[0][2]
        y = extremos[1][2]
        qp.drawLine(QPointF(x0, y0), QPointF(x, y))

    def dibujar_trazas_recta(self, qp, recta):
        qp.setPen(self.pen_trazas)
        if recta.infinita.isChecked():
            if recta.traza_h != "Contenida en PH" and recta.traza_h and recta.ver_traza_horizontal.isChecked():
                qp.drawPoint(round(recta.traza_h[0]), round(-recta.traza_h[1]))  # H "
                qp.drawPoint(round(recta.traza_h[0]), 0)  # H '
            if recta.traza_v != "Contenida en PV" and recta.traza_v and recta.ver_traza_vertical.isChecked():
                qp.drawPoint(round(recta.traza_v[0]), round(recta.traza_v[2]))  # V '
                qp.drawPoint(round(recta.traza_v[0]), 0)  # V "
        else:
            if recta.traza_v_entre_puntos and recta.traza_v:
                qp.drawPoint(round(recta.traza_v[0]), round(recta.traza_v[2]))  # H '
                qp.drawPoint(round(recta.traza_v[0]), 0)  # H "
            if recta.traza_h_entre_puntos and recta.traza_h:
                qp.drawPoint(round(recta.traza_h[0]), round(-recta.traza_h[1]))  # H "
                qp.drawPoint(round(recta.traza_h[0]), 0)  # H '

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


class VentanaBase(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)

        self.setWindowModality(Qt.ApplicationModal)
        self.setFixedSize(180, 140)
        self.setWindowFlags(Qt.Tool)
        font = QFont()
        font.setPointSize(10)
        self.setFont(font)
        self.widget_central = QWidget(self)
        self.setCentralWidget(self.widget_central)

        self.etiqueta_1 = QLabel(self.widget_central)
        self.etiqueta_1.setGeometry(10, 10, 130, 16)

        self.etiqueta_2 = QLabel(self.widget_central)
        self.etiqueta_2.setGeometry(10, 60, 130, 16)

        self.boton_crear = QPushButton("Crear", self.widget_central)
        self.boton_crear.setGeometry(10, 110, 80, 23)

        self.boton_cerrar = QPushButton("Cancelar", self.widget_central)
        self.boton_cerrar.setGeometry(90, 110, 80, 23)
        self.boton_cerrar.clicked.connect(self.cerrar)

        self.elegir_entidad_1 = QComboBox(self.widget_central)
        self.elegir_entidad_1.setGeometry(10, 30, 160, 25)

        self.elegir_entidad_2 = QComboBox(self.widget_central)
        self.elegir_entidad_2.setGeometry(10, 80, 160, 25)

        self.setWindowIcon(QIcon("Logo.ico"))

    def cerrar(self):
        self.close()


class VentanaBaseConNombre(VentanaBase):
    def __init__(self):
        VentanaBase.__init__(self)
        self.setFixedSize(180, 190)
        self.etiqueta_nombre = QLabel("Nombre:", self.widget_central)
        self.etiqueta_nombre.setGeometry(10, 105, 50, 20)

        self.boton_crear.setGeometry(10, 160, 80, 23)
        self.boton_cerrar.setGeometry(90, 160, 80, 23)

        self.nombre = QPlainTextEdit(self.widget_central)
        self.nombre.setGeometry(10, 125, 160, 28)


class PuntoMedio(VentanaBaseConNombre):
    def __init__(self):
        VentanaBaseConNombre.__init__(self)
        self.setWindowTitle("Punto medio")
        self.etiqueta_1.setText("Punto:")
        self.etiqueta_2.setText("Punto:")
        self.boton_crear.clicked.connect(self.crear_punto)

    def abrir(self):
        self.elegir_entidad_1.clear()
        self.elegir_entidad_2.clear()
        for i in range(programa.lista_puntos.count()):
            self.elegir_entidad_1.addItem(programa.lista_puntos.itemWidget(programa.lista_puntos.item(i)).nombre)

        for i in range(programa.lista_puntos.count()):
            self.elegir_entidad_2.addItem(programa.lista_puntos.itemWidget(programa.lista_puntos.item(i)).nombre)

        self.show()
        self.activateWindow()

    def crear_punto(self):
        punto = self.elegir_entidad_1.currentText()
        punto2 = self.elegir_entidad_2.currentText()
        for i in range(programa.lista_puntos.count()):
            if programa.lista_puntos.itemWidget(programa.lista_puntos.item(i)).nombre == punto:
                punto = programa.lista_puntos.itemWidget(programa.lista_puntos.item(i))

        for i in range(programa.lista_puntos.count()):
            if programa.lista_puntos.itemWidget(programa.lista_puntos.item(i)).nombre == punto2:
                punto2 = programa.lista_puntos.itemWidget(programa.lista_puntos.item(i))

        if punto == "" or punto2 == "":
            QMessageBox.critical(self, "Error al crear el punto medio",
                                 "Debes crear al menos dos puntos para calcular su punto medio")
        else:
            nombre = programa.evitar_nombre_punto_blanco(self.nombre.toPlainText())
            punto_medio = punto.sympy.midpoint(punto2.sympy)
            nombre = f"{nombre} ({punto_medio.x}, {punto_medio.y}, {punto_medio.z})"
            programa.crear_punto(nombre, punto_medio)
            self.cerrar()


class RectaPerpendicularAPlano(VentanaBaseConNombre):
    def __init__(self):
        VentanaBaseConNombre.__init__(self)
        self.setWindowTitle("Recta perpendicular a plano")
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
        self.activateWindow()

    def crear_recta(self):
        punto = self.elegir_entidad_1.currentText()
        plano = self.elegir_entidad_2.currentText()

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
            nombre = programa.evitar_nombre_recta_blanco(self.nombre.toPlainText())
            nombre = f"{nombre}({punto.nombre}⊥{plano.nombre})"
            recta = plano.sympy.perpendicular_line(punto.sympy)
            programa.crear_recta(nombre, recta)
            self.cerrar()


class PlanoPerpendicularAPlano(VentanaBaseConNombre):
    def __init__(self):
        VentanaBaseConNombre.__init__(self)
        self.setWindowTitle("Plano perpendicular a plano")
        self.setFixedSize(180, 240)

        self.etiqueta_1.setText("Punto:")
        self.etiqueta_2.setText("Plano:")
        self.etiqueta_2.setGeometry(10, 110, 41, 16)
        self.etiqueta_3 = QLabel("Punto:", self.widget_central)
        self.etiqueta_3.setGeometry(10, 60, 41, 16)

        self.elegir_entidad_3 = QComboBox(self.widget_central)
        self.elegir_entidad_3.setGeometry(10, 130, 160, 25)

        self.etiqueta_nombre.setGeometry(10, 155, 50, 20)
        self.nombre.setGeometry(10, 175, 160, 28)

        self.boton_crear.setGeometry(10, 210, 80, 23)
        self.boton_cerrar.setGeometry(90, 210, 80, 23)

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
        self.activateWindow()

    def crear_plano(self):
        punto = self.elegir_entidad_1.currentText()
        punto2 = self.elegir_entidad_2.currentText()
        plano = self.elegir_entidad_3.currentText()

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
            nombre = programa.evitar_nombre_plano_blanco(self.nombre.toPlainText())
            nombre = f"{nombre}⊥{plano.nombre}"
            plano_perpendicular = plano.sympy.perpendicular_plane(punto.sympy, punto2.sympy)
            programa.crear_plano(nombre, plano_perpendicular)
            self.cerrar()


class PlanoParaleloAPlano(VentanaBaseConNombre):
    def __init__(self):
        VentanaBaseConNombre.__init__(self)

        self.setWindowTitle("Plano paralelo a plano")
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
        self.activateWindow()

    def crear_plano(self):
        punto = self.elegir_entidad_1.currentText()
        plano = self.elegir_entidad_2.currentText()

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
            nombre = programa.evitar_nombre_plano_blanco(self.nombre.toPlainText())
            nombre = f"{nombre}║{plano.nombre}"
            plano_paralelo = plano.sympy.parallel_plane(punto.sympy)
            programa.crear_plano(nombre, plano_paralelo)
            self.cerrar()


class RectaPerpendicularARecta(VentanaBaseConNombre):
    def __init__(self):
        VentanaBaseConNombre.__init__(self)
        self.setWindowTitle("Recta perpendicular a recta")
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
        self.activateWindow()

    def crear_recta(self):
        punto = self.elegir_entidad_1.currentText()
        recta = self.elegir_entidad_2.currentText()

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
            nombre = programa.evitar_nombre_recta_blanco(self.nombre.toPlainText())
            nombre = f"{nombre}({recta.nombre}⊥{punto.nombre})"
            recta_perpendicular = recta.sympy.perpendicular_line(punto.sympy)
            programa.crear_recta(nombre, recta_perpendicular)
            self.cerrar()


class RectaParalelaARecta(VentanaBaseConNombre):
    def __init__(self):
        VentanaBaseConNombre.__init__(self)

        self.setWindowTitle("Recta paralela a recta")
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
        self.activateWindow()

    def crear_recta(self):
        punto = self.elegir_entidad_1.currentText()
        recta = self.elegir_entidad_2.currentText()
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
            nombre = programa.evitar_nombre_recta_blanco(self.nombre.toPlainText())
            nombre = f"{nombre}({recta.nombre}║{punto.nombre})"
            recta_perpendicular = recta.sympy.parallel_line(punto.sympy)
            programa.crear_recta(nombre, recta_perpendicular)
            self.cerrar()


class Distancia(VentanaBase):
    def __init__(self):
        VentanaBase.__init__(self)

        self.setWindowTitle("Calcular distancia")
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
        self.activateWindow()

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
                                 "Debes crear al menos dos elementos para calcular su distancia")
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

        self.setWindowTitle("Crear intersección")
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
        self.activateWindow()

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
                        nombre = f"{entidad_1.nombre}∩{entidad_2.nombre}"
                        programa.crear_punto(nombre, interseccion)
                elif isinstance(interseccion, Line3D):
                    QMessageBox.critical(self, "Error al calcular la intersección",
                                         "Las rectas son coincidentes")
                else:
                    QMessageBox.critical(self, "Error al calcular la intersección",
                                         "Las rectas son paralelas")

            elif isinstance(entidad_1, Plano) and isinstance(entidad_2, Plano):
                """
                Lo mismo, 3 casos:
                Planos paralelos -> No se crea nada
                Secantes -> Se crea una recta
                Coincidentes -> Ambos planos son iguales
                """

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
                        nombre = f"{entidad_1.nombre}∩{entidad_2.nombre}"
                        programa.crear_punto(nombre, interseccion)
                else:
                    QMessageBox.critical(self, "Error al calcular la intersección",
                                         "La recta se encuentra en el plano")


class Proyectar(VentanaBaseConNombre):
    def __init__(self):
        VentanaBaseConNombre.__init__(self)

        self.setWindowTitle("Proyectar elementos")
        self.setFixedSize(180, 240)

        self.etiqueta_1.setText("Punto:")
        self.etiqueta_2.setText("Plano:")

        self.boton_crear.setGeometry(10, 210, 80, 23)
        self.boton_cerrar.setGeometry(90, 210, 80, 23)

        etiqueta_modo = QLabel("Hacia el plano:", self.widget_central)
        etiqueta_modo.setGeometry(10, 155, 121, 25)

        self.modo = QComboBox(self.widget_central)
        self.modo.setGeometry(10, 180, 160, 25)
        self.modo.addItem("Perpendicular al plano")
        self.modo.addItem("Vertical")
        self.modo.addItem("Horizontal")
        self.modo.addItem("Perfil")

        self.boton_crear.clicked.connect(self.crear_punto)

    def abrir(self):
        self.elegir_entidad_1.clear()
        self.elegir_entidad_2.clear()

        for i in range(programa.lista_puntos.count()):
            self.elegir_entidad_1.addItem(programa.lista_puntos.itemWidget(programa.lista_puntos.item(i)).nombre)

        for i in range(programa.lista_planos.count()):
            self.elegir_entidad_2.addItem(programa.lista_planos.itemWidget(programa.lista_planos.item(i)).nombre)

        self.show()
        self.activateWindow()

    def crear_punto(self):
        punto = self.elegir_entidad_1.currentText()
        plano = self.elegir_entidad_2.currentText()

        for i in range(programa.lista_puntos.count()):
            if programa.lista_puntos.itemWidget(programa.lista_puntos.item(i)).nombre == punto:
                punto = programa.lista_puntos.itemWidget(programa.lista_puntos.item(i))

        for i in range(programa.lista_planos.count()):
            if programa.lista_planos.itemWidget(programa.lista_planos.item(i)).nombre == plano:
                plano = programa.lista_planos.itemWidget(programa.lista_planos.item(i))

        if punto == "" or plano == "":
            QMessageBox.critical(self, "Error al crear la proyección",
                                 "Debes crear al menos un punto y un plano para calcular su proyección")
        else:
            if plano.sympy.intersection(punto.sympy):
                QMessageBox.critical(self, "Error al crear la proyección", "El punto pertenece al plano")
            else:
                modo = self.modo.currentText()
                if modo == "Perpendicular al plano":
                    proyectado = plano.sympy.projection(punto.sympy)
                else:
                    if modo == "Vertical":
                        segmento = Segment3D(Point3D(punto.x, 500, punto.z), Point3D(punto.x, -500, punto.z))
                    elif modo == "Horizontal":
                        segmento = Segment3D(Point3D(punto.x, punto.y, 500), Point3D(punto.x, punto.y, -500))
                    else:
                        # modo = perfil
                        segmento = Segment3D(Point3D(500, punto.y, punto.z), Point3D(-500, punto.y, punto.z))
                    proyectado = plano.sympy.intersection(segmento)

                    if proyectado:
                        proyectado = proyectado[0]
                    else:
                        QMessageBox.critical(self, "Error al crear la proyección",
                                             "El punto no puede proyectarse en esa dirección")
                        return

                nombre = programa.evitar_nombre_punto_blanco(self.nombre.toPlainText())
                nombre = f"{nombre}({proyectado.x}, {proyectado.y}, {proyectado.z})"
                programa.crear_punto(nombre, proyectado)
                self.cerrar()


class Bisectriz(VentanaBaseConNombre):
    def __init__(self):
        VentanaBaseConNombre.__init__(self)

        self.setWindowTitle("Bisectriz")
        self.etiqueta_1.setText("Recta:")
        self.etiqueta_2.setText("Recta:")

        self.boton_crear.clicked.connect(self.crear_recta)

    def abrir(self):
        self.elegir_entidad_1.clear()
        self.elegir_entidad_2.clear()

        for i in range(programa.lista_rectas.count()):
            self.elegir_entidad_1.addItem(programa.lista_rectas.itemWidget(programa.lista_rectas.item(i)).nombre)
            self.elegir_entidad_2.addItem(programa.lista_rectas.itemWidget(programa.lista_rectas.item(i)).nombre)

        self.show()
        self.activateWindow()

    def crear_recta(self):
        recta1 = self.elegir_entidad_1.currentText()
        recta2 = self.elegir_entidad_2.currentText()

        for i in range(programa.lista_rectas.count()):
            if programa.lista_rectas.itemWidget(programa.lista_rectas.item(i)).nombre == recta1:
                recta1 = programa.lista_rectas.itemWidget(programa.lista_rectas.item(i))
            elif programa.lista_rectas.itemWidget(programa.lista_rectas.item(i)).nombre == recta2:
                recta2 = programa.lista_rectas.itemWidget(programa.lista_rectas.item(i))

        if recta1 == "" or recta2 == "":
            QMessageBox.critical(self, "Error al crear la bisectriz",
                                 "Debes crear al menos dos rectas que se corten para calcular su bisectriz")
        else:
            interseccion = recta1.sympy.intersection(recta2.sympy)
            if interseccion:
                if isinstance(interseccion[0], Line3D):
                    QMessageBox.critical(self, "Error al crear la bisectriz", "Las rectas son coincidentes")
                else:
                    punto = interseccion[0]

                    direccion1 = recta1.sympy.direction_ratio
                    direccion2 = recta2.sympy.direction_ratio

                    def normalize(vector: list):
                        # Normaliza los vectores para que tengan la misma longitud
                        length = (vector[0] ** 2 + vector[1] ** 2 + vector[2] ** 2) ** 0.5
                        vector = [x / length for x in vector]
                        return vector

                    d1 = normalize(direccion1)
                    d2 = normalize(direccion2)

                    direccion1 = [d1[i] + d2[i] for i in range(3)]
                    direccion2 = [d1[i] - d2[i] for i in range(3)]

                    bis1 = Line3D(punto, direction_ratio=direccion1)
                    bis2 = Line3D(punto, direction_ratio=direccion2)

                    nombre = programa.evitar_nombre_recta_blanco(self.nombre.toPlainText())
                    nombre2 = programa.evitar_nombre_recta_blanco(self.nombre.toPlainText()) + " ⊥"

                    programa.crear_recta(nombre, bis1)
                    programa.crear_recta(nombre2, bis2)
            else:
                QMessageBox.critical(self, "Error al crear la bisectriz",
                                     "Las rectas no se cortan, no tienen ningún punto en común")


class Controles(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowFlags(Qt.Tool)
        self.setFixedSize(355, 441)
        self.setWindowIcon(QIcon("Logo.ico"))
        self.setWindowTitle("Controles")

        centralwidget = QWidget()
        self.setCentralWidget(centralwidget)

        fuente = QFont()
        fuente.setPointSize(10)
        self.setFont(fuente)

        tecla = QLabel("Tecla:", centralwidget)
        tecla.setGeometry(5, 6, 40, 16)

        accion = QLabel("Acción:", centralwidget)
        accion.setGeometry(52, 6, 42, 16)

        uno = QLabel("1", centralwidget)
        uno.setGeometry(16, 54, 16, 16)

        dos = QLabel("2", centralwidget)
        dos.setGeometry(16, 78, 16, 16)

        tres = QLabel("3", centralwidget)
        tres.setGeometry(16, 102, 16, 16)

        alzado = QLabel("Vista alzado", centralwidget)
        alzado.setGeometry(52, 54, 69, 16)

        planta = QLabel("Vista planta", centralwidget)
        planta.setGeometry(52, 78, 67, 16)

        perfil = QLabel("Vista perfil", centralwidget)
        perfil.setGeometry(52, 102, 61, 16)

        reset = QLabel("Reestablecer la posición de la cámara", centralwidget)
        reset.setGeometry(52, 30, 217, 16)

        r = QLabel("R", centralwidget)
        r.setGeometry(16, 30, 16, 16)

        mas = QLabel("+", centralwidget)
        mas.setGeometry(16, 126, 16, 16)

        menos = QLabel("-", centralwidget)
        menos.setGeometry(16, 150, 16, 16)

        zoom_mas = QLabel("Aumentar el zoom", centralwidget)
        zoom_mas.setGeometry(52, 126, 111, 16)

        zoom_menos = QLabel("Reducir el zoom", centralwidget)
        zoom_menos.setGeometry(52, 150, 101, 16)

        w = QLabel("W", centralwidget)
        w.setGeometry(16, 174, 16, 16)

        a = QLabel("A", centralwidget)
        a.setGeometry(16, 199, 16, 16)

        s = QLabel("S", centralwidget)
        s.setGeometry(16, 223, 16, 16)

        d = QLabel("D", centralwidget)
        d.setGeometry(16, 247, 16, 16)

        q = QLabel("Q", centralwidget)
        q.setGeometry(16, 271, 16, 16)

        e = QLabel("E", centralwidget)
        e.setGeometry(16, 295, 16, 16)

        mover_y_mas = QLabel("Mover la cámara sobre el eje Y en sentido positivo", centralwidget)
        mover_y_mas.setGeometry(52, 271, 289, 16)

        mover_y_menos = QLabel("Mover la cámara sobre el eje Y en sentido negativo", centralwidget)
        mover_y_menos.setGeometry(52, 295, 294, 16)

        mover_z_mas = QLabel("Mover la cámara sobre el eje Z en sentido postivo", centralwidget)
        mover_z_mas.setGeometry(52, 319, 286, 16)

        mover_z_menos = QLabel("Mover la cámara sobre el eje Z en sentido negativo", centralwidget)
        mover_z_menos.setGeometry(52, 344, 294, 16)

        derecha = QLabel("Rotar la cámara hacia la derecha", centralwidget)
        derecha.setGeometry(52, 247, 190, 16)

        abajo = QLabel("Rotar la cámar hacia abajo", centralwidget)
        abajo.setGeometry(52, 223, 155, 16)

        izquierda = QLabel("Rotar la cámara hacia la izquierda", centralwidget)
        izquierda.setGeometry(52, 199, 196, 16)

        arriba = QLabel("Rotar la cámara hacia arriba", centralwidget)
        arriba.setGeometry(52, 174, 164, 16)

        flecha_arriba = QLabel("🢁", centralwidget)
        flecha_arriba.setGeometry(16, 319, 16, 17)

        flecha_abajo = QLabel("🢃", centralwidget)
        flecha_abajo.setGeometry(16, 344, 16, 17)

        flecha_derecha = QLabel("🢂", centralwidget)
        flecha_derecha.setGeometry(16, 369, 16, 17)

        flecha_izquierda = QLabel("🢀", centralwidget)
        flecha_izquierda.setGeometry(16, 394, 16, 17)

        mover_x_menos = QLabel("Mover la cámara sobre el eje X en sentido negativo", centralwidget)
        mover_x_menos.setGeometry(52, 369, 295, 16)

        mover_x_mas = QLabel("Mover la cámara sobre el eje X en sentido positivo", centralwidget)
        mover_x_mas.setGeometry(52, 394, 290, 16)

        raton = QLabel("Arrastrar el ratón: Rotar libremente la cámara", centralwidget)
        raton.setGeometry(11, 419, 271, 16)


class AcercaDe(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowFlags(Qt.Tool)
        self.setWindowTitle("Acerca de")
        self.setWindowIcon(QIcon("Logo.ico"))
        self.setFixedSize(1020, 170)
        widget_central = QWidget()
        self.setCentralWidget(widget_central)

        fuente = QFont()
        fuente.setPointSize(12)
        self.setFont(fuente)

        acerca_de = QLabel("Acerca de:", widget_central)
        acerca_de.setGeometry(10, 10, 80, 21)

        t = QLabel(widget_central)
        t.setGeometry(10, 35, 1000, 115)
        t.setOpenExternalLinks(True)
        t.setTextFormat(Qt.RichText)
        t.setText("Este es un programa enfocado al uso educativo del sistema diédrico.<br>"
                  "Ha sido desarrollado por Jaime Resano Aisa, estudiante de 18 años del instituto "
                  "IES Ribera del Arga de Peralta, Navarra.<br>Ha sido programado en el lenguaje Python 3. "
                  "Utiliza PyQt5 para la interfaz, Sympy para los cálculos matemáticos y OpenGL para el dibujado 3D."
                  "<br>El código fuente del programa se encuentra disponible en "
                  "<a href=\"https://github.com/Jaime02/Proyecto-de-investigacion-2019-Dibujo-tecnico/\">GitHub</a>."
                  "<br>También está disponible el trabajo de investigación realizado que explica cómo funciona el "
                  "sistema diédrico.<br>Ante cualquier duda, sugerencia o problema, por favor, contacta con el autor en"
                  " el siguiente email: jresanoais1@educacion.navarra.es")


class Ajustes(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setWindowFlags(Qt.Tool)
        self.setWindowModality(Qt.ApplicationModal)
        self.setFixedSize(420, 180)

        self.color_plano_vertical = (0.1, 1, 0.1, 0.5)
        self.color_plano_horizontal = (1, 0.1, 0.1, 0.5)

        widget_central = QWidget(self)

        ajustes = QLabel("Ajustes:", widget_central)
        ajustes.setGeometry(10, 10, 40, 16)

        puntos = QLabel("Puntos:", widget_central)
        puntos.setGeometry(10, 90, 37, 16)
        rectas = QLabel("Rectas", widget_central)
        rectas.setGeometry(140, 10, 41, 16)
        planos = QLabel("Planos", widget_central)
        planos.setGeometry(280, 10, 35, 16)

        self.ver_plano_horizontal = QCheckBox("Ver plano horizontal", widget_central)
        self.ver_plano_horizontal.setChecked(True)
        self.ver_plano_horizontal.setGeometry(10, 70, 118, 17)

        self.ver_plano_vertical = QCheckBox("Ver plano vertical", widget_central)
        self.ver_plano_vertical.setChecked(True)
        self.ver_plano_vertical.setGeometry(10, 50, 106, 17)

        self.ver_ejes = QCheckBox("Ver ejes", widget_central)
        self.ver_ejes.setChecked(True)
        self.ver_ejes.setGeometry(10, 30, 62, 17)

        self.ver_puntos = QCheckBox("Ver puntos", widget_central)
        self.ver_puntos.setChecked(True)
        self.ver_puntos.setGeometry(10, 110, 75, 17)

        self.ver_rectas = QCheckBox("Ver rectas", widget_central)
        self.ver_rectas.setChecked(True)
        self.ver_rectas.setGeometry(140, 30, 133, 17)

        self.ver_planos = QCheckBox("Ver planos", widget_central)
        self.ver_planos.setChecked(True)
        self.ver_planos.setGeometry(280, 30, 73, 17)

        self.ver_rectas_trazas_verticales = QCheckBox("Ver trazas verticales", widget_central)
        self.ver_rectas_trazas_verticales.setChecked(True)
        self.ver_rectas_trazas_verticales.setGeometry(140, 70, 121, 17)

        self.ver_rectas_trazas_horizontales = QCheckBox("Ver trazas horizontales", widget_central)
        self.ver_rectas_trazas_horizontales.setChecked(True)
        self.ver_rectas_trazas_horizontales.setGeometry(140, 50, 129, 17)

        boton_color_vertical = QPushButton("Cambiar el color del\n plano vertical", widget_central)
        boton_color_vertical.setGeometry(10, 130, 101, 41)
        boton_color_vertical.clicked.connect(self.cambiar_color_plano_vertical)
        reset_vertical = QPushButton("Reestablecer", widget_central)
        reset_vertical.setGeometry(120, 130, 75, 41)
        reset_vertical.clicked.connect(self.reset_color_vertical)

        boton_color_horizontal = QPushButton("Cambiar el color del\n plano horizontal", widget_central)
        boton_color_horizontal.setGeometry(200, 130, 101, 41)
        boton_color_horizontal.clicked.connect(self.cambiar_color_plano_horizontal)
        reset_horizontal = QPushButton("Reestablecer", widget_central)
        reset_horizontal.setGeometry(310, 130, 75, 41)

        self.setWindowTitle("Ajustes")
        self.setCentralWidget(widget_central)
        self.setWindowIcon(QIcon("Logo.ico"))

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


class VentanaPrincipal(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)

        widget_central = QWidget()
        self.setWindowTitle("Dibujo técnico")
        self.setWindowIcon(QIcon("Logo.ico"))

        self.showMinimized()
        self.showMaximized()

        self.menubar = QMenuBar()
        self.setMenuBar(self.menubar)
        self.menu = self.menubar.addMenu("Archivo")

        self.accion_guardar = QAction("Guardar")
        self.accion_guardar.triggered.connect(self.guardar)
        self.menu.addAction(self.accion_guardar)

        self.accion_abrir = QAction("Abrir")
        self.accion_abrir.triggered.connect(self.abrir)
        self.menu.addAction(self.accion_abrir)

        self.borrar_todo = QAction("Borrar todo")
        self.borrar_todo.triggered.connect(self.borrar_todos_los_elementos)
        self.menu.addAction(self.borrar_todo)

        self.salir = QAction("Salir")
        self.salir.triggered.connect(self.closeEvent)
        self.menu.addAction(self.salir)

        self.accion_ajustes = QAction("Ajustes")
        self.ajustes = Ajustes()
        self.accion_ajustes.triggered.connect(self.ajustes.show)
        self.menubar.addAction(self.accion_ajustes)

        self.accion_controles = QAction("Controles")
        self.controles = Controles()
        self.accion_controles.triggered.connect(self.controles.show)
        self.menubar.addAction(self.accion_controles)

        self.accion_acerca_de = QAction("Acerca de")
        self.acerca_de = AcercaDe()
        self.accion_acerca_de.triggered.connect(self.acerca_de.show)
        self.menubar.addAction(self.accion_acerca_de)

        self.accion_modo_oscuro = QAction("Cambiar a modo oscuro")
        self.accion_modo_oscuro.triggered.connect(self.cambiar_modo)
        self.menubar.addAction(self.accion_modo_oscuro)

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

        informacion = QLabel("Información:", widget_central, font=fuente)
        informacion.setGeometry(0, 10, 91, 16)

        posicion = QLabel("Posición:", widget_central, font=fuente)
        posicion.setGeometry(0, 30, 71, 16)

        self.posicion = QLabel("Primer cuadrante", widget_central, font=fuente)
        self.posicion.setGeometry(60, 30, 151, 16)

        self.angulo_vertical = QLabel(widget_central, font=fuente)
        self.angulo_vertical.setGeometry(0, 50, 121, 16)

        self.angulo_horizontal = QLabel(widget_central, font=fuente)
        self.angulo_horizontal.setGeometry(120, 50, 130, 16)

        vista = QLabel("Vista:", widget_central, font=fuente)
        vista.setGeometry(0, 70, 91, 16)

        crear_puntos = QLabel("Crear puntos:", widget_central, font=fuente)
        crear_puntos.setGeometry(0, 120, 91, 16)

        nombre_punto = QLabel("Nombre:", widget_central)
        nombre_punto.setGeometry(0, 200, 91, 16)

        distancia_al_origen = QLabel("Distancia al origen:", widget_central)
        distancia_al_origen.setGeometry(0, 140, 91, 16)

        alejamiento = QLabel("Alejamiento:", widget_central)
        alejamiento.setGeometry(0, 160, 91, 16)

        cota = QLabel("Cota:", widget_central)
        cota.setGeometry(0, 180, 91, 16)

        nombre_recta = QLabel("Nombre:", widget_central)
        nombre_recta.setGeometry(160, 180, 91, 21)

        crear_rectas = QLabel("Crear rectas:", widget_central, font=fuente)
        crear_rectas.setGeometry(160, 120, 91, 16)

        punto_1_recta = QLabel("Punto 1:", widget_central)
        punto_1_recta.setGeometry(160, 140, 51, 16)

        punto_2_recta = QLabel("Punto 2:", widget_central)
        punto_2_recta.setGeometry(160, 160, 51, 16)

        nombre_plano = QLabel("Nombre:", widget_central)
        nombre_plano.setGeometry(320, 200, 91, 21)

        crear_planos = QLabel("Crear planos:", widget_central, font=fuente)
        crear_planos.setGeometry(320, 120, 91, 16)

        punto_1_plano = QLabel("Punto 1:", widget_central)
        punto_1_plano.setGeometry(320, 140, 51, 16)

        punto_2_plano = QLabel("Punto 2:", widget_central)
        punto_2_plano.setGeometry(320, 160, 51, 16)

        punto_3_plano = QLabel("Punto 3:", widget_central)
        punto_3_plano.setGeometry(320, 180, 51, 16)

        boton_reset = QPushButton("Reset (R)", widget_central)
        boton_reset.setGeometry(0, 90, 81, 23)
        boton_reset.clicked.connect(self.renderizador.ver_reset)

        boton_alzado = QPushButton("Alzado (1) ''", widget_central)
        boton_alzado.setGeometry(90, 90, 81, 23)
        boton_alzado.clicked.connect(self.renderizador.ver_alzado)

        boton_planta = QPushButton("Planta (2) '", widget_central)
        boton_planta.setGeometry(180, 90, 81, 23)
        boton_planta.clicked.connect(self.renderizador.ver_planta)

        boton_perfil = QPushButton("Perfil (3) '''", widget_central)
        boton_perfil.setGeometry(270, 90, 81, 23)
        boton_perfil.clicked.connect(self.renderizador.ver_perfil)

        boton_punto = QPushButton("Crear", widget_central)
        boton_punto.setGeometry(0, 248, 151, 20)
        boton_punto.clicked.connect(self.comprobar_punto)

        boton_recta = QPushButton("Crear", widget_central)
        boton_recta.setGeometry(160, 228, 151, 20)
        boton_recta.clicked.connect(self.comprobar_recta)

        boton_plano = QPushButton("Crear", widget_central)
        boton_plano.setGeometry(320, 248, 151, 20)
        boton_plano.clicked.connect(self.comprobar_plano)

        self.valor_distancia_origen = QSpinBox(widget_central)
        self.valor_distancia_origen.setGeometry(100, 140, 51, 20)
        self.valor_distancia_origen.setRange(-499, 499)

        self.valor_alejamiento = QSpinBox(widget_central)
        self.valor_alejamiento.setGeometry(100, 160, 51, 20)
        self.valor_alejamiento.setRange(-499, 499)

        self.valor_cota = QSpinBox(widget_central)
        self.valor_cota.setGeometry(100, 180, 51, 20)
        self.valor_cota.setRange(-499, 499)

        self.punto_recta_1 = QComboBox(widget_central)
        self.punto_recta_1.setGeometry(205, 140, 105, 22)
        self.punto_recta_2 = QComboBox(widget_central)
        self.punto_recta_2.setGeometry(205, 160, 105, 21)
        self.punto_plano_1 = QComboBox(widget_central)
        self.punto_plano_1.setGeometry(365, 140, 105, 22)
        self.punto_plano_2 = QComboBox(widget_central)
        self.punto_plano_2.setGeometry(365, 160, 105, 22)
        self.punto_plano_3 = QComboBox(widget_central)
        self.punto_plano_3.setGeometry(365, 180, 105, 22)

        self.punto_nombre = QPlainTextEdit(widget_central)
        self.punto_nombre.setGeometry(0, 220, 151, 25)
        self.recta_nombre = QPlainTextEdit(widget_central)
        self.recta_nombre.setGeometry(160, 200, 151, 25)
        self.plano_nombre = QPlainTextEdit(widget_central)
        self.plano_nombre.setGeometry(320, 220, 151, 25)

        self.tercera_proyeccion = QCheckBox("Tercera proyección", dock_diedrico)
        self.tercera_proyeccion.setGeometry(58, 3, 111, 17)

        self.ver_puntos = QCheckBox("Puntos", dock_diedrico)
        self.ver_puntos.setGeometry(172, 3, 61, 17)
        self.ver_puntos.setChecked(True)

        self.ver_rectas = QCheckBox("Rectas", dock_diedrico)
        self.ver_rectas.setGeometry(230, 3, 61, 17)
        self.ver_rectas.setChecked(True)

        self.ver_planos = QCheckBox("Planos", dock_diedrico)
        self.ver_planos.setGeometry(288, 3, 70, 17)
        self.ver_planos.setChecked(True)

        widget_punto = QWidget(widget_central)
        widget_punto.setGeometry(0, 270, 150, 210)
        vertical_punto = QVBoxLayout(widget_punto)
        vertical_punto.setContentsMargins(0, 0, 0, 0)
        self.lista_puntos = QListWidget(widget_punto)
        vertical_punto.addWidget(self.lista_puntos)

        widget_recta = QWidget(widget_central)
        widget_recta.setGeometry(160, 250, 150, 230)
        vertical_recta = QVBoxLayout(widget_recta)
        vertical_recta.setContentsMargins(0, 0, 0, 0)
        self.lista_rectas = QListWidget(widget_recta)
        vertical_recta.addWidget(self.lista_rectas)

        widget_planos = QWidget(widget_central)
        widget_planos.setGeometry(320, 270, 151, 210)
        vertical_planos = QVBoxLayout(widget_planos)
        vertical_planos.setContentsMargins(0, 0, 0, 0)
        self.lista_planos = QListWidget(widget_planos)
        vertical_planos.addWidget(self.lista_planos)

        herramientas = QLabel("Herramientas:", widget_central, font=fuente)
        herramientas.setGeometry(0, 485, 100, 16)

        punto_medio = QPushButton("Punto medio", widget_central)
        punto_medio.setGeometry(0, 505, 91, 31)
        self.punto_medio = PuntoMedio()
        punto_medio.clicked.connect(self.punto_medio.abrir)

        distancia = QPushButton("Distancia", widget_central)
        distancia.setGeometry(100, 505, 101, 31)
        self.distancia = Distancia()
        distancia.clicked.connect(self.distancia.abrir)

        interseccion = QPushButton("Crear intersección", widget_central)
        interseccion.setGeometry(210, 505, 101, 31)
        self.interseccion = Interseccion()
        interseccion.clicked.connect(self.interseccion.abrir)

        proyectar = QPushButton("Proyectar", widget_central)
        proyectar.setGeometry(320, 505, 71, 31)
        self.proyectar = Proyectar()
        proyectar.clicked.connect(self.proyectar.abrir)

        bisectriz = QPushButton("Bisectriz", widget_central)
        bisectriz.setGeometry(400, 505, 71, 31)
        self.bisectriz = Bisectriz()
        bisectriz.clicked.connect(self.bisectriz.abrir)

        perpendicularidad = QLabel("Perpendicularidad:", widget_central, font=fuente)
        perpendicularidad.setGeometry(0, 545, 120, 16)

        recta_perpendicular_recta = QPushButton("Crear recta \nperpendicular a recta", widget_central)
        recta_perpendicular_recta.setGeometry(0, 565, 151, 41)
        self.recta_perpendicular_recta = RectaPerpendicularARecta()
        recta_perpendicular_recta.clicked.connect(self.recta_perpendicular_recta.abrir)

        recta_perpendicular_plano = QPushButton("Crear recta \nperpendicular a plano", widget_central)
        recta_perpendicular_plano.setGeometry(160, 565, 151, 41)
        self.recta_perpendicular_plano = RectaPerpendicularAPlano()
        recta_perpendicular_plano.clicked.connect(self.recta_perpendicular_plano.abrir)

        plano_perpendicular_plano = QPushButton("Crear plano\nperpendicular a plano", widget_central)
        plano_perpendicular_plano.setGeometry(320, 565, 151, 41)
        self.plano_perpendicular_plano = PlanoPerpendicularAPlano()
        plano_perpendicular_plano.clicked.connect(self.plano_perpendicular_plano.abrir)

        paralelismo = QLabel("Paralelismo:", widget_central, font=fuente)
        paralelismo.setGeometry(0, 615, 100, 16)

        recta_paralela_recta = QPushButton("Crear recta paralela a recta", widget_central)
        recta_paralela_recta.setGeometry(0, 635, 231, 31)
        self.recta_paralela_recta = RectaParalelaARecta()
        recta_paralela_recta.clicked.connect(self.recta_paralela_recta.abrir)

        plano_paralelo_plano = QPushButton("Crear plano paralelo a plano", widget_central)
        plano_paralelo_plano.setGeometry(240, 635, 231, 31)
        self.plano_paralelo_plano = PlanoParaleloAPlano()
        plano_paralelo_plano.clicked.connect(self.plano_paralelo_plano.abrir)

        # Variables para permitir borrar los elementos, se asigna una diferente a cada fila
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
        self.modo_oscuro = True
        self.cambiar_modo()
        self.setCentralWidget(widget_central)
        self.show()

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

        y = self.renderizador.y
        z = self.renderizador.z

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

    def evitar_nombre_punto_blanco(self, nombre: str):
        # Genera nombres genéricos si no se provee uno
        if nombre == "":
            nombre = self.mayusculas.__next__()
        return nombre

    def evitar_nombre_recta_blanco(self, nombre: str):
        # Genera nombres genéricos si no se provee uno
        if nombre == "":
            nombre = self.minusculas.__next__()
        return nombre

    def evitar_nombre_plano_blanco(self, nombre: str):
        # Genera nombres genéricos si no se provee uno
        if nombre == "":
            nombre = self.alfabeto_griego.__next__()
        return nombre

    def comprobar_punto(self):
        nombre = self.punto_nombre.toPlainText()
        do = self.valor_distancia_origen.value()
        alejamiento = self.valor_alejamiento.value()
        cota = self.valor_cota.value()
        nombre = self.evitar_nombre_punto_blanco(nombre)
        nombre = f"{nombre}({do}, {alejamiento}, {cota})"
        self.crear_punto(nombre, Point3D(do, alejamiento, cota))

    def crear_punto(self, nombre, sympy):
        punto = Punto(self.id_punto, nombre, sympy)
        item = QListWidgetItem()
        item.setSizeHint(punto.minimumSizeHint())
        self.lista_puntos.addItem(item)
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
        elif punto1.coordenadas == punto2.coordenadas:
            QMessageBox.critical(self, "Error al crear la recta",
                                 "La recta debe ser creada a partir de dos puntos no coincidentes")
        else:
            nombre = self.evitar_nombre_recta_blanco(self.recta_nombre.toPlainText())
            nombre = f"{nombre}({punto1.nombre}, {punto2.nombre})"
            sympy = Line3D(punto1.sympy, punto2.sympy)
            self.crear_recta(nombre, sympy, [punto1.sympy, punto2.sympy])

    def crear_recta(self, nombre, sympy, puntos=None):
        recta = Recta(self.id_recta, nombre, sympy, puntos)
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

        elif len({punto1.coordenadas, punto2.coordenadas, punto3.coordenadas}) < 3:
            QMessageBox.critical(self, "Error al crear el plano",
                                 "Dos de los puntos proporcionados son coincidentes")
        elif Point3D.is_collinear(punto1.sympy, punto2.sympy, punto3.sympy):
            QMessageBox.critical(self, "Error al crear el plano",
                                 "El plano debe ser creado por tres puntos no alineados")

        else:
            nombre = self.evitar_nombre_plano_blanco(self.plano_nombre.toPlainText())
            nombre = f"{nombre}({punto1.nombre}, {punto3.nombre}, {punto2.nombre})"
            plano = Plane(punto1.sympy, punto2.sympy, punto3.sympy)
            self.crear_plano(nombre, plano, puntos=[punto1.coordenadas, punto2.coordenadas, punto3.coordenadas])

    def crear_plano(self, nombre, sympy, puntos=None):
        plano = Plano(self.id_plano, nombre, sympy, puntos)
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

    def borrar_todos_los_elementos(self):
        self.lista_puntos.clear()
        self.lista_rectas.clear()
        self.lista_planos.clear()
        self.elegir_puntos_recta()
        self.elegir_puntos_plano()

    def guardar(self):
        try:
            nombre, extension = QFileDialog.getSaveFileName(self, "Guardar", "", "Diédrico (*.diedrico)")

            with open(nombre, 'wb') as archivo:
                dump(self.recolectar_elementos(), archivo)

        except OSError:
            QMessageBox.critical(self, "Error al guardar", "Se ha producido un error al guardar el archivo")

    def recolectar_elementos(self) -> dict:
        elementos = {"Puntos": [], "Rectas": [], "Planos": []}

        for i in range(self.lista_puntos.count()):
            punto = self.lista_puntos.itemWidget(self.lista_puntos.item(i)).guardar()
            elementos["Puntos"].append(punto)

        for i in range(self.lista_rectas.count()):
            recta = self.lista_rectas.itemWidget(self.lista_rectas.item(i)).guardar()
            elementos["Rectas"].append(recta)

        for i in range(self.lista_planos.count()):
            plano = self.lista_planos.itemWidget(self.lista_planos.item(i)).guardar()
            elementos["Planos"].append(plano)

        return elementos

    def abrir(self):
        try:
            nombre, extension = QFileDialog.getOpenFileName(self, "Abrir", "", "Diédrico (*.diedrico)")

            with open(nombre, 'rb') as archivo:
                elementos = loads(archivo.read())

                for punto in elementos["Puntos"]:
                    self.crear_punto(punto["Nombre"], punto["Sympy"])

                for recta in elementos["Rectas"]:
                    if "Punto_1" in recta:
                        puntos = (recta["Punto_1"], recta["Punto_2"])
                        self.crear_recta(recta["Nombre"], recta["Sympy"], puntos)
                    else:
                        self.crear_recta(recta["Nombre"], recta["Sympy"])

                for plano in elementos["Planos"]:
                    if "Punto_1" in plano:
                        puntos = (plano["Punto_1"], plano["Punto_2"], plano["Punto_3"])
                        self.crear_plano(plano["Nombre"], plano["Sympy"], puntos)
                    else:
                        self.crear_plano(plano["Nombre"], plano["Sympy"])
        except OSError:
            QMessageBox.critical(self, "Error al abrir", "Se ha producido un error al abrir el archivo")

    def cambiar_modo(self):
        if self.modo_oscuro:
            self.vista.setStyleSheet("background-color: rgb(240, 240, 240)")
            self.diedrico.setStyleSheet("background-color: white")
            self.diedrico.pen_base.setColor(QColor(0, 0, 0))
            modo_claro = QPalette(self.style().standardPalette())
            evento_principal.setPalette(modo_claro)
            self.modo_oscuro = False
            self.accion_modo_oscuro.setText("Cambiar a modo oscuro")

        else:
            self.vista.setStyleSheet("background-color: rgb(20, 20, 20)")
            self.diedrico.setStyleSheet("background-color: rgb(40, 40, 40)")
            self.diedrico.pen_base.setColor(QColor(200, 200, 200))
            modo_oscuro = QPalette()
            modo_oscuro.setColor(QPalette.Window, QColor(53, 53, 53))
            modo_oscuro.setColor(QPalette.WindowText, Qt.white)
            modo_oscuro.setColor(QPalette.Base, QColor(25, 25, 25))
            modo_oscuro.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
            modo_oscuro.setColor(QPalette.Text, Qt.white)
            modo_oscuro.setColor(QPalette.Button, QColor(53, 53, 53))
            modo_oscuro.setColor(QPalette.ButtonText, Qt.white)
            modo_oscuro.setColor(QPalette.Link, QColor(200, 130, 218))
            modo_oscuro.setColor(QPalette.Highlight, QColor(42, 130, 218))
            modo_oscuro.setColor(QPalette.HighlightedText, Qt.black)
            evento_principal.setPalette(modo_oscuro)
            self.modo_oscuro = True
            self.accion_modo_oscuro.setText("Cambiar a modo claro")

    def closeEvent(self, evento):
        exit()

    def sizeHint(self):
        return QSize(1200, 800)


if __name__ == "__main__":
    evento_principal = QApplication([])
    evento_principal.setStyle('Fusion')
    programa = VentanaPrincipal()

    # Reducir el zoom un poco para que quepa mejor
    programa.diedrico.zoom_out()
    programa.diedrico.zoom_out()
    evento_principal.exec()
