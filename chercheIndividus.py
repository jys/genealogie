#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
__author__ = "jys"
__copyright__ = "Copyright (C) 2020 LATEJCON"

import sys
from os import path
from GrampsDb import GrampsDb

def usage():
    script = '$PY/' + path.basename(sys.argv[0])
    print ("""© l'ATEJCON.  
Recherche dans la base Gramps spécifiée des individus dont le texte de leur 
prénom-nom contient ou correspond au modèle spécifié.
Les expressions régulières sont orthodoxes. 

usage   : %s <nom de la base> <modèle>
exemple : %s sage-devoucoux "Joseph Sage"
exemple : %s sage-devoucoux ".*Sage"
"""%(script, script, script))
    
def main():
    try:
        if len(sys.argv) < 3 : raise Exception()
        #nom de la base
        nomBase = sys.argv[1]
        modehle = sys.argv[2]
        chercheIndividus(nomBase, modehle)
        
    except Exception as exc:
        if len(exc.args) == 0: usage()
        else:
            print ("******************************")
            print (exc.args[0])
            print ("******************************")
            raise
        sys.exit()

def chercheIndividus(nomBase, modehle):
    grampsDb = GrampsDb(nomBase)
    if not grampsDb.estOuverte(): 
        print ("La base n'est pas ouverte")
        return
    listeIndividus = grampsDb.listeIndividus(modehle)
    rejsultat = []
    for individuPoigneje in listeIndividus:
        identifiant = grampsDb.identifiantIndividu(individuPoigneje)
        (prejnom, nom) = grampsDb.prejnomNom(individuPoigneje)
        (dateNaissance, lieuNaissance) = grampsDb.dateLieuNaissance(individuPoigneje)
        (dateDejcehs, lieuDejcehs) = grampsDb.dateLieuDejcehs(individuPoigneje)
        rejsultat.append((prejnom + ' ' + nom, identifiant, dateNaissance, lieuNaissance, dateDejcehs, lieuDejcehs))
    rejsultat.sort()
    for (prejnomNom, identifiant, dateNaissance, lieuNaissance, dateDejcehs, lieuDejcehs) in rejsultat:
        print('{:8s}{:30s}{:18s}{:25s}- {:18s}{:25s}'.format(identifiant, prejnomNom, dateNaissance, lieuNaissance, dateDejcehs, lieuDejcehs))
        
        
if __name__ == '__main__':
    main()
    
