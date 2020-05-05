from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import (QWidget, QCheckBox, QPushButton, QMainWindow, QLabel, QPlainTextEdit, QComboBox,
                             QMessageBox, QColorDialog, QSpinBox, QListWidgetItem)
from sympy import Point3D, Line3D, Plane, intersection

from .rodri import calcular_circunferencia
from . import entidades_geometricas


class VentanaBase(QMainWindow):
    def __init__(self, programa):
        QMainWindow.__init__(self)
        self.programa = programa
        self.setWindowModality(Qt.ApplicationModal)
        self.setFixedSize(180, 140)
        self.setWindowFlags(Qt.Tool)
        font = QFont()
        font.setPointSize(10)
        self.setFont(font)
        self.widget_central = QWidget(self)
        self.setCentralWidget(self.widget_central)

        self.etiqueta_1 = QLabel(self.widget_central, geometry=QRect(10, 10, 130, 16))
        self.etiqueta_2 = QLabel(self.widget_central, geometry=QRect(10, 60, 130, 16))

        self.boton_crear = QPushButton("Crear", self.widget_central, geometry=QRect(10, 110, 80, 23))
        self.boton_cerrar = QPushButton("Cancelar", self.widget_central, geometry=QRect(90, 110, 80, 23))
        self.boton_cerrar.clicked.connect(self.close)

        self.entidad_1 = QComboBox(self.widget_central, geometry=QRect(10, 30, 160, 25))
        self.entidad_2 = QComboBox(self.widget_central, geometry=QRect(10, 80, 160, 25))


class VentanaBaseConNombre(VentanaBase):
    def __init__(self, programa):
        VentanaBase.__init__(self, programa)
        self.setFixedSize(180, 190)
        self.etiqueta_nombre = QLabel("Nombre:", self.widget_central, geometry=QRect(10, 105, 50, 20))

        self.boton_crear.setGeometry(10, 160, 80, 23)
        self.boton_cerrar.setGeometry(90, 160, 80, 23)

        self.nombre = QPlainTextEdit(self.widget_central, geometry=QRect(10, 125, 160, 28))


class PuntoMedio(VentanaBaseConNombre):
    def __init__(self, programa):
        VentanaBaseConNombre.__init__(self, programa)
        self.setWindowTitle("Punto medio")
        self.etiqueta_1.setText("Punto:")
        self.etiqueta_2.setText("Punto:")
        self.boton_crear.clicked.connect(self.crear_punto)

    def abrir(self):
        self.entidad_1.clear()
        self.entidad_2.clear()
        for i in range(self.programa.lista_puntos.count()):
            self.entidad_1.addItem(self.programa.lista_puntos.itemWidget(self.programa.lista_puntos.item(i)).nombre)

        for i in range(self.programa.lista_puntos.count()):
            self.entidad_2.addItem(self.programa.lista_puntos.itemWidget(self.programa.lista_puntos.item(i)).nombre)

        self.show()
        self.activateWindow()

    def crear_punto(self):
        punto = self.entidad_1.currentText()
        punto2 = self.entidad_2.currentText()
        for i in range(self.programa.lista_puntos.count()):
            if self.programa.lista_puntos.itemWidget(self.programa.lista_puntos.item(i)).nombre == punto:
                punto = self.programa.lista_puntos.itemWidget(self.programa.lista_puntos.item(i))

        for i in range(self.programa.lista_puntos.count()):
            if self.programa.lista_puntos.itemWidget(self.programa.lista_puntos.item(i)).nombre == punto2:
                punto2 = self.programa.lista_puntos.itemWidget(self.programa.lista_puntos.item(i))

        if punto == "" or punto2 == "":
            QMessageBox.critical(self, "Error al crear el punto medio",
                                 "Debes crear al menos dos puntos para calcular su punto medio")
        else:
            nombre = self.programa.evitar_nombre_punto_blanco(self.nombre.toPlainText())
            punto_medio = punto.sympy.midpoint(punto2.sympy)
            nombre = f"{nombre} ({punto_medio.x}, {punto_medio.y}, {punto_medio.z})"
            self.programa.crear_punto(nombre, punto_medio)
            self.cerrar()


class RectaPerpendicularAPlano(VentanaBaseConNombre):
    def __init__(self, programa):
        VentanaBaseConNombre.__init__(self, programa)
        self.setWindowTitle("Recta perpendicular a plano")
        self.etiqueta_1.setText("Punto:")
        self.etiqueta_2.setText("Plano:")

        self.boton_crear.clicked.connect(self.crear_recta)

    def abrir(self):
        self.entidad_1.clear()
        self.entidad_2.clear()
        for i in range(self.programa.lista_puntos.count()):
            self.entidad_1.addItem(self.programa.lista_puntos.itemWidget(self.programa.lista_puntos.item(i)).nombre)

        for i in range(self.programa.lista_planos.count()):
            self.entidad_2.addItem(self.programa.lista_planos.itemWidget(self.programa.lista_planos.item(i)).nombre)

        self.show()
        self.activateWindow()

    def crear_recta(self):
        punto = self.entidad_1.currentText()
        plano = self.entidad_2.currentText()

        for i in range(self.programa.lista_puntos.count()):
            if self.programa.lista_puntos.itemWidget(self.programa.lista_puntos.item(i)).nombre == punto:
                punto = self.programa.lista_puntos.itemWidget(self.programa.lista_puntos.item(i))

        for i in range(self.programa.lista_planos.count()):
            if self.programa.lista_planos.itemWidget(self.programa.lista_planos.item(i)).nombre == plano:
                plano = self.programa.lista_planos.itemWidget(self.programa.lista_planos.item(i))

        if punto == "" or plano == "":
            QMessageBox.critical(self, "Error al crear la recta",
                                 "Debes crear al menos un plano y un punto para crear una recta")
        else:
            nombre = self.programa.evitar_nombre_recta_blanco(self.nombre.toPlainText())
            nombre = f"{nombre}({punto.nombre}⊥{plano.nombre})"
            recta = plano.sympy.perpendicular_line(punto.sympy)
            self.programa.crear_recta(nombre, recta)
            self.cerrar()


class PlanoPerpendicularAPlano(VentanaBaseConNombre):
    def __init__(self, programa):
        VentanaBaseConNombre.__init__(self, programa)
        self.setWindowTitle("Plano perpendicular a plano")
        self.setFixedSize(180, 240)

        self.etiqueta_1.setText("Punto:")
        self.etiqueta_2.setText("Plano:")
        self.etiqueta_2.setGeometry(10, 110, 41, 16)
        self.etiqueta_3 = QLabel("Punto:", self.widget_central, geometry=QRect(10, 60, 41, 16))

        self.entidad_3 = QComboBox(self.widget_central, geometry=QRect(10, 130, 160, 25))
        self.etiqueta_nombre.setGeometry(10, 155, 50, 20)
        self.nombre.setGeometry(10, 175, 160, 28)

        self.boton_crear.setGeometry(10, 210, 80, 23)
        self.boton_cerrar.setGeometry(90, 210, 80, 23)

        self.boton_crear.clicked.connect(self.crear_plano)

    def abrir(self):
        self.entidad_1.clear()
        self.entidad_2.clear()
        self.entidad_3.clear()
        for i in range(self.programa.lista_puntos.count()):
            self.entidad_1.addItem(self.programa.lista_puntos.itemWidget(self.programa.lista_puntos.item(i)).nombre)
            self.entidad_2.addItem(self.programa.lista_puntos.itemWidget(self.programa.lista_puntos.item(i)).nombre)
        for i in range(self.programa.lista_planos.count()):
            self.entidad_3.addItem(self.programa.lista_planos.itemWidget(self.programa.lista_planos.item(i)).nombre)

        self.show()
        self.activateWindow()

    def crear_plano(self):
        punto = self.entidad_1.currentText()
        punto2 = self.entidad_2.currentText()
        plano = self.entidad_3.currentText()

        for i in range(self.programa.lista_puntos.count()):
            if self.programa.lista_puntos.itemWidget(self.programa.lista_puntos.item(i)).nombre == punto:
                punto = self.programa.lista_puntos.itemWidget(self.programa.lista_puntos.item(i))
            if self.programa.lista_puntos.itemWidget(self.programa.lista_puntos.item(i)).nombre == punto2:
                punto2 = self.programa.lista_puntos.itemWidget(self.programa.lista_puntos.item(i))

        for i in range(self.programa.lista_planos.count()):
            if self.programa.lista_planos.itemWidget(self.programa.lista_planos.item(i)).nombre == plano:
                plano = self.programa.lista_planos.itemWidget(self.programa.lista_planos.item(i))

        if punto == "" or plano == "":
            QMessageBox.critical(self, "Error al crear el plano",
                                 "Debes crear al menos un plano y un punto para crear un plano perpendicular a este")
        elif punto.sympy == punto2.sympy:
            QMessageBox.critical(self, "Error al crear el plano", "Los puntos son coincidentes")
        else:
            nombre = self.programa.evitar_nombre_plano_blanco(self.nombre.toPlainText())
            nombre = f"{nombre}⊥{plano.nombre}"
            plano_perpendicular = plano.sympy.perpendicular_plane(punto.sympy, punto2.sympy)
            self.programa.crear_plano(nombre, plano_perpendicular)
            self.cerrar()


class PlanoParaleloAPlano(VentanaBaseConNombre):
    def __init__(self, programa):
        VentanaBaseConNombre.__init__(self, programa)

        self.setWindowTitle("Plano paralelo a plano")
        self.etiqueta_1.setText("Punto:")
        self.etiqueta_2.setText("Plano:")

        self.boton_crear.clicked.connect(self.crear_plano)

    def abrir(self):
        self.entidad_1.clear()
        self.entidad_2.clear()
        for i in range(self.programa.lista_puntos.count()):
            self.entidad_1.addItem(self.programa.lista_puntos.itemWidget(self.programa.lista_puntos.item(i)).nombre)
        for i in range(self.programa.lista_planos.count()):
            self.entidad_2.addItem(self.programa.lista_planos.itemWidget(self.programa.lista_planos.item(i)).nombre)

        self.show()
        self.activateWindow()

    def crear_plano(self):
        punto = self.entidad_1.currentText()
        plano = self.entidad_2.currentText()

        for i in range(self.programa.lista_puntos.count()):
            if self.programa.lista_puntos.itemWidget(self.programa.lista_puntos.item(i)).nombre == punto:
                punto = self.programa.lista_puntos.itemWidget(self.programa.lista_puntos.item(i))

        for i in range(self.programa.lista_planos.count()):
            if self.programa.lista_planos.itemWidget(self.programa.lista_planos.item(i)).nombre == plano:
                plano = self.programa.lista_planos.itemWidget(self.programa.lista_planos.item(i))

        if punto == "" or plano == "":
            QMessageBox.critical(self, "Error al crear el plano",
                                 "Debes crear al menos un plano y un punto para crear un plano paralelo a este")
        else:
            nombre = self.programa.evitar_nombre_plano_blanco(self.nombre.toPlainText())
            nombre = f"{nombre}║{plano.nombre}"
            plano_paralelo = plano.sympy.parallel_plane(punto.sympy)
            self.programa.crear_plano(nombre, plano_paralelo)
            self.cerrar()


class RectaPerpendicularARecta(VentanaBaseConNombre):
    def __init__(self, programa):
        VentanaBaseConNombre.__init__(self, programa)
        self.setWindowTitle("Recta perpendicular a recta")
        self.etiqueta_1.setText("Punto:")
        self.etiqueta_2.setText("Recta:")

        self.boton_crear.clicked.connect(self.crear_recta)

    def abrir(self):
        self.entidad_1.clear()
        self.entidad_2.clear()
        for i in range(self.programa.lista_puntos.count()):
            self.entidad_1.addItem(self.programa.lista_puntos.itemWidget(self.programa.lista_puntos.item(i)).nombre)
        for i in range(self.programa.lista_rectas.count()):
            self.entidad_2.addItem(self.programa.lista_rectas.itemWidget(self.programa.lista_rectas.item(i)).nombre)

        self.show()
        self.activateWindow()

    def crear_recta(self):
        punto = self.entidad_1.currentText()
        recta = self.entidad_2.currentText()

        for i in range(self.programa.lista_puntos.count()):
            if self.programa.lista_puntos.itemWidget(self.programa.lista_puntos.item(i)).nombre == punto:
                punto = self.programa.lista_puntos.itemWidget(self.programa.lista_puntos.item(i))

        for i in range(self.programa.lista_rectas.count()):
            if self.programa.lista_rectas.itemWidget(self.programa.lista_rectas.item(i)).nombre == recta:
                recta = self.programa.lista_rectas.itemWidget(self.programa.lista_rectas.item(i))
        if punto == "" or recta == "":
            QMessageBox.critical(self, "Error al crear la recta",
                                 "Debes crear al menos una recta y un punto para crear una recta")
        else:
            nombre = self.programa.evitar_nombre_recta_blanco(self.nombre.toPlainText())
            nombre = f"{nombre}({recta.nombre}⊥{punto.nombre})"
            recta_perpendicular = recta.sympy.perpendicular_line(punto.sympy)
            self.programa.crear_recta(nombre, recta_perpendicular)
            self.cerrar()


class RectaParalelaARecta(VentanaBaseConNombre):
    def __init__(self, programa):
        VentanaBaseConNombre.__init__(self, programa)

        self.setWindowTitle("Recta paralela a recta")
        self.etiqueta_1.setText("Punto:")
        self.etiqueta_2.setText("Recta:")

        self.boton_crear.clicked.connect(self.crear_recta)

    def abrir(self):
        self.entidad_1.clear()
        self.entidad_2.clear()
        for i in range(self.programa.lista_puntos.count()):
            self.entidad_1.addItem(self.programa.lista_puntos.itemWidget(self.programa.lista_puntos.item(i)).nombre)

        for i in range(self.programa.lista_rectas.count()):
            self.entidad_2.addItem(self.programa.lista_rectas.itemWidget(self.programa.lista_rectas.item(i)).nombre)

        self.show()
        self.activateWindow()

    def crear_recta(self):
        punto = self.entidad_1.currentText()
        recta = self.entidad_2.currentText()
        for i in range(self.programa.lista_puntos.count()):
            if self.programa.lista_puntos.itemWidget(self.programa.lista_puntos.item(i)).nombre == punto:
                punto = self.programa.lista_puntos.itemWidget(self.programa.lista_puntos.item(i))

        for i in range(self.programa.lista_rectas.count()):
            if self.programa.lista_rectas.itemWidget(self.programa.lista_rectas.item(i)).nombre == recta:
                recta = self.programa.lista_rectas.itemWidget(self.programa.lista_rectas.item(i))

        if punto == "" or recta == "":
            QMessageBox.critical(self, "Error al crear la recta",
                                 "Debes crear al menos una recta y un punto para crear una recta")
        else:
            nombre = self.programa.evitar_nombre_recta_blanco(self.nombre.toPlainText())
            nombre = f"{nombre}({recta.nombre}║{punto.nombre})"
            recta_perpendicular = recta.sympy.parallel_line(punto.sympy)
            self.programa.crear_recta(nombre, recta_perpendicular)
            self.cerrar()


class Distancia(VentanaBase):
    def __init__(self, programa):
        VentanaBase.__init__(self, programa)

        self.setWindowTitle("Calcular distancia")
        self.etiqueta_1.setText("Entidad geométrica 1:")
        self.etiqueta_2.setText("Entidad geométrica 2:")

        self.boton_crear.clicked.connect(self.calcular_distancia)

    def abrir(self):
        self.entidad_1.clear()
        self.entidad_2.clear()

        for i in range(self.programa.lista_puntos.count()):
            self.entidad_1.addItem(self.programa.lista_puntos.itemWidget(self.programa.lista_puntos.item(i)).nombre)
            self.entidad_2.addItem(self.programa.lista_puntos.itemWidget(self.programa.lista_puntos.item(i)).nombre)

        for i in range(self.programa.lista_planos.count()):
            self.entidad_1.addItem(self.programa.lista_planos.itemWidget(self.programa.lista_planos.item(i)).nombre)
            self.entidad_2.addItem(self.programa.lista_planos.itemWidget(self.programa.lista_planos.item(i)).nombre)

        for i in range(self.programa.lista_rectas.count()):
            self.entidad_1.addItem(self.programa.lista_rectas.itemWidget(self.programa.lista_rectas.item(i)).nombre)
            self.entidad_2.addItem(self.programa.lista_rectas.itemWidget(self.programa.lista_rectas.item(i)).nombre)

        self.show()
        self.activateWindow()

    def calcular_distancia(self):
        entidad_1 = self.entidad_1.currentText()
        entidad_2 = self.entidad_2.currentText()

        for i in range(self.programa.lista_puntos.count()):
            if self.programa.lista_puntos.itemWidget(self.programa.lista_puntos.item(i)).nombre == entidad_1:
                entidad_1 = self.programa.lista_puntos.itemWidget(self.programa.lista_puntos.item(i))
            if self.programa.lista_puntos.itemWidget(self.programa.lista_puntos.item(i)).nombre == entidad_2:
                entidad_2 = self.programa.lista_puntos.itemWidget(self.programa.lista_puntos.item(i))

        for i in range(self.programa.lista_rectas.count()):
            if self.programa.lista_rectas.itemWidget(self.programa.lista_rectas.item(i)).nombre == entidad_1:
                entidad_1 = self.programa.lista_rectas.itemWidget(self.programa.lista_rectas.item(i))
            if self.programa.lista_rectas.itemWidget(self.programa.lista_rectas.item(i)).nombre == entidad_2:
                entidad_2 = self.programa.lista_rectas.itemWidget(self.programa.lista_rectas.item(i))

        for i in range(self.programa.lista_planos.count()):
            if self.programa.lista_planos.itemWidget(self.programa.lista_planos.item(i)).nombre == entidad_1:
                entidad_1 = self.programa.lista_planos.itemWidget(self.programa.lista_planos.item(i))
            if self.programa.lista_planos.itemWidget(self.programa.lista_planos.item(i)).nombre == entidad_2:
                entidad_2 = self.programa.lista_planos.itemWidget(self.programa.lista_planos.item(i))

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
    def __init__(self, programa):
        VentanaBase.__init__(self, programa)

        self.setWindowTitle("Crear intersección")
        self.etiqueta_1.setText("Entidad geométrica 1:")
        self.etiqueta_2.setText("Entidad geométrica 2:")

        self.boton_crear.clicked.connect(self.calcular_interseccion)

    def abrir(self):
        self.entidad_1.clear()
        self.entidad_2.clear()

        for i in range(self.programa.lista_planos.count()):
            self.entidad_1.addItem(self.programa.lista_planos.itemWidget(self.programa.lista_planos.item(i)).nombre)
            self.entidad_2.addItem(self.programa.lista_planos.itemWidget(self.programa.lista_planos.item(i)).nombre)

        for i in range(self.programa.lista_rectas.count()):
            self.entidad_1.addItem(self.programa.lista_rectas.itemWidget(self.programa.lista_rectas.item(i)).nombre)
            self.entidad_2.addItem(self.programa.lista_rectas.itemWidget(self.programa.lista_rectas.item(i)).nombre)

        self.show()
        self.activateWindow()

    def calcular_interseccion(self):
        entidad_1 = self.entidad_1.currentText()
        entidad_2 = self.entidad_2.currentText()

        for i in range(self.programa.lista_rectas.count()):
            if self.programa.lista_rectas.itemWidget(self.programa.lista_rectas.item(i)).nombre == entidad_1:
                entidad_1 = self.programa.lista_rectas.itemWidget(self.programa.lista_rectas.item(i))
            if self.programa.lista_rectas.itemWidget(self.programa.lista_rectas.item(i)).nombre == entidad_2:
                entidad_2 = self.programa.lista_rectas.itemWidget(self.programa.lista_rectas.item(i))

        for i in range(self.programa.lista_planos.count()):
            if self.programa.lista_planos.itemWidget(self.programa.lista_planos.item(i)).nombre == entidad_1:
                entidad_1 = self.programa.lista_planos.itemWidget(self.programa.lista_planos.item(i))
            if self.programa.lista_planos.itemWidget(self.programa.lista_planos.item(i)).nombre == entidad_2:
                entidad_2 = self.programa.lista_planos.itemWidget(self.programa.lista_planos.item(i))

        if entidad_1 == "" or entidad_2 == "":
            QMessageBox.critical(self, "Error al calcular la intersección",
                                 "Debes crear al dos elementos para calcular su intersección")
        elif entidad_1 == entidad_2:
            QMessageBox.critical(self, "Error al calcular la intersección",
                                 "Los elementos seleccionados son el mismo")
        else:
            interseccion = intersection(entidad_1.sympy, entidad_2.sympy)
            if interseccion:
                # Si no se produce una intersección es porque los elementos son paralelos
                interseccion = interseccion[0]
                if isinstance(entidad_1.sympy, Line3D) and isinstance(entidad_2.sympy, Line3D):
                    """
                    Intersección recta-recta. Tres opciones: 
                    Ambas son coincidentes -> Se produce un error
                    Secantes -> Se crea un punto de intersección
                    Paralelas -> No tienen ningún punto en común
                    """
                    if isinstance(interseccion, Point3D):
                        if any(abs(i) > 499 for i in interseccion.coordinates):
                            QMessageBox.critical(self, "Error al calcular la intersección",
                                                 "Las rectas se cortan en un punto fuera de los límites establecidos en"
                                                 " el programa")
                        else:
                            self.programa.crear_punto(f"{entidad_1.nombre}∩{entidad_2.nombre}", interseccion)
                    else:
                        QMessageBox.critical(self, "Error al calcular la intersección", "Las rectas son coincidentes")
                elif isinstance(entidad_1.sympy, Plane) and isinstance(entidad_2.sympy, Plane):
                    """
                    Lo mismo, 3 casos:
                    Planos paralelos -> No se crea nada
                    Secantes -> Se crea una recta
                    Coincidentes -> Ambos planos son iguales
                    """
                    if isinstance(interseccion, Line3D):
                        try:
                            nombre = f"{entidad_1.nombre}∩{entidad_2.nombre}"
                            self.programa.crear_recta(nombre, interseccion)
                        except Exception as r:
                            print(r)
                            QMessageBox.critical(self, "Error al crear la intersección",
                                                 "Se ha producido un grave error debido a limitaciones del programa")
                else:
                    if isinstance(interseccion, Point3D):
                        if any(abs(i) > 499 for i in interseccion.coordinates):
                            QMessageBox.critical(self, "Error al calcular la intersección",
                                                 "Las intersección se encuentra en un punto fuera de los límites "
                                                 "establecidos en el programa")
                        else:
                            self.programa.crear_punto(f"{entidad_1.nombre}∩{entidad_2.nombre}", interseccion)
                    else:
                        QMessageBox.critical(self, "Error al calcular la intersección",
                                             "La recta se encuentra contenida en el plano")
            else:
                QMessageBox.critical(self, "Error al calcular la intersección", "Los elementos no se intersecan")


class Proyectar(VentanaBaseConNombre):
    def __init__(self, programa):
        VentanaBaseConNombre.__init__(self, programa)

        self.setWindowTitle("Proyectar elementos")
        self.setFixedSize(180, 240)

        self.etiqueta_1.setText("Punto:")
        self.etiqueta_2.setText("Plano:")

        self.boton_crear.setGeometry(10, 210, 80, 23)
        self.boton_cerrar.setGeometry(90, 210, 80, 23)

        etiqueta_modo = QLabel("Hacia el plano:", self.widget_central, geometry=QRect(10, 155, 121, 25))

        self.modo = QComboBox(self.widget_central, geometry=QRect(10, 180, 160, 25))
        self.modo.addItem("Perpendicular al plano")
        self.modo.addItem("Vertical")
        self.modo.addItem("Horizontal")
        self.modo.addItem("Perfil")

        self.boton_crear.clicked.connect(self.crear_punto)

    def abrir(self):
        self.entidad_1.clear()
        self.entidad_2.clear()

        for i in range(self.programa.lista_puntos.count()):
            self.entidad_1.addItem(self.programa.lista_puntos.itemWidget(self.programa.lista_puntos.item(i)).nombre)

        for i in range(self.programa.lista_planos.count()):
            self.entidad_2.addItem(self.programa.lista_planos.itemWidget(self.programa.lista_planos.item(i)).nombre)

        self.show()
        self.activateWindow()

    def crear_punto(self):
        punto = self.entidad_1.currentText()
        plano = self.entidad_2.currentText()

        for i in range(self.programa.lista_puntos.count()):
            if self.programa.lista_puntos.itemWidget(self.programa.lista_puntos.item(i)).nombre == punto:
                punto = self.programa.lista_puntos.itemWidget(self.programa.lista_puntos.item(i))

        for i in range(self.programa.lista_planos.count()):
            if self.programa.lista_planos.itemWidget(self.programa.lista_planos.item(i)).nombre == plano:
                plano = self.programa.lista_planos.itemWidget(self.programa.lista_planos.item(i))

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

                nombre = self.programa.evitar_nombre_punto_blanco(self.nombre.toPlainText())
                nombre = f"{nombre}({proyectado.x}, {proyectado.y}, {proyectado.z})"
                self.programa.crear_punto(nombre, proyectado)
                self.cerrar()


class Bisectriz(VentanaBaseConNombre):
    def __init__(self, programa):
        VentanaBaseConNombre.__init__(self, programa)

        self.setWindowTitle("Bisectriz")
        self.etiqueta_1.setText("Recta:")
        self.etiqueta_2.setText("Recta:")

        self.boton_crear.clicked.connect(self.crear_recta)

    def abrir(self):
        self.entidad_1.clear()
        self.entidad_2.clear()

        for i in range(self.programa.lista_rectas.count()):
            self.entidad_1.addItem(self.programa.lista_rectas.itemWidget(self.programa.lista_rectas.item(i)).nombre)
            self.entidad_2.addItem(self.programa.lista_rectas.itemWidget(self.programa.lista_rectas.item(i)).nombre)

        self.show()
        self.activateWindow()

    @staticmethod
    def normalizar(vector: list):
        # Normaliza los vectores para que tengan la misma longitud
        length = (vector[0] ** 2 + vector[1] ** 2 + vector[2] ** 2) ** 0.5
        vector = [x / length for x in vector]
        return vector

    def crear_recta(self):
        recta1 = self.entidad_1.currentText()
        recta2 = self.entidad_2.currentText()

        for i in range(self.programa.lista_rectas.count()):
            if self.programa.lista_rectas.itemWidget(self.programa.lista_rectas.item(i)).nombre == recta1:
                recta1 = self.programa.lista_rectas.itemWidget(self.programa.lista_rectas.item(i))
            elif self.programa.lista_rectas.itemWidget(self.programa.lista_rectas.item(i)).nombre == recta2:
                recta2 = self.programa.lista_rectas.itemWidget(self.programa.lista_rectas.item(i))

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

                    d1 = self.normalizar(direccion1)
                    d2 = self.normalizar(direccion2)

                    direccion1 = [d1[i] + d2[i] for i in range(3)]
                    direccion2 = [d1[i] - d2[i] for i in range(3)]

                    bis1 = Line3D(punto, direction_ratio=direccion1)
                    bis2 = Line3D(punto, direction_ratio=direccion2)

                    nombre = "bis. 1 " + self.programa.evitar_nombre_recta_blanco(self.nombre.toPlainText())
                    nombre2 = "bis. 2 " + self.programa.evitar_nombre_recta_blanco(self.nombre.toPlainText())

                    self.programa.crear_recta(nombre, bis1)
                    self.programa.crear_recta(nombre2, bis2)

            else:
                QMessageBox.critical(self, "Error al crear la bisectriz",
                                     "Las rectas no se cortan, no tienen ningún punto en común")


class VentanaRenombrar(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setStyleSheet("QMainWindow {border-style: outset; border-width: 1px; border-color: black;}")
        self.setFixedSize(180, 90)
        self.setWindowFlags(Qt.Tool)
        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowTitle("Renombrar")

        fuente = QFont()
        fuente.setPointSize(10)
        self.setFont(fuente)

        widget_central = QWidget(self)
        self.setCentralWidget(widget_central)

        nombre = QLabel("Nombre:", widget_central, geometry=QRect(5, 0, 50, 20))
        self.widget_texto = QPlainTextEdit(widget_central, geometry=QRect(5, 25, 170, 30))

        self.boton_crear = QPushButton("Renombrar", widget_central, geometry=QRect(5, 58, 85, 23))
        self.boton_crear.clicked.connect(self.close)
        boton_cerrar = QPushButton("Cancelar", widget_central, geometry=QRect(90, 58, 85, 23))
        boton_cerrar.clicked.connect(self.close)

    def abrir(self):
        self.show()
        self.activateWindow()


class Controles(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowFlags(Qt.Tool)
        self.setFixedSize(355, 441)
        self.setWindowTitle("Controles")

        wc = QWidget()
        self.setCentralWidget(wc)

        f = QFont()
        f.setPointSize(10)

        tecla = QLabel("Tecla:", wc, geometry=QRect(8, 8, 40, 16), font=f)
        accion = QLabel("Acción:", wc, geometry=QRect(52, 8, 42, 16), font=f)

        uno = QLabel("1", wc, geometry=QRect(16, 54, 16, 16), font=f)
        dos = QLabel("2", wc, geometry=QRect(16, 78, 16, 16), font=f)
        tres = QLabel("3", wc, geometry=QRect(16, 102, 16, 16), font=f)

        alzado = QLabel("Vista alzado", wc, geometry=QRect(52, 54, 69, 16), font=f)
        planta = QLabel("Vista planta", wc, geometry=QRect(52, 78, 67, 16), font=f)
        perfil = QLabel("Vista perfil", wc, geometry=QRect(52, 102, 61, 16), font=f)

        reset = QLabel("Reestablecer la posición de la cámara", wc, geometry=QRect(52, 30, 217, 16), font=f)
        r = QLabel("R", wc, geometry=QRect(16, 30, 16, 16), font=f)
        mas = QLabel("+", wc, geometry=QRect(16, 126, 16, 16), font=f)
        menos = QLabel("-", wc, geometry=QRect(16, 150, 16, 16), font=f)
        zoom_mas = QLabel("Aumentar el zoom", wc, geometry=QRect(52, 126, 111, 16), font=f)
        zoom_menos = QLabel("Reducir el zoom", wc, geometry=QRect(52, 150, 101, 16), font=f)
        w = QLabel("W", wc, geometry=QRect(16, 174, 16, 16), font=f)
        a = QLabel("A", wc, geometry=QRect(16, 199, 16, 16), font=f)
        s = QLabel("S", wc, geometry=QRect(16, 223, 16, 16), font=f)
        d = QLabel("D", wc, geometry=QRect(16, 247, 16, 16), font=f)
        q = QLabel("Q", wc, geometry=QRect(16, 271, 16, 16), font=f)
        e = QLabel("E", wc, geometry=QRect(16, 295, 16, 16), font=f)
        y_mas = QLabel("Mover la cámara sobre el eje Y en sentido positivo",
                       wc, geometry=QRect(52, 271, 289, 16), font=f)
        y_menos = QLabel("Mover la cámara sobre el eje Y en sentido negativo",
                         wc, geometry=QRect(52, 295, 294, 16), font=f)
        z_mas = QLabel("Mover la cámara sobre el eje Z en sentido postivo",
                       wc, geometry=QRect(52, 319, 286, 16), font=f)
        z_menos = QLabel("Mover la cámara sobre el eje Z en sentido negativo",
                         wc, geometry=QRect(52, 344, 294, 16), font=f)
        derecha = QLabel("Rotar la cámara hacia la derecha",
                         wc, geometry=QRect(52, 247, 190, 16), font=f)
        abajo = QLabel("Rotar la cámar hacia abajo", wc, geometry=QRect(52, 223, 155, 16), font=f)
        izquierda = QLabel("Rotar la cámara hacia la izquierda", wc, geometry=QRect(52, 199, 196, 16), font=f)
        arriba = QLabel("Rotar la cámara hacia arriba", wc, geometry=QRect(52, 174, 164, 16), font=f)
        flecha_arriba = QLabel("🢁", wc, geometry=QRect(16, 319, 16, 17), font=f)
        flecha_abajo = QLabel("🢃", wc, geometry=QRect(16, 344, 16, 17), font=f)
        flecha_derecha = QLabel("🢂", wc, geometry=QRect(16, 369, 16, 17), font=f)
        flecha_izquierda = QLabel("🢀", wc, geometry=QRect(16, 394, 16, 17), font=f)
        x_menos = QLabel("Mover la cámara sobre el eje X en sentido negativo",
                         wc, geometry=QRect(52, 369, 295, 16), font=f)
        x_mas = QLabel("Mover la cámara sobre el eje X en sentido positivo",
                       wc, geometry=QRect(52, 394, 290, 16), font=f)
        raton = QLabel("Arrastrar el ratón: Rotar libremente la cámara",
                       wc, geometry=QRect(11, 419, 271, 16), font=f)

    def show(self):
        QMainWindow.show(self)
        self.activateWindow()


class AcercaDe(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowFlags(Qt.Tool)
        self.setWindowTitle("Acerca de")
        self.setFixedSize(1020, 170)
        widget_central = QWidget()
        self.setCentralWidget(widget_central)

        f = QFont()
        f.setPointSize(12)

        self.acerca_de = QLabel("Acerca de:", widget_central, geometry=QRect(10, 10, 80, 21), font=f)
        self.t = QLabel(widget_central, geometry=QRect(10, 35, 1000, 115), font=f)
        self.t.setOpenExternalLinks(True)
        self.t.setTextFormat(Qt.RichText)
        self.t.setText("Este es un programa enfocado al uso educativo del sistema diédrico.<br>"
                       "Ha sido desarrollado por Jaime Resano Aisa, estudiante de 18 años del instituto "
                       "IES Ribera del Arga de Peralta, Navarra.<br>Ha sido programado en el lenguaje Python 3. "
                       "Utiliza PyQt5 para la interfaz, Sympy para los cálculos matemáticos y OpenGL para el dibujado "
                       "3D. <br>El código fuente del programa se encuentra disponible en "
                       "<a href=\"https://github.com/Jaime02/Proyecto-de-investigacion-2019-Dibujo-tecnico/\">GitHub</a>."
                       "<br>También está disponible el trabajo de investigación realizado que explica cómo funciona el "
                       "sistema diédrico.<br>Ante cualquier duda, sugerencia o problema, por favor, contacta con el autor en"
                       " el siguiente email: jresanoais1@educacion.navarra.es")

    def show(self):
        QMainWindow.show(self)
        self.activateWindow()


class Ajustes(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setWindowFlags(Qt.Tool)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.setFixedSize(420, 180)

        self.color_plano_vertical = (0.1, 1, 0.1, 0.5)
        self.color_plano_horizontal = (1, 0.1, 0.1, 0.5)

        wc = QWidget(self)

        ajustes = QLabel("Ajustes:", wc, geometry=QRect(10, 10, 40, 16))
        puntos = QLabel("Puntos:", wc, geometry=QRect(10, 90, 37, 16))
        rectas = QLabel("Rectas", wc, geometry=QRect(140, 10, 41, 16))
        planos = QLabel("Planos", wc, geometry=QRect(280, 10, 35, 16))

        self.ver_plano_horizontal = QCheckBox("Ver plano horizontal", wc, checked=True, geometry=QRect(10, 70, 118, 17))
        self.ver_plano_vertical = QCheckBox("Ver plano vertical", wc, checked=True, geometry=QRect(10, 50, 106, 17))
        self.ver_ejes = QCheckBox("Ver ejes", wc, checked=True, geometry=QRect(10, 30, 62, 17))

        self.ver_puntos = QCheckBox("Ver puntos", wc, checked=True, geometry=QRect(10, 110, 75, 17))
        self.ver_rectas = QCheckBox("Ver rectas", wc, checked=True, geometry=QRect(140, 30, 133, 17))
        self.ver_planos = QCheckBox("Ver planos", wc, checked=True, geometry=QRect(280, 30, 73, 17))

        self.rectas_trazas_v = QCheckBox("Ver trazas verticales", wc, checked=True, geometry=QRect(140, 70, 121, 17))
        self.rectas_trazas_h = QCheckBox("Ver trazas horizontales", wc, checked=True, geometry=QRect(140, 50, 129, 17))

        btn_color_v = QPushButton("Cambiar el color del\n plano vertical", wc, geometry=QRect(10, 130, 101, 41))
        btn_color_v.clicked.connect(self.cambiar_color_plano_vertical)
        reset_vertical = QPushButton("Reestablecer", wc, geometry=QRect(120, 130, 75, 41))
        reset_vertical.clicked.connect(self.reset_color_vertical)

        boton_color_h = QPushButton("Cambiar el color del\n plano horizontal", wc, geometry=QRect(200, 130, 101, 41))
        boton_color_h.clicked.connect(self.cambiar_color_plano_horizontal)
        reset_horizontal = QPushButton("Reestablecer", wc, geometry=QRect(310, 130, 75, 41))

        self.setWindowTitle("Ajustes")
        self.setCentralWidget(wc)

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

    def show(self):
        QMainWindow.show(self)
        self.activateWindow()


class VentanaCircunferencia(QMainWindow):
    def __init__(self, programa):
        QMainWindow.__init__(self)
        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowFlags(Qt.Tool)
        self.resize(185, 250)
        self.setWindowTitle("Crear circunferencia")
        self.programa = programa
        cw = QWidget()

        etiqueta_centro = QLabel("Centro:", cw, geometry=QRect(10, 10, 51, 16))
        self.centro = QComboBox(cw, geometry=QRect(10, 30, 161, 22))
        etiqueta_plano = QLabel("Paralela al plano:", cw, geometry=QRect(10, 60, 171, 16))
        self.plano = QComboBox(cw, geometry=QRect(10, 80, 161, 22))
        nombre = QLabel("Nombre:", cw, geometry=QRect(10, 160, 47, 13))
        self.nombre = QPlainTextEdit(cw, geometry=QRect(10, 180, 161, 31))
        self.boton_cancelar = QPushButton("Cancelar", cw, geometry=QRect(94, 220, 81, 23))
        self.boton_cancelar.clicked.connect(self.close)
        self.boton_crear = QPushButton("Crear", cw, geometry=QRect(10, 220, 81, 23))
        self.boton_crear.clicked.connect(self.crear_circunferencia)
        radio = QLabel("Radio:", cw, geometry=QRect(10, 110, 47, 13))
        self.radio = QSpinBox(cw, geometry=QRect(10, 130, 161, 22))

        self.setCentralWidget(cw)

    def abrir(self):
        self.centro.clear()
        self.plano.clear()

        for i in range(self.programa.lista_puntos.count()):
            self.centro.addItem(self.programa.lista_puntos.itemWidget(self.programa.lista_puntos.item(i)).nombre)
        for i in range(self.programa.lista_planos.count()):
            self.plano.addItem(self.programa.lista_planos.itemWidget(self.programa.lista_planos.item(i)).nombre)

        self.show()
        self.activateWindow()

    def crear_circunferencia(self):
        nombre = self.nombre.toPlainText()
        if not nombre:
            QMessageBox.critical(self, "Error al crear la circunferencia", "No ha introducido un nombre")
        else:
            centro = self.centro.currentText()
            plano = self.plano.currentText()
            radio = self.radio.value()
            for i in range(self.programa.lista_puntos.count()):
                if self.programa.lista_puntos.itemWidget(self.programa.lista_puntos.item(i)).nombre == centro:
                    centro = self.programa.lista_puntos.itemWidget(self.programa.lista_puntos.item(i))
            for i in range(self.programa.lista_planos.count()):
                if self.programa.lista_planos.itemWidget(self.programa.lista_planos.item(i)).nombre == plano:
                    plano = self.programa.lista_planos.itemWidget(self.programa.lista_planos.item(i))

            nombre = f"{nombre}⊂{plano.nombre}, r={radio}"
            circ = entidades_geometricas.Circunferencia(self.programa, self.programa.id_circunferencia,
                                                        nombre, plano.sympy.normal_vector, radio, centro.sympy)
            item = QListWidgetItem()
            item.setSizeHint(circ.minimumSizeHint())
            self.programa.lista_circunferencias.addItem(item)
            self.programa.lista_circunferencias.setItemWidget(item, circ)
            self.programa.id_circunferencia += 1