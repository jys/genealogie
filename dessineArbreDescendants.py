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
Par défaut les ancêtres sont dessinés au format court (C). On peut les 
dessiner au format long (L).
Les descendants sont identifiés par nom-prénom (NP) (défaut) ou prénom-nom (PN)
Il est possible de limiter le nombre de générations affichées (0 = toutes)
Le critère filtrant éventuel est l'identité des noms des descendants
au nom de l'ancêtre (ce qui limite à la descendance mâle seulement)
ou une liste d'identifiants de descendants (voir chercheIndividus.py)

usage   : {:s} <base> <individu-racine> [L|C] [NP|PN] [nbre générations] [<filtres>]
example : {:s} sage-devoucoux I0141
example : {:s} sage-devoucoux I0141 L PN 0 IDENT
example : {:s} sage-devoucoux I0141 L PN 0 I0000,I2181
""".format(script, script, script, script))

DIS_V = 2.2

def main():
    try:
        if len(sys.argv) < 3: raise Exception()
        nomBase = sys.argv[1].strip()
        racineIdentifiant = sys.argv[2].strip()
        formatLong = False
        ordreNp = True
        nbGejnejrations = 0
        ident = False
        idsFiltrants = []
        if len(sys.argv) > 3:
            arg = sys.argv[3].strip().upper()
            if arg not in ('L', 'C'): raise Exception('L ou C')
            formatLong = arg == 'L'
        if len(sys.argv) > 4:
            arg = sys.argv[4].strip().upper()
            if arg not in ('NP', 'PN'): raise Exception('NP ou PN')
            ordreNp = arg == 'NP'
        if len(sys.argv) > 5: nbGejnejrations = int(sys.argv[5])
        if len(sys.argv) > 6: 
            #if sys.argv[6].upper().startswith('ID'): ident = True
            #else: raise Exception ('IDENT non reconnu')
            ident = sys.argv[6].upper().startswith('ID')
            if not ident: idsFiltrants = sys.argv[6].strip().split(',')
            
        dessineArbre(nomBase, racineIdentifiant, formatLong, ordreNp, nbGejnejrations, ident, idsFiltrants)
    except Exception as exc:
        if len(exc.args) == 0: 
            usage()
        else:
            print ("******************************")
            print (exc.args[0])
            print ("******************************")
            raise
        sys.exit()
        
def dessineArbre(nomBase, racineIdentifiant, formatLong, ordreNp, nbGejnejrations, ident, idsFiltrants):
    # ejtablit l'arbre 
    arbreDescendants = ArbreDescendants(nomBase)
    # construit l'arbre complet des descendants de l'individu spejcifiej avec les numejros normalisejs
    arbreDescendants.arbreComplet(racineIdentifiant)
    print('sans filtre : {:4d} descendants sur {:2d} générations'.format(arbreDescendants.nombreTotal(), arbreDescendants.maxGejnejration()))
    if nbGejnejrations != 0:
        # restreint l'arbre par le nombre de gejnejrations max
        arbreDescendants.tailleArbre(nbGejnejrations)
        print('avec limite : {:4d} descendants sur {:2d} générations'.format(arbreDescendants.nombreTotal(), arbreDescendants.maxGejnejration()))
    if ident:
        # filtre l'arbre, ne garde que les descendants qui ont le mesme nom que la racine et leur conjoint
        arbreDescendants.filtreArbre()
        print('avec filtre : {:4d} descendants sur {:2d} générations'.format(arbreDescendants.nombreTotal(), arbreDescendants.maxGejnejration()))
    if len(idsFiltrants) != 0:
        # filtre l'arbre, ne garde que les descendants qui aboutissent aux ejlejments filtrants 
        arbreDescendants.filtreIdsArbre(idsFiltrants)
        print('avec filtre : {:4d} descendants sur {:2d} générations'.format(arbreDescendants.nombreTotal(), arbreDescendants.maxGejnejration()))
        
    # partiel ou complet
    partiel = ident or nbGejnejrations != 0 or len(idsFiltrants) != 0
    
    # ejtablit le nom du fichier pdf 
    numejroRacine = arbreDescendants.numejroRacine()
    ((prejnom, nom), raf, raf) = arbreDescendants.attributsDescendant(numejroRacine)
    extension = (prejnom + nom).replace(' ', '')
    extension = normalize('NFD', extension).encode('ascii','ignore').decode()    #tous les caracteres en ASCII    
    racine = '/'.join(path.dirname(path.abspath(sys.argv[0])).split('/')[:-1])
    if partiel: extFiltre = 'partiel'
    else: extFiltre = 'complet'
    nomFichierSortie = racine + '/rejsultat/' + extension +'-descendants-' + extFiltre
    nomFichierSortieC = nomFichierSortie + 'C.pdf'
    nomFichierSortieE = nomFichierSortie + 'E.pdf'
    nomFichierSortieF = nomFichierSortie + 'F.pdf'
    
    # titre, filigrane
    filigrane = (prejnom + nom).upper().replace(' ', '')
    titre = []
    if partiel: titre.append(u'Arbre partiel de descendance')
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
        # tous les arbres pour une gejnejration donneje
        arbres = arbreDescendants.listeArbres(gejnejration)
        listeContraints = []
        #print('gejnejration=', gejnejration, '   len(arbres)=', len(arbres))
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
            # la liste des maximum et minimum sur chaque gejnejration de l'arbre
            minis, maxis = arbreDescendants.listeMinisMaxis(arbre)
            #print('minis=', minis, '  maxis=', maxis)
            # calcule le dejcalage requis 
            dejcalageRequis = 0
            for index in range(len(minis)):
                (rang_h, rang_v) = positions[minis[index]]
                if index == 0: dejcalageRequis = max(dejcalageRequis, maxisPrejcedents[index] - rang_v + DIS_V)
                else: dejcalageRequis = max(dejcalageRequis, maxisPrejcedents[index] - rang_v + DIS_V*1.5)
            # procehde au dejcalage 
            for numejro in arbre: 
                (rang_h, rang_v) = positions[numejro]
                positions[numejro] = (rang_h, rang_v + dejcalageRequis)
            # mejmorise les maxis
            for index in range(len(maxis)): 
                (rang_h, rang_v) = positions[maxis[index]]
                maxisPrejcedents[index] = rang_v
                
        #print('listeContraints=', listeContraints)
        # 3) rejpartit harmonieusement les arbres non contraints dans l'espace entre les contraints
        # explication : les arbres non contraints (ceux qui n'ont pas de descendants) sont positionnejs
        # au plus haut, ce qui est disgrascieux. Il faut les rejpartir harmonieusement dans l'espace
        # non contraint entre deux contraints ou les mettre au plus bas s'ils sont les premiers en haut.
        # s'ils sont les derniers en bas, ils sont dejjah bien positionnejs.
        # si aucun n'est contraint (cas de tous feuilles), c'est dejjah bon, raf
        #if len(listeContraints) != 0:
        if False:
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
                    #print('arbres[index][0]=', arbres[index][0])
                    rang_vv += increjment
                    #print('positions[arbres[index][0]]=', positions[arbres[index][0]], ' => ', (rang_hh, rang_vv))
                    positions[arbres[index][0]] = (rang_hh, rang_vv)
                for numejro in arbreContraint: 
                    (rang_h, rang_v) = positions[numejro]
                    if rang_h != rang_hh: break
                    rang_vv = rang_v
                indexPrejcejdent = indexContraint
                    
    trace(positions)
    (max_h, max_v) = maximumHV(positions)
    #print('max_h=', max_h, 'max_v=', max_v)
    ejcritPdf(nomFichierSortieC, arbreDescendants, formatLong, ordreNp, positions, max_h, max_v, 2.0, titre, filigrane, latejcon, statistiques)
    ejcritPdfImprimable((nomFichierSortieE, nomFichierSortieF), arbreDescendants, formatLong, ordreNp, positions, titre, filigrane, latejcon, statistiques)         
                          
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
def ejcritPdf(nomFichierSortie, arbreDescendants, formatLong, ordreNp, positions, max_h, max_v, pos_2, titre, filigrane, image, statistiques):
    # max_h = max horizontal, max_v = max vertical, pos_2 = position verticale du pehre
    #ouvre le PDF
    ancestresPdf = AncestresPdf(nomFichierSortie, max_h +1, max_v, pos_2, filigrane, titre, image, statistiques, formatLong)

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
        #les conjoints en gris
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
        
    ancestresPdf.termine()
    
############################
#crée un PDF imprimable (en pages A4)
def ejcritPdfImprimable(nomsFichiersSortie, arbreDescendants, formatLong, ordreNp, positions, titre, filigrane, image, statistiques):
    #ouvre le PDF
    ancestresPdfImprimable = AncestresPdfImprimable(nomsFichiersSortie, filigrane, titre, image, statistiques, formatLong)
    # envoie toutes les infos sur les descendants au gestionnaire de PDF
    for numejro, (rang_h, rang_v) in positions.items():
        ((prejnom, nom), (dateNaissance, lieuNaissance), (dateDejcehs, lieuDejcehs)) = arbreDescendants.attributsDescendant(numejro)
        if nom == '' and prejnom == '': continue
        #ajoute un descendant
        if ordreNp: nomPrejnom = nom + ' ' + prejnom
        else: nomPrejnom = prejnom + ' ' + nom
        # les conjoints en gris
        enGris = len(numejro) == 3
        ancestresPdfImprimable.ajouteAncestre(numejro, rang_h, rang_v, nomPrejnom, dateNaissance, lieuNaissance, dateDejcehs, lieuDejcehs, enGris)
        
    # envoie toutes les infos sur les liens gauches et les mariages au gestionnaire de PDF
    for (mari, femme) in arbreDescendants.listeCouples():
        # pour les liens gauches
        ancestresPdfImprimable.ajouteLiensGauches((mari, femme))
        # pour les mariages
        (rang_h_m, rang_v_m) = positions[mari]
        (rang_h_f, rang_v_f) = positions[femme]
        if rang_h_m != rang_h_f: raise Exception ('INCOHÉRENCE POSITIONS 1')
        if len(mari) == 3: 
            (dateMariage, lieuMariage) = arbreDescendants.mariageDescendant(mari)
            rang_v_e = rang_v_m + DIS_V /4
        else: 
            (dateMariage, lieuMariage) = arbreDescendants.mariageDescendant(femme)
            rang_v_e = rang_v_f - DIS_V + DIS_V /4
        ancestresPdfImprimable.ajouteMariage2(rang_h_m, rang_v_e, dateMariage, lieuMariage)    
        
    # envoie toutes les infos sur les liens droits au gestionnaire de PDF
    for fratrie in arbreDescendants.listeFratries():
        ancestresPdfImprimable.ajouteLiensDroits(fratrie)
        
    pos_2 = 0
    ancestresPdfImprimable.vertical2(pos_2)
    #construit le fichier pdf
    ancestresPdfImprimable.termine()
    
    
if __name__ == '__main__':
    main()
     
