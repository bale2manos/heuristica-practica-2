import copy
from celda import Celda
from ambulancia import Ambulancia, ENERGY_REFILL
from nodo import Nodo
from queue import PriorityQueue

class Mapa:
    def __init__(self, archivo):
        self.nodos_expandidos = 0
        self.pacientes_restantes = 0
        self.max_rows = 0
        self.max_columns = 0
        self.celdas = self.cargar_mapa(archivo)
        self.acciones_posibles = ['recargar_energia', 'recoger_paciente', 'descargar_pacientes', 'mover_arriba', 'mover_abajo', 'mover_izquierda', 'mover_derecha']
        self.ambulancia = self.crear_ambulancia()
        self.parking = Celda(0, 0, 'P')

    def incrementar_nodos_expandidos(self):
        self.nodos_expandidos += 1
    def __eq__(self, other):
        return self.celdas == other.celdas and self.ambulancia == other.ambulancia

    def __str__(self):
        celdas = ''
        for celda in self.celdas:
            celdas += str(celda) + ';'
        ambulancia = str(self.ambulancia)
        return celdas + 'Ambulance: ' + ambulancia

    def __hash__(self):
        celdas = ''
        for celda in self.celdas:
            celdas += str(celda) + ';'
        ambulancia = str(self.ambulancia)
        return hash(celdas + 'Ambulance: ' + ambulancia)


    def mostrar_mapa(self):
        for celda in self.celdas:
            print(celda.tipo, end='')



    def cargar_mapa(self, archivo):
        with open(archivo, 'r') as file:
            mapa = [line.strip().split(';') for line in file.readlines()]

        celdas = []
        self.max_rows = len(mapa)
        self.max_columns = len(mapa[0])
        for fila in range(len(mapa)):
            for columna in range(len(mapa[fila])):
                celdas.append(Celda(fila+1, columna+1, mapa[fila][columna]))
                if mapa[fila][columna] == 'N' or mapa[fila][columna] == 'C':
                    self.pacientes_restantes += 1
                elif mapa[fila][columna] == 'P':
                    self.parking = celdas[-1]

        return celdas

    def crear_ambulancia(self):
        for celda in self.celdas:
            if celda.tipo == 'P':
                return Ambulancia(celda.fila, celda.columna)

    def get_celda(self, fila, columna):
        if fila < 1 or fila > self.max_rows or columna < 1 or columna > self.max_columns:
            return None # Celda fuera de los límites del mapa

        return self.celdas[(fila-1)*self.max_columns + (columna-1)]

    def recargar_energia(self):
        ambulanciaX = self.ambulancia.celdaX
        ambulanciaY = self.ambulancia.celdaY
        if self.get_celda(ambulanciaX, ambulanciaY).tipo == 'P' and self.ambulancia.energia_left < ENERGY_REFILL:
            self.ambulancia.recargar_energia()
            return 0
        return -1

    def recoger_paciente(self):
        ambulanciaX = self.ambulancia.celdaX
        ambulanciaY = self.ambulancia.celdaY
        celda_ambulancia = self.get_celda(ambulanciaX, ambulanciaY)

        if celda_ambulancia.tipo == 'N' or celda_ambulancia.tipo == 'C':
            posible_recoger_paciente = False
            if celda_ambulancia.tipo == 'N':
                if self.ambulancia.pacientesC == 0 and self.ambulancia.pacientesN < 10:
                    posible_recoger_paciente = True
            elif celda_ambulancia.tipo == 'C':
                if self.ambulancia.pacientesC < 2 and self.ambulancia.pacientesN < 9:
                    posible_recoger_paciente = True

            if posible_recoger_paciente:
                self.ambulancia.recoger_paciente(celda_ambulancia.tipo)
                celda_ambulancia.tipo = '1'
                self.pacientes_restantes -= 1
                return 0
        return -1

    def descargar_pacientes(self):
        ambulanciaX = self.ambulancia.celdaX
        ambulanciaY = self.ambulancia.celdaY
        celda_ambulancia = self.get_celda(ambulanciaX, ambulanciaY)

        if (celda_ambulancia.tipo == 'CC' and self.ambulancia.pacientesC > 0):
            self.ambulancia.descargar_pacientes(celda_ambulancia.tipo)
            return 0
        elif (celda_ambulancia.tipo == 'CN' and self.ambulancia.pacientesN > 0 and self.ambulancia.pacientesC == 0):
            self.ambulancia.descargar_pacientes(celda_ambulancia.tipo)
            return 0
        return -1

    def mover_arriba(self):
        ambulanciaX = self.ambulancia.celdaX
        ambulanciaY = self.ambulancia.celdaY
        celda_arriba = self.get_celda(ambulanciaX-1, ambulanciaY)
        if celda_arriba:
            potencial_energia_restante = self.ambulancia.energia_left - celda_arriba.coste
            if celda_arriba.tipo != 'X' and potencial_energia_restante >= 0:
                self.ambulancia.mover_a(celda_arriba, potencial_energia_restante)
                return celda_arriba.coste
        return -1

    def mover_abajo(self):
        ambulanciaX = self.ambulancia.celdaX
        ambulanciaY = self.ambulancia.celdaY
        celda_abajo = self.get_celda(ambulanciaX+1, ambulanciaY)
        if celda_abajo:
            potencial_energia_restante = self.ambulancia.energia_left - celda_abajo.coste
            if celda_abajo.tipo != 'X' and potencial_energia_restante >= 0:
                self.ambulancia.mover_a(celda_abajo, potencial_energia_restante)
                return celda_abajo.coste
        return -1

    def mover_izquierda(self):
        ambulanciaX = self.ambulancia.celdaX
        ambulanciaY = self.ambulancia.celdaY
        celda_izquierda = self.get_celda(ambulanciaX, ambulanciaY-1)
        if celda_izquierda:
            potencial_energia_restante = self.ambulancia.energia_left - celda_izquierda.coste
            if celda_izquierda.tipo != 'X' and potencial_energia_restante >= 0:
                self.ambulancia.mover_a(celda_izquierda, potencial_energia_restante)
                return celda_izquierda.coste
        return -1

    def mover_derecha(self):
        ambulanciaX = self.ambulancia.celdaX
        ambulanciaY = self.ambulancia.celdaY
        celda_derecha = self.get_celda(ambulanciaX, ambulanciaY+1)
        if celda_derecha:
            potencial_energia_restante = self.ambulancia.energia_left - celda_derecha.coste
            if celda_derecha.tipo != 'X' and potencial_energia_restante >= 0:
                self.ambulancia.mover_a(celda_derecha, potencial_energia_restante)
                return celda_derecha.coste
        return -1

    def a_estrella(self, heuristica):
        inicio = copy.deepcopy(self)
        cola_prioridad = PriorityQueue()  # cola de prioridad para almacenar los nodos
        valor_heuristica = self.calcular_heuristica(inicio, heuristica)
        cola_prioridad.put(Nodo(inicio, 0, valor_heuristica, [inicio]))
        coste_por_nodo = {inicio: 0}  # almacenar el coste acumulado de cada nodo

        while not cola_prioridad.empty():
            nodo_actual = cola_prioridad.get()
            print('------------------------------')
            print('Coste acumulado:', nodo_actual.coste_acumulado)
            print('Prioridad:', nodo_actual.prioridad)
            print('Energía restante:', nodo_actual.mapa.ambulancia.energia_left)

            self.incrementar_nodos_expandidos()


            if self.objetivo_cumplido(nodo_actual):
                # Reconstruir el camino y devolverlo
                return nodo_actual.camino_recorrido, nodo_actual.coste_acumulado, self.nodos_expandidos

            for accion, nuevo_estado, coste_accion in self.obtener_sucesores_y_coste(nodo_actual):
                nuevo_coste_acumulado = nodo_actual.coste_acumulado + coste_accion

                if nuevo_estado not in coste_por_nodo:
                    coste_por_nodo[nuevo_estado] = nuevo_coste_acumulado
                    valor_heuristica_nodo = self.calcular_heuristica(nuevo_estado, heuristica)
                    nuevo_camino = nodo_actual.camino_recorrido + [nuevo_estado]
                    cola_prioridad.put(Nodo(nuevo_estado, nuevo_coste_acumulado, valor_heuristica_nodo, nuevo_camino))

                elif nuevo_coste_acumulado < coste_por_nodo[nuevo_estado]:
                    coste_por_nodo[nuevo_estado] = nuevo_coste_acumulado
                    valor_heuristica_nodo = self.calcular_heuristica(nuevo_estado, heuristica)
                    nuevo_camino = nodo_actual.camino_recorrido + [nuevo_estado]
                    # Check if the node is already in the priority queue
                    # TODO no aparece en las implementaciones de python, pero creemos que es bueno para evitar duplicados
                    for node in cola_prioridad.queue:
                        if node.mapa == nuevo_estado:
                            cola_prioridad.queue.remove(node)
                            break
                    cola_prioridad.put(Nodo(nuevo_estado, nuevo_coste_acumulado, valor_heuristica_nodo, nuevo_camino))

        # No hay camino posible
        return None, None, self.nodos_expandidos

    def obtener_sucesores_y_coste(self, nodo):
        # Devuelve las acciones posibles y los nuevos estados alcanzables desde el estado dado
        # Puedes modificar esto según tu implementación específica
        acciones_y_sucesores = []


        for accion in self.acciones_posibles:
            # crear una copia en cada iteracion del nodo, que no se modificara en la siguiente iteracion
            nuevo_mapa = copy.deepcopy(nodo.mapa)
            coste_accion = -1

            if accion == 'recargar_energia':
                coste_accion = nuevo_mapa.recargar_energia()
            elif accion == 'recoger_paciente':
                coste_accion = nuevo_mapa.recoger_paciente()
            elif accion == 'descargar_pacientes':
                coste_accion = nuevo_mapa.descargar_pacientes()
            elif accion == 'mover_arriba':
                coste_accion = nuevo_mapa.mover_arriba()
            elif accion == 'mover_abajo':
                coste_accion = nuevo_mapa.mover_abajo()
            elif accion == 'mover_izquierda':
                coste_accion = nuevo_mapa.mover_izquierda()
            elif accion == 'mover_derecha':
                coste_accion = nuevo_mapa.mover_derecha()

            if coste_accion != -1:
                # poda de los estados que no son validos ya que no tienen energia suficiente para llegar al parking
                ambulancia = nuevo_mapa.ambulancia
                posicion_ambulancia = (ambulancia.celdaX, ambulancia.celdaY)
                distancia_parking = self.distancia_manhattan(self.parking.fila, self.parking.columna, posicion_ambulancia)
                if distancia_parking <= ambulancia.energia_left:
                    acciones_y_sucesores.append((accion, nuevo_mapa, coste_accion))

        return acciones_y_sucesores

    def calcular_heuristica(self, estado_actual, heuristica):
        if heuristica == 1:
            # Calcula la heurística según el número de pacientes restantes
            visita_a_CC = 1 if estado_actual.ambulancia.pacientesC > 0 else 0
            visita_A_CN = 1 if estado_actual.ambulancia.pacientesN > 0 else 0

            pacientes_restantes = estado_actual.pacientes_restantes + visita_a_CC + visita_A_CN
            return pacientes_restantes

        if heuristica == 2:
            #TODO añadir parking
            #TODO añadir si hay pacientes en la ambulancia que tenga q ir a un centro

            #buscar celdas con pacientes
            pacientes_pendientes = []
            celda_centro_CC = None
            celda_centro_CN = None
            celda_parking = None
            for celda in estado_actual.celdas:
                if celda.tipo == 'C' or celda.tipo == 'N':
                    pacientes_pendientes.append((celda.fila, celda.columna, celda.tipo))
                if celda.tipo == 'CC':
                    celda_centro_CC = (celda.fila, celda.columna)
                if celda.tipo == 'CN':
                    celda_centro_CN = (celda.fila, celda.columna)
                if celda.tipo == 'P':
                    celda_parking = (celda.fila, celda.columna)

            distancia_paciente_mas_lejano = 0
            distancia_desde_paciente_hasta_CC, distancia_desde_CC_hasta_parking = 0, 0
            distancia_hasta_parking = 0

            # SI AMBULANCIA VA LLENA
            if estado_actual.ambulancia.pacientesC == 2:
                distancia_hasta_CC = self.distancia_manhattan(estado_actual.ambulancia.celdaX, estado_actual.ambulancia.celdaY, celda_centro_CC)
                distancia_hasta_parking = self.distancia_manhattan(celda_centro_CC[0], celda_centro_CC[1], celda_parking)
                return distancia_hasta_CC + distancia_hasta_parking

            if estado_actual.ambulancia.pacientesN == 10:
                distancia_hasta_CN = self.distancia_manhattan(estado_actual.ambulancia.celdaX,
                                                                  estado_actual.ambulancia.celdaY, celda_centro_CN)
                distancia_hasta_parking = self.distancia_manhattan(celda_centro_CN[0], celda_centro_CN[1],
                                                                   celda_parking)
                return distancia_hasta_CN + distancia_hasta_parking

            # SI AMBULANCIA NO LLENA
            # SI LLEVO UN CONTAGIOSO DEBO BUSCAR AL OTRO Y SI NO -> A SU CENTRO
            if estado_actual.ambulancia.pacientesC == 1:
                distancia_contagioso_mas_lejano = 0 #TODO por que no al mas cercano?
                for paciente in pacientes_pendientes:
                    if paciente[2] == 'C':
                        distancia = self.distancia_manhattan(estado_actual.ambulancia.celdaX, estado_actual.ambulancia.celdaY, paciente)
                        if distancia > distancia_contagioso_mas_lejano:
                            distancia_contagioso_mas_lejano = distancia
                            distancia_desde_paciente_hasta_CC = self.distancia_manhattan(celda_centro_CC[0], celda_centro_CC[1], paciente)
                            distancia_desde_CC_hasta_parking = self.distancia_manhattan(celda_centro_CC[0], celda_centro_CC[1], celda_parking)

                if distancia_contagioso_mas_lejano != 0:
                    return distancia_contagioso_mas_lejano + distancia_desde_paciente_hasta_CC + distancia_desde_CC_hasta_parking

            # SI NO LLEVO CONTAGIOSO Y AMBULANCIA NO LLENA
            # SI HAY PACIENTES EN EL MAPA
            for paciente in pacientes_pendientes:
                distancia = self.distancia_manhattan(estado_actual.ambulancia.celdaX, estado_actual.ambulancia.celdaY, paciente)
                if distancia > distancia_paciente_mas_lejano:
                    distancia_paciente_mas_lejano = distancia
                    if paciente[2] == 'C':
                        distancia_hasta_centro = self.distancia_manhattan(celda_centro_CC[0], celda_centro_CC[1], paciente)
                        distancia_hasta_parking = self.distancia_manhattan(celda_centro_CC[0], celda_centro_CC[1], celda_parking)
                    else:  # celda[2] == 'N'
                        distancia_hasta_centro = self.distancia_manhattan(celda_centro_CN[0], celda_centro_CN[1], paciente)
                        distancia_hasta_parking = self.distancia_manhattan(celda_centro_CN[0], celda_centro_CN[1], celda_parking)

            # SI NO HAY PACIENTES EN EL MAPA
            if distancia_paciente_mas_lejano == 0:
                if estado_actual.ambulancia.pacientesC > 0 and estado_actual.ambulancia.pacientesN > 0:
                    distancia_hasta_centro_CC = self.distancia_manhattan(estado_actual.ambulancia.celdaX, estado_actual.ambulancia.celdaY, celda_centro_CC)
                    distancia_desde_CC_hasta_CN = self.distancia_manhattan(celda_centro_CC[0], celda_centro_CC[1], celda_centro_CN)
                    distancia_hasta_parking_desde_CN = self.distancia_manhattan(celda_centro_CN[0], celda_centro_CN[1], celda_parking)
                    return distancia_hasta_centro_CC + distancia_desde_CC_hasta_CN + distancia_hasta_parking_desde_CN

                elif estado_actual.ambulancia.pacientesC > 0:
                    distancia_hasta_CC = self.distancia_manhattan(estado_actual.ambulancia.celdaX, estado_actual.ambulancia.celdaY, celda_centro_CC)
                    distancia_desde_CC_hasta_parking = self.distancia_manhattan(celda_centro_CC[0], celda_centro_CC[1], celda_parking)
                    return distancia_hasta_CC + distancia_desde_CC_hasta_parking

                elif estado_actual.ambulancia.pacientesN > 0:
                    distancia_hasta_CN = self.distancia_manhattan(estado_actual.ambulancia.celdaX, estado_actual.ambulancia.celdaY, celda_centro_CN)
                    distancia_desde_CN_hasta_parking = self.distancia_manhattan(celda_centro_CN[0], celda_centro_CN[1], celda_parking)
                    return distancia_hasta_CN + distancia_desde_CN_hasta_parking


            return distancia_paciente_mas_lejano + distancia_hasta_centro + distancia_hasta_parking

        if heuristica == 3:
            # buscar celdas con pacientes
            pacientes_pendientes = []
            celda_centro_CC, celda_centro_CN, celda_parking = None, None, None
            for celda in estado_actual.celdas:
                if celda.tipo == 'C' or celda.tipo == 'N':
                    pacientes_pendientes.append((celda.fila, celda.columna, celda.tipo))
                if celda.tipo == 'CC':
                    celda_centro_CC = (celda.fila, celda.columna)
                if celda.tipo == 'CN':
                    celda_centro_CN = (celda.fila, celda.columna)
                if celda.tipo == 'P':
                    celda_parking = (celda.fila, celda.columna)

            distancia_paciente_mas_lejano = 0
            distancia_hasta_centro = 0
            distancia_hasta_parking = self.distancia_manhattan(estado_actual.ambulancia.celdaX, estado_actual.ambulancia.celdaY, celda_parking)

            # SI HAY PACIENTES EN EL MAPA
            for paciente in pacientes_pendientes:
                distancia = self.distancia_manhattan(estado_actual.ambulancia.celdaX, estado_actual.ambulancia.celdaY,
                                                     paciente)
                if distancia > distancia_paciente_mas_lejano:
                    distancia_paciente_mas_lejano = distancia
                    if paciente[2] == 'C':
                        distancia_hasta_centro = self.distancia_manhattan(celda_centro_CC[0], celda_centro_CC[1],
                                                                          paciente)
                        distancia_hasta_parking = self.distancia_manhattan(celda_centro_CC[0], celda_centro_CC[1],
                                                                           celda_parking)
                    else:  # celda[2] == 'N'
                        distancia_hasta_centro = self.distancia_manhattan(celda_centro_CN[0], celda_centro_CN[1],
                                                                          paciente)
                        distancia_hasta_parking = self.distancia_manhattan(celda_centro_CN[0], celda_centro_CN[1],
                                                                           celda_parking)

            # SI NO HAY PACIENTES EN EL MAPA
            if distancia_paciente_mas_lejano == 0:
                if estado_actual.ambulancia.pacientesC > 0 and estado_actual.ambulancia.pacientesN > 0:
                    distancia_hasta_centro_CC = self.distancia_manhattan(estado_actual.ambulancia.celdaX,
                                                                         estado_actual.ambulancia.celdaY,
                                                                         celda_centro_CC)
                    distancia_desde_CC_hasta_CN = self.distancia_manhattan(celda_centro_CC[0], celda_centro_CC[1],
                                                                           celda_centro_CN)
                    distancia_hasta_parking_desde_CN = self.distancia_manhattan(celda_centro_CN[0], celda_centro_CN[1],
                                                                                celda_parking)
                    return distancia_hasta_centro_CC + distancia_desde_CC_hasta_CN + distancia_hasta_parking_desde_CN

                elif estado_actual.ambulancia.pacientesC > 0:
                    distancia_hasta_CC = self.distancia_manhattan(estado_actual.ambulancia.celdaX,
                                                                  estado_actual.ambulancia.celdaY, celda_centro_CC)
                    distancia_desde_CC_hasta_parking = self.distancia_manhattan(celda_centro_CC[0], celda_centro_CC[1],
                                                                                celda_parking)
                    return distancia_hasta_CC + distancia_desde_CC_hasta_parking

                elif estado_actual.ambulancia.pacientesN > 0:
                    distancia_hasta_CN = self.distancia_manhattan(estado_actual.ambulancia.celdaX,
                                                                  estado_actual.ambulancia.celdaY, celda_centro_CN)
                    distancia_desde_CN_hasta_parking = self.distancia_manhattan(celda_centro_CN[0], celda_centro_CN[1],
                                                                                celda_parking)
                    return distancia_hasta_CN + distancia_desde_CN_hasta_parking

            return distancia_paciente_mas_lejano + distancia_hasta_centro + distancia_hasta_parking

        if heuristica == 4:
            # buscar celdas con pacientes
            pacientes_pendientes = []
            celda_centro_CC = None
            celda_centro_CN = None
            for celda in estado_actual.celdas:
                if celda.tipo == 'C' or celda.tipo == 'N':
                    pacientes_pendientes.append((celda.fila, celda.columna, celda.tipo))
                if celda.tipo == 'CC':
                    celda_centro_CC = (celda.fila, celda.columna)
                if celda.tipo == 'CN':
                    celda_centro_CN = (celda.fila, celda.columna)

            distancia_paciente_mas_lejano = 0
            distancia_hasta_centro = 0

            # SI HAY PACIENTES EN EL MAPA
            for paciente in pacientes_pendientes:
                distancia = self.distancia_manhattan(estado_actual.ambulancia.celdaX, estado_actual.ambulancia.celdaY,
                                                     paciente)
                if distancia > distancia_paciente_mas_lejano:
                    distancia_paciente_mas_lejano = distancia
                    if paciente[2] == 'C':
                        distancia_hasta_centro = self.distancia_manhattan(celda_centro_CC[0], celda_centro_CC[1],
                                                                          paciente)
                    else:  # celda[2] == 'N'
                        distancia_hasta_centro = self.distancia_manhattan(celda_centro_CN[0], celda_centro_CN[1],
                                                                          paciente)

            # SI NO HAY PACIENTES EN EL MAPA
            if distancia_paciente_mas_lejano == 0:
                if estado_actual.ambulancia.pacientesC > 0 and estado_actual.ambulancia.pacientesN > 0:
                    distancia_hasta_CC = self.distancia_manhattan(estado_actual.ambulancia.celdaX,
                                                                  estado_actual.ambulancia.celdaY, celda_centro_CC)
                    return distancia_hasta_CC

                elif estado_actual.ambulancia.pacientesC > 0:
                    distancia_hasta_CC = self.distancia_manhattan(estado_actual.ambulancia.celdaX,
                                                                  estado_actual.ambulancia.celdaY, celda_centro_CC)
                    return distancia_hasta_CC

                elif estado_actual.ambulancia.pacientesN > 0:
                    distancia_hasta_CN = self.distancia_manhattan(estado_actual.ambulancia.celdaX,
                                                                  estado_actual.ambulancia.celdaY, celda_centro_CN)
                    return distancia_hasta_CN

            return distancia_paciente_mas_lejano + distancia_hasta_centro

        if heuristica == 5:
            # buscar celdas con pacientes
            pacientes_pendientes = []
            parking = None
            for celda in estado_actual.celdas:
                if celda.tipo == 'C' or celda.tipo == 'N':
                    pacientes_pendientes.append((celda.fila, celda.columna, celda.tipo))
                if celda.tipo == 'P':
                    parking = (celda.fila, celda.columna)

            distancia_paciente_mas_lejano = 0
            distancia_hasta_parking = self.distancia_manhattan(estado_actual.ambulancia.celdaX, estado_actual.ambulancia.celdaY, parking)

            # SI HAY PACIENTES EN EL MAPA
            for paciente in pacientes_pendientes:
                distancia = self.distancia_manhattan(estado_actual.ambulancia.celdaX, estado_actual.ambulancia.celdaY,
                                                     paciente)
                if distancia > distancia_paciente_mas_lejano:
                    distancia_paciente_mas_lejano = distancia
                    distancia_hasta_parking = self.distancia_manhattan(paciente[0], paciente[1], parking)

            visita_a_CC = 1 if estado_actual.ambulancia.pacientesC > 0 else 0
            visita_A_CN = 1 if estado_actual.ambulancia.pacientesN > 0 else 0

            pacientes_restantes = estado_actual.pacientes_restantes -1 + visita_a_CC + visita_A_CN

            return distancia_paciente_mas_lejano + pacientes_restantes + distancia_hasta_parking



    def objetivo_cumplido(self, nodo):
        # Verifica si el estado cumple con el objetivo
        pacientes_restantes = nodo.mapa.pacientes_restantes
        pacientes_en_ambulancia = nodo.mapa.ambulancia.pacientesN + nodo.mapa.ambulancia.pacientesC
        ambulanciaX = nodo.mapa.ambulancia.celdaX
        ambulanciaY = nodo.mapa.ambulancia.celdaY
        celda_ambulancia = nodo.mapa.get_celda(ambulanciaX, ambulanciaY)
        celda_ambulancia_tipo = celda_ambulancia.tipo
        return pacientes_restantes == 0 and pacientes_en_ambulancia == 0 and celda_ambulancia_tipo == 'P'

    def distancia_manhattan(self, ambulanciaX, ambulanciaY, celda2):
        return abs(ambulanciaX - celda2[0]) + abs(ambulanciaY - celda2[1])
