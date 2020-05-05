from math import sin, cos, radians, acos, degrees
from sympy import Plane, Point3D
from pprint import pprint
import numpy as np


class Vec:
    def __init__(self, coords, normalizar=False):
        if normalizar:
            self.coords = self.normalizar(coords)
        else:
            self.coords = coords

    def dot(self, vec):
        # Producto escalar
        return sum([self.coords[indx] * vec.coords[indx] for indx in range(3)])

    def __mul__(self, scalar):
        # Producto escalar
        return Vec([coord * scalar for coord in self.coords])

    def __rmul__(self, scalar):
        # Producto escalar
        return Vec([coord * scalar for coord in self.coords])

    def cross(self, vec):
        # Producto vectorial
        return Vec([self.coords[1] * vec.coords[2] - self.coords[2] * vec.coords[1],
                    self.coords[2] * vec.coords[0] - self.coords[0] * vec.coords[2],
                    self.coords[0] * vec.coords[1] - self.coords[1] * vec.coords[0]])

    def __add__(self, other):
        if isinstance(other, (int, float)):
            # Suma de un vector con un escalar
            return Vec(self.coords[0] + other, self.coords[1] + other, self.coords[2] + other)
        else:
            # Suma de un vector mas otro
            return Vec([self.coords[0] + other.coords[0],
                        self.coords[1] + other.coords[1],
                        self.coords[2] + other.coords[2]])

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

    def __repr__(self):
        return str(self.coords)

def calcular_circunferencia(vector_normal, radio, centro):
    # Redefino estas funciones trigonométricas para evitar estar continuamente convirtiendo el ángulo a radianes
    def coseno(angulo):
        return cos(radians(angulo))

    def seno(angulo):
        return sin(radians(angulo))

    # Rotación de rodrigues
    def rodri(v: Vec, k: Vec, c):
        a = v*c
        b = k.cross(v)*((1-c**2)**0.5)
        c = k*(k.dot(v))*(1-c)
        return a + b + c

    def coseno_entre_vectores(vec1, vec2):
        return (vec1.dot(vec2)) / (vec1.modulo() * vec2.modulo())

    def calcular_vector_v(r: int, t: int):
        return Vec([r*coseno(t), r*seno(t), 0])

    # Lista que guarda los puntos
    puntos = []
    theta = coseno_entre_vectores(vector_e, vector_u)
    vector_k = vector_e.cross(vector_u)

    # Vector E, eje Z
    vector_e = Vec([0, 0, 1])

    # Al hacer que el número de segmentos dependa del radio, se mejora la resolución de la circunferencia
    n = radio*2 + 14

    # El vector normal al plano
    vector_u = Vec(vector_normal, normalizar=True)

    for i in range(1, n+1):
        vector_v = calcular_vector_v(radio, i * 360 / n)
        punto = rodri(vector_v, vector_k, theta)
        for j in range(3):
            punto.coords[j] = round(punto.coords[j] + centro.coordinates[j], 4)
        puntos.append(punto.coords)

    return puntos
