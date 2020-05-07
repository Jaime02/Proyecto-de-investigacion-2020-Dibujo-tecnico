from math import atan2, sin, cos, acos, radians

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QMessageBox, QAction, QColorDialog, QMenu
from sympy import Point3D, Line3D, Plane, Segment3D, intersection

from . import ventanas_base


class EntidadGeometrica(QWidget):
    def __init__(self, programa, internal_id: int, nombre: str, sympy):
        QWidget.__init__(self)
        self.programa = programa
        self.id = internal_id
        self.nombre = nombre
        self.sympy = sympy
        self.customContextMenuRequested.connect(self.context_menu)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.menu = QMenu()
        self.accion_borrar = QAction("Borrar")
        self.accion_borrar.triggered.connect(lambda: self.borrar(self.id))
        self.render = QAction("Visible", checkable=True, checked=True)
        self.actualizar_nombre = QAction("Renombrar")

        self.ventana_cambiar_nombre = ventanas_base.VentanaRenombrar()
        self.actualizar_nombre.triggered.connect(self.ventana_cambiar_nombre.abrir)
        self.ventana_cambiar_nombre.boton_crear.clicked.connect(self.cambiar_nombre)

        self.menu.addAction(self.accion_borrar)
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

    def cambiar_color(self):
        color_dialog = QColorDialog()
        color = color_dialog.getColor(options=QColorDialog.ShowAlphaChannel)
        if color.isValid():
            color = color.getRgb()
            self.color = tuple([i / 255 for i in color])

    def context_menu(self):
        self.menu.exec(QCursor.pos())

    def cambiar_nombre(self):
        nombre = self.ventana_cambiar_nombre.widget_texto.text()
        if nombre:
            nombres = []
            for i in range(self.programa.lista_puntos.count()):
                nombres.append(self.programa.lista_puntos.itemWidget(self.programa.lista_puntos.item(i)).nombre)
            for i in range(self.programa.lista_rectas.count()):
                nombres.append(self.programa.lista_rectas.itemWidget(self.programa.lista_rectas.item(i)).nombre)
            for i in range(self.programa.lista_planos.count()):
                nombres.append(self.programa.lista_planos.itemWidget(self.programa.lista_planos.item(i)).nombre)

            if nombre in nombres:
                QMessageBox.critical(self, "Error al cambiar el nombre",
                                     "Ha introducido un nombre que ya está siendo usado")
            else:
                self.nombre = nombre
                self.etiqueta.setText(nombre)
                self.programa.actualizar_opciones()
        else:
            QMessageBox.critical(self, "Error al cambiar el nombre", "Ha introducido un nombre en blanco")


class Punto(EntidadGeometrica):
    def __init__(self, programa, internal_id: int, nombre: str, sympy: Point3D):
        EntidadGeometrica.__init__(self, programa, internal_id, nombre, sympy)

        self.coordenadas = sympy.coordinates
        self.x = sympy.x
        self.y = sympy.y
        self.z = sympy.z

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

    def borrar(self, borrar_id: int):
        for indice in range(self.programa.lista_puntos.count()):
            item = self.programa.lista_puntos.item(indice)
            widget = self.programa.lista_puntos.itemWidget(item)
            if widget.id == borrar_id:
                self.programa.lista_puntos.takeItem(self.programa.lista_puntos.row(item))
                break
        self.programa.actualizar_opciones()


class Recta(EntidadGeometrica):
    def __init__(self, programa, internal_id: int, nombre: str, sympy: Line3D, puntos: list = None):
        EntidadGeometrica.__init__(self, programa, internal_id, nombre, sympy)

        self.ver_traza_horizontal = QAction("Traza en PH", checkable=True, checked=True)
        self.menu.addAction(self.ver_traza_horizontal)
        self.ver_traza_vertical = QAction("Traza en PV", checkable=True, checked=True)
        self.menu.addAction(self.ver_traza_vertical)

        self.infinita = QAction("Infinita", checkable=True, checked=True)
        self.menu.addAction(self.infinita)

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

    def borrar(self, borrar_id: int):
        for indice in range(self.programa.lista_rectas.count()):
            item = self.programa.lista_rectas.item(indice)
            widget = self.programa.lista_rectas.itemWidget(item)
            if widget.id == borrar_id:
                self.programa.lista_rectas.takeItem(self.programa.lista_rectas.row(item))
                break


class Plano(EntidadGeometrica):
    def __init__(self, programa, internal_id: int, nombre: str, sympy: Plane, puntos: list = None):
        EntidadGeometrica.__init__(self, programa, internal_id, nombre, sympy)

        self.plano_vertical_bordes = (Segment3D(Point3D(500, 0, 500), Point3D(-500, 0, 500)),
                                      Segment3D(Point3D(-500, 0, 500), Point3D(-500, 0, -500)),
                                      Segment3D(Point3D(-500, 0, -500), Point3D(500, 0, -500)),
                                      Segment3D(Point3D(500, 0, -500), Point3D(500, 0, 500)))

        self.plano_horizontal_bordes = (Segment3D(Point3D(500, 500, 0), Point3D(-500, 500, 0)),
                                        Segment3D(Point3D(-500, 500, 0), Point3D(-500, -500, 0)),
                                        Segment3D(Point3D(-500, -500, 0), Point3D(500, -500, 0)),
                                        Segment3D(Point3D(500, -500, 0), Point3D(500, 500, 0)))

        self.vector_normal = sympy.normal_vector
        self.infinito = QAction("Infinito", checkable=True, checked=True)
        self.menu.addAction(self.infinito)

        if not puntos:
            self.infinito.setDisabled(True)
            self.puntos = False
        else:
            self.puntos = puntos
            self.punto_1, self.punto_2, self.punto_3 = puntos[0], puntos[1], puntos[2]

        self.limites = self.limites()

        # Color por defecto del plano, azul
        self.color = (0, 0, 200, 0.4)
        self.editar_color = QAction("Color")
        self.menu.addAction(self.editar_color)
        self.editar_color.triggered.connect(self.cambiar_color)

        self.ver_traza_horizontal = QAction("Traza en PH", checkable=True, checked=True)
        self.menu.addAction(self.ver_traza_horizontal)
        self.ver_traza_vertical = QAction("Traza en PV", checkable=True, checked=True)
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
                    if abs(punto_en_LT[0][0]) <= 500:
                        self.punto_en_LT = punto_en_LT[0]

                    if self.traza_h[0][1] < self.traza_h[1][1]:
                        self.traza_h[0], self.traza_h[1] = self.traza_h[1], self.traza_h[0]
                    if self.traza_v[0][2] < self.traza_v[1][2]:
                        self.traza_v[0], self.traza_v[1] = self.traza_v[1], self.traza_v[0]

                    self.traza_h.insert(1, self.punto_en_LT)
                    self.traza_v.insert(1, self.punto_en_LT)

                    self.ver_trazas_negativas = QAction("Ver trazas negativas", checkable=True, checked=True)
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

        # Intersección con las doce aristas del cubo
        for i in range(12):
            inter = intersection(plano, self.aristas[i])
            if inter:
                if not isinstance(inter[0], Segment3D):
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

    def borrar(self, borrar_id: int):
        for indice in range(self.programa.lista_planos.count()):
            item = self.programa.lista_planos.item(indice)
            widget = self.programa.lista_planos.itemWidget(item)
            if widget.id == borrar_id:
                self.programa.lista_planos.takeItem(self.programa.lista_planos.row(item))
                break


class Circunferencia(EntidadGeometrica):
    def __init__(self, programa, internal_id: int, nombre: str, vector_normal, radio, centro):
        EntidadGeometrica.__init__(self, programa, internal_id, nombre, None)
        self.puntos = self.calcular_circunferencia(vector_normal, radio, centro)

    @staticmethod
    def calcular_circunferencia(vector_normal, radio, centro):
        # TODO: Mejorar el punto en el que la circunferencia toca a los planos de proyección
        # Rotación de rodrigues
        def rodri(v: Vector, k: Vector, theta):
            return v * cos(theta) + k.cross(v) * sin(theta) + k * (k.dot(v)) * (1 - cos(theta))

        def calcular_vector_v(r: int, t: int):
            return Vector([r * cos(radians(t)), r * sin(radians(t)), 0])

        # Vector E, eje Z
        vector_e = Vector([0, 0, 1])
        # El vector normal al plano paralelo a la circunferencia
        vector_u = Vector(vector_normal, normalizar=True)
        angulo_theta = acos(vector_e.dot(vector_u)/vector_u.modulo())
        vector_k = vector_e.cross(vector_u)/(vector_e.cross(vector_u).modulo())

        # Hacer que el número de segmentos dependa de r, mejora la resolución de la circunferencia cuando el r es grande
        numero_de_lados = radio + 20

        # Lista que guarda los puntos
        puntos = []

        for i in range(1, numero_de_lados + 1):
            vector_v = calcular_vector_v(radio, i * 360 / numero_de_lados)
            punto = rodri(vector_v, vector_k, angulo_theta)
            for j in range(3):
                punto.coords[j] = round(punto.coords[j] + centro.coordinates[j], 4)
            puntos.append(punto.coords)

        return puntos

    def borrar(self, borrar_id: int):
        for indice in range(self.programa.lista_circunferencias.count()):
            item = self.programa.lista_circunferencias.item(indice)
            widget = self.programa.lista_circunferencias.itemWidget(item)
            if widget.id == borrar_id:
                self.programa.lista_circunferencias.takeItem(self.programa.lista_circunferencias.row(item))
                break


class Vector:
    def __init__(self, coords, normalizar=False):
        if normalizar:
            self.coords = self.normalizar(coords)
        else:
            self.coords = coords

    def __mul__(self, scalar):
        # Producto escalar
        return Vector([coord * scalar for coord in self.coords])

    def __add__(self, other):
        if isinstance(other, (int, float)):
            # Suma de un vector con un escalar
            return Vector(self.coords[0] + other, self.coords[1] + other, self.coords[2] + other)
        else:
            # Suma de un vector mas otro
            return Vector([self.coords[0] + other.coords[0],
                           self.coords[1] + other.coords[1],
                           self.coords[2] + other.coords[2]])

    def __repr__(self):
        return str(self.coords)

    def __truediv__(self, scalar):
        return Vector([coord / scalar for coord in self.coords])

    def dot(self, vec):
        # Producto escalar
        return sum([self.coords[indx] * vec.coords[indx] for indx in range(3)])

    def cross(self, vec):
        # Producto vectorial
        return Vector([self.coords[1] * vec.coords[2] - self.coords[2] * vec.coords[1],
                       self.coords[2] * vec.coords[0] - self.coords[0] * vec.coords[2],
                       self.coords[0] * vec.coords[1] - self.coords[1] * vec.coords[0]])

    def modulo(self):
        return sum([coord ** 2 for coord in self.coords]) ** 0.5

    @staticmethod
    def normalizar(vector: list):
        # Normaliza los vectores para que tengan la misma longitud
        length = (vector[0] ** 2 + vector[1] ** 2 + vector[2] ** 2) ** 0.5
        if length == 0:
            return [0, 0, 0]
        vector = [x / length for x in vector]
        return vector