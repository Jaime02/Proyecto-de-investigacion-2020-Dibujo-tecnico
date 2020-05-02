# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QApplication
from clases.ventana_principal import VentanaPrincipal


if __name__ == "__main__":
    evento_principal = QApplication([])
    programa = VentanaPrincipal(evento_principal)
    evento_principal.exec()
