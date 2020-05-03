from math import sin, cos, radians, acos
from sympy import Plane, Point3D
from pprint import pprint

def calcular_circunferencia(plano, radio, centro, n=16):
    # Redefino estas funciones trigonométricas para evitar estar continuamente convirtiendo el ángulo a radianes
    def coseno(angulo):
        return cos(radians(angulo))

    def seno(angulo):
        return sin(radians(angulo))

    class Vec:
        def __init__(self, x, y, z):
            self.x = x
            self.y = y
            self.z = z
            self.coords = (x, y, z)

        def dot(self, vec):
            # Producto escalar
            return sum([self.coords[indx]*vec.coords[indx] for indx in range(len(self.coords))])

        def __mul__(self, scalar):
            # Producto escalar
            return Vec(*[coord*scalar for coord in self.coords])

        def __rmul__(self, scalar):
            # Producto escalar
            return Vec(*[coord*scalar for coord in self.coords])

        def cross(self, vec):
            # Producto vectorial
            return Vec(self.y * vec.z - self.z * vec.y, self.z * vec.x - self.x * vec.z, self.x * vec.y - self.y * vec.x)

        def __add__(self, other):
            if isinstance(other, (int, float)):
                # Suma de un vector con un escalar
                return Vec(self.x + other, self.y + other, self.z + other)
            else:
                # Suma de un vector mas otro
                return Vec(self.x + other.x, self.y + other.y, self.z + other.z)

        def modulo(self):
            return sum([coord**2 for coord in self.coords])**0.5

    # Vector E, eje Z
    vector_e = Vec(0, 1, 0)

    # El vector normal al plano
    vector_u = Vec(*plano.normal_vector)

    # Rotación de rodrigues
    def rodri(v: Vec, k: Vec, t: int):
        return v*cos(radians(t)) + k.cross(v)*seno(t) + k*(k.dot(v))*(1-coseno(t))

    def calcular_vector_v(r: int, t: int):
        return Vec(r*coseno(t), r*seno(t), 0)

    def calcular_k(e, u):
        return e.cross(u)

    def angulo_entre_vectores(vec1, vec2):
        return acos(radians((vec1.dot(vec2))/(vec1.modulo()*vec2.modulo())))

    # Lista que guarda los puntos
    puntos = []

    theta = angulo_entre_vectores(vector_e, vector_u)

    for i in range(1, n+1):
        vec_v = calcular_vector_v(1, i * 360 / n)
        punto = rodri(vec_v, calcular_k(vector_e, vector_u), theta)
        puntos.append(tuple([round(punto.coords[i] + centro[i], 3) for i in range(len(punto.coords))]))

    return puntos

# p = Plane(Point3D(0, 0, 0), normal_vector=(0, 1, 0))
# pprint(calcular_circunferencia(p, 1, Point3D(0, 0, 0)))
