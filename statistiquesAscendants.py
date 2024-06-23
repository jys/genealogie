#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
__author__ = "jys"
__copyright__ = "Copyright (C) 2022 LATEJCON"

import sys
from os import path
from unicodedata import normalize
from ArbreAncestres import ArbreAncestres

def usage():
    script = '$PY/' + path.basename(sys.argv[0])
    print (f"""© l'ATEJCON.  
Établit les statistiques sur les noms (N), prénoms (P), lieux (L) de 
naissance des ancêtres d'un individu désigné par son identifiant gramps.
(pour trouver l'identifiant gramps d'un individu, utiliser 
$PY/chercheIndividus.py)
Il est possible de limiter le nombre de générations explorées (0 = toutes)
Il est possible de filtrer les ancêtres en fournissant les identifiants 
gramps d'ancêtres particuliers (voir "Accès aux bases de données Gramps", 
LAT2020.JYS.483).

usage   : {script} <base> <individu-racine> <N,P,L> [nbre générations] [filtre]
example : {script} sage-devoucoux I0001 P
example : {script} sage-devoucoux I0001 N,L 10 I0008,I1243
""")

def main():
    try:
        if len(sys.argv) < 4: raise Exception()
        nomBase = sys.argv[1].strip()
        racineIdentifiant = sys.argv[2].strip()
        npl = sys.argv[3].strip().split(',')
        nbGejnejrations = 0
        identifiantsFiltrants = []
        if len(sys.argv) > 4: nbGejnejrations = int(sys.argv[4])
        if len(sys.argv) > 5: identifiantsFiltrants = sys.argv[5].strip().split(',')
        statistiquesAscendants(nomBase, racineIdentifiant, npl, nbGejnejrations, identifiantsFiltrants)
    except Exception as exc:
        if len(exc.args) == 0: 
            usage()
        else:
            print ("******************************")
            print (exc.args[0])
            print ("******************************")
            raise
        sys.exit()

def statistiquesAscendants(nomBase, racineIdentifiant, npl, nbGejnejrations, identifiantsFiltrants):
    # ejtablit l'arbre 
    arbreAncestres = ArbreAncestres(nomBase)
    arbreAncestres.arbreComplet(racineIdentifiant)
    print('sans filtre : {:4d} ancêtres sur {:2d} générations'.format(arbreAncestres.nombreTotal() -1, arbreAncestres.maxGejnejration()))
    arbreAncestres.filtreArbre(identifiantsFiltrants)
    print('avec filtre : {:4d} ancêtres sur {:2d} générations'.format(arbreAncestres.nombreTotal() -1, arbreAncestres.maxGejnejration()))
    arbreAncestres.tailleArbre(nbGejnejrations)
    print('avec limite : {:4d} ancêtres sur {:2d} générations'.format(arbreAncestres.nombreTotal() -1, arbreAncestres.maxGejnejration()))

    noms = {}
    prejnomsF = {}
    prejnomsG = {}
    lieux = {}
    #recupehre tous les attributs d'ancestres 
    tousNumejros = arbreAncestres.tousNumejros()
    for numejro in tousNumejros[1:]:    # on ne prend pas la source
        ((prejnom, nom), (dateNaissance, lieuNaissance), (dateDejcehs, lieuDejcehs), (dateMariage, lieuMariage)) = arbreAncestres.attributsAncestre(numejro)
        if nom not in noms: noms[nom] = 0
        noms[nom] +=1
        for prejnomUni in prejnom.split():
            if prejnomUni.isupper(): continue
            if not prejnomUni.replace('-','').isalpha(): continue
            if numejro &1 == 0:     
                if prejnomUni not in prejnomsG: prejnomsG[prejnomUni] = 0
                prejnomsG[prejnomUni] +=1
            else:
                if prejnomUni not in prejnomsF: prejnomsF[prejnomUni] = 0
                prejnomsF[prejnomUni] +=1
        if lieuNaissance == '': continue
        if lieuNaissance not in lieux: lieux[lieuNaissance] = 0
        lieux[lieuNaissance] +=1

    listeNoms = list(noms.items())
    listeNoms.sort(key = lambda i: i[1], reverse = True)
    listePrejnomsG = list(prejnomsG.items())
    listePrejnomsG.sort(key = lambda i: i[1], reverse = True)
    listePrejnomsF = list(prejnomsF.items())
    listePrejnomsF.sort(key = lambda i: i[1], reverse = True)
    listeLieux = list(lieux.items())
    listeLieux.sort(key = lambda i: i[1], reverse = True)
    
    if 'N' in npl:
        print(f'{len(listeNoms)} noms trouvés')
        affiche(listeNoms)
    if 'P' in npl:
        print(f'{len(listePrejnomsF)} prénoms de filles trouvés')
        affiche(listePrejnomsF)
        print(f'{len(listePrejnomsG)} prénoms de garçons trouvés')
        affiche(listePrejnomsG)
    if 'L' in npl:
        print(f'{len(listeLieux)} lieux trouvés')
        affiche(listeLieux)
    
def affiche(liste):
    nombreCourant = liste[0][1]
    listeCourante = [liste[0][0]]
    for (texte, nombre) in liste[1:]:
        if nombre == nombreCourant:
            listeCourante.append(texte)
            continue
        listeCourante.sort()
        print('{:4d} : {:s}'.format(nombreCourant, ', '.join(listeCourante)))
        nombreCourant = nombre
        listeCourante = [texte]
    listeCourante.sort()
    print('{:4d} : {:s}'.format(nombreCourant, ', '.join(listeCourante)))
              
    
if __name__ == '__main__':
    main()
