#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
__author__ = "jys"
__copyright__ = "Copyright (C) 2020 LATEJCON"

import sys
from os import path
from math import log2
from GrampsDb import GrampsDb 

def usage():
    script = '$PY/' + path.basename(sys.argv[0])
    print ("""© l'ATEJCON.  
Programme de test de la classe ArbreDescendants.

La classe ArbreDescendants établit l'arbre des descendants de l'individu 
spécifié par son identifiant gramps. Cet arbre peut être filtré tel 
qu'expliqué dans "Accès aux bases de données Gramps", LAT2020.JYS.483.
Il est possible de limiter le nombre de générations affichées (0 = toutes)
Le critère filtrant éventuel est l'identité des noms des descendants
au nom de l'ancêtre (ce qui limite à la descendance mâle seulement)
ou une liste d'identifiants de descendants (voir chercheIndividus.py)

usage   : {} <nom de la base> <id individu> [nbre générations] [<filtres>]
example : {} sage-devoucoux I0141
example : {} sage-devoucoux I0141 0 IDENT 
example : {} sage-devoucoux I0141 0 I0000,I2181 
""".format(script, script, script, script))
    
def main():
    try:
        nbGejnejrations = 0
        ident = False
        idsFiltrants = []
        if len(sys.argv) < 3: raise Exception()
        nomBase = sys.argv[1].strip()
        racineIdentifiant = sys.argv[2].strip()
        if len(sys.argv) > 3: nbGejnejrations = int(sys.argv[3])
        if len(sys.argv) > 4:
            ident = sys.argv[4].upper().startswith('ID')
            if not ident: idsFiltrants = sys.argv[4].strip().split(',')
            #if sys.argv[4].upper().startswith('ID'): ident = True
            #else: raise Exception ('IDENT non reconnu')
        testeArbreDescendants(nomBase, racineIdentifiant, nbGejnejrations, ident, idsFiltrants)
        
    except Exception as exc:
        if len(exc.args) == 0: 
            usage()
            raise
        else:
            print ("******************************")
            print (exc.args[0])
            print ("******************************")
            raise
        sys.exit()

def testeArbreDescendants(nomBase, racineIdentifiant, nbGejnejrations, ident, idsFiltrants):
    arbreDescendants = ArbreDescendants(nomBase)
    arbreDescendants.arbreComplet(racineIdentifiant)
    print('sans filtre')
    print('{:9d} descendants trouvés'.format(arbreDescendants.nombreTotal()))
    print('{:9d} générations trouvées'.format(arbreDescendants.maxGejnejration()))
    if nbGejnejrations != 0:
        arbreDescendants.tailleArbre(nbGejnejrations)
        print('avec limite')
        print('{:9d} descendants trouvés'.format(arbreDescendants.nombreTotal()))
        print('{:9d} générations trouvées'.format(arbreDescendants.maxGejnejration()))
    if ident: 
        arbreDescendants.filtreArbre()
        print('avec filtre sur patronyme')
        print('{:9d} descendants trouvés'.format(arbreDescendants.nombreTotal()))
        print('{:9d} générations trouvées'.format(arbreDescendants.maxGejnejration()))
    if len(idsFiltrants) != 0:
        arbreDescendants.filtreIdsArbre(idsFiltrants)
        print('avec filtre sur identifiants de descendants')
        print('{:9d} descendants trouvés'.format(arbreDescendants.nombreTotal()))
        print('{:9d} générations trouvées'.format(arbreDescendants.maxGejnejration()))
    arbreDescendants.afficheArbre()    
    
#################################  
# Numejrotation des individus :
# Chaque descendant est identifiej par un tuple de 2 ejlejments (G, I) 
# G = numejro de gejnejration (l'origine a la genejration 1)
# I = identification dans la gejnejration courante. Si n est le numejro d'ordre du descendant,
#     il aura 2*n comme identification si c'est un homme et 2n+1 si c'est une femme.
# Le descendant porte l'identifiant du parent de la gejnejration prejcejdente
# Chaque conjoint de descendant est identifiej par un tuple de 3 ejlejments (G, I, O)
# G est identique au G du conjoint 
# I = I du conjoint +1 si une femme, I du conjoint-1 si un homme
# O = numejro d'ordre dans la conjointalitej
# Le conjoint porte l'identifiant de son conjoint
#
# (1,0)      (0,0)    Joseph Sage
# (1,1,0)    (1,0)    Barbe Rique
# (2,1)      (1,1)    Anne Sage
# (2,3)      (1,1)    Antoinette Sage
# (2,2,0)    (2,3)    François Duclos
# (2,4)      (1,1)    Claude Sage
# (2,5,0)    (2,4)    Anne Delorme
# (2,6)      (1,1)    Jean-François Sage
# (2,9)      (1,1)    Benoite Sage
# (2,11)     (1,1)    Madeleine Sage
# (2,12)     (1,1)    Louys Sage
# (2,13,0)   (2,12)   Benoite Jay
# ...
# (9,1)      (8,7)    Jean-Yves Sage
# (9,2,0)    (9,1)    Martine Devoucoux
# (9,3)      (8,7)    Bernard Sage
# (9,4,0)    (9,3)    Pascale Jaillet
# (10,1)     (9,1)    Christophe Claude Arthur Sage
# (10,2,0)   (10,1)   Elisabeth MVoula
# (10,3)     (9,1)    Antonin Camille Sage
# (10,6)     (9,1)    Camille Libertad Sage
# (10,1)     (9,3)    Pablo Sage
# (10,7)     (9,3)    Lejonard Sage
# (11,9)     (10,1)   Adham Louis Sage
#################################    
class ArbreDescendants:
    def __init__(self, nomBase):
        self.grampsDb = GrampsDb(nomBase)
        if not self.grampsDb.estOuverte(): raise Exception('Base pas ouverte')
    
    ############################
    # construit l'arbre complet des descendants de l'individu spejcifiej avec les numejros normalisejs
    def arbreComplet(self, racineIdentifiant):
        self.descendants = {}
        # trouve la poigneje de la racine (n° 1)
        racinePoigneje = self.grampsDb.poignejeIndividu(racineIdentifiant)
        # homme ou femme ?
        if self.grampsDb.genre(racinePoigneje) == 1: racineNumejro = (1,0)
        else: racineNumejro = (1,1)
        # met la racine dans l'arbre
        self.descendants[racineNumejro] = ((0,0), racineIdentifiant, racinePoigneje, '')
        # init mejmorisation du nombre de descendants / gejnejration 
        nbParGejnejration = {}
        # remplit l'arbre rejcursivement 
        self._arbreIndividu(racinePoigneje, racineNumejro, nbParGejnejration)
        
    ############################
    # construit l'arbre complet des descendants de l'individu spejcifiej avec les numejros normalisejs
    def _arbreIndividu(self, individuPoigneje, individuNumejro, nbParGejnejration):
        # init numejrotation
        (numG, numI) = individuNumejro
        if numG not in nbParGejnejration: nbParGejnejration[numG] = 0
        numCourDescendant = nbParGejnejration[numG]
        # trouve les familles dont l'individu est un des parents, si elle est vide, c'est terminej 
        numCourFamille = 0
        for famillePoigneje in self.grampsDb.famillesDuParent(individuPoigneje):
            # trouve l'autre conjoint de cette famille 
            if self.grampsDb.genre(individuPoigneje) == 1:  
                # c'est un homme, cherche son ejpouse
                conjointNumejro = (numG, numI +1, numCourFamille)
                conjointPoigneje = self.grampsDb.mehreDeLaFamille(famillePoigneje)
            else:
                # c'est une femme, cherche son mari
                conjointNumejro = (numG, numI -1, numCourFamille)
                conjointPoigneje = self.grampsDb.pehreDeLaFamille(famillePoigneje)
            conjointIdentifiant = self.grampsDb.identifiantIndividu(conjointPoigneje)
            # c'est le conjoint qui porte l'identifiant de la famille du couple
            self.descendants[conjointNumejro] = (individuNumejro, conjointIdentifiant, conjointPoigneje, famillePoigneje)            
            # trouve les enfants de cette famille
            for enfantPoigneje in self.grampsDb.enfantsDeLaFamille(famillePoigneje):
                if self.grampsDb.genre(enfantPoigneje) == 1: 
                    # c'est un homme
                    enfantNumejro = (numG +1, numCourDescendant)
                else: 
                    # c'est une femme
                    enfantNumejro = (numG +1, numCourDescendant +1)
                enfantIdentifiant = self.grampsDb.identifiantIndividu(enfantPoigneje)
                # le descendant porte l'identifiant de la famille de ses parents
                self.descendants[enfantNumejro] = (individuNumejro, enfantIdentifiant, enfantPoigneje, famillePoigneje)
                self._arbreIndividu(enfantPoigneje, enfantNumejro, nbParGejnejration)
                numCourDescendant +=2
            numCourFamille +=1
        nbParGejnejration[numG] = numCourDescendant

    ############################
    # filtre l'arbre, ne garde que les descendants qui ont le mesme nom que la racine et leur conjoint
    def filtreArbre(self):
        # trouve le nom de la racine
        clefs = list(self.descendants.keys())
        clefs.sort()
        (raf, raf, racinePoigneje, raf) = self.descendants[clefs[0]]
        nomRacine = self.grampsDb.prejnomNom(racinePoigneje)[1]
        # enlehve de l'arbre tout ce qui n'a pas le mesme nom 
        clefsEffacejes = []
        # en 2 fois pour ne pas trop se creuser la teste
        # on repehre les descendants que l'on va effacer au 2ehme tour
        for clef in clefs:
            # si c'est un conjoint, on verra a second tour
            if len(clef) == 3: continue
            # si le parent a dejjah ejtej effacej, on efface le descendant
            (parentNumejro, raf, individuPoigneje, raf) = self.descendants[clef]
            if parentNumejro in clefsEffacejes:
                clefsEffacejes.append(clef)
                continue
            if self.grampsDb.prejnomNom(individuPoigneje)[1] != nomRacine:
                clefsEffacejes.append(clef)
        # on efface les des descendants reperejs et leurs conjoints
        for clef in clefs:
            if clef in clefsEffacejes: 
                self.descendants.pop(clef)
                continue
            # si le parent a dejjah ejtej effacej, on efface le descendant
            (parentNumejro, raf, raf, raf) = self.descendants[clef]
            if parentNumejro in clefsEffacejes:
                self.descendants.pop(clef)
                continue
            # on efface aussi les conjoints masles
            if len(clef) == 3 and clef[1]&1 == 0: self.descendants.pop(clef)
            
    ############################
    # filtre l'arbre, ne garde que les descendants qui aboutissent aux ejlejments filtrants 
    def filtreIdsArbre(self, idsFiltrants):
        # trouve les clefs des identifiants spejcifiejs
        clefsFiltrantes = []
        clefs = list(self.descendants.keys())
        for clef in clefs: 
            (raf, individuIdentifiant, raf, raf) = self.descendants[clef] 
            if individuIdentifiant in idsFiltrants: clefsFiltrantes.append(clef) 
        # constitue l'arbre a partir des ejlejments filtrants
        clefsAncestres = set()
        for clefFiltrante in clefsFiltrantes:
            clef = clefFiltrante
            while clef != (0,0):
                (parentNumejro, raf, raf, raf) = self.descendants[clef]
                clef = parentNumejro
                clefsAncestres.add(clef)
        # filtre ce qui n'a pas ejtej retenu
        clefs = list(self.descendants.keys())
        clefs.sort()
        for clef in clefs:
            # vire les reconjoints
            if len(clef) == 3 and clef[2] == 1:
                self.descendants.pop(clef)
                continue
            (parentNumejro, raf, raf, raf) = self.descendants[clef]
            if clef not in clefsAncestres and parentNumejro not in clefsAncestres:
                self.descendants.pop(clef)
        
    ############################
    # restreint l'arbre par le nombre de gejnejrations max
    def tailleArbre(self, nbGejnejrations):
        # si pas de limitation, raf
        if nbGejnejrations == 0: return
        # enlehve de l'arbre tout ce qui est hors limite 
        clefs = list(self.descendants.keys())
        for clef in clefs:
            if clef[0] > nbGejnejrations +1: self.descendants.pop(clef)

    ############################
    # retourne le nombre total de descendants + conjoints connus
    def nombreTotal(self):
        return len(self.descendants)
        
    ############################
    # retourne le nombre total de descendants connus
    def nombreDescendants(self):
        filles = garcons = 0
        clefs = list(self.descendants.keys())
        for clef in clefs: 
            # pas les conjoints
            if len(clef) == 3: continue
            # pas la racine
            if clef[0] == 1: continue
            if clef[1]%2 == 1: filles +=1
            else: garcons +=1
        return (filles, garcons)
        
    ############################
    # retourne le nombre de gejnejrations maximum de l'arbre
    def maxGejnejration(self):
        clefs = list(self.descendants.keys())
        clefs.sort()
        return clefs[-1][0]
    
    ############################
    # retourne le numejro de la racine de l'arbre
    def numejroRacine(self):
        clefs = list(self.descendants.keys())
        clefs.sort()
        if len(clefs[0]) == 2: return clefs[0]
        else: return clefs[1]
    
    ############################
    # retourne la liste des couples
    def listeCouples(self):
        couples = []
        clefs = list(self.descendants.keys())
        clefs.sort()
        for clef in clefs:
            if len(clef) == 3:
                (conjointNumejro, raf, raf, raf) = self.descendants[clef]
                couple = [conjointNumejro, clef]
                couple.sort()
                couples.append(tuple(couple))
        return couples
            
    ############################
    # retourne la liste des fratries
    def listeFratries(self):
        fratries = {}
        clefs = list(self.descendants.keys())
        clefs.sort()
        for clef in clefs:
            # les conjoints sont exclus
            if len(clef) == 3: continue
            (parentNumejro, raf, raf, raf) = self.descendants[clef]
            # la racine est exclue
            if parentNumejro == (0,0): continue
            if parentNumejro not in fratries: fratries[parentNumejro] = []
            fratries[parentNumejro].append(clef)
        return list(fratries.values())
    
    ############################
    # retourne les prejnom, nom, date et lieu naissance, date et lieu decehs
    def attributsDescendant(self, descendantNumejro):
        # si descendant inconnu, retourne tout ah vide
        if descendantNumejro not in self.descendants: return (('', ''), ('', ''), ('', ''))
        # trouve tous les attributs dans la base
        (parentNumejro, individuIdentifiant, individuPoigneje, famillePoigneje) = self.descendants[descendantNumejro]
        prejnomNom = self.grampsDb.prejnomNom(individuPoigneje)
        dateLieuNaissance = self.grampsDb.dateLieuNaissance(individuPoigneje)
        dateLieuDejcehs = self.grampsDb.dateLieuDejcehs(individuPoigneje)
        return (prejnomNom, dateLieuNaissance, dateLieuDejcehs)

    ############################
    # retourne les date et lieu mariage
    def mariageDescendant(self, descendantNumejro):
        # si descendant inconnu, retourne tout ah vide
        if descendantNumejro not in self.descendants: return (('', ''))
        # trouve tous les attributs dans la base
        (parentNumejro, individuIdentifiant, individuPoigneje, famillePoigneje) = self.descendants[descendantNumejro]
        return self.grampsDb.dateLieuMariage(famillePoigneje)
     
    ############################
    # retourne tous les numejros des descendants connus
    def tousNumejros(self):
        return list(self.descendants.keys())
    
    ############################
    # retourne tous les arbres pour une gejnejration donneje
    def listeArbres(self, gejnejration):
        arbres = []
        clefs = list(self.descendants.keys())
        clefs.sort()
        for clef in clefs:
            #les gejnejrations prejcejdentes ne sont pas prises en compte
            if clef[0] < gejnejration: continue
            # on traite les conjoints au deuxiehme passage
            if len(clef) == 3: continue
            (parentNumejro, raf, raf, raf) = self.descendants[clef]
            trouvej = False
            for arbre in arbres:
                if parentNumejro in arbre: 
                    arbre.append(clef)
                    trouvej = True
            if not trouvej: arbres.append([clef])
        # et maintenant, les conjoints
        for clef in clefs:
            #les gejnejrations prejcejdentes ne sont pas prises en compte
            if clef[0] < gejnejration: continue
            # on traite les conjoints 
            if len(clef) == 2: continue
            (conjointNumejro, raf, raf, raf) = self.descendants[clef]
            for arbre in arbres:
                if conjointNumejro in arbre: arbre.append(clef)
        # met dans l'ordre
        for arbre in arbres: arbre.sort()
        return arbres
    
    ############################
    # retourne la liste des descendants de 1ehre gejejration
    def listeEnfants(self, arbre):
        gejnejration = arbre[0][0] +1
        enfants = []
        for clef in arbre:
            # on ne prend pas les conjoints
            if len(clef) == 3: continue
            if clef[0] != gejnejration : continue
            enfants.append(clef)
        return enfants
    
    ############################
    # retourne la liste des descendants de 1ehre gejejration
    def listeParents(self, arbre):
        gejnejration = arbre[0][0]
        parents = []
        for clef in arbre:
            if clef[0] != gejnejration : continue
            parents.append(clef)
        return parents
    
    ############################
    # retourne la liste des maximum et minimum sur chaque gejnejration de l'arbre
    def listeMinisMaxis(self, arbre):
        minis = []
        maxis = []
        gejnejration = -1
        for clef in arbre:
            if clef[0] != gejnejration:
                if gejnejration != -1: maxis.append(clefPrejcejdente)
                minis.append(clef)
                gejnejration = clef[0]
            clefPrejcejdente = clef
        maxis.append(clefPrejcejdente)
        return minis, maxis
    
    ############################
    # affiche l'arbre
    def afficheArbre(self):
        clefs = list(self.descendants.keys())
        clefs.sort()
        for clef in clefs: 
            (parentNumejro, individuIdentifiant, individuPoigneje, famillePoigneje) = self.descendants[clef]
            prejnomNom = self.grampsDb.prejnomNom(individuPoigneje)
            dateLieuNaissance = self.grampsDb.dateLieuNaissance(individuPoigneje)
            dateLieuDejcehs = self.grampsDb.dateLieuDejcehs(individuPoigneje)
            #print('{:10s} : {:8s} {} {:30s} {} {} - \u2020 {} {}'.format(str(clef), str(parentNumejro), individuIdentifiant, ' '.join(prejnomNom), dateLieuNaissance[0], dateLieuNaissance[1], dateLieuDejcehs[0], dateLieuDejcehs[1]))   
            print('{:10s} : {:8s} {} {:30s}'.format(str(clef), str(parentNumejro), individuIdentifiant, ' '.join(prejnomNom)))
         
         
if __name__ == '__main__':
    main()


