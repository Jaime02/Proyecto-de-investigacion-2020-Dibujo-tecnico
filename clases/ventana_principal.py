from itertools import cycle
from pickle import dump, loads
from sys import exit

from PySide6.QtCore import Qt, QRect, QSize
from PySide6.QtGui import QFont, QColor, QIcon, QPalette, QAction
from PySide6.QtWidgets import (QWidget, QCheckBox, QPushButton, QMainWindow, QLabel, QVBoxLayout, QSpinBox, QMenuBar,
                               QComboBox, QMessageBox, QGraphicsScene, QGraphicsView, QListWidgetItem, QListWidget,
                               QDockWidget, QFileDialog, QStackedWidget, QLineEdit, QApplication, QHBoxLayout,
                               QFormLayout, QSizePolicy, QSpacerItem)

from .entidades_geometricas import WidgetPunto, WidgetRecta, WidgetPlano, Punto, Recta, Plano
from .ventanas_secundarias import (PuntoMedio, Interseccion, Bisectriz, Distancia, Proyectar, RectaParalelaARecta, Ajustes,
                                   RectaPerpendicularAPlano, RectaPerpendicularARecta, PlanoParaleloAPlano, Controles,
                                   AcercaDe, PlanoPerpendicularAPlano, VentanaCircunferencia, VentanaPoligono)
from .widgets_de_dibujo import Diedrico, Renderizador


class VentanaPrincipal(QMainWindow):
    def __init__(self, evento_principal: QApplication, archivo=None):
        QMainWindow.__init__(self)
        self.setWindowTitle("Dibujo técnico")
        self.evento_principal = evento_principal
        self.evento_principal.setStyle('Fusion')
        self.evento_principal.setWindowIcon(QIcon("Logo.ico"))

        widget_central: QWidget = QWidget()
        self.setCentralWidget(widget_central)

        self.layout_principal = QVBoxLayout()
        self.layout_principal.setContentsMargins(10, 5, 10, 0)
        widget_central.setLayout(self.layout_principal)

        # Menu:
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

        self.accion_tema_oscuro = QAction("Establecer tema nocturno")
        self.accion_tema_oscuro.triggered.connect(self.cambiar_tema)
        self.barra_menu.addAction(self.accion_tema_oscuro)

        self.renderizador = Renderizador(self)
        self.renderizador.setFocusPolicy(Qt.ClickFocus)
        self.dock_renderizador = QDockWidget(" Renderizador")
        self.dock_renderizador.setObjectName("dock_renderizador")
        self.setStyleSheet("QMainWindow::separator { width: 15px; } "
                           "QMainWindow::separator:hover {background: lightgray; }")
        self.dock_renderizador.setWidget(self.renderizador)
        self.dock_renderizador.setFeatures(QDockWidget.DockWidgetMovable)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.dock_renderizador)

        self.scene = QGraphicsScene()
        self.vista = QGraphicsView(self.scene)
        self.diedrico = Diedrico(self)
        self.diedrico.setFocusPolicy(Qt.ClickFocus)
        self.diedrico.setFixedSize(1000, 1000)
        self.scene.addWidget(self.diedrico)

        self.dock_diedrico = QDockWidget("Diédrico")
        self.dock_diedrico.setFeatures(QDockWidget.DockWidgetMovable)
        self.addDockWidget(Qt.RightDockWidgetArea, self.dock_diedrico)
        self.dock_diedrico.setWidget(self.vista)

        # The following class comes from
        # https://stackoverflow.com/a/68262511/11760835
        class LayoutIgnoraAnchura(QHBoxLayout):
            def setGeometry(self, geometry: QRect):
                geometry.setHeight(QHBoxLayout.minimumSize(self).height())
                QHBoxLayout.setGeometry(self, geometry)

            def minimumSize(self):
                return QSize(0, QHBoxLayout.sizeHint(self).height())

        self.layout_diedrico_checkbox = LayoutIgnoraAnchura()
        self.layout_diedrico_checkbox.setContentsMargins(5, 0, 5, 0)
        contenedor = QWidget()
        contenedor.setLayout(self.layout_diedrico_checkbox)
        label = QLabel("Diédrico")
        self.layout_diedrico_checkbox.addWidget(label)

        self.layout_diedrico_checkbox.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))

        self.tercera_proyeccion = QCheckBox("Tercera proyección")
        self.layout_diedrico_checkbox.addWidget(self.tercera_proyeccion)
        self.ver_puntos = QCheckBox("Puntos", checked=True)
        self.layout_diedrico_checkbox.addWidget(self.ver_puntos)
        self.ver_rectas = QCheckBox("Rectas", checked=True)
        self.layout_diedrico_checkbox.addWidget(self.ver_rectas)
        self.ver_planos = QCheckBox("Planos", checked=True)
        self.layout_diedrico_checkbox.addWidget(self.ver_planos)

        self.dock_diedrico.setTitleBarWidget(contenedor)

        # Reduce un poco el zoom inicial para que quede mejor
        self.diedrico.zoom_out()
        self.diedrico.zoom_out()

        fuente = QFont()
        fuente.setPointSize(11)
        informacion = QLabel("Información:", font=fuente)
        self.layout_principal.addWidget(informacion)

        self.posicion = QLabel("Posición: Primer cuadrante", font=fuente)
        self.layout_principal.addWidget(self.posicion)

        self.layout_angulos = QHBoxLayout()
        self.layout_principal.addLayout(self.layout_angulos)

        self.angulo_vertical = QLabel(font=fuente)
        self.layout_angulos.addWidget(self.angulo_vertical)

        self.angulo_horizontal = QLabel(font=fuente)
        self.layout_angulos.addWidget(self.angulo_horizontal)

        self.layout_angulos.addStretch(0)

        vista = QLabel("Vista:", font=fuente)
        self.layout_principal.addWidget(vista)

        self.layout_vistas = QHBoxLayout()
        self.layout_principal.addLayout(self.layout_vistas)
        boton_reset = QPushButton("Reset (R)")
        boton_reset.clicked.connect(self.renderizador.ver_reset)
        self.layout_vistas.addWidget(boton_reset)

        boton_alzado = QPushButton("Alzado (1) ''")
        boton_alzado.clicked.connect(self.renderizador.ver_alzado)
        self.layout_vistas.addWidget(boton_alzado)

        boton_planta = QPushButton("Planta (2) '")
        boton_planta.clicked.connect(self.renderizador.ver_planta)
        self.layout_vistas.addWidget(boton_planta)

        boton_perfil = QPushButton("Perfil (3) '''")
        boton_perfil.clicked.connect(self.renderizador.ver_perfil)
        self.layout_vistas.addWidget(boton_perfil)

        self.widget_stack = QStackedWidget()
        self.layout_principal.addWidget(self.widget_stack)

        # Paginas:
        pagina_1 = QWidget()
        pagina_2 = QWidget()
        self.widget_stack.addWidget(pagina_1)
        self.widget_stack.addWidget(pagina_2)

        boton_cambiar_a_tab_1 = QPushButton("Figuras")
        boton_cambiar_a_tab_1.clicked.connect(lambda: self.widget_stack.setCurrentIndex(1))
        self.layout_vistas.addWidget(boton_cambiar_a_tab_1)

        boton_cambiar_a_tab_2 = QPushButton("Volver")
        boton_cambiar_a_tab_2.clicked.connect(lambda: self.widget_stack.setCurrentIndex(0))

        self.layout_p1 = QVBoxLayout()
        self.layout_p1.setContentsMargins(0, 5, 0, 0)
        pagina_1.setLayout(self.layout_p1)

        self.layout_crear_elementos = QHBoxLayout()
        self.layout_crear_elementos_2 = QHBoxLayout()

        self.layout_p1.addLayout(self.layout_crear_elementos)
        self.layout_p1.addLayout(self.layout_crear_elementos_2)

        self.layout_col_1 = QVBoxLayout()
        self.layout_col_2 = QVBoxLayout()
        self.layout_col_3 = QVBoxLayout()
        self.layout_col_1_row_2 = QVBoxLayout()
        self.layout_col_2_row_2 = QVBoxLayout()
        self.layout_col_3_row_2 = QVBoxLayout()
        self.layout_crear_elementos.addLayout(self.layout_col_1)
        self.layout_crear_elementos.addLayout(self.layout_col_2)
        self.layout_crear_elementos.addLayout(self.layout_col_3)
        self.layout_crear_elementos_2.addLayout(self.layout_col_1_row_2)
        self.layout_crear_elementos_2.addLayout(self.layout_col_2_row_2)
        self.layout_crear_elementos_2.addLayout(self.layout_col_3_row_2)

        # Inicio de la creacion de puntos

        crear_puntos = QLabel("Crear puntos:", font=fuente)
        self.layout_col_1.addWidget(crear_puntos)

        self.layout_datos_punto = QFormLayout()
        self.layout_col_1.addLayout(self.layout_datos_punto)

        distancia_al_origen = QLabel("Distancia al origen:")
        self.valor_distancia_origen = QSpinBox()
        self.valor_distancia_origen.setRange(-499, 499)
        self.layout_datos_punto.addRow(distancia_al_origen, self.valor_distancia_origen)

        alejamiento = QLabel("Alejamiento:")
        self.valor_alejamiento = QSpinBox()
        self.valor_alejamiento.setRange(-499, 499)
        self.layout_datos_punto.addRow(alejamiento, self.valor_alejamiento)

        cota = QLabel("Cota:")
        self.valor_cota = QSpinBox()
        self.valor_cota.setRange(-499, 499)
        self.layout_datos_punto.addRow(cota, self.valor_cota)

        self.punto_nombre = QLineEdit(placeholderText="Nombre del punto")
        self.layout_col_1_row_2.addWidget(self.punto_nombre)

        boton_punto = QPushButton("Crear")
        boton_punto.clicked.connect(self.comprobar_punto)
        self.layout_col_1_row_2.addWidget(boton_punto)

        widget_punto = QWidget()
        vertical_punto = QVBoxLayout(widget_punto)
        vertical_punto.setContentsMargins(0, 0, 0, 0)
        self.lista_puntos = QListWidget(widget_punto)
        vertical_punto.addWidget(self.lista_puntos)
        self.layout_col_1_row_2.addWidget(widget_punto)

        # Fin de la creacion de puntos

        # Inicio de la creacion de rectas

        crear_rectas = QLabel("Crear rectas:", font=fuente)
        crear_rectas.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.layout_col_2.addWidget(crear_rectas)

        self.layout_puntos_recta = QFormLayout()
        self.layout_col_2.addLayout(self.layout_puntos_recta)

        punto_1_recta = QLabel("Punto 1:")
        self.punto_recta_1 = QComboBox()
        self.layout_puntos_recta.addRow(punto_1_recta, self.punto_recta_1)

        punto_2_recta = QLabel("Punto 2:")
        self.punto_recta_2 = QComboBox()
        self.layout_puntos_recta.addRow(punto_2_recta, self.punto_recta_2)

        self.recta_nombre = QLineEdit(placeholderText="Nombre de la recta")
        self.layout_col_2_row_2.addWidget(self.recta_nombre)

        boton_recta = QPushButton("Crear")
        boton_recta.clicked.connect(self.comprobar_recta)
        self.layout_col_2_row_2.addWidget(boton_recta)

        widget_recta = QWidget()
        vertical_recta = QVBoxLayout(widget_recta)
        vertical_recta.setContentsMargins(0, 0, 0, 0)
        self.lista_rectas = QListWidget(widget_recta)
        vertical_recta.addWidget(self.lista_rectas)
        self.layout_col_2_row_2.addWidget(widget_recta)

        # Fin de la creacion de rectas

        # Inicio de la creacion de planos

        crear_planos = QLabel("Crear planos:", font=fuente)
        self.layout_col_3.addWidget(crear_planos)

        self.layout_puntos_plano = QFormLayout()
        self.layout_col_3.addLayout(self.layout_puntos_plano)

        punto_1_plano = QLabel("Punto 1:")
        self.punto_plano_1 = QComboBox()
        self.layout_puntos_plano.addRow(punto_1_plano, self.punto_plano_1)

        punto_2_plano = QLabel("Punto 2:")
        self.punto_plano_2 = QComboBox()
        self.layout_puntos_plano.addRow(punto_2_plano, self.punto_plano_2)

        punto_3_plano = QLabel("Punto 3:")
        self.punto_plano_3 = QComboBox()
        self.layout_puntos_plano.addRow(punto_3_plano, self.punto_plano_3)

        self.plano_nombre = QLineEdit(placeholderText="Nombre del plano")
        self.layout_col_3_row_2.addWidget(self.plano_nombre)

        boton_plano = QPushButton("Crear")
        boton_plano.clicked.connect(self.comprobar_plano)
        self.layout_col_3_row_2.addWidget(boton_plano)

        widget_planos = QWidget()
        vertical_planos = QVBoxLayout(widget_planos)
        vertical_planos.setContentsMargins(0, 0, 0, 0)
        self.lista_planos = QListWidget(widget_planos)
        vertical_planos.addWidget(self.lista_planos)
        self.layout_col_3_row_2.addWidget(widget_planos)

        # Fin de la creacion de planos

        herramientas = QLabel("Herramientas:", font=fuente)
        self.layout_principal.addWidget(herramientas)

        self.layout_fila_1 = QHBoxLayout()
        self.layout_principal.addLayout(self.layout_fila_1)

        punto_medio = QPushButton("Punto medio")
        self.layout_fila_1.addWidget(punto_medio)
        self.punto_medio = PuntoMedio(self)
        punto_medio.clicked.connect(self.punto_medio.abrir)

        distancia = QPushButton("Distancia")
        self.layout_fila_1.addWidget(distancia)
        self.distancia = Distancia(self)
        distancia.clicked.connect(self.distancia.abrir)

        interseccion = QPushButton("Intersección")
        self.layout_fila_1.addWidget(interseccion)
        self.interseccion = Interseccion(self)
        interseccion.clicked.connect(self.interseccion.abrir)

        proyectar = QPushButton("Proyectar")
        self.layout_fila_1.addWidget(proyectar)
        self.proyectar = Proyectar(self)
        proyectar.clicked.connect(self.proyectar.abrir)

        bisectriz = QPushButton("Bisectriz")
        self.layout_fila_1.addWidget(bisectriz)
        self.bisectriz = Bisectriz(self)
        bisectriz.clicked.connect(self.bisectriz.abrir)

        perpendicularidad = QLabel("Perpendicularidad:", font=fuente)
        self.layout_principal.addWidget(perpendicularidad)

        self.layout_fila_2 = QHBoxLayout()
        self.layout_principal.addLayout(self.layout_fila_2)

        recta_perp_recta = QPushButton("Crear recta perpendicular a recta")
        self.layout_fila_2.addWidget(recta_perp_recta)
        self.recta_perpendicular_recta = RectaPerpendicularARecta(self)
        recta_perp_recta.clicked.connect(self.recta_perpendicular_recta.abrir)

        recta_perp_plano = QPushButton("Crear recta perpendicular a plano")
        self.layout_fila_2.addWidget(recta_perp_plano)
        self.recta_perpendicular_plano = RectaPerpendicularAPlano(self)
        recta_perp_plano.clicked.connect(self.recta_perpendicular_plano.abrir)

        plano_perp_plano = QPushButton("Crear plano perpendicular a plano")
        self.layout_fila_2.addWidget(plano_perp_plano)
        self.plano_perpendicular_plano = PlanoPerpendicularAPlano(self)
        plano_perp_plano.clicked.connect(self.plano_perpendicular_plano.abrir)

        paralelismo = QLabel("Paralelismo:", font=fuente)
        self.layout_principal.addWidget(paralelismo)

        self.layout_fila_3 = QHBoxLayout()
        self.layout_principal.addLayout(self.layout_fila_3)

        recta_paralela_recta = QPushButton("Crear recta paralela a recta")
        self.layout_fila_3.addWidget(recta_paralela_recta)
        self.recta_paralela_recta = RectaParalelaARecta(self)
        recta_paralela_recta.clicked.connect(self.recta_paralela_recta.abrir)

        plano_paralelo_plano = QPushButton("Crear plano paralelo a plano")
        self.layout_fila_3.addWidget(plano_paralelo_plano)
        self.plano_paralelo_plano = PlanoParaleloAPlano(self)
        plano_paralelo_plano.clicked.connect(self.plano_paralelo_plano.abrir)

        # Circunferencias y poligonos:

        etiqueta_circunferencia = QLabel("Circunferencia:", pagina_2, font=fuente)
        boton_circunferencia = QPushButton("Crear circunferencia", pagina_2)
        self.ventana_circunferencia = VentanaCircunferencia(self)
        boton_circunferencia.clicked.connect(self.ventana_circunferencia.abrir)

        widget_circunferencia = QWidget(pagina_2)
        vertical_circunferencia = QVBoxLayout(widget_circunferencia)
        vertical_circunferencia.setContentsMargins(0, 0, 0, 0)
        self.lista_circunferencias = QListWidget(widget_circunferencia)
        vertical_circunferencia.addWidget(self.lista_circunferencias)

        etiqueta_poligono = QLabel("Polígono:", pagina_2, font=fuente)
        boton_poligono = QPushButton("Crear polígono", pagina_2)
        self.ventana_poligono = VentanaPoligono(self)
        boton_poligono.clicked.connect(self.ventana_poligono.abrir)

        widget_poligono = QWidget(pagina_2)
        vertical_poligono = QVBoxLayout(widget_poligono)
        vertical_poligono.setContentsMargins(0, 0, 0, 0)
        self.lista_poligonos = QListWidget(widget_poligono)
        vertical_poligono.addWidget(self.lista_poligonos)

        # Un poco de espacio abajo
        self.layout_principal.addSpacing(20)

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
        self.tema_oscuro = False
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
            self.posicion.setText("Posición: Línea de tierra")
        elif z == 0:
            if y > 0:
                self.posicion.setText("Posición: Plano vertical positivo")
            else:
                self.posicion.setText("Posición: Plano vertical negativo")
        elif y == 0:
            if z > 0:
                self.posicion.setText("Posición: Plano horizontal positivo")
            else:
                self.posicion.setText("Posición: Plano horizontal negativo")
        elif z > 0:
            if y > 0:
                self.posicion.setText("Posición: Primer cuadrante")
            else:
                self.posicion.setText("Posición: Cuarto cuadrante")
        else:
            if y > 0:
                self.posicion.setText("Posición: Segundo cuadrante")
            else:
                self.posicion.setText("Posición: Tercer cuadrante")

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
                self.crear_recta(nombre, Recta(punto1.entidad_geometrica, punto2.entidad_geometrica),
                                 [punto1.entidad_geometrica, punto2.entidad_geometrica])

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
                self.crear_plano(nombre,
                                 Plano(punto1.entidad_geometrica, punto2.entidad_geometrica, punto3.entidad_geometrica),
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

    def cambiar_tema(self):
        if self.tema_oscuro:
            # Cambiar a tema claro
            self.setStyleSheet("QMainWindow::separator { width: 15px; } "
                               "QMainWindow::separator:hover {background: lightgray; }")
            self.vista.setStyleSheet("background-color: rgb(240, 240, 240)")
            self.diedrico.setStyleSheet("background-color: white")
            self.diedrico.pen_base.setColor(QColor(0, 0, 0))
            tema_claro = QPalette(self.evento_principal.style().standardPalette())
            self.evento_principal.setPalette(tema_claro)
            self.tema_oscuro = False
            self.accion_tema_oscuro.setText("Establecer tema nocturno")
        else:
            # Cambiar a tema oscuro
            self.setStyleSheet("QMainWindow::separator { width: 15px; } "
                               "QMainWindow::separator:hover {background: rgb(72, 72, 72); }")
            self.vista.setStyleSheet("background-color: rgb(20, 20, 20)")
            self.diedrico.setStyleSheet("background-color: rgb(40, 40, 40)")
            self.diedrico.pen_base.setColor(QColor(200, 200, 200))
            tema_oscuro = QPalette()
            tema_oscuro.setColor(QPalette.Window, QColor(53, 53, 53))
            tema_oscuro.setColor(QPalette.WindowText, Qt.white)
            tema_oscuro.setColor(QPalette.Base, QColor(25, 25, 25))
            tema_oscuro.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
            tema_oscuro.setColor(QPalette.Text, Qt.white)
            tema_oscuro.setColor(QPalette.Button, QColor(53, 53, 53))
            tema_oscuro.setColor(QPalette.ButtonText, Qt.white)
            tema_oscuro.setColor(QPalette.Link, Qt.red)
            tema_oscuro.setColor(QPalette.Highlight, QColor(42, 130, 218))
            tema_oscuro.setColor(QPalette.HighlightedText, Qt.white)
            tema_oscuro.setColor(QPalette.PlaceholderText, Qt.white)
            self.evento_principal.setPalette(tema_oscuro)
            self.tema_oscuro = True
            self.accion_tema_oscuro.setText("Establecer tema diurno")
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
            if resultado == QMessageBox.AcceptRole:  # Guardar
                if self.guardar():
                    exit()
                else:
                    evento.ignore()
            elif resultado == QMessageBox.RejectRole:  # Salir sin guardar
                exit()
            else:
                evento.ignore()
        else:
            # Si no hay nada que guardar, salimos directamente
            exit()
