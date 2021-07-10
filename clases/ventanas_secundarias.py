from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (QWidget, QCheckBox, QPushButton, QMainWindow, QLabel, QLineEdit, QComboBox,
                               QMessageBox, QColorDialog, QSpinBox, QListWidgetItem, QVBoxLayout, QHBoxLayout,
                               QSpacerItem, QSizePolicy, QFormLayout)

from . import entidades_geometricas


class VentanaBase(QMainWindow):
    def __init__(self, programa):
        QMainWindow.__init__(self)
        self.programa = programa
        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowFlags(Qt.Tool)

        font = QFont()
        font.setPointSize(10)
        self.setFont(font)

        self.widget_central = QWidget()
        self.setCentralWidget(self.widget_central)

        self.layout_principal = QVBoxLayout()
        self.widget_central.setLayout(self.layout_principal)

        self.etiqueta_1 = QLabel()
        self.layout_principal.addWidget(self.etiqueta_1)
        self.entidad_1 = QComboBox()
        self.layout_principal.addWidget(self.entidad_1)

        self.etiqueta_2 = QLabel()
        self.layout_principal.addWidget(self.etiqueta_2)
        self.entidad_2 = QComboBox()
        self.layout_principal.addWidget(self.entidad_2)

        self.layout_botones = QHBoxLayout()
        self.layout_principal.addLayout(self.layout_botones)

        self.boton_crear = QPushButton("Crear")
        self.layout_botones.addWidget(self.boton_crear)

        self.boton_cerrar = QPushButton("Cancelar")
        self.boton_cerrar.clicked.connect(self.close)
        self.layout_botones.addWidget(self.boton_cerrar)


class VentanaBaseConNombre(VentanaBase):
    def __init__(self, programa):
        VentanaBase.__init__(self, programa)

        self.etiqueta_nombre = QLabel("Nombre:")
        self.layout_principal.insertWidget(4, self.etiqueta_nombre)

        self.nombre = QLineEdit()
        self.layout_principal.insertWidget(5, self.nombre)

    def keyPressEvent(self, evento):
        # Si presionas enter, se crea el elemento geometrico
        if evento.key() == Qt.Key_Return:
            self.boton_crear.click()


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
            nombre = self.programa.evitar_nombre_punto_blanco(self.nombre.text())

            punto_medio = punto.entidad_geometrica.midpoint(punto2.entidad_geometrica)
            nombre = f"{nombre} ({punto_medio.x}, {punto_medio.y}, {punto_medio.z})"
            self.programa.crear_punto(nombre, punto_medio)
            self.close()


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
            nombre = self.programa.evitar_nombre_recta_blanco(self.nombre.text())
            nombre = f"{nombre}({punto.nombre}⊥{plano.nombre})"
            recta = plano.entidad_geometrica.perpendicular_line(punto.entidad_geometrica)
            self.programa.crear_recta(nombre, recta)
            self.close()


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
            nombre = self.programa.evitar_nombre_recta_blanco(self.nombre.text())
            nombre = f"{nombre}({recta.nombre}⊥{punto.nombre})"
            recta_perpendicular = recta.entidad_geometrica.perpendicular_line(punto.entidad_geometrica)
            self.programa.crear_recta(nombre, recta_perpendicular)
            self.close()


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
            nombre = self.programa.evitar_nombre_recta_blanco(self.nombre.text())
            nombre = f"{nombre}({recta.nombre}║{punto.nombre})"
            recta_perpendicular = recta.entidad_geometrica.parallel_line(punto.entidad_geometrica)
            self.programa.crear_recta(nombre, recta_perpendicular)
            self.close()


class PlanoPerpendicularAPlano(VentanaBaseConNombre):
    def __init__(self, programa):
        VentanaBaseConNombre.__init__(self, programa)
        self.setWindowTitle("Plano perpendicular a plano")

        # todo swappear esta wea
        self.etiqueta_1.setText("Punto:")
        self.etiqueta_2.setText("Plano:")

        self.etiqueta_3 = QLabel("Punto:")
        self.layout_principal.insertWidget(4, self.etiqueta_3)

        self.entidad_3 = QComboBox()
        self.layout_principal.insertWidget(5, self.entidad_3)

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
        elif punto.entidad_geometrica == punto2.entidad_geometrica:
            QMessageBox.critical(self, "Error al crear el plano", "Los puntos son coincidentes")
        else:
            nombre = self.programa.evitar_nombre_plano_blanco(self.nombre.text())
            nombre = f"{nombre}⊥{plano.nombre}"
            plano_perpendicular = plano.entidad_geometrica.perpendicular_plane(punto.entidad_geometrica,
                                                                              punto2.entidad_geometrica)
            self.programa.crear_plano(nombre, plano_perpendicular)
            self.close()


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
            nombre = self.programa.evitar_nombre_plano_blanco(self.nombre.text())
            nombre = f"{nombre}║{plano.nombre}"
            plano_paralelo = plano.entidad_geometrica.parallel_plane(punto.entidad_geometrica)
            self.programa.crear_plano(nombre, plano_paralelo)
            self.close()


class Distancia(VentanaBase):
    def __init__(self, programa):
        VentanaBase.__init__(self, programa)

        self.setWindowTitle("Calcular distancia")
        self.etiqueta_1.setText("Entidad geométrica 1:")
        self.etiqueta_2.setText("Entidad geométrica 2:")

        self.boton_crear.setText("Calcular")


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
                                 "Los elementos seleccionados son coincidentes")
        else:
            distancia = round(entidad_1.entidad_geometrica.distancia(entidad_2.entidad_geometrica), 2)
            QMessageBox.about(self, "Resultado",
                              f"La distancia entre estos dos elementos es de {distancia} unidades")


class Interseccion(VentanaBase):
    def __init__(self, programa):
        VentanaBase.__init__(self, programa)

        self.setWindowTitle("Crear intersección")
        self.etiqueta_1.setText("Entidad geométrica 1:")
        self.etiqueta_2.setText("Entidad geométrica 2:")

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
            interseccion = intersection(entidad_1.entidad_geometrica, entidad_2.entidad_geometrica)
            if interseccion:
                # Si no se produce una intersección es porque los elementos son paralelos
                interseccion = interseccion[0]
                if isinstance(entidad_1.entidad_geometrica, Recta) and isinstance(entidad_2.entidad_geometrica, Recta):
                    """
                    Intersección recta-recta. Tres opciones: 
                    Ambas son coincidentes -> Se produce un error
                    Secantes -> Se crea un punto de intersección
                    Paralelas -> No tienen ningún punto en común
                    """
                    if isinstance(interseccion, entidades_geometricas.Punto):
                        if any(abs(i) > 499 for i in interseccion.coordinates):
                            QMessageBox.critical(self, "Error al calcular la intersección",
                                                 "Las rectas se cortan en un punto fuera de los límites establecidos en"
                                                 " el programa")
                        else:
                            self.programa.crear_punto(f"{entidad_1.nombre}∩{entidad_2.nombre}", interseccion)
                    else:
                        QMessageBox.critical(self, "Error al calcular la intersección", "Las rectas son coincidentes")
                elif isinstance(entidad_1.entidad_geometrica, Plano) and isinstance(entidad_2.entidad_geometrica, Plano):
                    """
                    Lo mismo, 3 casos:
                    Planos paralelos -> No se crea nada
                    Secantes -> Se crea una recta
                    Coincidentes -> Ambos planos son iguales
                    """
                    if isinstance(interseccion, Recta):
                        try:
                            nombre = f"{entidad_1.nombre}∩{entidad_2.nombre}"
                            self.programa.crear_recta(nombre, interseccion)
                        except Exception as r:
                            print(r)
                            QMessageBox.critical(self, "Error al crear la intersección",
                                                 "Se ha producido un grave error debido a limitaciones del programa")
                else:
                    if isinstance(interseccion, entidades_geometricas.Punto):
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

        self.etiqueta_1.setText("Punto:")
        self.etiqueta_2.setText("Plano:")

        etiqueta_modo = QLabel("Dirección:")
        self.layout_principal.insertWidget(4, etiqueta_modo)

        self.modo = QComboBox()
        self.modo.addItem("Perpendicular al plano")
        self.modo.addItem("Vertical")
        self.modo.addItem("Horizontal")
        self.modo.addItem("Perfil")
        self.layout_principal.insertWidget(5, self.modo)

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
            if plano.entidad_geometrica.intersection(punto.entidad_geometrica):
                QMessageBox.critical(self, "Error al crear la proyección", "El punto pertenece al plano")
            else:
                modo = self.modo.currentText()
                if modo == "Perpendicular al plano":
                    proyectado = plano.entidad_geometrica.projection(punto.entidad_geometrica)
                else:
                    if modo == "Vertical":
                        segmento = Segment3D(entidades_geometricas.Punto(punto.x, 500, punto.z),
                                             entidades_geometricas.Punto(punto.x, -500, punto.z))
                    elif modo == "Horizontal":
                        segmento = Segment3D(entidades_geometricas.Punto(punto.x, punto.y, 500),
                                             entidades_geometricas.Punto(punto.x, punto.y, -500))
                    else:
                        # modo = perfil
                        segmento = Segment3D(entidades_geometricas.Punto(500, punto.y, punto.z),
                                             entidades_geometricas.Punto(-500, punto.y, punto.z))
                    proyectado = plano.entidad_geometrica.intersection(segmento)

                    if proyectado:
                        proyectado = proyectado[0]
                    else:
                        QMessageBox.critical(self, "Error al crear la proyección",
                                             "El punto no puede proyectarse en esa dirección")
                        return

                nombre = self.programa.evitar_nombre_punto_blanco(self.nombre.text())
                nombre = f"{nombre}({proyectado.x}, {proyectado.y}, {proyectado.z})"
                self.programa.crear_punto(nombre, proyectado)
                self.close()


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
            interseccion = recta1.entidad_geometrica.intersection(recta2.entidad_geometrica)
            if interseccion:
                if isinstance(interseccion[0], Recta):
                    QMessageBox.critical(self, "Error al crear la bisectriz", "Las rectas son coincidentes")
                else:
                    punto = interseccion[0]

                    direccion1 = recta1.entidad_geometrica.direction_ratio
                    direccion2 = recta2.entidad_geometrica.direction_ratio

                    d1 = self.normalizar(direccion1)
                    d2 = self.normalizar(direccion2)

                    direccion1 = [d1[i] + d2[i] for i in range(3)]
                    direccion2 = [d1[i] - d2[i] for i in range(3)]

                    bis1 = Recta(punto, direction_ratio=direccion1)
                    bis2 = Recta(punto, direction_ratio=direccion2)

                    nombre = "bis. 1 " + self.programa.evitar_nombre_recta_blanco(self.nombre.text())
                    nombre2 = "bis. 2 " + self.programa.evitar_nombre_recta_blanco(self.nombre.text())

                    self.programa.crear_recta(nombre, bis1)
                    self.programa.crear_recta(nombre2, bis2)

            else:
                QMessageBox.critical(self, "Error al crear la bisectriz",
                                     "Las rectas no se cortan, no tienen ningún punto en común")


class VentanaRenombrar(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setStyleSheet("QMainWindow {border-style: outset; border-width: 1px; border-color: black;}")
        self.setWindowFlags(Qt.Tool)
        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowTitle("Renombrar")

        fuente = QFont()
        fuente.setPointSize(10)
        self.setFont(fuente)

        widget_central = QWidget(self)
        self.setCentralWidget(widget_central)

        nombre = QLabel("Nombre:", widget_central)
        self.widget_texto = QLineEdit(widget_central)

        self.boton_crear = QPushButton("Renombrar", widget_central)
        self.boton_crear.clicked.connect(self.close)
        boton_cerrar = QPushButton("Cancelar", widget_central)
        boton_cerrar.clicked.connect(self.close)

    def abrir(self):
        self.show()
        self.activateWindow()


class Controles(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)

        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.WindowCloseButtonHint)

        self.setWindowTitle("Controles")

        widget_central = QWidget()
        self.setCentralWidget(widget_central)

        layout = QFormLayout()
        layout.setLabelAlignment(Qt.AlignCenter)
        widget_central.setLayout(layout)

        f = QFont()
        f.setPointSize(10)
        self.setFont(f)

        tecla = QLabel("Tecla:")
        accion = QLabel("Acción:")
        layout.addRow(tecla, accion)

        uno = QLabel("1")
        alzado = QLabel("Vista alzado")
        layout.addRow(uno, alzado)

        dos = QLabel("2")
        planta = QLabel("Vista planta")
        layout.addRow(dos, planta)

        tres = QLabel("3")
        perfil = QLabel("Vista perfil")
        layout.addRow(tres, perfil)

        r = QLabel("R")
        reset = QLabel("Reestablecer la posición de la cámara")
        layout.addRow(r, reset)

        mas = QLabel("+")
        zoom_mas = QLabel("Aumentar el zoom")
        layout.addRow(mas, zoom_mas)

        menos = QLabel("-")
        zoom_menos = QLabel("Reducir el zoom")
        layout.addRow(menos, zoom_menos)

        w = QLabel("W")
        arriba = QLabel("Rotar la cámara hacia arriba")
        layout.addRow(w, arriba)

        a = QLabel("A")
        izquierda = QLabel("Rotar la cámara hacia la izquierda")
        layout.addRow(a, izquierda)

        s = QLabel("S")
        abajo = QLabel("Mover la cámara hacia abajo")
        layout.addRow(s, abajo)

        d = QLabel("D")
        derecha = QLabel("Rotar la cámara hacia la derecha")
        layout.addRow(d, derecha)

        q = QLabel("Q")
        y_mas = QLabel("Mover la cámara sobre el eje Y en sentido positivo")
        layout.addRow(q, y_mas)

        e = QLabel("E")
        y_menos = QLabel("Mover la cámara sobre el eje Y en sentido negativo")
        layout.addRow(e, y_menos)

        flecha_arriba = QLabel("🢁")
        arriba = QLabel("Mover la cámara sobre el eje Z en sentido positivo")
        layout.addRow(flecha_arriba, arriba)

        flecha_abajo = QLabel("🢃")
        abajo = QLabel("Mover la cámara sobre el eje Z en sentido negativo")
        layout.addRow(flecha_abajo, abajo)

        flecha_izquierda = QLabel("🢀")
        x_mas = QLabel("Mover la cámara sobre el eje X en sentido positivo")
        layout.addRow(flecha_izquierda, x_mas)

        x_menos = QLabel("Mover la cámara sobre el eje X en sentido negativo")
        flecha_derecha = QLabel("🢂")
        layout.addRow(flecha_derecha, x_menos)

        raton = QLabel("Arrastrar el ratón: Rotar libremente la cámara")
        layout.addWidget(raton)

    def show(self):
        QMainWindow.show(self)
        self.activateWindow()
        self.setFixedSize(self.width(), self.height())


class AcercaDe(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.WindowCloseButtonHint)

        self.setWindowTitle("Acerca de")
        widget_central = QWidget()
        self.setCentralWidget(widget_central)

        f = QFont()
        f.setPointSize(12)
        self.setFont(f)

        layout_principal = QVBoxLayout()
        widget_central.setLayout(layout_principal)

        acerca_de = QLabel("Acerca de:")
        layout_principal.addWidget(acerca_de)

        t = QLabel()
        t.setOpenExternalLinks(True)
        t.setTextFormat(Qt.RichText)
        t.setText("Este es un programa enfocado al uso educativo del sistema diédrico.<br>"
                  "Ha sido desarrollado por Jaime Resano Aisa, estudiante de 18 años del instituto "
                  "IES Ribera del Arga de Peralta, Navarra.<br>Ha sido programado en el lenguaje Python 3. "
                  "Utiliza PySide6 para la interfaz, Sympy para los cálculos matemáticos y OpenGL para el dibujado"
                  " 3D. <br>El código fuente del programa se encuentra disponible en "
                  "<a href=\"https://github.com/Jaime02/Proyecto-de-investigacion-2019-Dibujo-tecnico/\">GitHub </a>."
                  "<br>También está disponible el trabajo de investigación realizado que explica cómo funciona el"
                  "sistema diédrico.<br>Ante cualquier duda, sugerencia o problema, por favor, contacta con el "
                  "autor en el siguiente email: gemailpersonal02@gmail.com")
        layout_principal.addWidget(t)

    def show(self):
        QMainWindow.show(self)
        self.activateWindow()
        self.setFixedSize(self.width(), self.height())


class Ajustes(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)

        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.WindowCloseButtonHint)

        self.color_plano_vertical = (0.1, 1, 0.1, 0.5)
        self.color_plano_horizontal = (1, 0.1, 0.1, 0.5)

        widget_central = QWidget(self)

        self.layout_principal = QVBoxLayout()
        widget_central.setLayout(self.layout_principal)

        self.fila_1 = QHBoxLayout()
        self.fila_2 = QHBoxLayout()

        self.layout_principal.addLayout(self.fila_1)
        self.layout_principal.addLayout(self.fila_2)

        self.columna_1 = QVBoxLayout()
        self.columna_1.setAlignment(Qt.AlignTop)
        self.columna_2 = QVBoxLayout()
        self.columna_3 = QVBoxLayout()

        self.fila_1.addLayout(self.columna_1)
        self.fila_1.addLayout(self.columna_2)
        self.fila_1.addLayout(self.columna_3)

        self.columna_1.addWidget(QLabel("Ajustes:"))
        self.ver_ejes = QCheckBox("Ver ejes", checked=True)
        self.columna_1.addWidget(self.ver_ejes)
        self.ver_plano_vertical = QCheckBox("Ver plano vertical", checked=True)
        self.columna_1.addWidget(self.ver_plano_vertical)
        self.ver_plano_horizontal = QCheckBox("Ver plano horizontal", checked=True)
        self.columna_1.addWidget(self.ver_plano_horizontal)

        self.columna_1.addWidget(QLabel("Puntos:"))
        self.ver_puntos = QCheckBox("Ver puntos", checked=True)
        self.columna_1.addWidget(self.ver_puntos)

        self.columna_2.addWidget(QLabel("Rectas"))
        self.ver_rectas = QCheckBox("Ver rectas", checked=True)
        self.columna_2.addWidget(self.ver_rectas)
        self.rectas_trazas_v = QCheckBox("Ver trazas verticales", checked=True)
        self.columna_2.addWidget(self.rectas_trazas_v)
        self.rectas_trazas_h = QCheckBox("Ver trazas horizontales", checked=True)
        self.columna_2.addWidget(self.rectas_trazas_h)
        self.columna_2.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))

        self.columna_3.addWidget(QLabel("Planos"))
        self.ver_planos = QCheckBox("Ver planos", checked=True)
        self.columna_3.addWidget(self.ver_planos)
        self.columna_3.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))

        boton_color_v = QPushButton("Cambiar el color del\n plano vertical")
        boton_color_v.clicked.connect(self.cambiar_color_plano_vertical)
        boton_color_v.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.fila_2.addWidget(boton_color_v)

        reset_vertical = QPushButton("Reestablecer")
        reset_vertical.clicked.connect(self.reset_color_vertical)
        reset_vertical.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.fila_2.addWidget(reset_vertical)

        boton_color_h = QPushButton("Cambiar el color del\n plano horizontal")
        boton_color_h.clicked.connect(self.cambiar_color_plano_horizontal)
        boton_color_h.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.fila_2.addWidget(boton_color_h)

        reset_horizontal = QPushButton("Reestablecer")
        reset_horizontal.clicked.connect(self.reset_color_horizontal)
        reset_horizontal.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.fila_2.addWidget(reset_horizontal)

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

    def show(self):
        QMainWindow.show(self)
        self.activateWindow()
        self.setFixedSize(self.width(), self.height())


class VentanaCircunferencia(QMainWindow):
    def __init__(self, programa):
        QMainWindow.__init__(self)
        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowFlags(Qt.Tool)
        self.resize(185, 250)
        self.setWindowTitle("Crear circunferencia")
        self.programa = programa
        cw = QWidget()

        etiqueta_centro = QLabel("Centro:", cw)
        self.centro = QComboBox(cw)
        etiqueta_plano = QLabel("Paralela al plano:", cw)
        self.plano = QComboBox(cw)
        nombre = QLabel("Nombre:", cw)
        self.nombre = QLineEdit(cw)
        radio = QLabel("Radio:", cw)
        self.radio = QSpinBox(cw)
        self.boton_cancelar = QPushButton("Cancelar", cw)
        self.boton_cancelar.clicked.connect(self.close)
        self.boton_crear = QPushButton("Crear", cw)
        self.boton_crear.clicked.connect(self.comprobar_circunferencia)
        self.radio.setRange(1, 250)
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

    def comprobar_circunferencia(self):
        nombre = self.nombre.text()
        if not nombre:
            QMessageBox.critical(self, "Error al crear la circunferencia", "No ha introducido un nombre")
        else:
            centro = self.centro.currentText()
            plano = self.plano.currentText()
            radio = self.radio.value()
            if plano == "" or centro == "":
                QMessageBox.critical(self, "Error al crear la circunferencia", "Debe crear un punto y un plano para "
                                                                               "definir la circunferencia")
            else:
                for i in range(self.programa.lista_puntos.count()):
                    if self.programa.lista_puntos.itemWidget(self.programa.lista_puntos.item(i)).nombre == centro:
                        centro = self.programa.lista_puntos.itemWidget(self.programa.lista_puntos.item(i))
                for i in range(self.programa.lista_planos.count()):
                    if self.programa.lista_planos.itemWidget(self.programa.lista_planos.item(i)).nombre == plano:
                        plano = self.programa.lista_planos.itemWidget(self.programa.lista_planos.item(i))
                nombre = f"{nombre}║{plano.nombre}, r={radio}"
                v_n = plano.entidad_geometrica.vector_normal
                centro = centro.entidad_geometrica.coords
                self.crear_circunferencia(nombre, v_n, radio, centro)

    def crear_circunferencia(self, nombre, vector_normal=None, radio=None, centro=None, puntos: list = None):
        if not puntos:
            circ = entidades_geometricas.Circunferencia(self.programa, nombre, vector_normal=vector_normal,
                                                        radio=radio, centro=centro)
        else:
            circ = entidades_geometricas.Circunferencia(self.programa, nombre, puntos=puntos)
        item = QListWidgetItem()
        item.setSizeHint(circ.minimumSizeHint())
        self.programa.lista_circunferencias.addItem(item)
        self.programa.lista_circunferencias.setItemWidget(item, circ)


class VentanaCambiarGrosorPunto(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.resize(170, 100)
        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowFlags(Qt.Tool)
        cw = QWidget()
        self.setCentralWidget(cw)
        self.setWindowTitle("Cambiar el grosor")
        etiqueta = QLabel("Grosor:", cw)
        self.spinbox_grosor = QSpinBox(cw)
        self.spinbox_grosor.setRange(1, 10)
        self.boton_crear = QPushButton("Cambiar", cw)
        self.boton_cancelar = QPushButton("Candelar", cw, clicked=self.close)

    def abrir(self):
        self.spinbox_grosor.setValue(5)
        self.show()
        self.activateWindow()


class VentanaCambiarGrosorRecta(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.resize(170, 100)
        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowFlags(Qt.Tool)
        cw = QWidget()
        self.setCentralWidget(cw)
        self.setWindowTitle("Cambiar el grosor")
        etiqueta = QLabel("Grosor:", cw)
        self.spinbox_grosor = QSpinBox(cw)
        self.spinbox_grosor.setRange(1, 10)
        self.boton_crear = QPushButton("Cambiar", cw)
        self.boton_cancelar = QPushButton("Candelar", cw, clicked=self.close)

    def abrir(self):
        self.spinbox_grosor.setValue(2)
        self.show()
        self.activateWindow()


class VentanaPoligono(QMainWindow):
    def __init__(self, programa):
        QMainWindow.__init__(self)
        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowFlags(Qt.Tool)
        self.resize(185, 270)
        self.setWindowTitle("Crear polígono")
        self.programa = programa
        cw = QWidget()
        self.setCentralWidget(cw)

        etiqueta_centro = QLabel("Centro:", cw)
        self.centro = QComboBox(cw)
        etiqueta_plano = QLabel("Paralelo al plano:", cw)
        self.plano = QComboBox(cw)
        etiqueta_vertice = QLabel("Vértice:", cw)
        self.vertice = QComboBox(cw)
        etiqueta_lados = QLabel("Número de lados:", cw)
        self.lados = QSpinBox(cw)
        self.lados.setRange(3, 20)
        nombre = QLabel("Nombre:", cw)
        self.nombre = QLineEdit(cw)
        self.boton_cancelar = QPushButton("Cancelar", cw)
        self.boton_cancelar.clicked.connect(self.close)
        self.boton_crear = QPushButton("Crear", cw)
        self.boton_crear.clicked.connect(self.comprobar_poligono)

    def abrir(self):
        self.centro.clear()
        self.plano.clear()
        self.vertice.clear()

        for i in range(self.programa.lista_puntos.count()):
            self.centro.addItem(self.programa.lista_puntos.itemWidget(self.programa.lista_puntos.item(i)).nombre)
            self.vertice.addItem(self.programa.lista_puntos.itemWidget(self.programa.lista_puntos.item(i)).nombre)

        for i in range(self.programa.lista_planos.count()):
            self.plano.addItem(self.programa.lista_planos.itemWidget(self.programa.lista_planos.item(i)).nombre)

        self.show()
        self.activateWindow()

    def comprobar_poligono(self):
        nombre = self.nombre.text()
        centro = self.centro.currentText()
        plano = self.plano.currentText()
        vertice = self.vertice.currentText()
        if not nombre:
            QMessageBox.critical(self, "Error al crear el polígono", "No ha introducido un nombre")
        elif plano == "" or centro == "" or vertice == "":
            QMessageBox.critical(self, "Error al crear el polígono", "Debe crear dos puntos diferentes y un plano para"
                                                                     " definir el polígono")
        else:
            num_lados = self.lados.value()
            for i in range(self.programa.lista_puntos.count()):
                if self.programa.lista_puntos.itemWidget(self.programa.lista_puntos.item(i)).nombre == centro:
                    centro = self.programa.lista_puntos.itemWidget(self.programa.lista_puntos.item(i))
                if self.programa.lista_puntos.itemWidget(self.programa.lista_puntos.item(i)).nombre == vertice:
                    vertice = self.programa.lista_puntos.itemWidget(self.programa.lista_puntos.item(i))
            for i in range(self.programa.lista_planos.count()):
                if self.programa.lista_planos.itemWidget(self.programa.lista_planos.item(i)).nombre == plano:
                    plano = self.programa.lista_planos.itemWidget(self.programa.lista_planos.item(i))
            if centro == vertice:
                QMessageBox.critical(self, "Error al crear el polígono", "El centro coincide con el vértice")
            else:
                nombre = f"{nombre}║{plano.nombre}, vertice: {vertice.nombre}"
                vertice = vertice.entidad_geometrica.coords
                centro = centro.entidad_geometrica.coords
                v_n = plano.entidad_geometrica.vector_normal
                self.crear_poligono(nombre, vector_normal=v_n, vertice=vertice, num_lados=num_lados, centro=centro)

    def crear_poligono(self, nombre, vector_normal=None, vertice=None, centro=None, num_lados=None,
                       puntos: list = None):
        if not puntos:
            poligono = entidades_geometricas.Poligono(self.programa, nombre, vector_normal=vector_normal,
                                                      num_lados=num_lados, vertice=vertice, centro=centro)
        else:
            poligono = entidades_geometricas.Poligono(self.programa, nombre, puntos=puntos)
        item = QListWidgetItem()
        item.setSizeHint(poligono.minimumSizeHint())
        self.programa.lista_poligonos.addItem(item)
        self.programa.lista_poligonos.setItemWidget(item, poligono)
