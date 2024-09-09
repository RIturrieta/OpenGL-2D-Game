""" Funciones para crear distintas figuras y escenas """

import glfw
import numpy as np
import math
from OpenGL.GL import *
import grafica.basic_shapes as bs
import grafica.easy_shaders as es
import grafica.transformations as tr
import grafica.ex_curves as cv
import grafica.scene_graph as sg
from random import *

# Definimos la clase shape para agrupar vertices e indices
class Shape:
    def __init__(self, vertices, indices, textureFileName=None):
        self.vertices = vertices
        self.indices = indices
        self.textureFileName = textureFileName

def createGPUShape(shape, pipeline):
    # Funcion Conveniente para facilitar la inicializacion de un GPUShape
    gpuShape = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuShape)
    gpuShape.fillBuffers(shape.vertices, shape.indices, GL_STATIC_DRAW)
    return gpuShape

def createTextureGPUShape(shape, pipeline, path):
    # Funcion Conveniente para facilitar la inicializacion de un GPUShape con texturas
    gpuShape = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuShape)
    gpuShape.fillBuffers(shape.vertices, shape.indices, GL_STATIC_DRAW)
    gpuShape.texture = es.textureSimpleSetup(
        path, GL_CLAMP_TO_EDGE, GL_CLAMP_TO_EDGE, GL_NEAREST, GL_NEAREST)
    return gpuShape

################################################################################### 

def createTexCuad(largo,alto,tx,ty):
    vertices = [
        -largo, -alto, 0, 0, ty,
         largo, -alto, 0, tx, ty,
         largo,  alto, 0, tx, 0,
        -largo,  alto, 0, 0, 0]
    indices = [
         0, 1, 2,
         2, 3, 0]
    return Shape(vertices,indices)


def hermiteRand(N):
    # Funcion para generar una curva de Hermite de N puntos

    # Puntos de Control
    inicio = uniform(-0.5,0.5)
    fin = uniform(-0.5,0.5)
    x1 = uniform(-0.5,0.5)
    x2 = uniform(-0.5,0.5)
    y1 = uniform(-2.0,-1.0)
    y2 = uniform(-2.0,-1.0)
    
    P0 = np.array([[inicio, 1.0, 0]]).T
    P1 = np.array([[fin, -1.0, 0]]).T
    T0 = np.array([[x1, y1, 0]]).T
    T1 = np.array([[x2, y2, 0]]).T
    # Matriz de Hermite
    H_M = cv.hermiteMatrix(P0, P1, T0, T1)

    # Arreglo de numeros entre 0 y 1
    ts = np.linspace(0.0, 1.0, N)
    
    # The computed value in R3 for each sample will be stored here
    curve = np.ndarray(shape=(len(ts), 3), dtype=float)
    
    # Se llenan los puntos de la curva
    for i in range(len(ts)):
        T = cv.generateT(ts[i])
        curve[i, 0:3] = np.matmul(H_M, T).T
        
    return curve

def bezierRand(N):
    # Funcion para generar una curva de Bezier de N puntos

    # Puntos de Control
    inicio = uniform(-0.5,0.5)
    fin = uniform(-0.5,0.5)
    x1 = uniform(-0.5,0.5)
    x2 = uniform(-0.5,0.5)
    y1 = uniform(-1.0,1.0)
    y2 = uniform(-1.0,1.0)
    
    P0 = np.array([[inicio, 1.0, 0]]).T
    P1 = np.array([[x1, y1, 0]]).T
    P2 = np.array([[x2, y2, 0]]).T
    P3 = np.array([[fin, -1.0, 0]]).T
    # Matrices de Hermite y Beziers
    H_M = cv.bezierMatrix(P0, P1, P2, P3)

    # Arreglo de numeros entre 0 y 1
    ts = np.linspace(0.0, 1.0, N)
    
    # The computed value in R3 for each sample will be stored here
    curve = np.ndarray(shape=(len(ts), 3), dtype=float)
    
    # Se llenan los puntos de la curva
    for i in range(len(ts)):
        T = cv.generateT(ts[i])
        curve[i, 0:3] = np.matmul(H_M, T).T
        
    return curve


def randomCurva(v):
    # Funcion que crea aleatoriamente una curva de Hermite o de Bezier con v puntos
    a = randint(0,1)
    curva = []
    if a == 1:
        curva = bezierRand(v)
    else:
        curva = hermiteRand(v)
    return curva


def createAla():
# Funcion para crear un ala negra

    vertices = [
        -1.0,  0.0, 0.0,  0, 0, 0,
        -0.75, 0.5, 0.0,  0, 0, 0,
        -0.75, 0.75, 0.0,  0, 0, 0,
        -0.5,  1.0, 0.0,  0, 0, 0,
        -0.5,  0.75, 0.0,  0, 0, 0,
        -0.25, 0.75, 0.0,  0, 0, 0,
        -0.25, 0.5, 0.0,  0, 0, 0,
         0.0,  0.0, 0.0,  0, 0, 0]

    indices = [0, 1, 2,
               1, 2, 3,
               2, 3, 4, 
               3, 4, 5,
               4, 5, 6,
               5, 6, 7]

    return bs.Shape(vertices, indices)

################################################################################### 

def createBandadas(pipeline):
    # Se crea la escena de un pajaro

    # Se crean las shapes en GPU
    gpuWing = createGPUShape(createAla(), pipeline) # Un ala

    # Nodo del ala izquierda
    lWingNode = sg.SceneGraphNode("lWing")
    lWingNode.childs = [gpuWing]

    # Nodo del ala derecha
    rWingNode = sg.SceneGraphNode("rWing")
    rWingNode.transform = tr.rotationY(math.pi)
    rWingNode.childs = [gpuWing]

    # Nodo de un pajaro
    pajaroNode = sg.SceneGraphNode("Pajaro")
    pajaroNode.transform = tr.identity()
    pajaroNode.childs = [lWingNode, rWingNode]

    # Nodo padre Pajaros
    bird1Node = sg.SceneGraphNode("Bird1")
    bird1Node.transform = tr.matmul([tr.translate(0.25,0.1,0),tr.uniformScale(0.05)])
    bird1Node.childs = [pajaroNode]

    bird2Node = sg.SceneGraphNode("Bird2")
    bird2Node.transform = tr.matmul([tr.translate(0.85,0.75,0),tr.uniformScale(0.05)])
    bird2Node.childs = [pajaroNode]

    bird3Node = sg.SceneGraphNode("Bird3")
    bird3Node.transform = tr.matmul([tr.translate(-0.35,0.1,0),tr.uniformScale(0.05)])
    bird3Node.childs = [pajaroNode]

    bird4Node = sg.SceneGraphNode("Bird4")
    bird4Node.transform = tr.matmul([tr.translate(0.5,-0.45,0),tr.uniformScale(0.05)])
    bird4Node.childs = [pajaroNode]

    bird5Node = sg.SceneGraphNode("Bird5")
    bird5Node.transform = tr.matmul([tr.translate(-0.65,-0.35,0),tr.uniformScale(0.05)])
    bird5Node.childs = [pajaroNode]

    bird6Node = sg.SceneGraphNode("Bird6")
    bird6Node.transform = tr.matmul([tr.translate(0.25,0.1,0),tr.uniformScale(0.05)])
    bird6Node.childs = [pajaroNode]

    bird7Node = sg.SceneGraphNode("Bird7")
    bird7Node.transform = tr.matmul([tr.translate(0.85,0.75,0),tr.uniformScale(0.05)])
    bird7Node.childs = [pajaroNode]

    bird8Node = sg.SceneGraphNode("Bird8")
    bird8Node.transform = tr.matmul([tr.translate(-0.35,0.1,0),tr.uniformScale(0.05)])
    bird8Node.childs = [pajaroNode]

    bird9Node = sg.SceneGraphNode("Bird9")
    bird9Node.transform = tr.matmul([tr.translate(0.5,-0.45,0),tr.uniformScale(0.05)])
    bird9Node.childs = [pajaroNode]

    bird10Node = sg.SceneGraphNode("Bird10")
    bird10Node.transform = tr.matmul([tr.translate(-0.65,-0.35,0),tr.uniformScale(0.05)])
    bird10Node.childs = [pajaroNode]

    # Nodo padre Bandadas
    bandada1Node = sg.SceneGraphNode("Bandada1")
    bandada1Node.childs = [bird1Node, bird2Node, bird3Node, bird4Node, bird5Node]

    bandada2Node = sg.SceneGraphNode("Bandada2")
    bandada2Node.childs = [bird6Node, bird7Node, bird8Node, bird9Node, bird10Node]

    # Escena Pajaros
    pajarosNode = sg.SceneGraphNode("Pajaros")
    pajarosNode.childs = [bandada1Node, bandada2Node]

    return pajarosNode

def createPasto(pipeline):
    
    # Se crean las shapes en GPU
    gpuPasto = createGPUShape(bs.createColorQuad(0,0.8,0), pipeline)

    pastoNode = sg.SceneGraphNode("pasto")
    pastoNode.transform = tr.identity()
    pastoNode.childs = [gpuPasto]

    pasto1Node = sg.SceneGraphNode("Pasto1")
    pasto1Node.transform = tr.matmul([tr.translate(0.8,-0.8,0),tr.scale(0.0075,0.01,0.01)])
    pasto1Node.childs = [pastoNode]

    pasto2Node = sg.SceneGraphNode("Pasto2")
    pasto2Node.transform = tr.matmul([tr.translate(0.9,-0.4,0),tr.scale(0.0075,0.01,0.01)])
    pasto2Node.childs = [pastoNode]

    pasto3Node = sg.SceneGraphNode("Pasto3")
    pasto3Node.transform = tr.matmul([tr.translate(0.8,0,0),tr.scale(0.0075,0.01,0.01)])
    pasto3Node.childs = [pastoNode]

    pasto4Node = sg.SceneGraphNode("Pasto4")
    pasto4Node.transform = tr.matmul([tr.translate(0.9,0.2,0),tr.scale(0.0075,0.01,0.01)])
    pasto4Node.childs = [pastoNode]

    pasto5Node = sg.SceneGraphNode("Pasto5")
    pasto5Node.transform = tr.matmul([tr.translate(0.8,0.6,0),tr.scale(0.0075,0.01,0.01)])
    pasto5Node.childs = [pastoNode]

    pasto6Node = sg.SceneGraphNode("Pasto6")
    pasto6Node.transform = tr.matmul([tr.translate(-0.8,-0.8,0),tr.scale(0.0075,0.01,0.01)])
    pasto6Node.childs = [pastoNode]

    pasto7Node = sg.SceneGraphNode("Pasto7")
    pasto7Node.transform = tr.matmul([tr.translate(-0.9,-0.4,0),tr.scale(0.0075,0.01,0.01)])
    pasto7Node.childs = [pastoNode]

    pasto8Node = sg.SceneGraphNode("Pasto8")
    pasto8Node.transform = tr.matmul([tr.translate(-0.8,0,0),tr.scale(0.0075,0.01,0.01)])
    pasto8Node.childs = [pastoNode]

    pasto9Node = sg.SceneGraphNode("Pasto9")
    pasto9Node.transform = tr.matmul([tr.translate(-0.9,0.2,0),tr.scale(0.0075,0.01,0.01)])
    pasto9Node.childs = [pastoNode]

    pasto10Node = sg.SceneGraphNode("Pasto10")
    pasto10Node.transform = tr.matmul([tr.translate(-0.9,0.6,0),tr.scale(0.0075,0.01,0.01)])
    pasto10Node.childs = [pastoNode]

    pastosNode = sg.SceneGraphNode("Pastos")
    pastosNode.childs = [pasto1Node, pasto2Node, pasto3Node, pasto4Node, pasto5Node, pasto6Node, pasto7Node, pasto8Node, pasto9Node, pasto10Node]

    return pastosNode

def createBandada(pipeline):
    # Se crea la escena de una bandada

    # Se crean las shapes en GPU
    gpuWing = createGPUShape(createAla, pipeline) # Un ala

    # Nodo del ala izquierda
    lWingNode = sg.SceneGraphNode("lWing")
    lWingNode.childs = [gpuWing]

    # Nodo del ala derecha
    rWingNode = sg.SceneGraphNode("rWing")
    rWingNode.transform = tr.rotationY(math.pi)
    rWingNode.childs = [gpuWing]

    # Nodo padre Pajaro
    birdNode = sg.SceneGraphNode("Bird")
    birdNode.childs = [lWingNode, rWingNode]

    return birdNode
