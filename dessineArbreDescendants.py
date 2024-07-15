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
Il est possible de limiter le nombre de générations affichées (0 = toutes, 
>0 = en partant de la racine, <0 = en partant des feuilles pour débogue)
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
        if len(sys.argv) < 3: raise Exception('USAGE')
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
            
        dessineArbreDescendant(nomBase, racineIdentifiant, formatLong, ordreNp, nbGejnejrations, ident, idsFiltrants)
    except Exception as exc:
        if len(exc.args) == 1 and exc.args[0] == 'USAGE': 
            usage()
        else:
            print ("******************************")
            print (exc.args[0])
            print ("******************************")
            raise
        sys.exit()
        
class dessineArbreDescendant:
    def __init__(self, nomBase, racineIdentifiant, formatLong, ordreNp, nbGejnejrations, ident, idsFiltrants):
       # ejtablit l'arbre 
        self.arbreDescendants = ArbreDescendants(nomBase)
        # construit l'arbre complet des descendants de l'individu spejcifiej avec les numejros normalisejs
        self.arbreDescendants.arbreComplet(racineIdentifiant)
        # rejcupehre les identifiants de la racine avant les filtres (qui peuvent ejventuellement l'effacer)
        numejroRacine = self.arbreDescendants.numejroRacine()
        ((prejnom, nom), raf, raf) = self.arbreDescendants.attributsDescendant(numejroRacine)
        print('sans filtre : {:4d} descendants sur {:2d} générations'.format(self.arbreDescendants.nombreTotal(), self.arbreDescendants.maxGejnejration()))
        if ident:
            # filtre l'arbre, ne garde que les descendants qui ont le mesme nom que la racine et leur conjoint
            self.arbreDescendants.filtreArbre()
            print('avec filtre : {:4d} descendants sur {:2d} générations'.format(self.arbreDescendants.nombreTotal(), self.arbreDescendants.maxGejnejration()))
        if len(idsFiltrants) != 0:
            # filtre l'arbre, ne garde que les descendants qui aboutissent aux ejlejments filtrants 
            self.arbreDescendants.filtreIdsArbre(idsFiltrants)
            print('avec filtre : {:4d} descendants sur {:2d} générations'.format(self.arbreDescendants.nombreTotal(), self.arbreDescendants.maxGejnejration()))
        if nbGejnejrations != 0:
            # restreint l'arbre par le nombre de gejnejrations max
            self.arbreDescendants.tailleArbre(nbGejnejrations)
            (gejnMin, gejnMax) = self.arbreDescendants.plageGejnejrations()
            print('avec limite : {:4d} descendants sur {:2d} générations'.format(self.arbreDescendants.nombreTotal(), gejnMax - gejnMin +1))
            
        # partiel ou complet
        partiel = ident or nbGejnejrations != 0 or len(idsFiltrants) != 0
        
        # ejtablit le nom du fichier pdf 
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
        (filles, garcons) = self.arbreDescendants.nombreDescendants()
        statistiques = [f'{filles + garcons} descendants, {filles} filles et {garcons} garçons']
            
        # calcule tous les positionnements thejoriques
        # avec les possibilitejs de filtres de nombre de gejnejrations en nejgatif ah des fins 
        # de debogue, il est possible de ne pas avoir ah reprejsenter la racine de l'arbre
        (gejnMin, gejnMax) = self.arbreDescendants.plageGejnejrations()
        self.positions = {}
        # on commence par les feuilles de l'arbre
        # la 1ehre gejnejration est 1 (pas 0)
        for gejnejration in reversed(range(gejnMin, gejnMax+1)):
            # sur chaque gejnejration, en 3 temps
            # 1) arbres basiques : les parents sont raccrochejs ah leurs enfants
            # 2) arbres groupejs par ancestres : ils sont positionnejs ah l'intejrieur du groupe d'arbres
            # 3) les groupes d'arbres sont positionnejs entre eux
            # ah la fin du traitement d'une gejneration tout est ordonnej
            arbresGroupejs = self.arbreDescendants.listeArbres(gejnejration)
            # 1) aligne les parents sur les enfants (indejpendamment de la gejnejration N-1)
            rang_h = gejnMax - gejnejration      #le 1er est 0
            for arbresGroupej in arbresGroupejs:
                for arbre in arbresGroupej:
                    self.aligneParentsSurEnfants(rang_h, arbre)
            # 2) positionne les arbres ejlejmentaires dans chaque groupe d'arbres
            for arbresGroupej in arbresGroupejs:
                self.positionneArbres(arbresGroupej)
            # 3) positionne les groupes d'arbres les uns / aux autres
            nbreGejnejrations = gejnMax - gejnejration + 1
            self.positionneArbresGroupejs(arbresGroupejs, nbreGejnejrations)
        self.trace()
        (max_h, max_v) = self.maximumHV()
        #print('max_h=', max_h, 'max_v=', max_v)
        ejcritPdf(nomFichierSortieC, self.arbreDescendants, formatLong, ordreNp, self.positions, max_h, max_v, 2.0, titre, filigrane, latejcon, statistiques)
        ejcritPdfImprimable((nomFichierSortieE, nomFichierSortieF), self.arbreDescendants, formatLong, ordreNp, self.positions, titre, filigrane, latejcon, statistiques)         

    ##################
    # positionne les parents d'un arbre par rapport ah ses enfants
    def aligneParentsSurEnfants(self, rang_h, arbre):
        enfants = self.arbreDescendants.listeEnfants(arbre)
        parents = self.arbreDescendants.listeParents(arbre)
        # diffejrencie les arbres libres (sans enfants) des autres
        if len(enfants) == 0: milieuEnfants = 0
        else : 
            (rang_hp, rang_vp) = self.positions[enfants[0]]
            (rang_hd, rang_vd) = self.positions[enfants[-1]]
            milieuEnfants = (rang_vp + rang_vd) /2
        # positionne les parents
        if len(parents) == 0: raise Exception ('INCOHÉRENCE ARBRE 1')
        if len(parents) == 1: 
            self.positions[parents[0]] = (rang_h, milieuEnfants)
        elif len(parents) == 2:
            self.positions[parents[0]] = (rang_h, milieuEnfants -DIS_V/2)
            self.positions[parents[1]] = (rang_h, milieuEnfants +DIS_V/2)
        elif len(parents) == 3:
            self.positions[parents[0]] = (rang_h, milieuEnfants -DIS_V)
            self.positions[parents[1]] = (rang_h, milieuEnfants)
            self.positions[parents[2]] = (rang_h, milieuEnfants +DIS_V)
        elif len(parents) == 4:
            self.positions[parents[0]] = (rang_h, milieuEnfants -DIS_V-DIS_V/2)
            self.positions[parents[1]] = (rang_h, milieuEnfants -DIS_V/2)
            self.positions[parents[2]] = (rang_h, milieuEnfants +DIS_V/2)
            self.positions[parents[3]] = (rang_h, milieuEnfants +DIS_V+DIS_V/2)
        else: raise Exception ('INCOHÉRENCE ARBRE 2')

    ##################
    # positionne les arbres ah l'intejrieur d'un groupe d'arbres
    def positionneArbres(self, arbresGroupej):
        feuilles = []
        enTeste = True
        memPosition = 0
        memDejcalage = 0
        for arbre in arbresGroupej:
            # cherche les feuilles et les mejmorise
            # une feuille est un arbre sans enfant, un couple sans enfant est une feuille
            # FEUILLE
            if len(self.arbreDescendants.listeEnfants(arbre)) == 0:
                feuilles.append(arbre)
                continue
            # ARBRE
            # trouve les positions verticales des parents de l'arbre
            (rang_h, rang_vhaut, rang_vbas) = self.positionsParents(arbre)
            # positionne les feuilles de teste
            # inutile de dejcaler l'arbre
            if enTeste:
                position = rang_vhaut
                for feuille in reversed(feuilles):
                    # il faut trouver prendre en compte l'ejpaisseur de la feuille 
                    position -= (DIS_V * len(feuille))
                    (raf, rang_vh, raf) = self.positionsParents(feuille)
                    dejcalage = position - rang_vh
                    self.dejcaleArbre(feuille, dejcalage)
                enTeste = False
                feuilles = []
                memPosition = rang_vbas
                continue
            # positionne les feuilles entre arbres
            # l'espace minimum requis pour mettre les feuilles (y compris 0 feuille)
            espaceRequis = DIS_V
            for feuille in feuilles: espaceRequis += (DIS_V * len(feuille))
            espaceDispo = rang_vhaut - memPosition
            if espaceRequis > espaceDispo: 
                memDejcalage += espaceRequis - espaceDispo
                espaceDispo = espaceRequis
            # dejcale l'arbre
            self.dejcaleArbre(arbre, memDejcalage)
            # rejpartit harmonieusement les feuilles
            increjment = espaceDispo / (len(feuilles) +1)
            position = memPosition
            for feuille in feuilles:
                position += increjment
                (raf, rang_vh, raf) = self.positionsParents(feuille)
                dejcalage = position - rang_vh
                self.dejcaleArbre(feuille, dejcalage)
            (rang_h, rang_vhaut, rang_vbas) = self.positionsParents(arbre)
            feuilles = []
            memPosition = rang_vbas
        # positionne les feuilles de queue
        position = memPosition
        position += DIS_V
        for feuille in feuilles:
            (raf, rang_vh, raf) = self.positionsParents(feuille)
            dejcalage = position - rang_vh
            self.dejcaleArbre(feuille, dejcalage)
            position += (DIS_V * len(feuille))
    
    ##################
    # positionne les groupes d'arbres entre eux
    def positionneArbresGroupejs(self, arbresGroupejs, nbreGejnejrations):
        maxisPrejcedents = [0 for x in range(nbreGejnejrations)]
        for arbresGroupej in arbresGroupejs:
            # INVARIANT : chaque groupe d'arbres est bien positionnej en interne
            # calcul des minis du groupe d'arbres
            minis = [sys.maxsize for x in range(nbreGejnejrations)]
            for arbre in arbresGroupej:
                for numejro in arbre: 
                    (rang_h, rang_v) = self.positions[numejro]
                    minis[rang_h] = min(minis[rang_h], rang_v)
            # calcul le dejcalage  
            dejcalageRequis = 0
            for gejnejration in range(nbreGejnejrations):
                ejcart = maxisPrejcedents[gejnejration] - minis[gejnejration]
                dejcalageRequis = max(dejcalageRequis, ejcart + DIS_V*1.5)
            # applique le dejcalage et mejmorise les maxis
            for arbre in arbresGroupej:
                for numejro in arbre: 
                    (rang_h, rang_v) = self.positions[numejro]
                    self.positions[numejro] = (rang_h, rang_v + dejcalageRequis)
                    maxisPrejcedents[rang_h] = max(maxisPrejcedents[rang_h], rang_v + dejcalageRequis)

    ##################
    # trouve les positions des parents de l'arbre 
    def positionsParents(self, arbre):
        parents = self.arbreDescendants.listeParents(arbre)
        (rang_h, rang_vhaut) = self.positions[parents[0]]
        (rang_h, rang_vbas) = self.positions[parents[-1]]
        return (rang_h, rang_vhaut, rang_vbas)
                    
    ##################
    # dejcale tous les noeuds de l'arbres 
    def dejcaleArbre(self, arbre, dejcalage):
        for numejro in arbre:
            (rang_h, rang_v) = self.positions[numejro]
            self.positions[numejro] = (rang_h, rang_v + dejcalage)
    
    ############################
    # trouve le maximum horizontal et vertical d'une liste d'ancehtres
    def maximumHV(self):
        maxH = maxV = 0
        for (rang_h, rang_v) in self.positions.values():
            maxH = max(maxH, rang_h)
            maxV = max(maxV, rang_v)
        return (maxH, maxV)

    ############################
    # trace sur la console
    def trace(self):
        #print(self.positions)
        controsle = []
        for (clef, (h, v)) in self.positions.items(): controsle.append((v, clef))
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
     
