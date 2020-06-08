from math import atan2, sin, cos, acos, radians, degrees

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QMessageBox, QAction, QColorDialog, QMenu

from . import ventanas_base


class Vector:
    def __init__(self, coords, normalizar=False):
        if normalizar:
            self.coords = self.normalizar(coords)
        else:
            self.coords = coords
        self.x, self.y, self.z = self.coords

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

    def __sub__(self, other):
        if isinstance(other, (int, float)):
            # Suma de un vector con un escalar
            return Vector(self.coords[0] - other, self.coords[1] - other, self.coords[2] - other)
        else:
            # Suma de un vector mas otro
            return Vector([self.coords[0] - other.coords[0],
                           self.coords[1] - other.coords[1],
                           self.coords[2] - other.coords[2]])

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
    def normalizar(vector):
        # Normaliza los vectores para que tengan la misma longitud
        longitud = (vector.x ** 2 + vector.y ** 2 + vector.z ** 2) ** 0.5
        if longitud == 0:
            return [0, 0, 0]
        vector = [i / longitud for i in vector.coords]
        return vector


class Punto:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
        self.coords = (x, y, z)

    def __sub__(self, other):
        if isinstance(other, Punto):
            return Punto(*[self.coords[i] - other.coords[i] for i in range(3)])
        return Punto(*[self.coords[i] - other.coords for i in range(3)])

    def __add__(self, other):
        if isinstance(other, Punto):
            return Punto(*[self.coords[i] + other.coords[i] for i in range(3)])
        return Punto(*[self.coords[i] + other.coords for i in range(3)])

    def __mul__(self, escalar):
        return Punto(*[self.coords[i] * escalar for i in range(3)])

    def __rmul__(self, escalar):
        return Punto(*[self.coords[i] * escalar for i in range(3)])

    def distancia(self, punto):
        return sum([(self.coords[i] - punto.coords[i]) ** 2 for i in range(3)]) ** 0.5

    def colinear(self, p2, p3):
        recta = Recta(p2, p3)
        if recta.comprobar_punto_en_recta(self):
            return True
        return False


class Recta:
    def __init__(self, p1: Punto, p2: Punto):
        self.p1 = p1
        self.p2 = p2
        self.ecuacion_parametrica = self.calcular_ecuacion_parametrica

    def comprobar_punto_en_recta(self, p):
        if self.p2.x - self.p1.x == 0:
            if self.p2.y - self.p1.y == 0:
                l = (p.z - self.p1.z) / (self.p2.z - self.p1.z)
            else:
                l = (p.y - self.p1.y) / (self.p2.y - self.p1.y)
        else:
            l = (p.x - self.p1.x) / (self.p2.x - self.p1.x)
        if self.p1.x + l * (self.p2.x - self.p1.x) == p.x:
            if self.p1.y + l * (self.p2.y - self.p1.y) == p.y:
                if self.p1.z + l * (self.p2.z - self.p1.z) == p.z:
                    return True
        return False

    @property
    def calcular_ecuacion_parametrica(self):
        return {"x": (self.p1.x, self.p2.x - self.p1.x),
                "y": (self.p1.y, self.p2.y - self.p1.y),
                "z": (self.p1.z, self.p2.z - self.p1.z)}

    def evaluar(self, escalar):
        return self.p1 + escalar * (self.p2 - self.p1)

    def interseccion_con_recta(self, recta):
        ec1 = self.ecuacion_parametrica
        ec2 = recta.ecuacion_parametrica

        a = ec1["x"][1]
        b = ec2["x"][1]
        c = ec2["x"][0] - ec1["x"][0]
        a0 = ec1["y"][1]
        b0 = ec2["y"][1]
        c0 = ec2["y"][0] - ec1["y"][0]
        if a != 0:
            nu = (c0 - a0 * c / a) / (b0 - b * a0 / a)
            return recta.evaluar(nu)


class Segmento(Recta):
    def __init__(self, p1: Punto, p2: Punto):
        Recta.__init__(self, p1, p2)
        self.distancia_entre_extremos = p1.distancia(p2)

    def comprobar_punto_en_segmento(self, p):
        if self.comprobar_punto_en_recta(p):
            if self.distancia_entre_extremos > self.p1.distancia(
                    p) and self.distancia_entre_extremos > self.p2.distancia(p):
                return True
            else:
                return False
        else:
            return False


class Plano:
    def __init__(self, p1, p2=None, p3=None, normal=None):
        if normal:
            self.p1 = p1
            self.ecuacion = {"A": normal.x, "B": normal.y, "C": normal.z,
                             "D": normal.x * p1.x + normal.y * p1.y + normal.z * p1.z}
            self.vector_normal = Vector(normal)
        else:
            self.p1 = p1
            self.p2 = p2
            self.p3 = p3
            self.ecuacion = self.calcular_ecuacion(p1, p2, p3)
            self.vector_normal = Vector([self.ecuacion["A"], self.ecuacion["B"], self.ecuacion["C"]])

    @staticmethod
    def calcular_ecuacion(p1, p2, p3):
        v1 = p2 - p1
        v2 = p3 - p1
        a = v1.y * v2.z - v1.z * v2.y
        b = -(v1.x * v2.z - v1.z * v2.x)
        c = v1.x * v2.y - v1.y * v2.x
        return {"A": a, "B": b, "C": c, "D": a * p1.x + b * p1.y + c * p1.z}

    def interseccion_con_recta(self, r: Recta):
        recta = r.ecuacion_parametrica
        plano = self.ecuacion
        denominador = plano["A"] * recta["x"][1] + plano["B"] * recta["y"][1] + plano["C"] * recta["z"][1]
        if denominador == 0:
            # La recta es paralela al plano
            if self.punto_pertenece_a_plano(r.p1):
                return "Recta contenida en plano"
            return False
        numerador = plano["D"] - plano["A"] * recta["x"][0] - plano["B"] * recta["y"][0] - plano["C"] * recta["z"][0]
        return r.evaluar(numerador / denominador)

    def punto_pertenece_a_plano(self, p: Punto):
        if self.ecuacion["A"] * p.x + self.ecuacion["B"] * p.y + self.ecuacion["C"] * p.z == self.ecuacion["D"]:
            return True
        else:
            return False

    def interseccion_con_segmento(self, s: Segmento):
        punto = self.interseccion_con_recta(s)
        if punto:
            if punto == "Recta contenida en plano":
                return punto
            if s.comprobar_punto_en_segmento(punto):
                return punto
            else:
                return False
        return False


class WidgetFila(QWidget):
    def __init__(self, programa, internal_id: int, nombre: str):
        QWidget.__init__(self)
        self.programa = programa
        self.id = internal_id
        self.nombre = nombre
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

        # Por defecto las entidades geométricas tienen color negro
        self.color = (0, 0, 0, 1)

        # Vértices del cubo
        vertices = (Punto(500, 500, 500), Punto(-500, 500, 500), Punto(-500, -500, 500), Punto(500, -500, 500),
                    Punto(500, 500, -500), Punto(-500, 500, -500), Punto(-500, -500, -500), Punto(500, -500, -500))
        # Aristas del cubo
        self.aristas = (Segmento(vertices[0], vertices[1]), Segmento(vertices[1], vertices[2]),
                        Segmento(vertices[2], vertices[3]), Segmento(vertices[3], vertices[0]),
                        Segmento(vertices[0], vertices[4]), Segmento(vertices[1], vertices[5]),
                        Segmento(vertices[2], vertices[6]), Segmento(vertices[3], vertices[7]),
                        Segmento(vertices[4], vertices[5]), Segmento(vertices[5], vertices[6]),
                        Segmento(vertices[6], vertices[7]), Segmento(vertices[7], vertices[4]))

        # Caras del cubo
        self.planos = (Plano(vertices[0], vertices[1], vertices[2]), Plano(vertices[0], vertices[1], vertices[5]),
                       Plano(vertices[0], vertices[4], vertices[7]), Plano(vertices[4], vertices[5], vertices[7]),
                       Plano(vertices[2], vertices[3], vertices[7]), Plano(vertices[1], vertices[2], vertices[5]))
        self.plano_vertical = Plano(Punto(0, 0, 1), Punto(0, 0, 0), Punto(1, 0, 0))
        self.plano_horizontal = Plano(Punto(0, 1, 0), Punto(0, 0, 0), Punto(1, 0, 0))

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
            if self.programa.evitar_nombre_duplicado(nombre):
                self.nombre = nombre
                self.etiqueta.setText(nombre)
                self.programa.actualizar_opciones()
        else:
            QMessageBox.critical(self, "Error al cambiar el nombre", "Ha introducido un nombre en blanco")


class WidgetPunto(WidgetFila):
    def __init__(self, programa, internal_id: int, nombre: str, entidad_geometrica: Punto):
        WidgetFila.__init__(self, programa, internal_id, nombre)
        self.entidad_geometrica = entidad_geometrica
        self.coordenadas = entidad_geometrica.coords
        self.x = entidad_geometrica.x
        self.y = entidad_geometrica.y
        self.z = entidad_geometrica.z

        self.cuadrante = self.calcular_cuadrante(self.coordenadas)

        self.grosor = 5
        self.accion_grosor = QAction("Cambiar grosor")
        self.ventana_cambiar_grosor = ventanas_base.VentanaCambiarGrosorPunto()
        self.ventana_cambiar_grosor.boton_crear.clicked.connect(self.cambiar_grosor)
        self.accion_grosor.triggered.connect(self.ventana_cambiar_grosor.abrir)
        self.menu.addAction(self.accion_grosor)

    def guardar(self) -> dict:
        return {"Nombre": self.nombre, "Sympy": self.entidad_geometrica}

    def borrar(self, borrar_id: int):
        for indice in range(self.programa.lista_puntos.count()):
            item = self.programa.lista_puntos.item(indice)
            widget = self.programa.lista_puntos.itemWidget(item)
            if widget.id == borrar_id:
                self.programa.lista_puntos.takeItem(self.programa.lista_puntos.row(item))
                break
        self.programa.actualizar_opciones()

    @staticmethod
    def calcular_cuadrante(coordenadas) -> str:
        # Se considera que los puntos contenidos en el plano vertical positivo
        # o en el horizontal positivo pertenecen al primer cuadrante

        # Los contenidos en el PH- pertenecen al segundo cuadrante
        # Los contenidos en el PV- pertenecen al cuarto cuadrante

        if coordenadas[1] >= 0 and coordenadas[2] >= 0:
            return "I"
        elif coordenadas[1] < 0 <= coordenadas[2]:
            return "II"
        elif coordenadas[1] >= 0 > coordenadas[2]:
            return "IV"
        else:
            return "III"

    def cambiar_grosor(self):
        self.grosor = self.ventana_cambiar_grosor.spinbox_grosor.value()


class WidgetRecta(WidgetFila):
    def __init__(self, programa, internal_id: int, nombre: str, entidad_geometrica: Recta, puntos: list = None):
        WidgetFila.__init__(self, programa, internal_id, nombre)
        self.entidad_geometrica = entidad_geometrica
        self.grosor = 2
        self.accion_grosor = QAction("Cambiar grosor")
        self.ventana_cambiar_grosor = ventanas_base.VentanaCambiarGrosorRecta()
        self.ventana_cambiar_grosor.boton_crear.clicked.connect(self.cambiar_grosor)
        self.accion_grosor.triggered.connect(self.ventana_cambiar_grosor.abrir)
        self.menu.addAction(self.accion_grosor)

        self.ver_traza_horizontal = QAction("Traza en PH", checkable=True, checked=True)
        self.menu.addAction(self.ver_traza_horizontal)
        self.ver_traza_vertical = QAction("Traza en PV", checkable=True, checked=True)
        self.menu.addAction(self.ver_traza_vertical)

        self.infinita = QAction("Infinita", checkable=True, checked=True)
        self.menu.addAction(self.infinita)

        self.e = self.extremos(entidad_geometrica)
        # Extremos de la recta separados por cuadrantes
        self.extremos_I = tuple([i for i in self.e if i.y >= 0 and i.z >= 0])
        self.extremos_II = tuple([i for i in self.e if i.z > 0 > i.y or (i.y < 0 and i.z == 0)])
        self.extremos_III = tuple([i for i in self.e if i.y < 0 and i.z < 0])
        self.extremos_IV = tuple([i for i in self.e if i.y > 0 > i.z or (i.y == 0 and i.z < 0)])

        self.traza_v = self.calcular_traza_v()
        self.traza_h = self.calcular_traza_h()

        # Solo se pueden utilizar segmentos cuando la recta ha sido definida por dos puntos, podría ser mejorado
        if puntos:
            self.puntos = puntos
            self.cuadrante_punto_1 = WidgetPunto.calcular_cuadrante(puntos[0].coords)
            self.cuadrante_punto_2 = WidgetPunto.calcular_cuadrante(puntos[1].coords)
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

    def guardar(self):
        if self.puntos:
            return {"Nombre": self.nombre, "Punto_1": self.punto_1, "Punto_2": self.punto_2, "Sympy": self.entidad_geometrica}
        else:
            return {"Nombre": self.nombre, "Sympy": self.entidad_geometrica}

    def borrar(self, borrar_id: int):
        for indice in range(self.programa.lista_rectas.count()):
            item = self.programa.lista_rectas.item(indice)
            widget = self.programa.lista_rectas.itemWidget(item)
            if widget.id == borrar_id:
                self.programa.lista_rectas.takeItem(self.programa.lista_rectas.row(item))
                break

    def cambiar_grosor(self):
        self.grosor = self.ventana_cambiar_grosor.spinbox_grosor.value()

    def extremos(self, recta: Recta) -> tuple:
        intersecciones = []
        for i in range(6):
            interseccion = self.planos[i].interseccion_con_recta(recta)
            if interseccion:
                if all(abs(i) <= 500 for i in interseccion.coords):
                    intersecciones.append(interseccion)
        # Elimina duplicados
        intersecciones = tuple(set([i.coords for i in intersecciones]))
        intersecciones = tuple([Punto(*p) for p in intersecciones])
        return intersecciones

    def calcular_traza_h(self):
        traza_h = self.plano_horizontal.interseccion_con_recta(self.entidad_geometrica)
        if traza_h:
            if traza_h != "Recta contenida en plano":
                if all(abs(i) <= 500 for i in traza_h.coords):
                    return traza_h
            else:
                return "Contenida en PH"
        else:
            return False

    def calcular_traza_v(self):
        traza_v = self.plano_vertical.interseccion_con_recta(self.entidad_geometrica)
        if traza_v:
            if traza_v != "Recta contenida en plano":
                if all(abs(i) <= 500 for i in traza_v.coords):
                    return traza_v
            else:
                return "Contenida en PV"
        else:
            return False

    def trazas_entre_puntos(self):
        segmento = Segmento(self.punto_1, self.punto_2)
        interseccion_pv = self.plano_vertical.interseccion_con_segmento(segmento)
        interseccion_ph = self.plano_horizontal.interseccion_con_segmento(segmento)
        if interseccion_pv and interseccion_pv != "Contenida en PV":
            if interseccion_pv.z > 0:
                self.traza_v_entre_puntos = "PV+"
            else:
                self.traza_v_entre_puntos = "PV-"
        if interseccion_ph and interseccion_ph != "Contenida en PH":
            if interseccion_ph.y >= 0:
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
            if traza_v.z >= 0:
                partes['I'] = traza_v, extremos_I[0]
                partes['II'] = traza_v, extremos_II[0]
            else:
                partes['III'] = traza_v, extremos_III[0]
                partes['IV'] = traza_v, extremos_IV[0]
        elif not traza_v and traza_h:
            if traza_h.y >= 0:
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
            elif traza_v.z > 0 and traza_h.y > 0:
                partes['I'] = traza_v, traza_h
                partes['II'] = traza_v, extremos_II[0]
                partes['IV'] = traza_h, extremos_IV[0]
            elif traza_v.z < 0 and traza_h.y < 0:
                partes['II'] = extremos_II[0], traza_h
                partes['III'] = traza_h, traza_v
                partes['IV'] = traza_v, extremos_IV[0]
            elif traza_v.z > 0 and traza_h.y < 0:
                partes['I'] = extremos_I[0], traza_v
                partes['II'] = traza_v, traza_h
                partes['III'] = traza_h, extremos_III[0]
            else:
                partes['I'] = extremos_I[0], traza_h
                partes['IV'] = traza_h, traza_v
                partes['III'] = traza_v, extremos_III[0]
        return partes


class WidgetPlano(WidgetFila):
    def __init__(self, programa, internal_id: int, nombre: str, entidad_geometrica: Plano, puntos: list = None):
        WidgetFila.__init__(self, programa, internal_id, nombre)
        self.entidad_geometrica = entidad_geometrica
        self.infinito = QAction("Infinito", checkable=True, checked=True)
        self.menu.addAction(self.infinito)

        if not puntos:
            self.infinito.setDisabled(True)
            self.puntos = False
        else:
            self.puntos = puntos
            self.punto_1, self.punto_2, self.punto_3 = puntos[0], puntos[1], puntos[2]

        # Color por defecto del plano, azul
        self.color = (0, 0, 200, 0.4)
        self.editar_color = QAction("Color")
        self.menu.addAction(self.editar_color)
        self.editar_color.triggered.connect(self.cambiar_color)

        self.ver_traza_horizontal = QAction("Traza en PH", checkable=True, checked=True)
        self.menu.addAction(self.ver_traza_horizontal)
        self.ver_traza_vertical = QAction("Traza en PV", checkable=True, checked=True)
        self.menu.addAction(self.ver_traza_vertical)

        self.plano_vertical_bordes = (Segmento(Punto(500, 0, 500), Punto(-500, 0, 500)),
                                      Segmento(Punto(-500, 0, 500), Punto(-500, 0, -500)),
                                      Segmento(Punto(-500, 0, -500), Punto(500, 0, -500)),
                                      Segmento(Punto(500, 0, -500), Punto(500, 0, 500)))
        self.plano_horizontal_bordes = (Segmento(Punto(500, 500, 0), Punto(-500, 500, 0)),
                                        Segmento(Punto(-500, 500, 0), Punto(-500, -500, 0)),
                                        Segmento(Punto(-500, -500, 0), Punto(500, -500, 0)),
                                        Segmento(Punto(500, -500, 0), Punto(500, 500, 0)))

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

        if self.traza_h and self.traza_v:
            punto_en_lt = self.entidad_geometrica.interseccion_con_segmento(Segmento(Punto(500, 0, 0), Punto(-500, 0, 0)))
            if punto_en_lt and not isinstance(punto_en_lt, Segmento):
                if self.traza_h[0].y < self.traza_h[1].y:
                    self.traza_h[0], self.traza_h[1] = self.traza_h[1], self.traza_h[0]
                if self.traza_v[0].z < self.traza_v[1].z:
                    self.traza_v[0], self.traza_v[1] = self.traza_v[1], self.traza_v[0]
                self.traza_h.insert(1, punto_en_lt)
                self.traza_v.insert(1, punto_en_lt)

                self.ver_trazas_negativas = QAction("Ver trazas negativas", checkable=True, checked=True)
                self.menu.addAction(self.ver_trazas_negativas)

        self.limites = self.calcular_limites()
        self.partes = self.calcular_partes()

    def guardar(self):
        if self.puntos:
            return {"Nombre": self.nombre, "Punto_1": self.punto_1, "Punto_2": self.punto_2,
                    "Punto_3": self.punto_3, "Sympy": self.entidad_geometrica}
        else:
            return {"Nombre": self.nombre, "Sympy": self.entidad_geometrica}

    def borrar(self, borrar_id: int):
        for indice in range(self.programa.lista_planos.count()):
            item = self.programa.lista_planos.item(indice)
            widget = self.programa.lista_planos.itemWidget(item)
            if widget.id == borrar_id:
                self.programa.lista_planos.takeItem(self.programa.lista_planos.row(item))
                break

    def ordenar_vertices(self, puntos: list):
        # Si es un triángulo no hace falta ordenar su vértices
        if len(puntos) <= 3:
            return tuple(puntos)
        else:
            proyectados = []
            # Proyectar en:
            # Perfil
            if self.entidad_geometrica.vector_normal.y == self.entidad_geometrica.vector_normal.z == 0:
                for i in puntos:
                    punto = (i.y, i.z)
                    proyectados.append(punto)
            # Vertical
            elif self.entidad_geometrica.vector_normal.z == 0:
                for i in puntos:
                    punto = (i.x, i.z)
                    proyectados.append(punto)
            # Horizontal
            else:
                for i in puntos:
                    punto = (i.x, i.y)
                    proyectados.append(punto)

            centroide = self.centroide(proyectados)

            for index, punto in enumerate(proyectados):
                punto = (punto[0] - centroide[0], punto[1] - centroide[1])
                proyectados[index] = punto

            angulos = []
            for i in proyectados:
                angulos.append(atan2(i[0], i[1]))
            juntados = sorted(zip(angulos, puntos))
            ordenados = tuple([i[1] for i in juntados])
            return ordenados

    @staticmethod
    def centroide(puntos):
        x = 0
        y = 0
        for punto in puntos:
            x += punto[0]
            y += punto[1]
        return x / len(puntos), y / len(puntos)

    def calcular_limites(self):
        buenos = []
        # Intersección con las doce aristas del cubo
        for arista in self.aristas:
            inter = self.entidad_geometrica.interseccion_con_segmento(arista)
            if inter and inter != "Recta contenida en plano":
                buenos.append(inter)

        # Elimina duplicados
        buenos = list(set([p.coords for p in buenos]))
        buenos = [Punto(*p) for p in buenos]
        return self.ordenar_vertices(buenos)

    def calcular_partes(self):
        puntos = list(self.limites)
        partes = {'I': [], 'II': [], 'III': [], 'IV': []}
        for segmento in self.plano_vertical_bordes:
            interseccion = self.entidad_geometrica.interseccion_con_segmento(segmento)
            if interseccion:
                if interseccion == "Recta contenida en plano":
                    puntos.append(segmento.p1)
                    puntos.append(segmento.p2)
                else:
                    puntos.append(interseccion)
        for segmento in self.plano_horizontal_bordes:
            interseccion = self.entidad_geometrica.interseccion_con_segmento(segmento)
            if interseccion:
                if interseccion == "Recta contenida en plano":
                    puntos.append(segmento.p1)
                    puntos.append(segmento.p2)
                else:
                    puntos.append(interseccion)
        interseccion = self.entidad_geometrica.interseccion_con_segmento(Segmento(Punto(500, 0, 0), Punto(-500, 0, 0)))
        if interseccion:
            if interseccion == "Recta contenida en plano":
                puntos.append(Punto(500, 0, 0))
                puntos.append(Punto(-500, 0, 0))
            else:
                puntos.append(interseccion)
        for punto in puntos:
            if punto.y >= 0 and punto.z >= 0:
                partes['I'].append(punto)
            if punto.z >= 0 >= punto.y:
                partes['II'].append(punto)
            if punto.y <= 0 and punto.z <= 0:
                partes['III'].append(punto)
            if punto.y >= 0 >= punto.z:
                partes['IV'].append(punto)

        partes['I'] = self.ordenar_vertices(partes['I'])
        partes['II'] = self.ordenar_vertices(partes['II'])
        partes['III'] = self.ordenar_vertices(partes['III'])
        partes['IV'] = self.ordenar_vertices(partes['IV'])
        return partes

    def calcular_traza_h(self):
        if self.entidad_geometrica.vector_normal.x == 0 and self.entidad_geometrica.vector_normal.y == 0:
            return False
        else:
            trazas = []
            for i in range(4):
                if not len(trazas) == 2:
                    interseccion = self.entidad_geometrica.interseccion_con_segmento(self.plano_horizontal_bordes[i])
                    if interseccion and interseccion != "Recta contenida en plano":
                        trazas.append(interseccion)
            trazas = list(set(trazas))
            if len(trazas) == 1:
                return False
            else:
                return trazas

    def calcular_traza_v(self):
        if self.entidad_geometrica.vector_normal.x == 0 and self.entidad_geometrica.vector_normal.z == 0:
            return False
        else:
            trazas = []
            for i in range(4):
                if not len(trazas) == 2:
                    interseccion = self.entidad_geometrica.interseccion_con_segmento(self.plano_vertical_bordes[i])
                    if interseccion and interseccion != "Recta contenida en plano":
                        trazas.append(interseccion)
            trazas = list(set(trazas))
            if len(trazas) == 1:
                return False
            else:
                return trazas


class Circunferencia(WidgetFila):
    def __init__(self, programa, nombre: str, vector_normal=None, radio=None, centro=None, puntos=None):
        WidgetFila.__init__(self, programa, programa.id_circunferencia, nombre)
        programa.id_circunferencia += 1
        if not puntos:
            self.puntos = self.calcular_puntos(vector_normal, radio, centro)
        else:
            self.puntos = puntos

    @staticmethod
    def calcular_puntos(vector_normal, radio, centro):
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
        angulo_theta = acos(vector_e.dot(vector_u) / vector_u.modulo())
        denominador = vector_e.cross(vector_u).modulo()
        if denominador != 0:
            vector_k = vector_e.cross(vector_u) / (vector_e.cross(vector_u).modulo())
        else:
            vector_k = Vector([0, 0, 1])

        # Hacer que el número de segmentos dependa de r mejora la resolución de la circunferencia cuando el r es grande
        numero_de_lados = radio + 20

        puntos = []

        for i in range(1, numero_de_lados + 1):
            vector_v = calcular_vector_v(radio, i * 360 / numero_de_lados)
            punto = Punto(*rodri(vector_v, vector_k, angulo_theta).coords) + Punto(*centro)
            puntos.append(punto)

        return puntos

    def borrar(self, borrar_id: int):
        for indice in range(self.programa.lista_circunferencias.count()):
            item = self.programa.lista_circunferencias.item(indice)
            widget = self.programa.lista_circunferencias.itemWidget(item)
            if widget.id == borrar_id:
                self.programa.lista_circunferencias.takeItem(self.programa.lista_circunferencias.row(item))
                break

    def guardar(self) -> dict:
        return {"Nombre": self.nombre, "Puntos": self.puntos}


class Poligono(WidgetFila):
    def __init__(self, programa, nombre: str, vector_normal=None,
                 vertice=None, centro=None, num_lados=None, puntos=None):
        WidgetFila.__init__(self, programa, programa.id_circunferencia, nombre)
        programa.id_poligono += 1
        if not puntos:
            self.puntos = self.calcular_vertices(vector_normal, vertice, centro, num_lados)
        else:
            self.puntos = puntos

    @staticmethod
    def calcular_vertices(vector_normal, vertice, centro, numero_de_lados):

        def distancia_entre_puntos(p1: list, p2: list):
            return ((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2 + (p2[2] - p1[2]) ** 2) ** 0.5

        radio = distancia_entre_puntos(vertice, centro)

        # Rotación de rodrigues
        def rodri(v: Vector, k: Vector, theta):
            return v * cos(theta) + k.cross(v) * sin(theta) + k * (k.dot(v)) * (1 - cos(theta))

        def calcular_vector_v(r: int, t: int):
            return Vector([r * cos(radians(t)), r * sin(radians(t)), 0])

        def calcular_angulo_entre_vectores(v1, v2, vn):
            if vn.coords[2] != 0:
                dot = v1.coords[0] * v2.coords[0] + v1.coords[1] * v2.coords[1]
                det = v1.coords[1] * v2.coords[0] - v1.coords[0] * v2.coords[1]
                alfa = atan2(det, dot)
            elif vn.coords[1] != 0:
                alfa = atan2(v2.coords[0], v2.coords[2]) - atan2(v1.coords[0], v1.coords[2])
            else:
                alfa = atan2(v1.coords[1], v1.coords[2]) + atan2(v2.coords[1], v2.coords[2])
            return degrees(alfa)

        # Vector E, eje Z
        vector_e = Vector([0, 0, 1])
        # El vector normal al plano paralelo al polígono
        vector_u = Vector(vector_normal, normalizar=True)
        angulo_theta = acos(vector_e.dot(vector_u) / vector_u.modulo())
        denominador = vector_e.cross(vector_u).modulo()
        if denominador != 0:
            vector_k = vector_e.cross(vector_u) / denominador
        else:
            vector_k = Vector([0, 0, 1])

        puntos = []
        desviacion = Vector([vertice[i] - centro[i] for i in range(3)])
        angulo_desviacion = calcular_angulo_entre_vectores(desviacion, Vector([1, 0, 0]), vector_u)

        for i in range(1, numero_de_lados + 1):
            vector_v = calcular_vector_v(radio, angulo_desviacion + i * 360 / numero_de_lados)
            punto = rodri(vector_v, vector_k, angulo_theta)
            for j in range(3):
                punto.coords[j] = round(punto.coords[j] + centro[j], 4)
            puntos.append(punto)
        return puntos

    def borrar(self, borrar_id: int):
        for indice in range(self.programa.lista_poligonos.count()):
            item = self.programa.lista_poligonos.item(indice)
            widget = self.programa.lista_poligonos.itemWidget(item)
            if widget.id == borrar_id:
                self.programa.lista_poligonos.takeItem(self.programa.lista_poligonos.row(item))
                break

    def guardar(self) -> dict:
        return {"Nombre": self.nombre, "Puntos": self.puntos}
