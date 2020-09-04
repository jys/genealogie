#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
__author__ = "jys"
__copyright__ = "Copyright (C) 2014 LATEJCON"

import sys
from os import path
from unicodedata import normalize
from copy import deepcopy
from Ancestres import Ancestres
from AncestresPdf import AncestresPdf
from AncestresPdfImprimable import AncestresPdfImprimable

def usage():
    script = '$PY/' + path.basename(sys.argv[0])
    print (u"""© l'ATEJCON.  
Crée sur un PDF le tableau de tous les ancêtres classés par génération
et par ordre d'ancêtres.
Le PDF est écrit dans rejsultat/<prénom-nom>-ancestres-complet.pdf 
ou rejsultat/<prénom-nom>-ancestres-partiel.pdf
Les ancestres sont identifiés par nom-prénom (NP) (défaut) ou prénom-nom (PN)
Il est possible de limiter le nombre de générations affichées (0 = toutes)
Il est possible de filtrer les ancestres en fournissant les numéros d'ancestres
particuliers (voir "Géométrie pour la présentation des arbres généalogiques"
LAT2013.JYS.432 rev B) par exemple "1" ou "2", "1,3" ou "1,6" ou "2,3"ou "2,6",
"1,3,5", "1,3,5,7", "1,3,5,7,9", etc.

usage   : {:s} <rapport texte HTML Gramps> [NP|PN] [nbre générations] [filtre]
example : {:s} det_ancestor_report.html
example : {:s} det_ancestor_report.html PN 0 1,3
""".format(script, script, script))

def main():
    try:
        if len(sys.argv) < 2 : raise Exception()
        nomRapportGramps = sys.argv[1]
        ordreNp = True
        nbGejnejrations = 0
        filtre = []
        if len(sys.argv) > 2:
            arg2 = sys.argv[2].upper()
            if arg2 not in ('NP', 'PN'): raise Exception('NP ou PN')
            ordreNp = arg2 == 'NP'
        if len(sys.argv) > 3: nbGejnejrations = int(sys.argv[3])
        if len(sys.argv) > 4:
            filtreStr = sys.argv[4]
            for nb in filtreStr.split(','): filtre.append(int(nb))        
        tousAncestres(nomRapportGramps, ordreNp, nbGejnejrations, filtre)
    except Exception as exc:
        if len(exc.args) == 0: usage()
        else:
            print ("******************************")
            print (exc.args[0])
            print ("******************************")
            raise
        sys.exit()
        
def tousAncestres(nomRapportGramps, ordreNp, nbGejnejrations, filtre):
    #extrait tous les ancestres
    ancestres = Ancestres(nomRapportGramps, filtre, nbGejnejrations)
    print ('{:d} ancêtres pris en compte'.format(ancestres.nombreTotal()))
    
    #recupehre la racine de l'arbre pour le nom et prejnom de la racine
    (nom, prejnom, dateNaissance, lieuNaissance, dateDejcehs, lieuDejcehs, dateMariage, lieuMariage) = ancestres.attributs(1)
    extension = (prejnom + nom).replace(' ', '')
    extension = normalize('NFD', extension).encode('ascii','ignore').decode()    #passe tous les caracteres en ASCII
    #nom du fichier de sortie. On prend le chemin moins la fin 
    racine = '/'.join(path.dirname(path.abspath(sys.argv[0])).split('/')[:-1])
    if len(filtre) == 0: extFiltre = 'complet'
    else: extFiltre = 'partiel'
    nomFichierSortie = racine + '/rejsultat/' + extension +'-ancestres-' + extFiltre
    nomFichierSortieA = nomFichierSortie + 'A.pdf'
    nomFichierSortieB = nomFichierSortie + 'B.pdf'
    nomFichierSortieC = nomFichierSortie + 'C.pdf'
    nomFichierSortieD = nomFichierSortie + 'D.pdf'
    nomFichierSortieE = nomFichierSortie + 'E.pdf'
    nomFichierSortieF = nomFichierSortie + 'F.pdf'
    #titre, filigrane
    filigrane = (prejnom + nom).upper().replace(' ', '')
    titre = prejnom + ' ' + nom
    #latecon = '%s/rejsultat/echiquierLatejcon4-150T.png'%(racine)   #la transparence ne fonctionne pas
    latecon = racine + '/rejsultat/echiquierLatejcon4-150.png'
    #le message de statistiques
    statistiques = ['{:4d} ancêtres'.format(ancestres.nombreTotal() -1)]  #on ne compte pas la racine
    nombreParGejnejration = list(ancestres.rejpartitionParGejnejration().items())
    nombreParGejnejration.sort()
    for (gejnejration, nombre) in nombreParGejnejration[1:]: 
        if len(filtre) == 0:
            statistiques.append('{:4d} en génération {:3d}  : {:4d}%%'.format(nombre, 1-gejnejration, round(100.0*nombre//(2**(gejnejration-1)))))
        else:
            statistiques.append('{:4d} en génération {:3d}'.format(nombre, 1-gejnejration))

    #recupehre tous les ancestres et y ajoute les manquants
    tousIdentifiants = ancestres.tousIdentifiants()
    tousIdentifiants.extend(ancestres.lesManquants())
    tousIdentifiants.sort()
      
    #1) calcule tous les positionnements théoriques
    positions = {}
    for identifiant in tousIdentifiants:
        rang_h = ancestres.gejnejration(identifiant)       #le 1er est 0
        rang_v = vertical(identifiant, ancestres) -1     #le 1er est 0
        positions[identifiant] = (rang_h, rang_v)
    trace(positions)
    #trouve les maximums pour la taille de la page et la position verticale du pehre (telescopage avec le cartouche)
    (max_h, max_v) = maximumHV(positions)
    pos_2 = positions[2][1]       #position vertical du pehre (pour calcul anti-carambolage avec le cartouche)
    #ejcrit le PDF des ancestres version "normale"
    ejcritPdf(nomFichierSortieA, ancestres, ordreNp, positions, max_h, max_v, pos_2, titre, filigrane, latecon, statistiques)
    
    #2) calcule les positionnements moyennés
    positionsMoyennes = calculePositionsMoyennes(positions)
    #trouve les maximums pour la taille de la page et la position verticale du pehre (telescopage avec le cartouche)
    (max_h, max_v) = maximumHV(positionsMoyennes)
    pos_2 = positionsMoyennes[2][1]        #position vertical du pehre (pour calcul anti-carambolage avec le cartouche)
    #ejcrit le PDF des ancestres version "positionnements moyennés"
    ejcritPdf(nomFichierSortieB, ancestres, ordreNp, positionsMoyennes, max_h, max_v, pos_2, titre, filigrane, latecon, statistiques)
    
    #3) calcule des positionnements tassés
    positionsTassejes = calculePositionsTassejes(positions, ancestres)
    #trouve les maximums pour la taille de la page et la position verticale du pehre (telescopage avec le cartouche)
    (max_h, max_v) = maximumHV(positionsTassejes)
    pos_2 = positionsTassejes[2][1]        #position vertical du pehre (pour calcul anti-carambolage avec le cartouche)
    trace(positionsTassejes)
    #ejcrit le PDF des ancestres version "positionnements moyennés"
    ejcritPdf(nomFichierSortieC, ancestres, ordreNp, positionsTassejes, max_h, max_v, pos_2, titre, filigrane, latecon, statistiques)
    ejcritPdfImprimable((nomFichierSortieE, nomFichierSortieF), ancestres, ordreNp, positionsTassejes, titre, filigrane, latecon, statistiques)

    #4) calcule les positionnements tassés moyennés
    positionsTassejesMoyennes = calculePositionsMoyennes(positionsTassejes)
    #trouve les maximums pour la taille de la page et la position verticale du pehre (telescopage avec le cartouche)
    (max_h, max_v) = maximumHV(positionsTassejesMoyennes)
    pos_2 = positionsTassejesMoyennes[2][1]        #position vertical du pehre (pour calcul anti-carambolage avec le cartouche)
    #ejcrit le PDF des ancestres version "positionnements tassés moyennés"
    ejcritPdf(nomFichierSortieD, ancestres, ordreNp, positionsTassejesMoyennes, max_h, max_v, pos_2, titre, filigrane, latecon, statistiques)
    #ejcrit le PDF imprimable
    ejcritPdfImprimable((nomFichierSortieE, nomFichierSortieF), ancestres, ordreNp, positionsTassejesMoyennes, titre, filigrane, latecon, statistiques)

    # trace sur la console
def trace(positions):
    #print(positions)
    controsle = []
    for (clef, (h, v)) in positions.items(): controsle.append((v, clef))
    controsle.sort()
    print (controsle)

#calcule les positionnements moyennés
def calculePositionsMoyennes(positions):
    positionsMoyennes = {}
    tousIdentifiants = list(positions.keys())
    tousIdentifiants.sort()
    tousIdentifiants.reverse()
    for identifiant in tousIdentifiants:
        identifiantPehre = identifiant*2
        identifiantMehre = identifiant*2 +1
        #si pas un père et une mère, rien de changé en position
        if identifiantPehre not in positionsMoyennes or identifiantMehre not in positionsMoyennes:
            positionsMoyennes[identifiant] = positions[identifiant]
        else:
            rang_h = positions[identifiant][0]
            rang_v_p = positionsMoyennes[identifiantPehre][1]
            rang_v_m = positionsMoyennes[identifiantMehre][1]
            positionsMoyennes[identifiant] = (rang_h, float(rang_v_p + rang_v_m) //2)
    return positionsMoyennes
    
DISTANCE_MINI = 3   
# calcule les positions tassejes 
def calculePositionsTassejes(positions, ancestres):
    positionsTassejes = deepcopy(positions)
    tousIdentifiants = list(positionsTassejes.keys())
    tousIdentifiants.sort()
    tousIdentifiants.reverse()
    #on commence par les feuilles de l'arbre
    yaChangement = True
    while yaChangement:
        print('***while yaChangement')
        yaChangement = False
        for identifiant in tousIdentifiants:
            #on évalue la distance minimum entre les arbres de ses 2 parents
            identifiantPehre = identifiant*2
            identifiantMehre = identifiant*2 +1
            #si pas un père et une mère, rien de changé en position
            if identifiantPehre not in positionsTassejes or identifiantMehre not in positionsTassejes: continue
            #on trouve les listes des identifiants d'ancehtres haute et basse
            limitesBassesPehre = ancestres.limitesBasses(identifiantPehre)
            limitesHautesMehre = ancestres.limitesHautes(identifiantMehre)
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
            ascendantsMehre = ancestres.ascendants(identifiantMehre)
            for identifiantM in ascendantsMehre: 
                (rang_h, rang_v) = positionsTassejes[identifiantM]
                positionsTassejes[identifiantM] = (rang_h, rang_v - tassage)
            #positionne l'individu pile au milieur entre ses pehre et mehre
            (rang_h, rang_v) = positionsTassejes[identifiant]
            rang_v_p = positionsTassejes[identifiantPehre][1]
            rang_v_m = positionsTassejes[identifiantMehre][1]
            positionsTassejes[identifiant] = (rang_h, float(rang_v_p + rang_v_m) /2)
    #si l'arbre est remonte trop haut, descend tout le monde
    min_v = 0
    for (rang_h, rang_v) in positionsTassejes.values(): min_v = min(min_v, rang_v)
    for identifiant in positionsTassejes.keys(): 
        (rang_h, rang_v) = positionsTassejes[identifiant]
        positionsTassejes[identifiant] = (rang_h, rang_v - min_v)
    return positionsTassejes
    
#crée un PDF
def ejcritPdf(nomFichierSortie, ancestres, ordreNp, positions, max_h, max_v, pos_2, titre, filigrane, image, statistiques):
    # max_h = max horizontal, max_v = max vertical, pos_2 = position verticale du pehre
    #ouvre le PDF
    ancestresPdf = AncestresPdf(nomFichierSortie, max_h +1, max_v, pos_2, filigrane, titre, image, statistiques)
    #dessine tous les ancestres
    manquants = ancestres.lesManquants()
    for identifiant, (rang_h, rang_v) in positions.items():
        if identifiant in manquants: continue
        (nom, prejnom, dateNaissance, lieuNaissance, dateDejcehs, lieuDejcehs, dateMariage, lieuMariage) = ancestres.attributs(identifiant)
        #dessine un ancêtre
        if ordreNp: ancestresPdf.dessineAncestre(rang_h, rang_v, nom, prejnom, dateNaissance, lieuNaissance, dateDejcehs, lieuDejcehs)
        else: ancestresPdf.dessineAncestre(rang_h, rang_v, prejnom, nom, dateNaissance, lieuNaissance, dateDejcehs, lieuDejcehs)
        #dessine le lien vers ses antécédents s'ils existent
        identifiantPehre = identifiant*2
        identifiantMehre = identifiant*2 +1
        rang_v_p = rang_v_m = -1
        if identifiantPehre in positions and identifiantPehre not in manquants: 
            rang_v_p = positions[identifiantPehre][1]
        if identifiantMehre in positions and identifiantMehre not in manquants: 
            rang_v_m = positions[identifiantMehre][1]
        ancestresPdf.dessineLien(rang_h, rang_v, rang_v_p, rang_v_m)
        #écrit la date et le lieu du mariage s'ils existent
        if identifiant &1 == 0:
            identifiantEnfant = identifiant //2
            if identifiantEnfant in positions:
                rang_v_e = positions[identifiantEnfant][1]
                ancestresPdf.ejcritMariage(rang_h, rang_v_e, dateMariage, lieuMariage)
    ancestresPdf.termine()
    
#crée un PDF imprimable (en pages A4)
def ejcritPdfImprimable(nomsFichiersSortie, ancestres, ordreNp, positions, titre, filigrane, image, statistiques):
    #ouvre le PDF
    ancestresPdfImprimable = AncestresPdfImprimable(nomsFichiersSortie, filigrane, titre, image, statistiques)
    #envoie toutes les infos au gestionnaire de PDF
    for identifiant, (rang_h, rang_v) in positions.items():
        (nom, prejnom, dateNaissance, lieuNaissance, dateDejcehs, lieuDejcehs, dateMariage, lieuMariage) = ancestres.attributs(identifiant)
        if nom == '' and prejnom == '': continue
        #ajoute un ancêtre
        if ordreNp: ancestresPdfImprimable.ajouteAncestre(identifiant, rang_h, rang_v, nom, prejnom, dateNaissance, lieuNaissance, dateDejcehs, lieuDejcehs)
        else: ancestresPdfImprimable.ajouteAncestre(identifiant, rang_h, rang_v, prejnom, nom, dateNaissance, lieuNaissance, dateDejcehs, lieuDejcehs)
        #ajoute le lien vers ses antécédents systématiquement 
        identifiantPehre = identifiant*2
        identifiantMehre = identifiant*2 +1
        ancestresPdfImprimable.ajouteLien(identifiant, identifiantPehre, identifiantMehre)
        #ajoute la date et le lieu du mariage s'ils existent
        if identifiant &1 == 0:
            identifiantEnfant = identifiant //2
            ancestresPdfImprimable.ajouteMariage(identifiant, identifiantEnfant, dateMariage, lieuMariage)
    #donne le rang vertical du pehre pour le calcul antitelescopage avec le cartouche
    ancestresPdfImprimable.vertical2(positions[2][1])
    #construit le fichier pdf
    ancestresPdfImprimable.termine()    

#trouve le rang vertical "normal" en fonction de l'identifiant
def vertical(identifiant, ancestres):
    #si l'identifiant est 1 sort les nombre d'ascendants paternels +1
    if identifiant == 1: return ancestres.nombreAncestresPaternels(1) +1
    #calcule la position verticale de son descendant
    descendant = identifiant //2
    verticalDescendant = vertical(descendant, ancestres)
    #le calcul de la position dépend si c'est un garçon ou une fille
    if identifiant &1 == 0:
        return verticalDescendant - ancestres.nombreAncestresPaternels(descendant) + ancestres.nombreAncestresPaternels(identifiant)
    else:
        return verticalDescendant + ancestres.nombreAncestresMaternels(descendant) - ancestres.nombreAncestresMaternels(identifiant)
    
#trouve le maximum horizontal et vertical d'une liste d'ancehtres
def maximumHV(positions):
    maxH = maxV = 0
    for (rang_h, rang_v) in positions.values():
        maxH = max(maxH, rang_h)
        maxV = max(maxV, rang_v)
    return (maxH, maxV)
    
         
if __name__ == '__main__':
    main()
    

