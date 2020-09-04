#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
__author__ = "jys"
__copyright__ = "Copyright (C) 2020 LATEJCON"

import sys
from os import path
from unicodedata import normalize
from ArbreAncestres import ArbreAncestres
from AncestresPdf import AncestresPdf
from AncestresPdfImprimable import AncestresPdfImprimable

def usage():
    script = '$PY/' + path.basename(sys.argv[0])
    print (u"""© l'ATEJCON.  
Crée sur un PDF le tableau de tous les ancêtres classés par génération
et par ordre d'ancêtres d'un individu-racine spécifié par son identifiant
gramps.
Le PDF est écrit dans rejsultat/<prénom-nom>-ancestres-complet.pdf 
ou rejsultat/<prénom-nom>-ancestres-partiel.pdf
Les ancêtres sont identifiés par nom-prénom (NP) (défaut) ou prénom-nom (PN)
Il est possible de limiter le nombre de générations affichées (0 = toutes)
Il est possible de filtrer les ancêtres en fournissant les identifiants 
gramps d'ancêtres particuliers (voir "Accès aux bases de données Gramps", 
LAT2020.JYS.483). 

usage   : {:s} <base> <individu-racine> [NP|PN] [nbre générations] [filtre]
example : {:s} sage I0001
example : {:s} sage I0001 PN 0 I0008,I1243
""".format(script, script, script))

def main():
    try:
        if len(sys.argv) < 3: raise Exception()
        nomBase = sys.argv[1].strip()
        racineIdentifiant = sys.argv[2].strip()
        ordreNp = True
        nbGejnejrations = 0
        identifiantsFiltrants = []
        if len(sys.argv) > 3:
            arg2 = sys.argv[3].strip().upper()
            if arg2 not in ('NP', 'PN'): raise Exception('NP ou PN')
            ordreNp = arg2 == 'NP'
        if len(sys.argv) > 4: nbGejnejrations = int(sys.argv[4])
        if len(sys.argv) > 5: identifiantsFiltrants = sys.argv[5].strip().split(',')
        dessineArbre(nomBase, racineIdentifiant, ordreNp, nbGejnejrations, identifiantsFiltrants)
    except Exception as exc:
        if len(exc.args) == 0: usage()
        else:
            print ("******************************")
            print (exc.args[0])
            print ("******************************")
            raise
        sys.exit()
        
def dessineArbre(nomBase, racineIdentifiant, ordreNp, nbGejnejrations, identifiantsFiltrants):
    # ejtablit l'arbre 
    arbreAncestres = ArbreAncestres(nomBase)
    arbreAncestres.arbreComplet(racineIdentifiant)
    print('sans filtre : {:4d} ancêtres sur {:2d} générations'.format(arbreAncestres.nombreTotal(), arbreAncestres.maxGejnejration() +1))
    arbreAncestres.filtreArbre(identifiantsFiltrants)
    print('avec filtre : {:4d} ancêtres sur {:2d} générations'.format(arbreAncestres.nombreTotal(), arbreAncestres.maxGejnejration() +1))
    arbreAncestres.tailleArbre(nbGejnejrations)
    print('avec limite : {:4d} ancêtres sur {:2d} générations'.format(arbreAncestres.nombreTotal(), arbreAncestres.maxGejnejration() +1))
    arbreAncestres.calculeManquants()
    print('              {:4d} ancêtres ajoutés pour la géométrie'.format(arbreAncestres.nombreManquants()))
    
    # ejtablit le nom du fichier pdf 
    ((prejnom, nom), dl1, dl2, dl3) = arbreAncestres.attributsAncestre(1)
    extension = (prejnom + nom).replace(' ', '')
    extension = normalize('NFD', extension).encode('ascii','ignore').decode()    #tous les caracteres en ASCII    
    racine = '/'.join(path.dirname(path.abspath(sys.argv[0])).split('/')[:-1])
    if len(identifiantsFiltrants) == 0: extFiltre = 'complet'
    else: extFiltre = 'partiel'
    nomFichierSortie = racine + '/rejsultat/' + extension +'-ancestres-' + extFiltre
    nomFichierSortieC = nomFichierSortie + 'C.pdf'
    nomFichierSortieE = nomFichierSortie + 'E.pdf'
    nomFichierSortieF = nomFichierSortie + 'F.pdf'
    
    # titre, filigrane
    filigrane = (prejnom + nom).upper().replace(' ', '')
    titre = []
    if len(identifiantsFiltrants) == 0: titre.append(u'Arbre généalogique')
    else: titre.append(u'Arbre généalogique partiel')
    titre.append(u'de '+ prejnom + ' ' + nom)
    latejcon = racine + '/rejsultat/echiquierLatejcon4-150.png'
    
    #le message de statistiques
    statistiques = ['{:4d} ancêtres'.format(arbreAncestres.nombreTotal() -1)]  #on ne compte pas la racine
    nombreParGejnejration = list(arbreAncestres.rejpartitionParGejnejration().items())
    nombreParGejnejration.sort()
    for (gejnejration, nombre) in nombreParGejnejration[1:]: 
        if len(identifiantsFiltrants) == 0:
            statistiques.append('{:4d} en génération {:3d}  : {:4d}%%'.format(nombre, -gejnejration, round(100.0*nombre//(2**(gejnejration)))))
        #else:
            #statistiques.append('{:4d} en génération {:3d}'.format(nombre, 1-gejnejration))
            
    #recupehre tous les numejros d'ancestres et y ajoute les manquants
    tousNumejros = arbreAncestres.tousNumejros()
    tousNumejros.extend(arbreAncestres.lesManquants())
    tousNumejros.sort()
    
    #1) calcule tous les positionnements thejoriques
    positions = {}
    for numejro in tousNumejros:
        rang_h = arbreAncestres.gejnejration(numejro)         #le 1er est 0
        rang_v = vertical(numejro, arbreAncestres) -1         #le 1er est 0
        positions[numejro] = (rang_h, rang_v)
    trace(positions)
         
    ##2) calcule les positionnements moyennés
    #positionsMoyennes = calculePositionsMoyennes(positions)
         
    #3) calcule des positionnements tassés
    positionsTassejes = calculePositionsTassejes(positions, arbreAncestres)
    #trouve les maximums pour la taille de la page et la position verticale du pehre (telescopage avec le cartouche)
    (max_h, max_v) = maximumHV(positionsTassejes)
    if len(positionsTassejes) > 1: 
        pos_2 = positionsTassejes[2][1]  #position verticale du pehre (pour calcul anti-carambolage avec le cartouche)
    else : pos_2 = 0
    trace(positionsTassejes)
    
    #ejcrit le PDF des ancestres version "positionnements moyennejs"
    ejcritPdf(nomFichierSortieC, arbreAncestres, ordreNp, positionsTassejes, max_h, max_v, pos_2, titre, filigrane, latejcon, statistiques)
    ejcritPdfImprimable((nomFichierSortieE, nomFichierSortieF), arbreAncestres, ordreNp, positionsTassejes, titre, filigrane, latejcon, statistiques)         
         
############################
#trouve le rang vertical "normal" en fonction du numejro
def vertical(numejro, arbreAncestres):
    #si le numejro est 1 sort les nombre d'ascendants paternels +1
    if numejro == 1: return arbreAncestres.nombreAncestresPaternels(1) +1
    #calcule la position verticale de son descendant
    descendant = numejro //2
    verticalDescendant = vertical(descendant, arbreAncestres)
    #le calcul de la position dejpend si c'est un garçon ou une fille
    if numejro &1 == 0:
        return verticalDescendant - arbreAncestres.nombreAncestresPaternels(descendant) + arbreAncestres.nombreAncestresPaternels(numejro)
    else:
        return verticalDescendant + arbreAncestres.nombreAncestresMaternels(descendant) - arbreAncestres.nombreAncestresMaternels(numejro)
    
############################    
##calcule les positionnements moyennejs
#def calculePositionsMoyennes(positions):
    #positionsMoyennes = {}
    #tousNumejros = list(positions.keys())
    #tousNumejros.sort()
    #tousNumejros.reverse()
    #for numejro in tousNumejros:
        #numejroPehre = numejro*2
        #numejroMehre = numejro*2 +1
        ##si pas un pehre et une mehre, rien de changej en position
        #if numejroPehre not in positionsMoyennes or numejroMehre not in positionsMoyennes:
            #positionsMoyennes[numejro] = positions[numejro]
        #else:
            #rang_h = positions[numejro][0]
            #rang_v_p = positionsMoyennes[numejroPehre][1]
            #rang_v_m = positionsMoyennes[numejroMehre][1]
            #positionsMoyennes[numejro] = (rang_h, float(rang_v_p + rang_v_m) //2)
    #return positionsMoyennes
    
############################    
# calcule les positions tassejes 
DISTANCE_MINI = 3   
def calculePositionsTassejes(positions, arbreAncestres):
    positionsTassejes = positions.copy()
    tousNumerojs = list(positionsTassejes.keys())
    tousNumerojs.sort()
    tousNumerojs.reverse()
    # on commence par les feuilles de l'arbre
    yaChangement = True
    while yaChangement:
        yaChangement = False
        for numejro in tousNumerojs:
            # on ejvalue la distance minimum entre les arbres de ses 2 parents
            numejroPehre = numejro*2
            numejroMehre = numejro*2 +1
            #si pas un pehre et une mehre, rien de changej en position
            if numejroPehre not in positionsTassejes or numejroMehre not in positionsTassejes: continue
            # on trouve les listes des numejros d'ancestres haute et basse
            limitesBassesPehre = arbreAncestres.limitesBasses(numejroPehre)
            limitesHautesMehre = arbreAncestres.limitesHautes(numejroMehre)
            ##prolonge la branche la plus courte de 1 ah l'identique pour ejviter les tassements excessifs
            #if len(limitesBassesPehre) < len(limitesHautesMehre):
                #limitesBassesPehre.append(limitesBassesPehre[-1])
            #if len(limitesHautesMehre) < len(limitesBassesPehre):
                #limitesHautesMehre.append(limitesHautesMehre[-1])
            #le calcul se fait sur deux listes de mesme taille
            indexRange = min(len(limitesBassesPehre), len(limitesHautesMehre))
            if indexRange == 0: continue
            minDistance = 100000
            for index in range(indexRange):
                distance = positionsTassejes[limitesHautesMehre[index]][1] - positionsTassejes[limitesBassesPehre[index]][1]
                minDistance = min(minDistance, distance)
            #si la distance minimum est > DISTANCE_MINI, on tasse
            tassage = minDistance - DISTANCE_MINI
            # si pas de tassage, on centre quand mesme l'individu
            if tassage <= 0: tassage = 0
            else: yaChangement = True
            #remonte l'arbre de la mère de la valeur du tassage
            ascendantsMehre = arbreAncestres.ascendants(numejroMehre)
            for numejroM in ascendantsMehre: 
                (rang_h, rang_v) = positionsTassejes[numejroM]
                positionsTassejes[numejroM] = (rang_h, rang_v - tassage)
            #positionne l'individu pile au milieur entre ses pehre et mehre
            (rang_h, rang_v) = positionsTassejes[numejro]
            rang_v_p = positionsTassejes[numejroPehre][1]
            rang_v_m = positionsTassejes[numejroMehre][1]
            positionsTassejes[numejro] = (rang_h, float(rang_v_p + rang_v_m) /2)
    #si l'arbre est remonte trop haut, descend tout le monde
    min_v = 0
    for (rang_h, rang_v) in positionsTassejes.values(): min_v = min(min_v, rang_v)
    for numejro in positionsTassejes.keys(): 
        (rang_h, rang_v) = positionsTassejes[numejro]
        positionsTassejes[numejro] = (rang_h, rang_v - min_v)
    return positionsTassejes
    
############################
# trouve le maximum horizontal et vertical d'une liste d'ancehtres
def maximumHV(positions):
    maxH = maxV = 0
    for (rang_h, rang_v) in positions.values():
        maxH = max(maxH, rang_h)
        maxV = max(maxV, rang_v)
    return (maxH, maxV)
    
############################
# trace sur la console
def trace(positions):
    #print(positions)
    controsle = []
    for (clef, (h, v)) in positions.items(): controsle.append((v, clef))
    controsle.sort()
    #print (controsle)
    
############################
#creje un PDF
def ejcritPdf(nomFichierSortie, arbreAncestres, ordreNp, positions, max_h, max_v, pos_2, titre, filigrane, image, statistiques):
    # max_h = max horizontal, max_v = max vertical, pos_2 = position verticale du pehre
    #ouvre le PDF
    ancestresPdf = AncestresPdf(nomFichierSortie, max_h +1, max_v, pos_2, filigrane, titre, image, statistiques)
    #dessine tous les ancestres
    manquants = arbreAncestres.lesManquants()
    for numejro, (rang_h, rang_v) in positions.items():
        if numejro in manquants: continue
        ((prejnom, nom), (dateNaissance, lieuNaissance), (dateDejcehs, lieuDejcehs), (dateMariage, lieuMariage)) = arbreAncestres.attributsAncestre(numejro)
        #dessine un ancêtre
        if ordreNp: ancestresPdf.dessineAncestre(rang_h, rang_v, nom, prejnom, dateNaissance, lieuNaissance, dateDejcehs, lieuDejcehs)
        else: ancestresPdf.dessineAncestre(rang_h, rang_v, prejnom, nom, dateNaissance, lieuNaissance, dateDejcehs, lieuDejcehs)
        #dessine le lien vers ses antécédents s'ils existent
        numejroPehre = numejro*2
        numejroMehre = numejro*2 +1
        rang_v_p = rang_v_m = -1
        if numejroPehre in positions and numejroPehre not in manquants: 
            rang_v_p = positions[numejroPehre][1]
        if numejroMehre in positions and numejroMehre not in manquants: 
            rang_v_m = positions[numejroMehre][1]
        ancestresPdf.dessineLien(rang_h, rang_v, rang_v_p, rang_v_m)
        #écrit la date et le lieu du mariage s'ils existent
        if numejro &1 == 0:
            numejroEnfant = numejro //2
            if numejroEnfant in positions:
                rang_v_e = positions[numejroEnfant][1]
                ancestresPdf.ejcritMariage(rang_h, rang_v_e, dateMariage, lieuMariage)
    ancestresPdf.termine()

############################
#crée un PDF imprimable (en pages A4)
def ejcritPdfImprimable(nomsFichiersSortie, arbreAncestres, ordreNp, positions, titre, filigrane, image, statistiques):
    #ouvre le PDF
    ancestresPdfImprimable = AncestresPdfImprimable(nomsFichiersSortie, filigrane, titre, image, statistiques)
    #envoie toutes les infos au gestionnaire de PDF
    for numejro, (rang_h, rang_v) in positions.items():
        ((prejnom, nom), (dateNaissance, lieuNaissance), (dateDejcehs, lieuDejcehs), (dateMariage, lieuMariage)) = arbreAncestres.attributsAncestre(numejro)
        if nom == '' and prejnom == '': continue
        #ajoute un ancêtre
        if ordreNp: ancestresPdfImprimable.ajouteAncestre(numejro, rang_h, rang_v, nom, prejnom, dateNaissance, lieuNaissance, dateDejcehs, lieuDejcehs)
        else: ancestresPdfImprimable.ajouteAncestre(numejro, rang_h, rang_v, prejnom, nom, dateNaissance, lieuNaissance, dateDejcehs, lieuDejcehs)
        #ajoute le lien vers ses antécédents systématiquement 
        numejroPehre = numejro*2
        numejroMehre = numejro*2 +1
        ancestresPdfImprimable.ajouteLien(numejro, numejroPehre, numejroMehre)
        #ajoute la date et le lieu du mariage s'ils existent
        if numejro &1 == 0:
            numejroEnfant = numejro //2
            ancestresPdfImprimable.ajouteMariage(numejro, numejroEnfant, dateMariage, lieuMariage)
    #donne le rang vertical du pehre pour le calcul antitelescopage avec le cartouche
    if len(positions) > 1: pos_2 = positions[2][1]
    else: pos_2 = 0
    ancestresPdfImprimable.vertical2(pos_2)
    #construit le fichier pdf
    ancestresPdfImprimable.termine()
    
    
if __name__ == '__main__':
    main()
     
