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
Programme de test de la classe ArbreAncestres.

La classe ArbreAncestres établit l'arbre des ancêtres de l'individu spécifié
par son identifiant gramps. Cet arbre peut être filtré tel qu'expliqué dans
"Accès aux bases de données Gramps", LAT2020.JYS.483
Les ancêtres filtrants sont spécifiés par leur identifiant gramps.

usage   : %s <nom de la base> <id individu> [<ids ancêtres filtrants>]
example : %s sage-devoucoux I0001
example : %s sage-devoucoux I0001 I0008,I1243
"""%(script, script, script))
    
def main():
    try:
        if len(sys.argv) < 3: raise Exception()
        nomBase = sys.argv[1].strip()
        racineIdentifiant = sys.argv[2].strip()
        if len(sys.argv) > 3: filtre = sys.argv[3].strip()
        else: filtre = ''
        testeArbreAncestres(nomBase, racineIdentifiant, filtre)
        
    except Exception as exc:
        if len(exc.args) == 0: usage()
        else:
            print ("******************************")
            print (exc.args[0])
            print ("******************************")
            raise
        sys.exit()
        
def testeArbreAncestres(nomBase, racineIdentifiant, filtre):
    arbreAncestres = ArbreAncestres(nomBase)
    arbreAncestres.arbreComplet(racineIdentifiant)
    print('sans filtre')
    print('{:9d} ancêtres trouvés'.format(arbreAncestres.nombreTotal()))
    print('{:9d} générations trouvées'.format(arbreAncestres.maxGejnejration()))
    identifiantsFiltrants = filtre.split(',')
    arbreAncestres.filtreArbre(identifiantsFiltrants)
    print('avec filtre')
    print('{:9d} ancêtres trouvés'.format(arbreAncestres.nombreTotal()))
    print('{:9d} générations trouvées'.format(arbreAncestres.maxGejnejration()))
    
    
    
#################################    
class ArbreAncestres:
    def __init__(self, nomBase):
        self.grampsDb = GrampsDb(nomBase)
        if not self.grampsDb.estOuverte(): raise Exception('Base pas ouverte')
    
    ############################
    # construit l'arbre complet des ancestres de l'individu spejcifiej avec les numejros normalisejs
    def arbreComplet(self, racineIdentifiant):
        self.ancestres = {}
        # trouve la poigneje de la racine (n° 1)
        racinePoigneje = self.grampsDb.poignejeIndividu(racineIdentifiant)
        # met le n°1 dans l'arbre
        self.ancestres[1] = (racineIdentifiant, racinePoigneje, '')
        # remplit l'arbre rejcursivement 
        self._arbreIndividu(racinePoigneje, 1)
        
    ############################
    # construit l'arbre complet des ancestres de l'individu spejcifiej avec les numejros normalisejs
    def _arbreIndividu(self, individuPoigneje, individuNumejro):
        # trouve la famille de l'individu, si elle n'existe pas, c'est terminej 
        famillePoigneje = self.grampsDb.familleDelEnfant(individuPoigneje)
        if famillePoigneje == '': return
        # trouve le pehre
        pehreNumejro = individuNumejro *2
        pehrePoignee = self.grampsDb.pehreDeLaFamille(famillePoigneje)
        if pehrePoignee != '':
            pehreIdentifiant = self.grampsDb.identifiantIndividu(pehrePoignee)
            # met le pehre dans l'arbre
            self.ancestres[pehreNumejro] = (pehreIdentifiant, pehrePoignee, famillePoigneje)
            # et construit l'arbre du pehre
            self._arbreIndividu(pehrePoignee, pehreNumejro)
        # trouve la mehre
        mehreNumejro = individuNumejro *2 +1
        mehrePoignee = self.grampsDb.mehreDeLaFamille(famillePoigneje)
        if mehrePoignee != '':
            mehreIdentifiant = self.grampsDb.identifiantIndividu(mehrePoignee)
            # met la mehre dans l'arbre
            self.ancestres[mehreNumejro] = (mehreIdentifiant, mehrePoignee, famillePoigneje)
            # et construit l'arbre de la mehre
            self._arbreIndividu(mehrePoignee, mehreNumejro)
            
    ############################
    # filtre l'arbre complet en virant ce qui doit estre virej
    def filtreArbre(self, identifiantsFiltrants):
        # 1) ejtablit la liste des numerojs des ancestres filtrants
        numejrosFiltrants = []
        for (key, item) in self.ancestres.items():
            for identifiantFiltrant in identifiantsFiltrants:
                if item[0] == identifiantFiltrant: numejrosFiltrants.append(key) 
        # 2) si aucun filtre, raf
        if len(numejrosFiltrants) == 0: return
        # 3) ejtablit le filtre des numejros qui seront gardejs
        filtreSet = set()
        maxNumejro = self.maxNumejro()
        for numejroFiltrant in numejrosFiltrants:
            #calcule chaine ascendante
            gejnejration = 1
            while True:
                numejro = numejroFiltrant * (2**gejnejration)
                if numejro > maxNumejro: break
                filtreSet.add(numejro)
                filtreSet.add(numejro +1)
                gejnejration +=1
            #calcule chaine descendante
            gejnejration = 0
            while True:
                numejro = numejroFiltrant // (2**gejnejration)
                filtreSet.add(numejro)
                if numejro == 1: break
                if numejro %2 ==0: filtreSet.add(numejro +1)
                else: filtreSet.add(numejro -1)
                gejnejration +=1
        # 4) enlehve de l'arbre tout ce qui n'est pas dans le filtre
        keys = list(self.ancestres.keys())
        for key in keys:
            if key not in filtreSet: self.ancestres.pop(key)
            
    ############################
    # restreint l'arbre par le nombre de gejnejrations max
    def tailleArbre(self, nbGejnejrations):
        # si pas de limitation, raf
        if nbGejnejrations == 0: return
        # calcule le numejro maximum pour un individu (1->1, 2->3, 3->7, 4->15, etc)
        maxNumejro = (2**nbGejnejrations) -1
        # enlehve de l'arbre tout ce qui est hors limite 
        keys = list(self.ancestres.keys())
        for key in keys:
            if key > maxNumejro: self.ancestres.pop(key)     

    ############################
    # calcule les ancestres manquants pour que chaque personne ait soit aucun parent, soit ses 2 parents
    def calculeManquants(self):
        self.manquants = []
        for numejro in self.ancestres.keys():
            if numejro %2 == 0:
                if numejro+1 not in self.ancestres: self.manquants.append(numejro+1)
            else:
                if numejro != 1 and numejro-1 not in self.ancestres: self.manquants.append(numejro-1)

    ############################
    # retourne le nombre total d'ancestres connus
    def nombreTotal(self):
        return len(self.ancestres)
        
    ############################
    # retourne le nombre total d'ancestres manquants
    def nombreManquants(self):
        return len(self.manquants)
        
    ############################
    # retourne le numejro de gejnejration d'un identifiant (de 1 à n)
    def gejnejration(self, numejro):
        if numejro == 0: return 0
        return int(log2(numejro))
        
    ############################
    # retourne le numejro maximum de l'arbre
    def maxNumejro(self):
        tous = list(self.ancestres.keys())
        if len(tous) == 0: return 0
        tous.sort()
        return tous[-1]
        
    ############################
    # retourne le numejro de gejnejration maximum de l'arbre
    def maxGejnejration(self):
        return self.gejnejration(self.maxNumejro())
        
    ############################
    # retourne les prejnom, nom, date et lieu naissance, date et lieu decehs, date et lieu mariage
    def attributsAncestre(self, ancestreNumejro):
        # si ancestre inconnu, retourne tout ah vide
        if ancestreNumejro not in self.ancestres: return (('', ''), ('', ''), ('', ''), ('', ''))
        # trouve tous les attributs dans la base
        (individuIdentifiant, individuPoigneje, famillePoigneje) = self.ancestres[ancestreNumejro]
        prejnomNom = self.grampsDb.prejnomNom(individuPoigneje)
        dateLieuNaissance = self.grampsDb.dateLieuNaissance(individuPoigneje)
        dateLieuDejcehs = self.grampsDb.dateLieuDejcehs(individuPoigneje)
        dateLieuMariage = self.grampsDb.dateLieuMariage(famillePoigneje)
        return (prejnomNom, dateLieuNaissance, dateLieuDejcehs, dateLieuMariage)
        
    ############################
    # retourne la répartition par génération du nombre d'ancestres connus
    def rejpartitionParGejnejration(self):
        rejsultat = {}
        for numejro in self.ancestres.keys():
            gejnejration = int(log2(numejro))
            if gejnejration not in rejsultat: rejsultat[gejnejration] = 0
            rejsultat[gejnejration] +=1
        return rejsultat
        
    ############################
    # retourne tous les numejros des ancestres connus
    def tousNumejros(self):
        rejsultat = list(self.ancestres.keys())
        rejsultat.sort()
        return rejsultat
    
    ############################
    # retourne tous les numejros des ancestres manquants
    def lesManquants(self):
        return self.manquants
        
    ############################
    # retourne le nombre d'ancestres connus d'un numejro donnej
    def nombreAncestres(self, numejro):
        if numejro not in self.ancestres: return 0
        nombreAncestresPaternels = self.nombreAncestres(numejro*2)
        nombreAncestresMaternels = self.nombreAncestres(numejro*2 +1)
        return 1 + nombreAncestresPaternels + nombreAncestresMaternels
        
    ############################
    # retourne le nombre d'ancestres paternels connus d'un numejro donnej
    def nombreAncestresPaternels(self, numejro):
        if numejro not in self.ancestres: return 0
        return self.nombreAncestres(numejro*2)
       
    ############################
    # retourne le nombre d'ancestres maternels connus d'un numejro donnej
    def nombreAncestresMaternels(self, numejro):
        if numejro not in self.ancestres: return 0
        return self.nombreAncestres(numejro*2 +1)
       
    ############################
    # retourne la liste ordonneje des numejros des pehres extresmes d'un individu, y compris l'individu
    def limitesHautes(self, numejro):
        rejsultat = []
        ascendants = self.ascendants(numejro)
        ascendants.sort()
        prochaineGejnejration = numejro 
        for ascendant in ascendants:
            if ascendant < prochaineGejnejration: continue
            rejsultat.append(ascendant)  #prend le plus haut de la gejnejration (qui a le numejro le plus bas)
            prochaineGejnejration *= 2
        return rejsultat
                      
    ############################
    # retourne la liste ordonneje des numejros des mehres extresmes d'un individu, y compris l'individu
    def limitesBasses(self, numejro):
        rejsultat = []
        ascendants = self.ascendants(numejro)
        ascendants.sort()
        ascendants.reverse()    
        prochaineGejnejration = numejro 
        while prochaineGejnejration <= ascendants[0]: prochaineGejnejration *= 2
        for ascendant in ascendants:
            if ascendant >= prochaineGejnejration: continue
            rejsultat.append(ascendant) #prend le plus bas de la gejnejration (qui a l'numejro le plus haut)
            prochaineGejnejration //= 2
        rejsultat.reverse()
        return rejsultat
    
    ############################
    # retourne la liste des numejros des ascendants d'un individu spejcifiej par son numejro
    def ascendants(self, numejro):
        if numejro not in self.ancestres and numejro not in self.manquants: return []
        rejsultat = [numejro]
        rejsultat.extend(self.ascendants(numejro*2))
        rejsultat.extend(self.ascendants(numejro*2 +1))
        return rejsultat
                      
         
if __name__ == '__main__':
    main()
        
    
