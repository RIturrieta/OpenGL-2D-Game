""" T1: Beauchefville """

import sys
import math
import glfw
import OpenGL.GL.shaders
import numpy as np
import grafica.basic_shapes as bs
import grafica.easy_shaders as es
import shader as sh
import grafica.transformations as tr
import grafica.performance_monitor as pm
import grafica.scene_graph as sg
import grafica.ex_curves as cv
from shapes import *
from model import *
from random import *


# We will use 32 bits data, so an integer has 4 bytes
# 1 byte = 8 bits
SIZE_IN_BYTES = 4

print("Zombies que entran: ",sys.argv[1])
print("Humanos que entran: ",sys.argv[2])
print("Cada cuantos segundos entran: ",sys.argv[3])
print("Probabilidad de que humano contagiado se convierta en Zombie: ",sys.argv[4])

Z = int(sys.argv[1])
H = int(sys.argv[2])
T = float(sys.argv[3])
P = float(sys.argv[4])

# Clase controlador con variables para manejar el estado de ciertos botones
class Controller:
    def __init__(self):
        self.fillPolygon = True
        self.is_w_pressed = False
        self.is_s_pressed = False
        self.is_a_pressed = False
        self.is_d_pressed = False
        self.scan = False

# we will use the global controller as communication with the callback function
controller = Controller()

# Funcion que se ejecutara cuando se presione una tecla
def on_key(window, key, scancode, action, mods):
    
    global controller
    
    # Caso de detectar la tecla [W], actualiza estado de variable
    if key == glfw.KEY_W:
        if action ==glfw.PRESS:
            controller.is_w_pressed = True
        elif action == glfw.RELEASE:
            controller.is_w_pressed = False

    # Caso de detectar la tecla [S], actualiza estado de variable
    if key == glfw.KEY_S:
        if action ==glfw.PRESS:
            controller.is_s_pressed = True
        elif action == glfw.RELEASE:
            controller.is_s_pressed = False

    # Caso de detectar la tecla [A], actualiza estado de variable
    if key == glfw.KEY_A:
        if action ==glfw.PRESS:
            controller.is_a_pressed = True
        elif action == glfw.RELEASE:
            controller.is_a_pressed = False

    # Caso de detectar la tecla [D], actualiza estado de variable
    if key == glfw.KEY_D:
        if action ==glfw.PRESS:
            controller.is_d_pressed = True
        elif action == glfw.RELEASE:
            controller.is_d_pressed = False

    # Caso de detecar la barra espaciadora, se cambia el metodo de dibujo
    if key == glfw.KEY_SPACE:  
        if action ==glfw.PRESS:
            controller.scan = not controller.scan

    # Caso en que se cierra la ventana
    elif key == glfw.KEY_ESCAPE and action ==glfw.PRESS:
        glfw.set_window_should_close(window, True)

################################################################################### 

if __name__ == "__main__":

    # Initialize glfw
    if not glfw.init():
        glfw.set_window_should_close(window, True)

    # Creating a glfw window
    width = 1000
    height = 1000
    title = "T1 - Beauchefville"
    window = glfw.create_window(width, height, title, None, None)

    if not window:
        glfw.terminate()
        glfw.set_window_should_close(window, True)

    glfw.make_context_current(window)

    # Connecting the callback function 'on_key' to handle keyboard events
    glfw.set_key_callback(window, on_key)

    ################################################################################### 

    # Pipeline para dibujar los pajaros
    pajaros = sh.BirdShaderProgram()

    # Pipeline para dibujar los pastos
    pastos = es.SimpleTransformShaderProgram()
    
    # Pipeline para dibujar shapes con texturas
    tex_pipeline = es.SimpleTextureTransformShaderProgram()
    
    # Pipelines "gafas detectoras" para identificar humanos infectados
    tex_humano = sh.ScannerShader()
    tex_player = sh.PlayerShader()
    
    # Pipeline para dibujar shapes con texturas de win/lose
    end_pipeline = sh.FadingShader()

    ################################################################################### 

    # Setting up the clear screen color
    glClearColor(0.15, 0.15, 0.15, 1.0)

    # Enabling transparencies
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    ################################################################################### 

    # Grafos de escena de los adornos
    pajarosScene = createBandadas(pajaros)
    pastosScene = createPasto(pastos)

    # Shapes con texturas de los zombies y humanos
    npc0 = createTextureGPUShape(bs.createTextureQuad(1,1), tex_pipeline, "sprites/humano.png")
    npc1 = createTextureGPUShape(bs.createTextureQuad(1,1), tex_pipeline, "sprites/zombie.png")
    
    
    def crearNpc(scene, es, lista, prob):
        # Funcion que crea un npc y le asigna la textura de humano o zombie en base a los parametros

        nombre = str(uniform(0.0, 10.0)) # Nombre aleatorio para asignar al nodo
        
        inf = uniform(0.0,1.0)

        v = randint(3000,6000) # Cantidad de puntos que tendrá la curva
        
        # Se crea el nodo
        npcNode = sg.SceneGraphNode(nombre)
        if es == 0:
            npcNode.childs = [npc0]
        else:
            npcNode.childs = [npc1]
        scene.childs += [npcNode]

        linea = randomCurva(v)

        npc = NPC(0, 1, 0.08, es)
        npc.set_model(npcNode)
        npc.nombre = nombre
        npc.vel = v
        npc.mov = linea
        
        if prob >= inf:
            npc.infectado = 1

        lista.append(npc)

    ################################################################################### 

    # Se instancia el modelo de hinata
    player = Player(0.08)

    # Shape con la textura de hinata
    hinata = createTextureGPUShape(bs.createTextureQuad(1,1), tex_pipeline, "sprites/hinata.png")
    hinataNode = sg.SceneGraphNode("Hinata")
    hinataNode.childs = [hinata]

    # Se indican las referencias del nodo y el controller al modelo
    player.set_model(hinataNode)
    player.set_controller(controller)


    # Shape con la textura de la tienda
    lado = randint(1,2) # Variable que asigna a que lado aparece la tienda
    if lado == 2:
        lado = -1

    tienda = createTextureGPUShape(createTexCuad(1,0.75,1,1), tex_pipeline, "sprites/tienda.png")
    tiendaNode = sg.SceneGraphNode("tienda")
    tiendaNode.transform = tr.matmul([tr.translate(0.775*lado, 0.845, 0), tr.uniformScale(0.2)])
    tiendaNode.childs = [tienda]
    
    # Shape con la textura del fondo
    fondo = createTextureGPUShape(createTexCuad(1,1,1,1), tex_pipeline, "sprites/fondo.png")
    fondoNode = sg.SceneGraphNode("fondo")
    fondoNode.childs = [fondo]

    # Shape con la textura si se pierde
    lose = createTextureGPUShape(bs.createTextureQuad(1,1), tex_pipeline, "sprites/death.png")
    loseNode = sg.SceneGraphNode("lose")
    loseNode.transform = tr.translate(0,5,0)
    loseNode.childs = [lose]

    # Shape con la textura si se gana
    win = createTextureGPUShape(bs.createTextureQuad(1,1), tex_pipeline, "sprites/win.png")
    winNode = sg.SceneGraphNode("win")
    winNode.transform = tr.translate(0,5,0)
    winNode.childs = [win]

    # Se crea el grafo de escena con texturas y se agregan los nodos
    tex_scene = sg.SceneGraphNode("textureScene")
    tex_scene.childs = [fondoNode, hinataNode, tiendaNode]

    # Se crea el grafo de escena con texturas de victoria y derrota y se agregan sus nodos
    end_scene = sg.SceneGraphNode("textureScene")
    end_scene.childs = [loseNode, winNode]

    perfMonitor = pm.PerformanceMonitor(glfw.get_time(), 0.5)

    # Variable para que no se pueda ganar y perder al mismo tiempo
    fin = 0

    # Indicador del fade de las pantallas win/lose
    fading = False
    fade = 0

    # glfw will swap buffers as soon as possible
    glfw.swap_interval(0)
    t0 = glfw.get_time()

    seg = 0 # Variable para contar los T segundos
    aleteo = 0 # Variable para contar cada segundo que se usara para el aleteo
    updown = 1 # Variable que indica si las alas estan hacia arriba o hacia abajo

    lista = [] # Lista para ser llenada con los npcs

    ################################################################################### 

    # Application loop
    while not glfw.window_should_close(window):
        
        ################################################################################### 
        # Llamadas a nodos para aplicar transformaciones

        bandada1 = sg.findNode(pajarosScene, "Bandada1")
        bandada2 = sg.findNode(pajarosScene, "Bandada2")


        pajaro = sg.findNode(pajarosScene, "Pajaro")

        verde = sg.findNode(pastosScene, "pasto")

        ################################################################################### 
        
        # Variables del tiempo
        t1 = glfw.get_time()
        delta = t1 -t0
        t0 = t1

        v = t1*-0.5
        seg += delta
        aleteo += delta

        # Movimiento de las bandadas    
        bandada1.transform = tr.translate(v%2,0,0) 
        bandada2.transform = tr.translate(v%2 - 2,0,0)
        
        # Balanceo del pasto para simular viento
        verde.transform = tr.shearing(math.cos(t1*2),0,0,0,0,0)

        if aleteo > 1: # Cada segundo, los pajaros aletean
            aleteo = 0
            pajaro.transform = tr.rotationX(math.pi*updown)
            updown += 1

        if seg > T: # Cada T segundos:
            seg = 0
            for z in range(Z): # Se crean Z zombies
                crearNpc(tex_scene,1,lista,P)
            for h in range(H): # Se crean H humanos
                crearNpc(tex_scene,0,lista,P)
            for a in lista:
                if a.infectado == 1: # Si estan infectados, se ve, en base a la probabilidad dada, si cambian a zombies
                    if a.conversion(P):
                        sg.findNode(tex_scene,a.nombre).childs = [npc1]
                        a.infectado = 0
                        a.eszombie = 1
            if player.infectado: # Si el jugador esta infectado, se ve, en base a la probabilidad dada, si cambia a zombie
                player.conversion(P)


        for a in lista:
            a.update() # Se actualiza la posicion de cada npc
            if a.eszombie == 0: # Si no es un zombie:
                if a.collision(lista): # Si choca con un zombie, pasa a ser zombie
                    sg.findNode(tex_scene,a.nombre).childs = [npc1]
                    a.infectado = 0
                    a.eszombie = 1
                if a.infectado == 0: # Si choca con un infectado, se infecta
                    if a.collisionI(lista):
                        a.infectado = 1
            if a.eszombie == 1: # Si es un zombie:
                a.infectado = 0 # Para evitar casos en que ciertos zombies se veian afectados por el scanner

            # Se le asigna una nueva posicion a cada npc
            a.posA += 1
            a.posS += 1
            if a.posS == a.vel + 1: # Si un npc alcanza su ultima posicion, se borra para ahorrar memoria
                lista.remove(a)
                tex_scene.childs.remove(sg.findNode(tex_scene,a.nombre))
          
        ###################################################################################  

        # Measuring performance
        perfMonitor.update(glfw.get_time())
        glfw.set_window_title(window, title + str(perfMonitor))
        # Using GLFW to check for input events
        glfw.poll_events()

        # Filling or not the shapes depending on the controller state
        if (controller.fillPolygon):
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

        # Clearing the screen
        glClear(GL_COLOR_BUFFER_BIT)


        ################################################################################### 

        # Se verifica si el jugador ha sido contagiado por un npc
        player.contagio(lista)

        # Se llama al metodo del player para detectar colisiones
        if player.collision(lista) and fin == 0 or player.zombie:
            # Si choca con un zombie o tiene mala suerte y debido a una infeccion se convierte en uno, se cambia su textura a la de un zombie y se muestra la pantalla de lose
             fin = 1
             loseNode.transform = tr.matmul([tr.scale(2,0.5,1),tr.translate(0,0,0)])
             sg.findNode(tex_scene, "Hinata").childs = [npc1]
             fading = True
        if player.llegar(lado) and fin == 0:
            # Si llega a la tienda se muestra la pantalla de win
             fin = 1
             winNode.transform = tr.matmul([tr.scale(2,1,1),tr.translate(0,0,0)])
             fading = True

        # Se aplica el fading a las pantallas de win/lose cuando sea necesario
        if fading and fade <= 0.99:
            fade += 0.001

        # Se llama al metodo del player para actualizar su posicion
        player.update(delta)

        ################################################################################### 

        # Se dibuja el grafo de escena con texturas
        glUseProgram(tex_pipeline.shaderProgram)
        sg.drawSceneGraphNode(tex_scene, tex_pipeline, "transform")

        # Si se activa el scanner, se cambia el shader para los humanos infectados (Verde=Infectado)
        if controller.scan:    
            for a in lista:
                if a.infectado == 1:
                    glUseProgram(tex_humano.shaderProgram)
                    sg.drawSceneGraphNode(sg.findNode(tex_scene, a.nombre), tex_humano, "transform")


        # Si se activa el scanner, se cambia el shader para el jugador. (Azul=Sano, Rojo=Infectado)
        if controller.scan and fin != 1:
            glUseProgram(tex_player.shaderProgram)
            if player.infectado:
                sh.drawHinataScan(sg.findNode(tex_scene, "Hinata"), tex_player, "transform", 1)
            else:
                sh.drawHinataScan(sg.findNode(tex_scene, "Hinata"), tex_player, "transform", 0)

        # Se dibujan los grafos de escena con los adornos
        glUseProgram(pastos.shaderProgram)
        sg.drawSceneGraphNode(pastosScene, pastos, "transform")

        glUseProgram(pajaros.shaderProgram)
        sg.drawSceneGraphNode(pajarosScene, pajaros, "transform")
        
        # Se dibuja el grafo de escena con las pantallas de win/lose
        glUseProgram(end_pipeline.shaderProgram)
        sh.drawSceneGraphNodeF(end_scene, end_pipeline, "transform", fade) # , tr.identity() , variable)

        # Once the drawing is rendered, buffers are swap so an uncomplete drawing is never seen.
        glfw.swap_buffers(window)

    # freeing GPU memory
    pajarosScene.clear()
    pastosScene.clear()
    tex_scene.clear()
    end_scene.clear()
    
    glfw.terminate()