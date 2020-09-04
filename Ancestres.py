#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
__author__ = "jys"
__copyright__ = "Copyright (C) 2014 LATEJCON"

import sys
import os
import codecs
import re
from math import log2

def usage():
    print ("""© l'ATEJCON.  
Programme de test de la classe Ancestres. 
Les ancêtres sont comptés par génération.

La classe Ancestres 
o extrait tous les ancêtres fournis dans le rapport texte de Gramps
  (Rapports / Rapports texte / Liste détaillée des ascendants...)
  et les repère par leur identifiant généalogique.
o donne la liste des identifiant généalogiques extraite
o donne tous les attributs de l'individu spécifié par son identifiant
o donne le numéro de génération d'un identifiant
o donne le numéro de génération maximum de l'arbre
o donne le nombre total d'ascendants d'un individu
o donne le nombre d'ascendants paternels ou maternels d'un individu
o donne la répartition du nombre d'individus par génération

usage   : %s <rapport texte HTML Gramps> 
example : %s det_ancestor_report.html
"""%(sys.argv[0], sys.argv[0]))

def main():
    #os.chdir(sys.path[0])
    if len(sys.argv) < 2 :
        usage()
        sys.exit()
        
    #nom du fichier
    nomRapportGramps = sys.argv[1]
    ancestres = Ancestres(nomRapportGramps, True, [])
    print ('%d toutes générations confondues'%(ancestres.nombreTotal()))
    nombreParGejnejration = list(ancestres.rejpartitionParGejnejration().items())
    nombreParGejnejration.sort()
    for (gejnejration, nombre) in nombreParGejnejration:
        print ('%d en gejnejration %d'%(nombre, gejnejration))
        
    #affiche tous les attributs de tous les ancestres
    #for identifiant in ancestres.tousIdentifiants():
        #print identifiant, ancestres.attributs(identifiant)
    #affiche tous les identifiants par génération
    #gejnejration = 1
    #identParGejnejration = []
    #for identifiant in ancestres.tousIdentifiants():
        #if identifiant >= 2**gejnejration:
            #print identParGejnejration
            #gejnejration +=1
            #identParGejnejration = [] 
        #identParGejnejration.append(identifiant)
    #print identParGejnejration
    
    #for identifiant in range(1,8):
        #print ('#%d : %d ancestres'%(identifiant, ancestres.nombreAncetres(identifiant)))
    #for identifiant in range(1,8):
        #print ('#%d : %d ancestres'%(identifiant, ancestres.nombreAncetresPaternels(identifiant)))
    #mehresExtresmes = ancestres.mehresExtresmes(2)
    #print mehresExtresmes
    
    

class Ancestres:
    def __init__(self, nomRapportGramps, filtre, nbGejnejrations):
        # calcule le filtre des ancestres, filtre vide si pas filtre
        filtreSet = self.calculeFiltre(filtre)
        # construit les ancestres en lisant le fichier source
        self.personnes = {}
        self.construitAncestres(nomRapportGramps, filtreSet, nbGejnejrations)
        # calcule les ancestres manquants pour que chaque personne ait soit aucun parent, soit ses 2 parents
        self.manquants = []
        self.calculeManquants()
        
    
    # calcule filtre des ancestres
    def calculeFiltre(self, filtre):
        filtreSet = set()
        for entree in filtre:
            #if entree %2 ==0: continue        #nombre pair sans effet
            #calcule chaine ascendante
            gejnejration = 1
            while True:
                identifiant = entree * (2**gejnejration)
                if identifiant > 2**64: break
                filtreSet.add(identifiant)
                filtreSet.add(identifiant +1)
                gejnejration +=1
            #print ("filtreSet=",filtreSet)
            #calcule chaine descendante
            gejnejration = 0
            while True:
                identifiant = entree // (2**gejnejration)
                filtreSet.add(identifiant)
                if identifiant == 1: break
                if identifiant %2 ==0: filtreSet.add(identifiant +1)
                else: filtreSet.add(identifiant -1)
                gejnejration +=1
        #print ("filtreSet=",filtreSet)  
        return filtreSet
    
    #construit les ancestres en lisant le fichier source
    def construitAncestres(self, nomRapportGramps, filtreSet, nbGejnejrations):
        pasFiltre = len(filtreSet) == 0
        rapportGramps = codecs.open(nomRapportGramps, 'r', 'utf-8')
        cmptLignes = cmptAncestres = 0
        for ligne in rapportGramps:
            ligne = ligne.strip()
            cmptLignes +=1
            if '<p class="DAR-First-Entry">' not in ligne: continue
            cmptAncestres +=1
            #vire les espaces bizarres mis par Gramps
            ligne = ligne.replace(chr(160), u' ')
            #vire l'indication de date révolutionnaire
            ligne = ligne.replace(u'(Révolutionnaire) ', u'')
            #extrait l'identifiant, le nom et le prénom (obligatoires !)
            (identifiant, nom, prenom, finLigne) = self.extraitIdentNomPrejnom(ligne)
            #extrait la date et le lieu de naissance (éventuellement)
            (dateNaissance, lieuNaissance, finLigne) = self.extraitNaissance(finLigne)
            #extrait la date et le lieu de décès (éventuellement)
            (dateDejcehs, lieuDejcehs, finLigne) = self.extraitDejcehs(finLigne)
            #extrait la date et le lieu du mariage (éventuellement)
            (dateMariage, lieuMariage, finLigne) = self.extraitMariage(finLigne)
            # teste si nombre de gejnejrations dejjah atteint
            if nbGejnejrations != 0 and self.gejnejration(identifiant) > nbGejnejrations: break
            #met toutes ces infos en dico indexé par l'identifiant si pas filtre
            if pasFiltre or identifiant in filtreSet:
                self.personnes[identifiant] = (nom, prenom, dateNaissance, lieuNaissance, dateDejcehs, lieuDejcehs, dateMariage, lieuMariage)
            #print u'%d %s %s, N: %s à %s, D: %s à %s, M: %s à %s'%(identifiant, nom, prenom, dateNaissance, lieuNaissance, dateDejcehs, lieuDejcehs, dateMariage, lieuMariage)
        rapportGramps.close()
        print ('%d lignes lues dans %s'%(cmptLignes, nomRapportGramps))
        print ('%d ancestres trouvés'%(cmptAncestres))

    # calcule les ancestres manquants pour que chaque personne ait soit aucun parent, soit ses 2 parents
    def calculeManquants(self):
        for ident in self.personnes.keys():
            if ident %2 == 0:
                if ident+1 not in self.personnes: self.manquants.append(ident+1)
            else:
                if ident != 1 and ident-1 not in self.personnes: self.manquants.append(ident-1)
        print('{:d} identifiants ajoutés pour les calculs de géométrie'.format(len(self.manquants)))

    #extrait l'identifiant, le nom et le prénom (obligatoires !)
    def extraitIdentNomPrejnom(self, texte):
        #<p class="DAR-First-Entry">4. <strong>Sage, Claude Louis. </strong>Fils de Sage, Jean-Baptiste et Fayot, Claudine. Naissance : 5 août 1893 à Longessaigne.  Décédé(e) le 12 oct 1962 Chazelles sur Lyon.  Épousa Bourdon, Marguerite le 4 déc 1917 à Feurs. </p>
        match = re.match(u".*>([0-9]+)\. <strong>([\w -']*)\, ([\w -]+)(.*)", texte, re.UNICODE)
        if match: return (int(match.group(1)), match.group(2), match.group(3), match.group(4))
        #<p class="DAR-First-Entry">48. <strong>Monnier. </strong>Épousa Rey, Anne. </p>
        match = re.match(u".*>([0-9]+)\. <strong>([\w -']*)(.*)", texte, re.UNICODE)
        if match: return (int(match.group(1)), match.group(2), u'', match.group(3))
        print (texte)
        raise Exception('ERREUR MATCH 1 : %s'%(texte))
                    
    #extrait la date et le lieu de naissance
    def extraitNaissance(self, texte):
        #. </strong>Fils de Sage, Jean-Baptiste et Fayot, Claudine. Naissance : 5 août 1893 à Longessaigne.  Décédé(e) le 12 oct 1962 Chazelles sur Lyon.  Épousa Bourdon, Marguerite le 4 déc 1917 à Feurs. </p>
        match = re.match(u'.*Naissance : ([0-9]* [a-zéû]* [0-9]+) à ([\w -]+)(.*)', texte, re.UNICODE)
        if match: return (match.group(1), match.group(2), match.group(3))
        #</strong>Fille de Goguelat, Claude et Rouiller, Antoinette. Naissance : 22 septembre 1793.  Décédé(e) le 19 janvier 1870 Lavault-de-Frétoy.  </p>
        match = re.match(u'.*Naissance : ([0-9]* [a-zéû]* [0-9]+)(.*)', texte, re.UNICODE)
        if match: return (match.group(1), u'', match.group(2))        
        #. </strong>Né(e) en 1836 à Papiol.  Une relation avec Amigo Laramoves, Eulalia. </p>
        match = re.match(u'.*Né\(e\) en ([0-9]+) à ([\w -]+)(.*)', texte, re.UNICODE)
        if match: return (match.group(1), match.group(2), match.group(3))
        #. </strong>Fils de Aubert, Mathieu et Mure, Anne. Né(e) en 1769.  Épousa Chambon, Anne le 14 sept 1789 à Gumières. </p>
        match = re.match(u'.*Né\(e\) en ([0-9]+)(.*)', texte, re.UNICODE)
        if match: return (match.group(1), u'', match.group(2))
        #. </strong>Né(e) vers 1655 à Berne.  Décédé(e) le 16 janvier 1728 Longessaigne.  </p>
        match = re.match(u'.*Né\(e\) (vers [0-9]+) à ([\w -]+)(.*)', texte, re.UNICODE)
        if match: return (match.group(1), match.group(2), match.group(3))
        #. </strong>Fille de Roulier, Barthelemy et Rateau, Jeanne. Né(e) vers 1776.  Décédé(e) le 9 mars 1836 Planchez.  </p>
        match = re.match(u'.*Né\(e\) (vers [0-9]+)(.*)', texte, re.UNICODE)
        if match: return (match.group(1), u'', match.group(2))        
        #. </strong>Fils de Amigo Olivé, Francisco et Amigo Laramoves, Eulalia. Né(e) à Papiol.  Épousa Murray Jamana, Jacinta. </p>
        match = re.match(u'.*Né\(e\) à ([\w -]+)(.*)', texte, re.UNICODE)
        if match: return (u'', match.group(1), match.group(2))
        #. </strong>Né(e) entre 1854 et 1862.  Épousa Landas, Rosalie. </p>
        match = re.match(u'.*Né\(e\) (entre [0-9]+ et [0-9]+)(.*)', texte, re.UNICODE)
        if match: return (match.group(1), u'', match.group(2))        
        return (u'', u'', texte)
            
    #extrait la date et le lieu de décès
    def extraitDejcehs(self, texte):
        #.  Décédé(e) le 12 oct 1962 Chazelles sur Lyon.  Épousa Bourdon, Marguerite le 4 déc 1917 à Feurs. </p>
        match = re.match(u'.*Décédé\(e\) le ([0-9]* [a-zéû]* [0-9]+) ([\w -]+)\.(.*)', texte, re.UNICODE)
        if match: return (match.group(1), match.group(2), match.group(3))
        match = re.match(u'.*Décédé\(e\) le ([0-9]* [a-zéû]* [0-9]+)\.(.*)', texte, re.UNICODE)
        if match: return (match.group(1), u'', match.group(2))
        #.  Décédé(e) en 1834 à Disparu en mer.  Épousa Rio, Marie-Louise le 28 novembre 1815 à Quiberon. </p>
        match = re.match(u'.*Décédé\(e\) en ([0-9]+) à ([\w -]+)\.(.*)', texte, re.UNICODE)
        if match: return (match.group(1), match.group(2), match.group(3))
        match = re.match(u'.*Décédé\(e\) en ([a-zéû]* [0-9]+) ([\w -]+)\.(.*)', texte, re.UNICODE)
        if match: return (match.group(1), match.group(2), match.group(3))
        #.  Décédé(e) en 1975-07-00.  Épousa Sendra Casas, Leonor. </p>
        match = re.match(u'.*Décédé\(e\) en ([a-zéû]* [0-9]+)\.(.*)', texte, re.UNICODE)
        if match: return (match.group(1), u'', match.group(2))
        match = re.match(u'.*Décédé\(e\) en ([0-9]+) ([\w -]+)\.(.*)', texte, re.UNICODE)
        if match: return (match.group(1), match.group(2), match.group(3))
        match = re.match(u'.*Décédé\(e\) en ([0-9]+)\.(.*)', texte, re.UNICODE)
        if match: return (match.group(1), u'', match.group(2))
        #Décédé(e) le avant 1804 Saint-Martin-Lestra.  Épousa Marchand, Claudine.
        match = re.match(u'.*Décédé\(e\) le ([0-9a-zè ]+) ([\w -]+)\.(.*)', texte, re.UNICODE)
        if match: return (match.group(1), match.group(2), match.group(3))
        #Décédé(e) le entre 1769 et 1778.
        #match = re.match(u'.*Décédé\(e\) le (entre [0-9]+ et [0-9]+)\.(.*)', texte, re.UNICODE)
        match = re.match(u'.*Décédé\(e\) le ([0-9a-zè ]+)\.(.*)', texte, re.UNICODE)
        if match: return (match.group(1), u'', match.group(2))
        return (u'', u'', texte)
        
    #extrait la date et le lieu du mariage
    def extraitMariage(self, texte):
        #.  Épousa Bourdon, Marguerite le 4 déc 1917 à Feurs. </p>
        match = re.match(u'.* le ([0-9]* [a-zéû]* [0-9]+) à ([\w -]+)\.(.*)', texte, re.UNICODE)
        if match: return (match.group(1), match.group(2), match.group(3))
        match = re.match(u'.* le ([0-9]* [a-zéû]* [0-9]+)\.(.*)', texte, re.UNICODE)
        if match: return (match.group(1), u'', match.group(2))
        #.  Épousa Gras, Jeanne-Marie avant 1799. </p>
        match = re.match(u'.* (avant [0-9]+) à ([\w -]+)\.(.*)', texte, re.UNICODE)
        if match: return (match.group(1), match.group(2), match.group(3))
        match = re.match(u'.* (avant [0-9]+)\.(.*)', texte, re.UNICODE)
        if match: return (match.group(1), u'', match.group(2))
        #.  Épousa Plantagenêt, Eléonore en septembre 1177 à Burgos. </p>
        #.  Épousa de Castille, Berenguela en 1197 à Valladolid. </p>
        match = re.match(u'.* en ([a-zéû ]*[0-9]+) à ([\w -]+)\.(.*)', texte, re.UNICODE)
        if match: return (match.group(1), match.group(2), match.group(3))
        #.  Épousa Plantagenêt, Eléonore en septembre 1177. </p>
        #.  Épousa de Castille, Berenguela en 1197. </p>
        match = re.match(u'.* en ([a-zéû ]*[0-9]+)\.(.*)', texte, re.UNICODE)
        if match: return (match.group(1), u'', match.group(2))
        #.  Épousa Plantagenêt, Eléonore vers septembre 1177. </p>
        #.  Épousa de Castille, Berenguela vers 1197. </p>
        match = re.match(u'.* (vers [a-zéû ]*[0-9]+)\.(.*)', texte, re.UNICODE)
        if match: return (match.group(1), u'', match.group(2))
        
        return (u'', u'', texte)
         
    #retourne le nombre total d'ancestres connus
    def nombreTotal(self):
        return len(self.personnes)
        
    #retourne le nombre d'ancestres connus d'un identifiant donné
    def nombreAncestres(self, identifiant):
        if identifiant not in self.personnes: return 0
        nombreAncestresPaternels = self.nombreAncestres(identifiant*2)
        nombreAncestresMaternels = self.nombreAncestres(identifiant*2 +1)
        return 1 + nombreAncestresPaternels + nombreAncestresMaternels
        
    #retourne le nombre d'ancestres paternels connus d'un identifiant donné
    def nombreAncestresPaternels(self, identifiant):
        if identifiant not in self.personnes: return 0
        return self.nombreAncestres(identifiant*2)
       
    #retourne le nombre d'ancestres maternels connus d'un identifiant donné
    def nombreAncestresMaternels(self, identifiant):
        if identifiant not in self.personnes: return 0
        return self.nombreAncestres(identifiant*2 +1)
       
    #retourne les attributs d'un ancêtre repéré par son identifiant
    def attributs(self, identifiant):
        if identifiant not in self.personnes: return ('', '', '', '', '', '', '', '')
        return self.personnes[identifiant]
        
    #retourne le numéro de génération d'un identifiant (de 1 à n)
    def gejnejration(self, identifiant):
        return int(log2(identifiant))
        
    #retourne le numéro de génération maximum de l'arbre
    def maxGejnejration(self):
        tous = self.personnes.keys()
        tous.sort()
        return self.gejnejration(tous[-1])
        
    #retourne la liste ordonnée des identifiants des pères extrêmes d'un individu, y compris l'individu
    def limitesHautes(self, identifiant):
        resultat = []
        ascendants = self.ascendants(identifiant)
        ascendants.sort()
        prochaineGejnejration = identifiant 
        for ascendant in ascendants:
            if ascendant < prochaineGejnejration: continue
            resultat.append(ascendant)  #prend le plus haut de la gejnejration (qui a l'identifiant le plus bas)
            prochaineGejnejration *= 2
        return resultat
                      
    #retourne la liste ordonnée des identifiants des mères extrêmes d'un individu, y compris l'individu
    def limitesBasses(self, identifiant):
        resultat = []
        ascendants = self.ascendants(identifiant)
        ascendants.sort()
        ascendants.reverse()    
        prochaineGejnejration = identifiant 
        while prochaineGejnejration <= ascendants[0]: prochaineGejnejration *= 2
        for ascendant in ascendants:
            if ascendant >= prochaineGejnejration: continue
            resultat.append(ascendant) #prend le plus bas de la gejnejration (qui a l'identifiant le plus haut)
            prochaineGejnejration //= 2
        resultat.reverse()
        return resultat
    
    #retourne l'identifiant de la mère extrême
    def mehreExtresme(self):
        identifiant = 1
        identifiantMere = identifiant *2 +1
        while identifiantMere in self.personnes: 
            identifiant = identifiantMere
            identifiantMere = identifiantMere *2 +1
        return identifiant
                      
    ##retourne la liste ordonnée des identifiants des pères extrêmes d'un individu
    #def peresExtresmes(self, identifiant):
        #resultat = []
        #identifiantPere = identifiant * 2
        #while identifiantPere in self.personnes: 
            #resultat.append(identifiantPere)
            #identifiantPere = identifiantPere * 2
        #return resultat
                      
    ##retourne la liste ordonnée des identifiants des mères extrêmes d'un individu
    #def mehresExtresmes(self, identifiant):
        #resultat = []
        #identifiantMere = identifiant * 2 + 1
        #while identifiantMere in self.personnes: 
            #resultat.append(identifiantMere)
            #identifiantMere = identifiantMere * 2 + 1
        #return resultat
                      
    #retourne la liste des identifiants des ascendants d'un individu spécifié par son identifiant
    def ascendants(self, identifiant):
        if identifiant not in self.personnes and identifiant not in self.manquants: return []
        resultat = [identifiant]
        resultat.extend(self.ascendants(identifiant*2))
        resultat.extend(self.ascendants(identifiant*2 +1))
        return resultat
                      
    #retourne la répartition par génération du nombre d'ancestres connus
    def rejpartitionParGejnejration(self):
        resultat = {}
        for identifiant in self.personnes.keys():
            gejnejration = 0
            while identifiant >= 2**gejnejration: gejnejration +=1
            if gejnejration not in resultat: resultat[gejnejration] = 0
            resultat[gejnejration] +=1
        return resultat
        
    #retourne tous les identifiants des ancestres connus
    def tousIdentifiants(self):
        resultat = list(self.personnes.keys())
        resultat.sort()
        return resultat
        
    #retourne tous les identifiants des ancestres manquants
    def lesManquants(self):
        return self.manquants
        
    #retourne tous les identifiants des ancestres connus 4 par gejnejration (1, 2, 3, 4, 5, 6, 7, 8, 9, 12, 13, 16, 17, 24, 25, etc.)
    def tousIdentifiants4parGen(self):
        filtre = set([1, 2, 3])
        for gen in range(1,12):
            filtre.add(2*(2**gen))
            filtre.add(2*(2**gen)+1)
            filtre.add(3*(2**gen))
            filtre.add(3*(2**gen)+1)
        resultat = list(set(self.personnes.keys()) & filtre)
        resultat.sort()
        return resultat
        
    
if __name__ == '__main__':
    main()

            
