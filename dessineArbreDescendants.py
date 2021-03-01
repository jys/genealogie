#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
__author__ = "jys"
__copyright__ = "Copyright (C) 2021 LATEJCON"

import sys
from os import path
from unicodedata import normalize
from ArbreDescendants import ArbreDescendants
from AncestresPdf import AncestresPdf
from AncestresPdfImprimable import AncestresPdfImprimable

def usage():
    script = '$PY/' + path.basename(sys.argv[0])
    print (u"""© l'ATEJCON.  
Crée sur un PDF le tableau de tous les descendants classés par génération
et par ordre de descendant d'un individu-racine spécifié par son identifiant
gramps.
Le PDF est écrit dans rejsultat/<prénom-nom>-descendants-complet.pdf 
ou rejsultat/<prénom-nom>-descendants-partiel.pdf
Les descendants sont identifiés par nom-prénom (NP) (défaut) ou prénom-nom (PN)
Il est possible de limiter le nombre de générations affichées (0 = toutes)
Le critère filtrant éventuel est l'identité des noms des descendants
au nom de l'ancêtre (ce qui limite à la descendance mâle seulement)

usage   : {:s} <base> <individu-racine> [NP|PN] [nbre générations] [<noms identique>]
example : {:s} sage-devoucoux I0141
example : {:s} sage-devoucoux I0141 PN 0 IDENT
""".format(script, script, script))

DIS_V = 2.2

def main():
    try:
        if len(sys.argv) < 3: raise Exception()
        nomBase = sys.argv[1].strip()
        racineIdentifiant = sys.argv[2].strip()
        ordreNp = True
        nbGejnejrations = 0
        ident = False
        if len(sys.argv) > 3:
            arg2 = sys.argv[3].strip().upper()
            if arg2 not in ('NP', 'PN'): raise Exception('NP ou PN')
            ordreNp = arg2 == 'NP'
        if len(sys.argv) > 4: nbGejnejrations = int(sys.argv[4])
        if len(sys.argv) > 5: 
            if sys.argv[5].upper().startswith('ID'): ident = True
            else: raise Exception ('IDENT non reconnu')
        dessineArbre(nomBase, racineIdentifiant, ordreNp, nbGejnejrations, ident)
    except Exception as exc:
        if len(exc.args) == 0: usage()
        else:
            print ("******************************")
            print (exc.args[0])
            print ("******************************")
            raise
        sys.exit()
        
def dessineArbre(nomBase, racineIdentifiant, ordreNp, nbGejnejrations, ident):
    # ejtablit l'arbre 
    arbreDescendants = ArbreDescendants(nomBase)
    arbreDescendants.arbreComplet(racineIdentifiant)
    print('sans filtre : {:4d} descendants sur {:2d} générations'.format(arbreDescendants.nombreTotal(), arbreDescendants.maxGejnejration()))
    if nbGejnejrations != 0:
        arbreDescendants.tailleArbre(nbGejnejrations)
        print('avec limite : {:4d} descendants sur {:2d} générations'.format(arbreDescendants.nombreTotal(), arbreDescendants.maxGejnejration()))
    if ident:
        arbreDescendants.filtreArbre()
        print('avec filtre : {:4d} descendants sur {:2d} générations'.format(arbreDescendants.nombreTotal(), arbreDescendants.maxGejnejration()))

    # ejtablit le nom du fichier pdf 
    numejroRacine = arbreDescendants.numejroRacine()
    ((prejnom, nom), raf, raf) = arbreDescendants.attributsDescendant(numejroRacine)
    extension = (prejnom + nom).replace(' ', '')
    extension = normalize('NFD', extension).encode('ascii','ignore').decode()    #tous les caracteres en ASCII    
    racine = '/'.join(path.dirname(path.abspath(sys.argv[0])).split('/')[:-1])
    if ident: extFiltre = 'partiel'
    else: extFiltre = 'complet'
    nomFichierSortie = racine + '/rejsultat/' + extension +'-descendants-' + extFiltre
    nomFichierSortieC = nomFichierSortie + 'C.pdf'
    nomFichierSortieE = nomFichierSortie + 'E.pdf'
    nomFichierSortieF = nomFichierSortie + 'F.pdf'
    
    # titre, filigrane
    filigrane = (prejnom + nom).upper().replace(' ', '')
    titre = []
    if ident: titre.append(u'Arbre partiel de descendance')
    else: titre.append(u'Arbre de descendance')
    titre.append(u'de '+ prejnom + ' ' + nom)
    latejcon = racine + '/rejsultat/echiquierLatejcon4-150.png'
    
    #le message de statistiques
    (filles, garcons) = arbreDescendants.nombreDescendants()
    statistiques = ['{:d} descendants, {:d} filles et {:d} garçons'.format(filles + garcons, filles, garcons)]
            
    #recupehre tous les numejros d'ancestres 
    tousNumejros = arbreDescendants.tousNumejros()
    tousNumejros.sort()
        
    # calcule tous les positionnements thejoriques
    maxGejnejration = arbreDescendants.maxGejnejration()
    positions = {}
    # on commence par les feuilles de l'arbre
    # la 1ehre gejnejration est 1 (pas 0)
    for gejnejration in reversed(range(1, maxGejnejration+1)):
        arbres = arbreDescendants.listeArbres(gejnejration)
        listeContraints = []
        #print('arbres=', arbres)
        # 1) aligne les parents sur les enfants
        rang_h = maxGejnejration - gejnejration      #le 1er est 0
        #print('rang_h=', rang_h)
        for index in range(len(arbres)):
            arbre = arbres[index]
            enfants = arbreDescendants.listeEnfants(arbre)
            parents = arbreDescendants.listeParents(arbre)
            # diffejrencie les arbres libres (sans enfants) des autres
            if len(enfants) == 0: milieuEnfants = 0
            else : 
                listeContraints.append(index)
                (rang_hp, rang_vp) = positions[enfants[0]]
                (rang_hd, rang_vd) = positions[enfants[-1]]
                milieuEnfants = (rang_vp + rang_vd) /2
            # positionne les parents
            if len(parents) == 0: raise Exception ('INCOHÉRENCE ARBRE 1')
            if len(parents) == 1: 
                positions[parents[0]] = (rang_h, milieuEnfants)
            elif len(parents) == 2:
                positions[parents[0]] = (rang_h, milieuEnfants -DIS_V/2)
                positions[parents[1]] = (rang_h, milieuEnfants +DIS_V/2)
            elif len(parents) == 3:
                positions[parents[0]] = (rang_h, milieuEnfants -DIS_V)
                positions[parents[1]] = (rang_h, milieuEnfants)
                positions[parents[2]] = (rang_h, milieuEnfants +DIS_V)
            elif len(parents) == 4:
                positions[parents[0]] = (rang_h, milieuEnfants -DIS_V-DIS_V/2)
                positions[parents[1]] = (rang_h, milieuEnfants -DIS_V/2)
                positions[parents[2]] = (rang_h, milieuEnfants +DIS_V/2)
                positions[parents[3]] = (rang_h, milieuEnfants +DIS_V+DIS_V/2)
            else: raise Exception ('INCOHÉRENCE ARBRE 2')
        
        # 2) positionne les arbres les uns / autres
        nbGejnejrations = maxGejnejration - gejnejration + 1
        maxisPrejcedents = [0 for x in range(nbGejnejrations)]
        #print('nbGejnejrations=', nbGejnejrations)
        for arbre in arbres:
            #print('maxisPrejcedents=', maxisPrejcedents)
            minis, maxis = arbreDescendants.listeMinisMaxis(arbre)
            #print('minis=', minis, '  maxis=', maxis)
            # calcule le dejcalage requis 
            dejcalageRequis = 0
            for index in range(len(minis)):
                (rang_h, rang_v) = positions[minis[index]]
                dejcalageRequis = max(dejcalageRequis, maxisPrejcedents[index] - rang_v + DIS_V)
            # procehde au dejcalage 
            for numejro in arbre: 
                (rang_h, rang_v) = positions[numejro]
                positions[numejro] = (rang_h, rang_v + dejcalageRequis)
            # mejmorise les maxis
            for index in range(len(maxis)): 
                (rang_h, rang_v) = positions[maxis[index]]
                maxisPrejcedents[index] = rang_v
                
        # 3) tasse le haut ejventuellement
        # aucun n'est contraint (cas de tous feuilles), raf
        if len(listeContraints) != 0:
            # init avec l'index virtuel -1 et sa position
            index1erContraint = listeContraints[0]
            numejro1erContraint = arbres[index1erContraint][0]
            (rang_hh, rang_v) = positions[numejro1erContraint]
            indexPrejcejdent = -1
            rang_vv = rang_v - (index1erContraint - indexPrejcejdent) *DIS_V
            for indexContraint in listeContraints:
                nbEspacesLibres = indexContraint - indexPrejcejdent
                arbreContraint = arbres[indexContraint]
                (raf, rang_v) = positions[arbreContraint[0]]
                increjment = (rang_v - rang_vv) / (indexContraint - indexPrejcejdent)
                for index in range(indexPrejcejdent+1, indexContraint):
                    rang_vv += increjment
                    positions[arbres[index][0]] = (rang_hh, rang_vv)
                for numejro in arbreContraint: 
                    (rang_h, rang_v) = positions[numejro]
                    if rang_h != rang_hh: break
                    rang_vv = rang_v
                indexPrejcejdent = indexContraint
                    
    trace(positions)
    (max_h, max_v) = maximumHV(positions)
    #print('max_h=', max_h, 'max_v=', max_v)
    ejcritPdf(nomFichierSortieC, arbreDescendants, ordreNp, positions, max_h, max_v, 2.0, titre, filigrane, latejcon, statistiques)
                      
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
def ejcritPdf(nomFichierSortie, arbreDescendants, ordreNp, positions, max_h, max_v, pos_2, titre, filigrane, image, statistiques):
    # max_h = max horizontal, max_v = max vertical, pos_2 = position verticale du pehre
    #ouvre le PDF
    ancestresPdf = AncestresPdf(nomFichierSortie, max_h +1, max_v, pos_2, filigrane, titre, image, statistiques, True)

    # dessine les liens de couples et les date et lieu de mariage
    for (mari, femme) in arbreDescendants.listeCouples():
        (rang_h_m, rang_v_m) = positions[mari]
        (rang_h_f, rang_v_f) = positions[femme]
        if rang_h_m != rang_h_f: raise Exception ('INCOHÉRENCE POSITIONS 1')
        ancestresPdf.dessineLiensGauches(rang_h_m, [rang_v_m, rang_v_f])
        
        if len(mari) == 3: 
            (dateMariage, lieuMariage) = arbreDescendants.mariageDescendant(mari)
            rang_v_e = rang_v_m + DIS_V/2
        else: 
            (dateMariage, lieuMariage) = arbreDescendants.mariageDescendant(femme)
            rang_v_e = rang_v_f - DIS_V/2
            
        #rang_v_e = (rang_v_m + rang_v_f) /2
        ancestresPdf.ejcritMariage(rang_h_m, rang_v_e, dateMariage, lieuMariage)
        
    #dessine tous les ancestres
    for numejro, (rang_h, rang_v) in positions.items():
        ((prejnom, nom), (dateNaissance, lieuNaissance), (dateDejcehs, lieuDejcehs)) = arbreDescendants.attributsDescendant(numejro)
        #dessine un ancêtre
        if ordreNp: nomPrejnom = nom + ' ' + prejnom
        else: nomPrejnom = prejnom + ' ' + nom
        # les conjoints en gris
        enGris = len(numejro) == 3
        ancestresPdf.dessineAncestre(rang_h, rang_v, nomPrejnom, dateNaissance, lieuNaissance, dateDejcehs, lieuDejcehs, enGris)
    # dessine les liens entre frehres et soeurs
    for fratrie in arbreDescendants.listeFratries():
        rang_h_ref = -1
        rangs_v = []
        for frehreOuSoeur in fratrie:
            (rang_h, rang_v) = positions[frehreOuSoeur]
            if rang_h_ref == -1: rang_h_ref = rang_h
            if rang_h != rang_h_ref: raise Exception ('INCOHÉRENCE POSITIONS 2')
            rangs_v.append(rang_v)
        ancestresPdf.dessineLiensDroits(rang_h_ref, rangs_v)
        
        #dessine le lien vers ses antécédents s'ils existent
        #numejroPehre = numejro*2
        #numejroMehre = numejro*2 +1
        #rang_v_p = rang_v_m = -1
        #if numejroPehre in positions and numejroPehre not in manquants: 
            #rang_v_p = positions[numejroPehre][1]
        #if numejroMehre in positions and numejroMehre not in manquants: 
            #rang_v_m = positions[numejroMehre][1]
        #ancestresPdf.dessineLien(rang_h, rang_v, rang_v_p, rang_v_m)
        ##écrit la date et le lieu du mariage s'ils existent
        #if numejro &1 == 0:
            #numejroEnfant = numejro //2
            #if numejroEnfant in positions:
                #rang_v_e = positions[numejroEnfant][1]
                #ancestresPdf.ejcritMariage(rang_h, rang_v_e, dateMariage, lieuMariage)
    ancestresPdf.termine()
    
    
if __name__ == '__main__':
    main()
     
