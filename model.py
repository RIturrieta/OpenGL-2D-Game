""" Clases usadas en el programa"""

import glfw
import numpy as np
import grafica.transformations as tr
from random import *

class Player():
    # Clase que contiene al modelo del player / auro
    def __init__(self, size):
        self.pos = [0,-0.85] # Posicion en el escenario
        self.vel = [0.3,0.2] # Velocidad de desplazamiento
        self.infectado = False # El jugador esta infectado o no
        self.zombie = False # El jugador se ha convertido en zombie o no
        self.model = None # Referencia al grafo de escena asociado
        self.controller = None # Referencia del controlador, para acceder a sus variables
        self.size = size # Escala a aplicar al nodo 
        self.radio = 0.025 # Distancia para realizar los calculos de colision

    def set_model(self, new_model):
        # Se obtiene una referencia a uno nodo
        self.model = new_model

    def set_controller(self, new_controller):
        # Se obtiene la referncia al controller
        self.controller = new_controller

    def update(self, delta):
        # Se actualiza la posicion del jugador

        # Si detecta la tecla [D] presionada se mueve hacia la derecha
        if self.controller.is_d_pressed and self.pos[0] < 0.5:
            self.pos[0] += self.vel[0] * delta
        # Si detecta la tecla [A] presionada se mueve hacia la izquierda
        if self.controller.is_a_pressed and self.pos[0] > -0.5:
            self.pos[0] -= self.vel[0] * delta
        # Si detecta la tecla [W] presionada y no se ha salido de la pista se mueve hacia arriba
        if self.controller.is_w_pressed and self.pos[1] < 0.9:
            self.pos[1] += self.vel[1] * delta
        # Si detecta la tecla [S] presionada y no se ha salido de la pista se mueve hacia abajo
        if self.controller.is_s_pressed and self.pos[1] > -0.9:
            self.pos[1] -= self.vel[1] * delta

        # Se le aplica la transformacion de traslado segun la posicion actual
        self.model.transform = tr.matmul([tr.translate(self.pos[0], self.pos[1], 0), tr.scale(self.size, self.size, 1)])

    def collision(self, npcs):
        # Funcion para detectar las colisiones con zombies

        # Se recorren los npcs
        for npc in npcs:
            if npc.eszombie == 1: # Solo se ejecuta para zombies
                # si la distancia al npc es menor que la suma de los radios ha ocurrido en la colision
                if (self.radio+npc.radio)**2 > ((self.pos[0]- npc.mov[npc.posA][0])**2 + (self.pos[1]-npc.mov[npc.posA][1])**2):
                    return True


    def contagio(self, npcs):
        # Funcion para detectar las colisiones con humanos contagiados

        # Se recorren los npcs
        for npc in npcs:
            if npc.infectado == 1: # Solo se ejecuta para infectados
                # si la distancia al npc es menor que la suma de los radios ha ocurrido en la colision
                if (self.radio+npc.radio)**2 > ((self.pos[0]- npc.mov[npc.posA][0])**2 + (self.pos[1]-npc.mov[npc.posA][1])**2):
                    self.infectado = True

    
    def conversion(self, prob):
        # Se convierte, con cierta probabilidad, de zombie a humano
        convertir = uniform(0.0,1.0)
        if prob >= convertir:
            self.zombie = True
            
    
    def llegar(self, lado):
        # Funcion para detectar una colision con la tienda

        # si la distancia a la tienda es menor que la suma de los radios ha ocurrido en la colision
        if (self.radio+0.275)**2 > ((self.pos[0]- 0.775*lado)**2 + (self.pos[1]- 0.845)**2):
            return True
        
###################################################################################

class NPC():
    # Clase para contener las caracteristicas de un objeto que representa un NPC
    def __init__(self, posA, posS, size, eszombie):
        self.posA = posA # Indicador del vector con la posicion del npc
        self.posS = posS # Vector siguiente
        self.eszombie = eszombie # Indicador de si es zombie o humano
        self.infectado = 0 # Indicador de si está infectado o no
        self.nombre = "" # Nombre que se le otorgara al nodo para poder ser encontrado
        self.vel = 0 # Cantidad total de puntos que tiene la curva asignada, directamente proporcional a la velocidad del npc
        self.mov = [] # Vectores que corresponderan a la curva que sigue el npc
        self.radio = 0.04 # Distancia para realizar los calculos de colision
        self.size = size # Escala a aplicar al nodo
        self.model = None # Referencia al grafo de escena asociado
    
    def set_model(self, new_model):
        # Se obtiene una referencia a uno nodo
        self.model = new_model

    def update(self):
        # Se posiciona el nodo referenciado
        self.model.transform = tr.matmul([tr.translate(self.mov[self.posA][0], self.mov[self.posA][1], 0), tr.scale(self.size, self.size, 1)])

    def conversion(self, prob):
        # Se convierte, con cierta probabilidad, de humano a zombie
        convertir = uniform(0.0,1.0)
        if prob >= convertir and self.mov[self.posA][1] <= 0.9:
            return True

    def collision(self, lista):
        # Funcion para detectar las colisiones entre npcs

        # Se recorren los npcs
        for b in lista:
            # si la distancia al npc es menor que la suma de los radios ha ocurrido en la colision
            if b.eszombie == 1 and self.nombre != b.nombre:
                if (self.radio+b.radio)**2 > ((self.mov[self.posA][0] - b.mov[b.posA][0])**2 + (self.mov[self.posA][1] - b.mov[b.posA][1])**2):
                    return True

    def collisionI(self, lista):
        # Funcion para detectar las colisiones entre npcs infecados y sanos

        # Se recorren los npcs
        for b in lista:
            # si la distancia al npc es menor que la suma de los radios ha ocurrido en la colision
            if b.infectado == 1 and self.nombre != b.nombre:
                if (self.radio+b.radio)**2 > ((self.mov[self.posA][0] - b.mov[b.posA][0])**2 + (self.mov[self.posA][1] - b.mov[b.posA][1])**2):
                    return True


    
