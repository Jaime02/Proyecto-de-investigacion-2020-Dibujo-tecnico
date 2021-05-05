from itertools import cycle
from pickle import dump, loads
from sys import exit

from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QFont, QColor, QIcon, QPalette
from PyQt5.QtWidgets import (QWidget, QCheckBox, QPushButton, QMainWindow, QLabel, QVBoxLayout, QSpinBox, QMenuBar,
                             QComboBox, QMessageBox, QGraphicsScene, QGraphicsView, QListWidgetItem, QListWidget,
                             QAction, QDockWidget, QFileDialog, QStackedWidget, QLineEdit)

from .entidades_geometricas import WidgetPunto, WidgetRecta, WidgetPlano, Punto, Recta, Plano
from .ventanas_base import (PuntoMedio, Interseccion, Bisectriz, Distancia, Proyectar, RectaParalelaARecta, Ajustes,
                            RectaPerpendicularAPlano, RectaPerpendicularARecta, PlanoParaleloAPlano, Controles,
                            AcercaDe, PlanoPerpendicularAPlano, VentanaCircunferencia, VentanaPoligono)
from .widgets_de_dibujo import Diedrico, Renderizador


class VentanaPrincipal(QMainWindow):
    def __init__(self, evento_principal, archivo=None):
        QMainWindow.__init__(self)
        self.setWindowTitle("Dibujo técnico")
        self.evento_principal = evento_principal
        self.evento_principal.setStyle('Fusion')
        self.evento_principal.setWindowIcon(QIcon("Logo.ico"))

        wc = QWidget()
        self.setCentralWidget(wc)

        self.barra_menu = QMenuBar()
        self.menu_archivo = self.barra_menu.addMenu("Archivo")

        self.accion_guardar = QAction("Guardar")
        self.accion_guardar.triggered.connect(self.guardar)
        self.menu_archivo.addAction(self.accion_guardar)

        self.accion_abrir = QAction("Abrir")
        self.accion_abrir.triggered.connect(self.elegir_archivo)
        self.menu_archivo.addAction(self.accion_abrir)

        self.borrar_todo = QAction("Borrar todo")
        self.borrar_todo.triggered.connect(self.borrar_todos_los_elementos)
        self.menu_archivo.addAction(self.borrar_todo)

        self.salir = QAction("Salir")
        self.salir.triggered.connect(self.closeEvent)
        self.menu_archivo.addAction(self.salir)

        self.accion_ajustes = QAction("Ajustes")
        self.ajustes = Ajustes()
        self.accion_ajustes.triggered.connect(self.ajustes.show)
        self.barra_menu.addAction(self.accion_ajustes)

        self.accion_controles = QAction("Controles")
        self.controles = Controles()
        self.accion_controles.triggered.connect(self.controles.show)
        self.barra_menu.addAction(self.accion_controles)

        self.accion_acerca_de = QAction("Acerca de")
        self.acerca_de = AcercaDe()
        self.accion_acerca_de.triggered.connect(self.acerca_de.show)
        self.barra_menu.addAction(self.accion_acerca_de)

        self.accion_modo_oscuro = QAction("Establecer modo nocturno")
        self.accion_modo_oscuro.triggered.connect(self.cambiar_modo)
        self.barra_menu.addAction(self.accion_modo_oscuro)

        self.renderizador = Renderizador(self)
        self.renderizador.setFocusPolicy(Qt.ClickFocus)
        dock_renderizador = QDockWidget("Renderizador")
        dock_renderizador.setWidget(self.renderizador)
        dock_renderizador.setFeatures(QDockWidget.DockWidgetMovable)
        self.addDockWidget(Qt.LeftDockWidgetArea, dock_renderizador)

        scene = QGraphicsScene()
        self.vista = QGraphicsView(scene)
        self.diedrico = Diedrico(self)
        self.diedrico.setFocusPolicy(Qt.ClickFocus)
        self.diedrico.setFixedSize(1000, 1000)
        scene.addWidget(self.diedrico)

        dock_diedrico = QDockWidget("Diédrico")
        dock_diedrico.setFeatures(QDockWidget.DockWidgetMovable)
        self.addDockWidget(Qt.RightDockWidgetArea, dock_diedrico)
        dock_diedrico.setWidget(self.vista)

        # Reduce un poco el zoom inicial para que quede mejor
        self.diedrico.zoom_out()
        self.diedrico.zoom_out()

        fuente = QFont("Arial")
        fuente.setPointSize(10)

        self.widget_stack = QStackedWidget(wc)
        self.widget_stack.setGeometry(0, 90, 500, 470)

        p1 = QWidget()
        p2 = QWidget()
        self.widget_stack.addWidget(p1)
        self.widget_stack.addWidget(p2)

        boton_cambiar_tab = QPushButton("Figuras", p1, geometry=QRect(400, 0, 70, 23))
        boton_cambiar_tab.clicked.connect(lambda: self.widget_stack.setCurrentIndex(1))

        boton_cambiar_a_tab_2 = QPushButton("Volver", p2, geometry=QRect(400, 0, 70, 23))
        boton_cambiar_a_tab_2.clicked.connect(lambda: self.widget_stack.setCurrentIndex(0))

        etiqueta_circunferencia = QLabel("Circunferencia:", p2, font=fuente, geometry=QRect(0, 30, 91, 16))
        boton_circunferencia = QPushButton("Crear circunferencia", p2, geometry=QRect(0, 50, 140, 20))
        self.ventana_circunferencia = VentanaCircunferencia(self)
        boton_circunferencia.clicked.connect(self.ventana_circunferencia.abrir)

        widget_circunferencia = QWidget(p2, geometry=QRect(0, 75, 140, 140))
        vertical_circunferencia = QVBoxLayout(widget_circunferencia)
        vertical_circunferencia.setContentsMargins(0, 0, 0, 0)
        self.lista_circunferencias = QListWidget(widget_circunferencia)
        vertical_circunferencia.addWidget(self.lista_circunferencias)

        etiqueta_poligono = QLabel("Polígono:", p2, font=fuente, geometry=QRect(150, 30, 91, 16))
        boton_poligono = QPushButton("Crear polígono", p2, geometry=QRect(150, 50, 140, 20))
        self.ventana_poligono = VentanaPoligono(self)
        boton_poligono.clicked.connect(self.ventana_poligono.abrir)

        widget_poligono = QWidget(p2, geometry=QRect(150, 75, 140, 140))
        vertical_poligono = QVBoxLayout(widget_poligono)
        vertical_poligono.setContentsMargins(0, 0, 0, 0)
        self.lista_poligonos = QListWidget(widget_poligono)
        vertical_poligono.addWidget(self.lista_poligonos)

        informacion = QLabel("Información:", wc, font=fuente, geometry=QRect(0, 10, 91, 16))
        posicion = QLabel("Posición:", wc, font=fuente, geometry=QRect(0, 30, 71, 16))

        self.posicion = QLabel("Primer cuadrante", wc, font=fuente, geometry=QRect(60, 30, 151, 16))
        self.angulo_vertical = QLabel(wc, font=fuente, geometry=QRect(0, 50, 121, 16))
        self.angulo_horizontal = QLabel(wc, font=fuente, geometry=QRect(120, 50, 130, 16))

        vista = QLabel("Vista:", wc, font=fuente, geometry=QRect(0, 71, 91, 16))
        boton_reset = QPushButton("Reset (R)", wc, geometry=QRect(0, 90, 81, 23))
        boton_reset.clicked.connect(self.renderizador.ver_reset)
        boton_alzado = QPushButton("Alzado (1) ''", wc, geometry=QRect(90, 90, 81, 23))
        boton_alzado.clicked.connect(self.renderizador.ver_alzado)
        boton_planta = QPushButton("Planta (2) '", wc, geometry=QRect(180, 90, 81, 23))
        boton_planta.clicked.connect(self.renderizador.ver_planta)
        boton_perfil = QPushButton("Perfil (3) '''", wc, geometry=QRect(270, 90, 81, 23))
        boton_perfil.clicked.connect(self.renderizador.ver_perfil)

        crear_puntos = QLabel("Crear puntos:", p1, font=fuente, geometry=QRect(0, 30, 91, 16))
        distancia_al_origen = QLabel("Distancia al origen:", p1, geometry=QRect(0, 50, 91, 16))
        alejamiento = QLabel("Alejamiento:", p1, geometry=QRect(0, 70, 91, 16))
        cota = QLabel("Cota:", p1, geometry=QRect(0, 90, 91, 16))

        crear_rectas = QLabel("Crear rectas:", p1, font=fuente, geometry=QRect(160, 30, 91, 16))
        punto_1_recta = QLabel("Punto 1:", p1, geometry=QRect(160, 50, 51, 16))
        punto_2_recta = QLabel("Punto 2:", p1, geometry=QRect(160, 70, 51, 16))

        crear_planos = QLabel("Crear planos:", p1, font=fuente, geometry=QRect(320, 30, 91, 16))
        punto_1_plano = QLabel("Punto 1:", p1, geometry=QRect(320, 50, 51, 16))
        punto_2_plano = QLabel("Punto 2:", p1, geometry=QRect(320, 70, 51, 16))
        punto_3_plano = QLabel("Punto 3:", p1, geometry=QRect(320, 90, 51, 16))

        self.punto_nombre = QLineEdit(p1, geometry=QRect(0, 115, 151, 25), placeholderText="Nombre del punto")
        self.recta_nombre = QLineEdit(p1, geometry=QRect(160, 115, 151, 25), placeholderText="Nombre de la recta")
        self.plano_nombre = QLineEdit(p1, geometry=QRect(320, 115, 151, 25), placeholderText="Nombre del plano")

        boton_punto = QPushButton("Crear", p1, geometry=QRect(0, 142, 151, 22))
        boton_punto.clicked.connect(self.comprobar_punto)
        boton_recta = QPushButton("Crear", p1, geometry=QRect(160, 142, 151, 22))
        boton_recta.clicked.connect(self.comprobar_recta)
        boton_plano = QPushButton("Crear", p1, geometry=QRect(320, 142, 151, 22))
        boton_plano.clicked.connect(self.comprobar_plano)

        self.valor_distancia_origen = QSpinBox(p1, geometry=QRect(100, 50, 51, 20))
        self.valor_distancia_origen.setRange(-499, 499)
        self.valor_alejamiento = QSpinBox(p1, geometry=QRect(100, 70, 51, 20))
        self.valor_alejamiento.setRange(-499, 499)
        self.valor_cota = QSpinBox(p1, geometry=QRect(100, 90, 51, 20))
        self.valor_cota.setRange(-499, 499)

        self.punto_recta_1 = QComboBox(p1, geometry=QRect(205, 50, 105, 22))
        self.punto_recta_2 = QComboBox(p1, geometry=QRect(205, 70, 105, 21))
        self.punto_plano_1 = QComboBox(p1, geometry=QRect(365, 50, 105, 22))
        self.punto_plano_2 = QComboBox(p1, geometry=QRect(365, 70, 105, 22))
        self.punto_plano_3 = QComboBox(p1, geometry=QRect(365, 90, 105, 22))

        widget_punto = QWidget(p1, geometry=QRect(0, 165, 150, 230))
        vertical_punto = QVBoxLayout(widget_punto)
        vertical_punto.setContentsMargins(0, 0, 0, 0)
        self.lista_puntos = QListWidget(widget_punto)
        vertical_punto.addWidget(self.lista_puntos)

        widget_recta = QWidget(p1, geometry=QRect(160, 165, 150, 230))
        vertical_recta = QVBoxLayout(widget_recta)
        vertical_recta.setContentsMargins(0, 0, 0, 0)
        self.lista_rectas = QListWidget(widget_recta)
        vertical_recta.addWidget(self.lista_rectas)

        widget_planos = QWidget(p1, geometry=QRect(320, 165, 151, 230))
        vertical_planos = QVBoxLayout(widget_planos)
        vertical_planos.setContentsMargins(0, 0, 0, 0)
        self.lista_planos = QListWidget(widget_planos)
        vertical_planos.addWidget(self.lista_planos)

        self.tercera_proyeccion = QCheckBox("Tercera proyección", dock_diedrico, geometry=QRect(55, 2, 111, 17))
        self.ver_puntos = QCheckBox("Puntos", dock_diedrico, checked=True, geometry=QRect(169, 2, 61, 17))
        self.ver_rectas = QCheckBox("Rectas", dock_diedrico, checked=True, geometry=QRect(227, 2, 61, 17))
        self.ver_planos = QCheckBox("Planos", dock_diedrico, checked=True, geometry=QRect(285, 2, 70, 17))

        herramientas = QLabel("Herramientas:", wc, font=fuente, geometry=QRect(0, 486, 100, 16))

        punto_medio = QPushButton("Punto medio", wc, geometry=QRect(0, 505, 91, 31))
        self.punto_medio = PuntoMedio(self)
        punto_medio.clicked.connect(self.punto_medio.abrir)

        distancia = QPushButton("Distancia", wc, geometry=QRect(100, 505, 101, 31))
        self.distancia = Distancia(self)
        distancia.clicked.connect(self.distancia.abrir)

        interseccion = QPushButton("Crear intersección", wc, geometry=QRect(210, 505, 101, 31))
        self.interseccion = Interseccion(self)
        interseccion.clicked.connect(self.interseccion.abrir)

        proyectar = QPushButton("Proyectar", wc, geometry=QRect(320, 505, 71, 31))
        self.proyectar = Proyectar(self)
        proyectar.clicked.connect(self.proyectar.abrir)

        bisectriz = QPushButton("Bisectriz", wc, geometry=QRect(400, 505, 71, 31))
        self.bisectriz = Bisectriz(self)
        bisectriz.clicked.connect(self.bisectriz.abrir)

        perpendicularidad = QLabel("Perpendicularidad:", wc, font=fuente, geometry=QRect(0, 545, 120, 16))

        recta_perp = QPushButton("Crear recta \nperpendicular a recta", wc, geometry=QRect(0, 565, 151, 41))
        self.recta_perpendicular_recta = RectaPerpendicularARecta(self)
        recta_perp.clicked.connect(self.recta_perpendicular_recta.abrir)

        rect_perp_plano = QPushButton("Crear recta \nperpendicular a plano", wc, geometry=QRect(160, 565, 151, 41))
        self.recta_perpendicular_plano = RectaPerpendicularAPlano(self)
        rect_perp_plano.clicked.connect(self.recta_perpendicular_plano.abrir)

        plano_perp_plano = QPushButton("Crear plano\nperpendicular a plano", wc, geometry=QRect(320, 565, 151, 41))
        self.plano_perpendicular_plano = PlanoPerpendicularAPlano(self)
        plano_perp_plano.clicked.connect(self.plano_perpendicular_plano.abrir)

        paralelismo = QLabel("Paralelismo:", wc, font=fuente, geometry=QRect(0, 615, 100, 16))

        recta_paralela_recta = QPushButton("Crear recta paralela a recta", wc, geometry=QRect(0, 635, 231, 31))
        self.recta_paralela_recta = RectaParalelaARecta(self)
        recta_paralela_recta.clicked.connect(self.recta_paralela_recta.abrir)

        plano_paralelo_plano = QPushButton("Crear plano paralelo a plano", wc, geometry=QRect(240, 635, 231, 31))
        self.plano_paralelo_plano = PlanoParaleloAPlano(self)
        plano_paralelo_plano.clicked.connect(self.plano_paralelo_plano.abrir)

        # Variables para permitir borrar los elementos, se asigna una diferente a cada fila
        self.id_punto = 1
        self.id_recta = 1
        self.id_plano = 1
        self.id_circunferencia = 1
        self.id_poligono = 1

        self.mayusculas = cycle("PQRSTUVWXYZABCDEFGHIJKLMNO")
        self.minusculas = cycle("rstuvwxyzabcdefghijklmnopq")

        alfabeto_griego = (u'\u03B1', u'\u03B2', u'\u03B3', u'\u03B4', u'\u03B5', u'\u03B6', u'\u03B7', u'\u03B8',
                           u'\u03B9', u'\u03BA', u'\u03BB', u'\u03BC', u'\u03BD', u'\u03BE', u'\u03BF', u'\u03C0',
                           u'\u03C1', u'\u03C3', u'\u03C4', u'\u03C5', u'\u03C6', u'\u03C7', u'\u03C8', u'\u03C9')
        self.alfabeto_griego = cycle(alfabeto_griego)
        self.actualizar_texto()
        self.modo_oscuro = False
        evento_principal.setStyleSheet(evento_principal.styleSheet() + "QMainWindow{border: 1px outset black;}")
        self.showMaximized()
        self.setMenuBar(self.barra_menu)

        if archivo:
            self.cargar_archivo(archivo)

    def actualizar_opciones(self):
        self.punto_recta_1.clear()
        self.punto_recta_2.clear()
        for i in range(self.lista_puntos.count()):
            self.punto_recta_1.addItem(self.lista_puntos.itemWidget(self.lista_puntos.item(i)).nombre)
            self.punto_recta_2.addItem(self.lista_puntos.itemWidget(self.lista_puntos.item(i)).nombre)

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
        if nombre == "":
            nombre = self.minusculas.__next__()
        return nombre

    def evitar_nombre_plano_blanco(self, nombre: str):
        if nombre == "":
            nombre = self.alfabeto_griego.__next__()
        return nombre

    def evitar_nombre_duplicado(self, nombre):
        nombres = []
        for i in range(self.lista_puntos.count()):
            nombres.append(self.lista_puntos.itemWidget(self.lista_puntos.item(i)).nombre)
        for i in range(self.lista_rectas.count()):
            nombres.append(self.lista_rectas.itemWidget(self.lista_rectas.item(i)).nombre)
        for i in range(self.lista_planos.count()):
            nombres.append(self.lista_planos.itemWidget(self.lista_planos.item(i)).nombre)

        if nombre in nombres:
            QMessageBox.critical(self, "Error al crear el punto", "Ha introducido un nombre que ya está siendo usado")
        else:
            return True

    def comprobar_punto(self):
        nombre = self.punto_nombre.text()
        do = self.valor_distancia_origen.value()
        alejamiento = self.valor_alejamiento.value()
        cota = self.valor_cota.value()
        nombre = self.evitar_nombre_punto_blanco(nombre)
        nombre = f"{nombre}({do}, {alejamiento}, {cota})"
        if self.evitar_nombre_duplicado(nombre):
            self.crear_punto(nombre, Punto(do, alejamiento, cota))

    def crear_punto(self, nombre: str, entidad_geometrica: Punto):
        punto = WidgetPunto(self, self.id_punto, nombre, entidad_geometrica)
        item = QListWidgetItem()
        item.setSizeHint(punto.minimumSizeHint())
        self.lista_puntos.addItem(item)
        self.lista_puntos.setItemWidget(item, punto)
        self.id_punto += 1
        self.actualizar_opciones()

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
            nombre = self.evitar_nombre_recta_blanco(self.recta_nombre.text())
            nombre = f"{nombre}({punto1.nombre}, {punto2.nombre})"

            if self.evitar_nombre_duplicado(nombre):
                self.crear_recta(nombre, Recta(punto1.entidad_geometrica, punto2.entidad_geometrica), [punto1.entidad_geometrica, punto2.entidad_geometrica])

    def crear_recta(self, nombre: str, entidad_geometrica: Recta, puntos: list = None):
        recta = WidgetRecta(self, self.id_recta, nombre, entidad_geometrica, puntos)
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
        elif punto1.entidad_geometrica.colinear(punto2.entidad_geometrica, punto3.entidad_geometrica):
            QMessageBox.critical(self, "Error al crear el plano",
                                 "El plano debe ser creado por tres puntos no alineados")
        else:
            nombre = self.evitar_nombre_plano_blanco(self.plano_nombre.text())
            nombre = f"{nombre}({punto1.nombre}, {punto3.nombre}, {punto2.nombre})"

            if self.evitar_nombre_duplicado(nombre):
                self.crear_plano(nombre, Plano(punto1.entidad_geometrica, punto2.entidad_geometrica, punto3.entidad_geometrica),
                                 puntos=[punto1.coordenadas, punto2.coordenadas, punto3.coordenadas])

    def crear_plano(self, nombre: str, entidad_geometrica: Plano, puntos: list = None):
        plano = WidgetPlano(self, self.id_plano, nombre, entidad_geometrica, puntos)
        item = QListWidgetItem()
        self.lista_planos.addItem(item)
        item.setSizeHint(plano.minimumSizeHint())
        self.lista_planos.setItemWidget(item, plano)
        self.id_plano += 1

    def borrar_todos_los_elementos(self):
        self.lista_puntos.clear()
        self.lista_rectas.clear()
        self.lista_planos.clear()
        self.lista_circunferencias.clear()
        self.lista_poligonos.clear()
        self.actualizar_opciones()

    def guardar(self):
        try:
            elementos = self.recolectar_elementos()
            if elementos:
                nombre, extension = QFileDialog.getSaveFileName(self, "Guardar", "", "Diédrico (*.diedrico)")
                with open(nombre, 'wb') as archivo:
                    dump(elementos, archivo)
            else:
                QMessageBox.critical(self, "Error al guardar", "No se ha creado ningún elemento")
        except FileNotFoundError:
            return False
        except OSError:
            QMessageBox.critical(self, "Error al guardar", "Se ha producido un error al guardar el archivo")

    def recolectar_elementos(self) -> dict:
        elementos = {"Puntos": [], "Rectas": [], "Planos": [], "Circunferencias": [], "Poligonos": []}

        for i in range(self.lista_puntos.count()):
            punto = self.lista_puntos.itemWidget(self.lista_puntos.item(i)).guardar()
            elementos["Puntos"].append(punto)

        for i in range(self.lista_rectas.count()):
            recta = self.lista_rectas.itemWidget(self.lista_rectas.item(i)).guardar()
            elementos["Rectas"].append(recta)

        for i in range(self.lista_planos.count()):
            plano = self.lista_planos.itemWidget(self.lista_planos.item(i)).guardar()
            elementos["Planos"].append(plano)

        for i in range(self.lista_circunferencias.count()):
            circunferencia = self.lista_circunferencias.itemWidget(self.lista_circunferencias.item(i)).guardar()
            elementos["Circunferencias"].append(circunferencia)

        for i in range(self.lista_poligonos.count()):
            poligono = self.lista_poligonos.itemWidget(self.lista_poligonos.item(i)).guardar()
            elementos["Poligonos"].append(poligono)

        if elementos != {"Puntos": [], "Rectas": [], "Planos": [], "Circunferencias": [], "Poligonos": []}:
            return elementos
        else:
            return False

    def elegir_archivo(self):
        try:
            nombre, extension = QFileDialog.getOpenFileName(self, "Abrir", "", "Diédrico (*.diedrico)")
            self.cargar_archivo(nombre)
        except FileNotFoundError:
            pass
        except OSError:
            QMessageBox.critical(self, "Error al abrir", "Se ha producido un error al abrir el archivo")

    def cargar_archivo(self, nombre):
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

            for circ in elementos["Circunferencias"]:
                self.ventana_circunferencia.crear_circunferencia(circ["Nombre"], puntos=circ["Puntos"])

            for poligono in elementos["Poligonos"]:
                self.ventana_poligono.crear_poligono(poligono["Nombre"], puntos=poligono["Puntos"])

    def cambiar_modo(self):
        if self.modo_oscuro:
            # Cambiar a modo claro
            self.vista.setStyleSheet("background-color: rgb(240, 240, 240)")
            self.diedrico.setStyleSheet("background-color: white")
            self.diedrico.pen_base.setColor(QColor(0, 0, 0))
            modo_claro = QPalette(self.evento_principal.style().standardPalette())
            self.evento_principal.setPalette(modo_claro)
            self.modo_oscuro = False
            self.accion_modo_oscuro.setText("Establecer modo nocturno")
        else:
            # Cambiar a modo oscuro
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
            modo_oscuro.setColor(QPalette.Link, Qt.red)
            modo_oscuro.setColor(QPalette.Highlight, QColor(42, 130, 218))
            modo_oscuro.setColor(QPalette.HighlightedText, Qt.black)
            self.evento_principal.setPalette(modo_oscuro)
            self.modo_oscuro = True
            self.accion_modo_oscuro.setText("Establecer modo diurno")
        self.evento_principal.setStyleSheet(self.evento_principal.styleSheet() +
                                            "QMainWindow{border: 1px outset black;}")

    def closeEvent(self, evento):
        if self.recolectar_elementos():
            reply = QMessageBox()
            reply.setWindowTitle("Salir")
            reply.setText("¿Quiere guardar los elementos geométricos antes de salir?")
            reply.addButton("Guardar", QMessageBox.AcceptRole)
            reply.addButton("Salir sin guardar", QMessageBox.DestructiveRole)
            reply.addButton("Cancelar", QMessageBox.RejectRole)
            resultado = reply.exec()
            if resultado == QMessageBox.AcceptRole: # Guardar
                if self.guardar():
                    exit()
                else:
                    evento.ignore()
            elif resultado == QMessageBox.RejectRole: # Salir sin guardar
                exit()
            else:
                evento.ignore()
        else:
            exit()
