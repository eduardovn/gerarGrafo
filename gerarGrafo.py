import os
import numpy as np
import networkx as nx
import metis

from collections import defaultdict
from matplotlib import pyplot as plt
from matplotlib.path import Path



def grouped(iterable, n):
    return zip(*[iter(iterable)]*n)


def geraListaGrafos(listaDeListasOrdenadasEmEspiral):
    listaCordenadasIniciais = []
    for itemLista in listaDeListasOrdenadasEmEspiral:
        listaCordenadasIniciais.append(itemLista[0])

    listaOrdenada = sorted(listaCordenadasIniciais,key=lambda l:(l[1],l[0]))
    
    listaAux = listaOrdenada
    listaGrafo = []
    tamanhoLista = len(listaOrdenada)-1
    for h in range (len(listaOrdenada)):
        if (h < 4):
            for i, j, k, l, m in grouped(listaAux, 5):
                pontoA = np.array(i)
                pontoB = np.array(j)
                dist = np.linalg.norm(pontoA - pontoB)
                listaGrafo.append((pontoA.tolist(),pontoB.tolist(),round(dist,1)))
                
                pontoA = np.array(i)
                pontoC = np.array(k)
                dist = np.linalg.norm(pontoA - pontoC)
                listaGrafo.append((pontoA.tolist(),pontoC.tolist(),round(dist,1)))
                
                pontoA = np.array(i)
                pontoD = np.array(m)
                dist = np.linalg.norm(pontoA - pontoD)
                listaGrafo.append((pontoA.tolist(),pontoD.tolist(),round(dist,1)))
                break    
            listaOrdenada.pop(0)

        if ((h >= 4) and (h < tamanhoLista-1)):
            for i, j, k in grouped(listaAux, 3):
                pontoA = np.array(i)
                pontoB = np.array(j)
                dist = np.linalg.norm(pontoA - pontoB)
                listaGrafo.append((pontoA.tolist(),pontoB.tolist(),round(dist,1)))
                
                pontoA = np.array(i)
                pontoC = np.array(k)
                dist = np.linalg.norm(pontoA - pontoC)
                listaGrafo.append((pontoA.tolist(),pontoC.tolist(),round(dist,1)))
                break
            listaOrdenada.pop(0)
        listaAux = listaOrdenada

        if (h == tamanhoLista):
            for i, j in grouped(listaAux, 2):
                pontoA = np.array(i)
                pontoB = np.array(j)
                dist = np.linalg.norm(pontoA - pontoB)
                listaGrafo.append((pontoA.tolist(),pontoB.tolist(),round(dist,1)))
                break
            listaOrdenada.pop(0)
        listaAux = listaOrdenada
   
    return listaGrafo 


def gerarGrafo(listaOrdenada, listaGrafo):
    grafo = nx.Graph()
    dicionario = ({tuple(k): v for v, k in enumerate(listaOrdenada)})
    listaPosicoes = []
    
    i = 0
    for key in dicionario.keys():    
        for itemLista in listaGrafo:
            if(key == tuple(itemLista[0])):
                listaPosicoes.append(((tuple(itemLista[0])),(tuple(itemLista[1])),(itemLista[2])))
        i = i + 1
    
    
    grafo.add_weighted_edges_from(listaPosicoes)

    return grafo



def printaGrafo(grafo, semente):
    elarge = [(u, v) for (u, v, d) in grafo.edges(data=True) if d["weight"] > 0.5]
    esmall = [(u, v) for (u, v, d) in grafo.edges(data=True) if d["weight"] <= 0.5]
    
    pos = nx.spring_layout(grafo, seed=semente)  # positions for all nodes - seed for reproducibility

    # nodes
    nx.draw_networkx_nodes(grafo, pos, node_size=700)

    # edges
    nx.draw_networkx_edges(grafo, pos, edgelist=elarge, width=2)
    nx.draw_networkx_edges(grafo, pos, edgelist=esmall, width=2, alpha=0.5, edge_color="b", style="dashed")

    # node labels
    nx.draw_networkx_labels(grafo, pos, font_size=20, font_family="sans-serif")
    # edge weight labels
    edge_labels = nx.get_edge_attributes(grafo, "weight")
    nx.draw_networkx_edge_labels(grafo, pos, edge_labels)

    ax = plt.gca()
    ax.margins(0.08)
    plt.axis("off")
    plt.tight_layout()
    plt.show()



def reverse2DList(inputList):
    inputList.reverse()
    inputList = list(map(lambda x: x[::1], inputList))
    
    return inputList



def geraCaminho1UAV(listaCordenadasIniciais, listaGrafo):
    grafo = nx.Graph()

    listaOrdenada = sorted(listaCordenadasIniciais,key=lambda l:(l[1],l[0]))  
    #plt.scatter(*zip(* listaOrdenada))
    #plt.show()
        
    grafo = gerarGrafo(listaOrdenada, listaGrafo)
    #printaGrafo(grafo, len(listaOrdenada)-1)
    tsp = nx.approximation.traveling_salesman_problem
    path = tsp(grafo, cycle=False)
        
    swapList = path[:2]
    swapList.reverse()

    listaFinal = []
    listaFinal = swapList + path[2:]
    #print("listaFinal1: ",listaFinal)
    #print("path: ",listaFinal)
    
    return listaFinal
    


def geraCaminho2UAV(listaCordenadasIniciais, listaGrafo):   
    listaOrdenada = sorted(listaCordenadasIniciais,key=lambda l:(l[0],l[1]))    

    resultado = ((listaOrdenada[0][0] + listaOrdenada[len(listaOrdenada)-1][0])/2)
    lista1 = []
    lista2 = []
    for i in range (len(listaOrdenada)):
        if(resultado > listaOrdenada[i][0]):
            lista1.append((listaOrdenada[i][0], listaOrdenada[i][1]))
            
        else:
            lista2.append((listaOrdenada[i][0], listaOrdenada[i][1]))
                

    maiorElementoLista1 = max(lista1)    
    listaA = []
    listaB = []
    for i in range (len(lista1)):
        for itemLista in listaGrafo:
            if((tuple(lista1[i]) == tuple(itemLista[0])) and (tuple(itemLista[1])[0] <= maiorElementoLista1[0])):
                listaA.append(itemLista)
            if((tuple(lista2[i]) == tuple(itemLista[0])) and (tuple(itemLista[1])[0] > maiorElementoLista1[0])):
                listaB.append(itemLista)
         
    grafo1 = nx.Graph()
    grafo1 = gerarGrafo(lista1, listaA)
    #printaGrafo(grafo1, len(listaA)-1)
       
    grafo2 = nx.Graph()
    grafo2 = gerarGrafo(lista2, listaB)
    #printaGrafo(grafo2, len(listaB)-1)

    tsp = nx.approximation.traveling_salesman_problem
    path1 = []
    path1 = reverse2DList(tsp(grafo1, cycle=False))
    #print("path1: ",path1)
        
    path2 = []
    path2 = reverse2DList(tsp(grafo2, cycle=False))
    #print("path2: ",path2)

    listaFinal = []
    listaFinal.append(path1)
    listaFinal.append(path2)

    return listaFinal


def geraCaminho3UAV(listaCordenadasIniciais, listaGrafo):
    listaOrdenada = sorted(listaCordenadasIniciais,key=lambda l:(l[0],l[1]))    

    resultado = ((listaOrdenada[0][0] + listaOrdenada[len(listaOrdenada)-1][0])/2)
    lista1 = []
    lista2 = []
    for i in range (len(listaOrdenada)):
        if(resultado > listaOrdenada[i][0]):
            lista1.append((listaOrdenada[i][0], listaOrdenada[i][1]))
            
        else:
            lista2.append((listaOrdenada[i][0], listaOrdenada[i][1]))

    maiorElementoLista1 = max(lista1)  
    listaA = []
    listaB = []
    for i in range (len(lista1)):
        for itemLista in listaGrafo:
            if((tuple(lista1[i]) == tuple(itemLista[0])) and (tuple(itemLista[1])[0] <= maiorElementoLista1[0])):
                listaA.append(itemLista)
                
            if((tuple(lista2[i]) == tuple(itemLista[0])) and (tuple(itemLista[1])[0] > maiorElementoLista1[0])):
                listaB.append(itemLista)

    grafo1 = nx.Graph()
    grafo1 = gerarGrafo(lista1, listaA)
    #printaGrafo(grafo1, len(listaA)-1)
       
    grafo2 = nx.Graph()
    grafo2 = gerarGrafo(lista2, listaB)
    #printaGrafo(grafo2, len(listaB)-1)

    tsp = nx.approximation.traveling_salesman_problem
    path1 = []
    path1 = reverse2DList(tsp(grafo1, cycle=False))
        
    path2 = []
    path2 = reverse2DList(tsp(grafo2, cycle=False))

    path3 = []
    path3.append(max(path1))
    path3.append(max(path2))
    
    path1.pop(-2)
    path2.pop(-2)
    
    listaFinal = []
    listaFinal.append(path1)
    listaFinal.append(path2)
    listaFinal.append(path3)
    
    return listaFinal


def geraCaminho4UAV(listaCordenadasIniciais, listaGrafo):
    listaOrdenada = sorted(listaCordenadasIniciais,key=lambda l:(l[0],l[1]))    

    resultado = ((listaOrdenada[0][0] + listaOrdenada[len(listaOrdenada)-1][0])/2)
    lista1 = []
    lista2 = []
    for i in range (len(listaOrdenada)):
        if(resultado > listaOrdenada[i][0]):
            lista1.append((listaOrdenada[i][0], listaOrdenada[i][1]))
            
        else:
            lista2.append((listaOrdenada[i][0], listaOrdenada[i][1]))

    maiorElementoLista1 = max(lista1)  
    listaA = []
    listaB = []
    for i in range (len(lista1)):
        for itemLista in listaGrafo:
            if((tuple(lista1[i]) == tuple(itemLista[0])) and (tuple(itemLista[1])[0] <= maiorElementoLista1[0])):
                listaA.append(itemLista)
                
            if((tuple(lista2[i]) == tuple(itemLista[0])) and (tuple(itemLista[1])[0] > maiorElementoLista1[0])):
                listaB.append(itemLista)

    grafo1 = nx.Graph()
    grafo1 = gerarGrafo(lista1, listaA)
    #printaGrafo(grafo1, len(listaA)-1)
       
    grafo2 = nx.Graph()
    grafo2 = gerarGrafo(lista2, listaB)
    #printaGrafo(grafo2, len(listaB)-1)

    tsp = nx.approximation.traveling_salesman_problem
    path1 = []
    path1 = reverse2DList(tsp(grafo1, cycle=False))
    half1 = len(path1)//2
    caminho1 = []
    caminho1 = path1[:half1]
    caminho2 = []
    caminho2 = path1[half1:]

    path2 = []
    path2 = reverse2DList(tsp(grafo2, cycle=False))
    half2 = len(path2)//2
    caminho3 = []
    caminho3 = path2[:half2]
    caminho4 = []
    caminho4 = path2[half2:]

    listaFinal = []
    listaFinal.append(caminho1) 
    listaFinal.append(caminho2)
    listaFinal.append(caminho3)
    listaFinal.append(caminho4)

    return listaFinal


def gerarArquivo(numeroDeUAVs, caminhoComlistaPontos):
    
    if(numeroDeUAVs == 1):
        f = open("dados.txt", "w")
        for item in caminhoComlistaPontos:
            f.write("UAV: "+str(numeroDeUAVs))
            f.write('\n')
            f.write(str(item))
            f.write('\n')
        f.close()

    if(numeroDeUAVs == 2):
        f = open("dados.txt", "w")
        
        half = len(caminhoComlistaPontos)//2
        part1 = []
        part1 = caminhoComlistaPontos[:half]
        for item in part1:
                f.write("UAV: 1")
                f.write('\n')
                f.write(str(item))
                f.write('\n')

        part2 = []
        part2 = caminhoComlistaPontos[half:]
        for item in part2:
                f.write("UAV: 2")
                f.write('\n')
                f.write(str(item))
                f.write('\n')

        f.close()

    if(numeroDeUAVs == 3):
        f = open("dados.txt", "w")     

        f.write("UAV: 1")
        f.write('\n')
        f.write(str(caminhoComlistaPontos[0]))
        f.write('\n')

        f.write("UAV: 1")
        f.write('\n')
        f.write(str(caminhoComlistaPontos[1]))
        f.write('\n')

        f.write("UAV: 1")
        f.write('\n')
        f.write(str(caminhoComlistaPontos[3]))
        f.write('\n')    


        f.write("UAV: 2")
        f.write('\n')
        f.write(str(caminhoComlistaPontos[2]))
        f.write('\n')

        f.write("UAV: 2")
        f.write('\n')
        f.write(str(caminhoComlistaPontos[6]))
        f.write('\n')

        f.write("UAV: 3")
        f.write('\n')
        f.write(str(caminhoComlistaPontos[4]))
        f.write('\n')    

        f.write("UAV: 3")
        f.write('\n')
        f.write(str(caminhoComlistaPontos[5]))
        f.write('\n')

        f.write("UAV: 3")
        f.write('\n')
        f.write(str(caminhoComlistaPontos[7]))
        f.write('\n')

        f.close()

    if(numeroDeUAVs == 4):
        f = open("dados.txt", "w")        

        f.write("UAV: 1")
        f.write('\n')
        f.write(str(caminhoComlistaPontos[0]))
        f.write('\n')
        
        f.write("UAV: 1")
        f.write('\n')
        f.write(str(caminhoComlistaPontos[1]))
        f.write('\n')
        
        f.write("UAV: 2")
        f.write('\n')
        f.write(str(caminhoComlistaPontos[2]))
        f.write('\n')

        f.write("UAV: 2")
        f.write('\n')
        f.write(str(caminhoComlistaPontos[3]))
        f.write('\n')

        f.write("UAV: 3")
        f.write('\n')
        f.write(str(caminhoComlistaPontos[4]))
        f.write('\n')

        f.write("UAV: 3")
        f.write('\n')
        f.write(str(caminhoComlistaPontos[5]))
        f.write('\n')

        f.write("UAV: 4")
        f.write('\n')
        f.write(str(caminhoComlistaPontos[6]))
        f.write('\n')

        f.write("UAV: 4")
        f.write('\n')
        f.write(str(caminhoComlistaPontos[7]))
        f.write('\n')

        f.close()
       
        

def listaOrdemInvestigacao(caminhoComlistaPontos, listaDeListasOrdenadasEmEspiral):
    listaOrdenada = []

    for itemLista2 in listaDeListasOrdenadasEmEspiral:
        for itemLista1 in caminhoComlistaPontos:
            for i in range (len(itemLista1)):
                if itemLista1[i] == itemLista2[0]:
                    listaOrdenada.append(itemLista2)
    
    return listaOrdenada


def listaOrdemInvestigacao_1UAV(caminhoComlistaPontos, listaDeListasOrdenadasEmEspiral):
    listaOrdenada = []

    cont = 0
    for itemLista2 in listaDeListasOrdenadasEmEspiral:
        for itemLista1 in caminhoComlistaPontos:
            if((itemLista1[0] == itemLista2[0][0]) and (cont % 2 == 0)):
                listaOrdenada.append(itemLista2)
            cont = cont + 1
    
    return listaOrdenada
    

def definirCaminhoseUAVs(numeroDeUAVs, listaCordenadasIniciais, listaGrafo):
    if(numeroDeUAVs == 1):
        caminhoComlistaPontos = []
        caminhoComlistaPontos = geraCaminho1UAV(listaCordenadasIniciais, listaGrafo)
        listaOrdenada = []
        listaOrdenada = listaOrdemInvestigacao_1UAV(caminhoComlistaPontos, listaDeListasOrdenadasEmEspiral)
        gerarArquivo(numeroDeUAVs, listaOrdenada)

    if(numeroDeUAVs == 2):
        caminhoComlistaPontos = []
        caminhoComlistaPontos = geraCaminho2UAV(listaCordenadasIniciais, listaGrafo)
        listaOrdenada = []
        listaOrdenada = listaOrdemInvestigacao(caminhoComlistaPontos, listaDeListasOrdenadasEmEspiral)
        gerarArquivo(numeroDeUAVs, listaOrdenada)
        
    if(numeroDeUAVs == 3):
        caminhoComlistaPontos = []
        caminhoComlistaPontos = geraCaminho3UAV(listaCordenadasIniciais, listaGrafo)
        listaOrdenada = []
        listaOrdenada = listaOrdemInvestigacao(caminhoComlistaPontos, listaDeListasOrdenadasEmEspiral)
        gerarArquivo(numeroDeUAVs, listaOrdenada)
        
    if(numeroDeUAVs == 4):
        caminhoComlistaPontos = []
        caminhoComlistaPontos = geraCaminho4UAV(listaCordenadasIniciais, listaGrafo)
        listaOrdenada = []
        listaOrdenada = listaOrdemInvestigacao(caminhoComlistaPontos, listaDeListasOrdenadasEmEspiral)
        gerarArquivo(numeroDeUAVs, listaOrdenada)


# Driver Code
if __name__=='__main__':
    numeroDeUAVs = 2

    listaDeListasOrdenadasEmEspiral = [
        [(41.4, 20.0), (35.6, 20.0), (35.6, 25.0), (41.4, 25.0), (47.2, 25.0), (47.2, 20.0), (47.2, 15.0), (41.4, 15.0), (35.6, 15.0), (29.8, 15.0), (29.8, 20.0), (29.8, 25.0), (29.8, 30.0), (35.6, 30.0), (41.4, 30.0), (47.2, 30.0), (53.0, 30.0), (53.0, 25.0), (53.0, 20.0), (53.0, 15.0), (53.0, 10.0), (47.2, 10.0), (41.4, 10.0), (35.6, 10.0), (29.8, 10.0), (24.0, 10.0), (24.0, 15.0), (24.0, 20.0), (24.0, 25.0), (24.0, 30.0), (24.0, 35.0), (29.8, 35.0), (35.6, 35.0), (41.4, 35.0), (47.2, 35.0), (53.0, 35.0), (58.0, 30.0), (58.0, 25.0), (58.0, 20.0), (58.0, 15.0), (58.0, 10.0), (53.0, 5.0), (47.2, 5.0), (41.4, 5.0), (35.6, 5.0), (29.8, 5.0), (24.0, 5.0), (19.0, 10.0), (19.0, 15.0), (19.0, 20.0), (19.0, 25.0), (19.0, 30.0), (24.0, 40.0), (29.8, 40.0), (35.6, 40.0), (41.4, 40.0), (47.2, 40.0), (53.0, 40.0), (63.0, 20.0), (53.0, 0.0), (47.2, 0.0), (41.4, 0.0), (35.6, 0.0), (29.8, 0.0), (24.0, 0.0), (14.0, 20.0)], 
        [(41.4, 59.0), (35.6, 59.0), (35.6, 63.8), (41.4, 63.8), (47.2, 63.8), (47.2, 59.0), (47.2, 54.3), (41.4, 54.3), (35.6, 54.3), (29.8, 54.3), (29.8, 59.0), (29.8, 63.8), (29.8, 68.5), (35.6, 68.5), (41.4, 68.5), (47.2, 68.5), (53.0, 68.5), (53.0, 63.8), (53.0, 59.0), (53.0, 54.3), (53.0, 49.5), (47.2, 49.5), (41.4, 49.5), (35.6, 49.5), (29.8, 49.5), (24.0, 49.5), (24.0, 54.3), (24.0, 59.0), (24.0, 63.8), (24.0, 68.5), (24.0, 73.3), (29.8, 73.3), (35.6, 73.3), (41.4, 73.3), (47.2, 73.3), (53.0, 73.3), (58.0, 68.5), (58.0, 63.75), (58.0, 59.0), (58.0, 54.25), (58.0, 49.5), (53.0, 44.8), (47.2, 44.8), (41.4, 44.8), (35.6, 44.8), (29.8, 44.8), (24.0, 44.8), (19.0, 49.5), (19.0, 54.25), (19.0, 59.0), (19.0, 63.75), (19.0, 68.5), (24.0, 78.0), (29.8, 78.0), (35.6, 78.0), (41.4, 78.0), (47.2, 78.0), (53.0, 78.0), (62.75, 59.0), (53.0, 40.0), (47.2, 40.0), (41.4, 40.0), (35.6, 40.0), (29.8, 40.0), (24.0, 40.0), (14.25, 59.0)], 
        [(79.4, 77.0), (73.6, 77.0), (73.6, 81.8), (79.4, 81.8), (85.2, 81.8), (85.2, 77.0), (85.2, 72.3), (79.4, 72.3), (73.6, 72.3), (67.8, 72.3), (67.8, 77.0), (67.8, 81.8), (67.8, 86.5), (73.6, 86.5), (79.4, 86.5), (85.2, 86.5), (91.0, 86.5), (91.0, 81.8), (91.0, 77.0), (91.0, 72.3), (91.0, 67.5), (85.2, 67.5), (79.4, 67.5), (73.6, 67.5), (67.8, 67.5), (62.0, 67.5), (62.0, 72.3), (62.0, 77.0), (62.0, 81.8), (62.0, 86.5), (62.0, 91.3), (67.8, 91.3), (73.6, 91.3), (79.4, 91.3), (85.2, 91.3), (91.0, 91.3), (96.0, 86.5), (96.0, 81.75), (96.0, 77.0), (96.0, 72.25), (96.0, 67.5), (91.0, 62.8), (85.2, 62.8), (79.4, 62.8), (73.6, 62.8), (67.8, 62.8), (62.0, 62.8), (57.0, 67.5), (57.0, 72.25), (57.0, 77.0), (57.0, 81.75), (57.0, 86.5), (62.0, 96.0), (67.8, 96.0), (73.6, 96.0), (79.4, 96.0), (85.2, 96.0), (91.0, 96.0), (100.75, 77.0), (91.0, 58.0), (85.2, 58.0), (79.4, 58.0), (73.6, 58.0), (67.8, 58.0), (62.0, 58.0), (52.25, 77.0)], 
        [(79.4, 39.0), (73.6, 39.0), (73.6, 43.8), (79.4, 43.8), (85.2, 43.8), (85.2, 39.0), (85.2, 34.3), (79.4, 34.3), (73.6, 34.3), (67.8, 34.3), (67.8, 39.0), (67.8, 43.8), (67.8, 48.5), (73.6, 48.5), (79.4, 48.5), (85.2, 48.5), (91.0, 48.5), (91.0, 43.8), (91.0, 39.0), (91.0, 34.3), (91.0, 29.5), (85.2, 29.5), (79.4, 29.5), (73.6, 29.5), (67.8, 29.5), (62.0, 29.5), (62.0, 34.3), (62.0, 39.0), (62.0, 43.8), (62.0, 48.5), (62.0, 53.3), (67.8, 53.3), (73.6, 53.3), (79.4, 53.3), (85.2, 53.3), (91.0, 53.3), (96.0, 48.5), (96.0, 43.75), (96.0, 39.0), (96.0, 34.25), (96.0, 29.5), (91.0, 24.8), (85.2, 24.8), (79.4, 24.8), (73.6, 24.8), (67.8, 24.8), (62.0, 24.8), (57.0, 29.5), (57.0, 34.25), (57.0, 39.0), (57.0, 43.75), (57.0, 48.5), (62.0, 58.0), (67.8, 58.0), (73.6, 58.0), (79.4, 58.0), (85.2, 58.0), (91.0, 58.0), (100.75, 39.0), (91.0, 20.0), (85.2, 20.0), (79.4, 20.0), (73.6, 20.0), (67.8, 20.0), (62.0, 20.0), (52.25, 39.0)],
        [(117.4, 20.0), (111.6, 20.0), (111.6, 25.0), (117.4, 25.0), (123.2, 25.0), (123.2, 20.0), (123.2, 15.0), (117.4, 15.0), (111.6, 15.0), (105.8, 15.0), (105.8, 20.0), (105.8, 25.0), (105.8, 30.0), (111.6, 30.0), (117.4, 30.0), (123.2, 30.0), (129.0, 30.0), (129.0, 25.0), (129.0, 20.0), (129.0, 15.0), (129.0, 10.0), (123.2, 10.0), (117.4, 10.0), (111.6, 10.0), (105.8, 10.0), (100.0, 10.0), (100.0, 15.0), (100.0, 20.0), (100.0, 25.0), (100.0, 30.0), (100.0, 35.0), (105.8, 35.0), (111.6, 35.0), (117.4, 35.0), (123.2, 35.0), (129.0, 35.0), (134.0, 30.0), (134.0, 25.0), (134.0, 20.0), (134.0, 15.0), (134.0, 10.0), (129.0, 5.0), (123.2, 5.0), (117.4, 5.0), (111.6, 5.0), (105.8, 5.0), (100.0, 5.0), (95.0, 10.0), (95.0, 15.0), (95.0, 20.0), (95.0, 25.0), (95.0, 30.0), (100.0, 40.0), (105.8, 40.0), (111.6, 40.0), (117.4, 40.0), (123.2, 40.0), (129.0, 40.0), (139.0, 20.0), (129.0, 0.0), (123.2, 0.0), (117.4, 0.0), (111.6, 0.0), (105.8, 0.0), (100.0, 0.0), (90.0, 20.0)], 
        [(117.4, 59.0), (111.6, 59.0), (111.6, 63.8), (117.4, 63.8), (123.2, 63.8), (123.2, 59.0), (123.2, 54.3), (117.4, 54.3), (111.6, 54.3), (105.8, 54.3), (105.8, 59.0), (105.8, 63.8), (105.8, 68.5), (111.6, 68.5), (117.4, 68.5), (123.2, 68.5), (129.0, 68.5), (129.0, 63.8), (129.0, 59.0), (129.0, 54.3), (129.0, 49.5), (123.2, 49.5), (117.4, 49.5), (111.6, 49.5), (105.8, 49.5), (100.0, 49.5), (100.0, 54.3), (100.0, 59.0), (100.0, 63.8), (100.0, 68.5), (100.0, 73.3), (105.8, 73.3), (111.6, 73.3), (117.4, 73.3), (123.2, 73.3), (129.0, 73.3), (134.0, 68.5), (134.0, 63.75), (134.0, 59.0), (134.0, 54.25), (134.0, 49.5), (129.0, 44.8), (123.2, 44.8), (117.4, 44.8), (111.6, 44.8), (105.8, 44.8), (100.0, 44.8), (95.0, 49.5), (95.0, 54.25), (95.0, 59.0), (95.0, 63.75), (95.0, 68.5), (100.0, 78.0), (105.8, 78.0), (111.6, 78.0), (117.4, 78.0), (123.2, 78.0), (129.0, 78.0), (138.75, 59.0), (129.0, 40.0), (123.2, 40.0), (117.4, 40.0), (111.6, 40.0), (105.8, 40.0), (100.0, 40.0), (90.25, 59.0)], 
        [(155.4, 77.0), (149.6, 77.0), (149.6, 81.8), (155.4, 81.8), (161.2, 81.8), (161.2, 77.0), (161.2, 72.3), (155.4, 72.3), (149.6, 72.3), (143.8, 72.3), (143.8, 77.0), (143.8, 81.8), (143.8, 86.5), (149.6, 86.5), (155.4, 86.5), (161.2, 86.5), (167.0, 86.5), (167.0, 81.8), (167.0, 77.0), (167.0, 72.3), (167.0, 67.5), (161.2, 67.5), (155.4, 67.5), (149.6, 67.5), (143.8, 67.5), (138.0, 67.5), (138.0, 72.3), (138.0, 77.0), (138.0, 81.8), (138.0, 86.5), (138.0, 91.3), (143.8, 91.3), (149.6, 91.3), (155.4, 91.3), (161.2, 91.3), (167.0, 91.3), (172.0, 86.5), (172.0, 81.75), (172.0, 77.0), (172.0, 72.25), (172.0, 67.5), (167.0, 62.8), (161.2, 62.8), (155.4, 62.8), (149.6, 62.8), (143.8, 62.8), (138.0, 62.8), (133.0, 67.5), (133.0, 72.25), (133.0, 77.0), (133.0, 81.75), (133.0, 86.5), (138.0, 96.0), (143.8, 96.0), (149.6, 96.0), (155.4, 96.0), (161.2, 96.0), (167.0, 96.0), (176.75, 77.0), (167.0, 58.0), (161.2, 58.0), (155.4, 58.0), (149.6, 58.0), (143.8, 58.0), (138.0, 58.0), (128.25, 77.0)], 
        [(155.4, 39.0), (149.6, 39.0), (149.6, 43.8), (155.4, 43.8), (161.2, 43.8), (161.2, 39.0), (161.2, 34.3), (155.4, 34.3), (149.6, 34.3), (143.8, 34.3), (143.8, 39.0), (143.8, 43.8), (143.8, 48.5), (149.6, 48.5), (155.4, 48.5), (161.2, 48.5), (167.0, 48.5), (167.0, 43.8), (167.0, 39.0), (167.0, 34.3), (167.0, 29.5), (161.2, 29.5), (155.4, 29.5), (149.6, 29.5), (143.8, 29.5), (138.0, 29.5), (138.0, 34.3), (138.0, 39.0), (138.0, 43.8), (138.0, 48.5), (138.0, 53.3), (143.8, 53.3), (149.6, 53.3), (155.4, 53.3), (161.2, 53.3), (167.0, 53.3), (172.0, 48.5), (172.0, 43.75), (172.0, 39.0), (172.0, 34.25), (172.0, 29.5), (167.0, 24.8), (161.2, 24.8), (155.4, 24.8), (149.6, 24.8), (143.8, 24.8), (138.0, 24.8), (133.0, 29.5), (133.0, 34.25), (133.0, 39.0), (133.0, 43.75), (133.0, 48.5), (138.0, 58.0), (143.8, 58.0), (149.6, 58.0), (155.4, 58.0), (161.2, 58.0), (167.0, 58.0), (176.75, 39.0), (167.0, 20.0), (161.2, 20.0), (155.4, 20.0), (149.6, 20.0), (143.8, 20.0), (138.0, 20.0), (128.25, 39.0)]
        ]

    listaCordenadasIniciais = []
    for itemLista in listaDeListasOrdenadasEmEspiral:
        listaCordenadasIniciais.append(itemLista[0])
      
    listaGrafo = geraListaGrafos(listaDeListasOrdenadasEmEspiral) 
    
    definirCaminhoseUAVs(numeroDeUAVs, listaCordenadasIniciais, listaGrafo)
    ############################################################
    ############################################################

        
         

