#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
__author__ = "jys"
__copyright__ = "Copyright (C) 2014 LATEJCON"

import sys
import os
import datetime
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import cm
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.lib.styles import getSampleStyleSheet

def usage():
    print ("""© l'ATEJCON.  
Programme de test de la classe AncestresPdfImprimable. Il crée simplement
une page de test.

La classe AncestresPdfImprimable crée un fichier PDF imprimable représentant 
un arbre généalogique. 
o le fichier est composé de plusieurs pages découpables et raboutables.
o les positionnements en horizontal sont donnés par le n° de génération
o les positionnements en vertical sont donnés par un numéro d'ordre
o chaque ancêtre est créé avec son positionnement et ses attributs
o les liens entre ancêtres sont dessinés
o la date de mariage est écrite

usage   : %s <n'importe quoi> 
example : %s toto
"""%(sys.argv[0], sys.argv[0]))

def main():
    os.chdir(sys.path[0])
    if len(sys.argv) < 2 :
        usage()
        sys.exit()
        
    #nom du fichier
    racine = '/'.join(os.path.dirname(sys.argv[0]).split('/')[:-1])
    nomFichierSortie = '%s/rejsultat/AncestresPdfImprimable-test'%(racine)
    nomsFichiersSortie = (nomFichierSortie + '-G.pdf', nomFichierSortie + '-P.pdf')
    ancestresPdfImprimable = AncestresPdfImprimable(nomsFichiersSortie, 'filigrane', 'titre', 'echiquierLatejcon4-150.png', ["l'air de rien"])
    positions = [(1, (0, 12.0)), (2, (1, 10.5)), (3, (1, 13.5)), (4, (2, 9.0)), (5, (2, 12.0)), (8, (3, 7.5)), (9, (3, 10.5)), (16, (4, 6.0)), (17, (4, 9.0)), (34, (5, 7.5)), (35, (5, 10.5)), (68, (6, 6.0)), (69, (6, 9.0)), (1142889469, (0, 19.5)), (2285778938, (1, 18.0)), (2285778939, (1, 21.0)), (4571557878, (2, 19.5)), (4571557879, (2, 22.5)), (9143115758, (3, 21.5)), (9143115759, (3, 23.5))]
    for (numejro, (rang_h, rang_v)) in positions:
        ancestresPdfImprimable.ajouteAncestre(numejro, rang_h, rang_v, str(numejro), '', str(rang_h), '', str(rang_v), '')
        ancestresPdfImprimable.ajouteLien(numejro, numejro*2, numejro*2+1)
    ancestresPdfImprimable.vertical2(10)
    ancestresPdfImprimable.termine()

M_H = 1.0*cm            #marge haute
M_B = 0.1*cm            #marge basse (0 si imprimante borderless)
M_G = 1.0*cm            #marge gauche
M_D = 0.1*cm            #marge droite (0 si imprimante borderless)
D_G = 0.25*cm           #dejcalage horizontal pour ejloigner les rectangles du bord gauche des pages
D_H = 0.65*cm           #dejcalage de dejpart
#D_H = 0.0*cm           #dejcalage de dejpart
N_REC_X = 6             #nombre de rectangles par page en largeur
N_REC_XL = 3            #nombre de rectangles longs par page en largeur
ESP_X = 0.7*cm          #longueur espace
# longueur page = landscape(A4)[0] = M_G + (REC_X + ESP_X) * N_REC_X + M_D
# c'est REC_X qui est la variable d'ajustement en fonction des autres valeurs 
#REC_X = (landscape(A4)[0] - M_G - M_D) / N_REC_X - ESP_X
REC_Y = 1.1*cm          #hauteur rectangle
REC_YL = 0.8*cm         #hauteur rectangle long
#C_G = 1.0*cm            #cartouche
C_G = 41.0*cm            #cartouche
ESP_Y = -8             #hauteur espace
#ESP_Y = -3              #hauteur espace
MH_REC = 9              #marge haute dans rectangle
MG_REC = 3              #marge gauche dans rectangle
MD_REC = 3              #marge droite dans rectangle
P_NOM = 8               #police du nom 
P_DATE = 7              #police des dates
P_FILI = 20             #police filigrane
P_TITRE1 = 30           #police titre 1
P_TITRE2 = 20           #police titre 2
P_TITRE3 = 12           #police titre 3
RANG_RACINE = 0         #position de la racine (0 = max à gauche)

    
class AncestresPdfImprimable:
    def __init__(self, nomsFichiersSortie, filigrane, titre, image, statistiques, enLongueur=False):
        self.enLongueur = enLongueur
        if enLongueur:
            self.n_rec_x = N_REC_XL
            self.rec_y = REC_YL
        else:
            self.n_rec_x = N_REC_X
            self.rec_y = REC_Y
        # c'est rec_x qui est la variable d'ajustement en fonction des autres valeurs 
        self.rec_x = (landscape(A4)[0] - M_G - M_D) / self.n_rec_x - ESP_X
        
        self.nomFichierGlobal = nomsFichiersSortie[0]
        self.nomFichierPages = nomsFichiersSortie[1]
        self.filigrane = filigrane
        self.titre = titre
        self.image = image
        self.statistiques = statistiques
        self.ancestres = {}
        self.positionsAncestres = []
        self.liensGauches = []
        self.liensDroits = []
        self.liens = []
        self.mariages = []
        self.mariages2 = {}
        self.ident = -13

    # accueille un nouvel ancestre
    def ajouteAncestre(self, identifiant, rang_h, rang_v, nomPrejnom, dateN, lieuN, dateD, lieuD, enGris=False):
        donnejes = (nomPrejnom, dateN, lieuN, dateD, lieuD, enGris)
        self.ancestres[identifiant] = [donnejes]
        self.positionsAncestres.append((rang_v, rang_h, identifiant))
        
    # accueille un nouvel ensemble de liens gauches
    def ajouteLiensGauches(self, individus):
        self.liensGauches.append(individus)
        
    # accueille un nouvel ensemble de liens droits
    def ajouteLiensDroits(self, individus):
        self.liensDroits.append(individus)
        
    # accueille un nouveau mariage 
    def ajouteMariage2(self, rang_h, rang_v, dateMariage, lieuMariage):
        donnejes = (dateMariage, lieuMariage)
        self.mariages2[(self.ident, )] = [donnejes]
        self.positionsAncestres.append((rang_v, rang_h, (self.ident, )))
        self.ident -=1
        
    #accueille un nouveau lien entre un ancestre et son pehre et sa mehre, s'ils existent
    def ajouteLien(self, identifiant, identifiantPehre, identifiantMehre):
        self.liens.append((identifiant, identifiantPehre, identifiantMehre))
        
    #accueille la date et le lieu du mariage devant le rectangle du descendant
    def ajouteMariage(self, identifiant, identifiantEnfant, dateMariage, lieuMariage):
        self.mariages.append((identifiant, identifiantEnfant, dateMariage, lieuMariage))
        
    #donne le rang vertical du pehre pour le calcul antitejlescopage avec le cartouche
    def vertical2(self, v_2):
        self.v_2 = v_2
        
    #construit le pdf
    def termine(self):
        #1) trouve l'offset de cartouche pour prejvenir le tejlescopage
        self.can = canvas.Canvas(self.nomFichierGlobal, pagesize=(1000, 1000))
        self.max_y = 1000       # maximum provisoire pour simuler l'ejcriture du cartouche
        y_cartouche = self.ejcritTitre() - 1.0*cm       #la coordonneje verticale du cartouche
        y_2 = 1000 - M_H - D_H - (self.rec_y + ESP_Y) * self.v_2
        if y_2 > y_cartouche: y_tejlescopage = y_2 - y_cartouche
        else: y_tejlescopage = 0
        #print('y_cartouche=', y_cartouche, 'y_2=', y_2, 'y_tejlescopage=', y_tejlescopage)

        #2) classe les ancestres par ordre de verticalitej
        self.positionsAncestres.sort()
        
        #3) calcule les x et les y de chaque ancestre ainsi que les maximums
        max_x = max_y = 0
        # l'offset vertical pour respecter la pagination 
        #self.offset_y = y_tejlescopage + D_H + self.rec_y
        self.offset_y = D_H + self.rec_y
        # le premier n'est pas forcejment ah zejro
        (premier_v, raf, raf) = self.positionsAncestres[0]
        for (rang_v, rang_h, identifiant) in self.positionsAncestres:
            x = self.calculeX(rang_h)
            y = self.calculeY(rang_v - premier_v)
            max_x = max(max_x, x)
            max_y = max(max_y, y)
            if isinstance(identifiant, tuple) and identifiant[0] < 0 :
                self.mariages2[identifiant].append((x, y))
            else:
                self.ancestres[identifiant].append((x, y))
                #print(self.ancestres[identifiant])
        self.nbPages_x = int(max_x/landscape(A4)[0]) +1
        self.nbPages_y = int(max_y/landscape(A4)[1]) +1
        self.max_x = self.nbPages_x * landscape(A4)[0]
        self.max_y = self.nbPages_y * landscape(A4)[1]

        #print('self.ancestres=', self.ancestres)
        #print('self.mariages2=', self.mariages2)
        #print('self.liensGauches=', self.liensGauches)
        #print('self.liensDroits=', self.liensDroits)
        
        #4) écrit un grand pdf 
        self.can = canvas.Canvas(self.nomFichierGlobal, pagesize=(landscape(A4)[0]*self.nbPages_x, landscape(A4)[1]*self.nbPages_y))          
        self.ejcritFiligrane()
        self.dessineArbre()
        self.ejcritTitre()
        self.marquesDejcoupage()
        self.can.showPage()
        self.can.save()
        
        #5) écrit le fichier imprimable en plusieurs pages
        self.can = canvas.Canvas(self.nomFichierPages, pagesize=landscape(A4))
        for page_y in range(self.nbPages_y):
            for page_x in range(self.nbPages_x):
                self.ejcritFiligrane()
                self.can.saveState()
                self.can.translate(- landscape(A4)[0] * page_x, 0)
                self.max_y = landscape(A4)[1] * (page_y + 1)
                self.dessineArbre()
                self.ejcritTitre()
                self.can.restoreState()
                self.marquesDejcoupagePage(page_x, page_y)
                self.can.showPage()
        self.can.save()      
        
    #dessine tout l'arbre
    def dessineArbre(self):
        #dessine tous les mariages
        for (identifiant, identifiantEnfant, dateMariage, lieuMariage) in self.mariages:
            self.ejcritMariage(identifiant, identifiantEnfant, dateMariage, lieuMariage)
        #dessine tous les ancestres
        for (nomPrejnom, dateN, lieuN, dateD, lieuD, enGris), (x, y) in self.ancestres.values():
            self.dessineAncestre(x, y, nomPrejnom, dateN, lieuN, dateD, lieuD, enGris)
            
        #dessine tous les mariages
        for (dateMariage, lieuMariage), (x, y) in self.mariages2.values():
            self.ejcritMariage2(x, y, dateMariage, lieuMariage)
            
        #dessine tous les liens
        for (identifiant, identifiantPehre, identifiantMehre) in self.liens:
            self.dessineLien(identifiant, identifiantPehre, identifiantMehre)
        # dessine liens gauches
        for individus in self.liensGauches:
            l_x = 0
            les_y = []
            for individu in individus:
                if individu in self.ancestres:
                    (x, y) = self.ancestres[individu][1]
                    l_x = x
                    les_y.append(y)
            if len(les_y) != 0:
                self.dessineLiensGauches(l_x, les_y)
        
        # dessine liens droits
        for individus in self.liensDroits:
            l_x = 0
            les_y = []
            for individu in individus:
                if individu in self.ancestres:
                    (x, y) = self.ancestres[individu][1]
                    l_x = x
                    les_y.append(y)
            if len(les_y) != 0:
                self.dessineLiensDroits(l_x, les_y)
        
    #dessine un nouvel ancestre
    def dessineAncestre(self, x, y, nomPrejnom, dateN, lieuN, dateD, lieuD, enGris):
        #bricole les lieux pour permettre le "disparu en mer"
        if len(lieuN) != 0 and lieuN[0].isupper(): lieuN = u'à ' + lieuN
        if len(lieuD) != 0 and lieuD[0].isupper(): lieuD = u'à ' + lieuD
        #le x est ok, le y est inversé
        y = self.max_y - y
        if enGris: self.can.setFillGray(0.85)
        else: self.can.setFillColor(colors.white)
        self.can.rect(x, y, self.rec_x, self.rec_y, fill=1)
        self.can.setFillColor(colors.black)
        texte = self.can.beginText()
        texte.setTextOrigin(x + MG_REC, y + self.rec_y - MH_REC)
        self.ejcritLigneLimiteje(texte, nomPrejnom, 'Helvetica-Bold', P_NOM)
        if dateN != '' or lieuN != '': dateLieuN = u'n {} {}'.format(dateN, lieuN)
        else : dateLieuN = ''
        if dateD != '' or lieuD != '': dateLieuD = u'\u2020 {} {}'.format(dateD, lieuD)
        else : dateLieuD = ''
        if self.enLongueur:
            self.ejcritLigneLimiteje(texte, u'{}  {}'.format(dateLieuN, dateLieuD), 'Helvetica', P_DATE)
        else:
            self.ejcritLigneLimiteje(texte, dateLieuN, 'Helvetica', P_DATE)
            self.ejcritLigneLimiteje(texte, dateLieuD, 'Helvetica', P_DATE)
        self.can.drawText(texte)
        
    # ejcrit mariage 
    def ejcritMariage2(self, x, y, dateMariage, lieuMariage):
        #print('ejcritMariage2 ', 'dateMariage=', dateMariage, 'lieuMariage=', lieuMariage)
        #le x est ok, le y est inversé
        y1 = self.max_y - y
        texte = self.can.beginText()
        texte.setTextOrigin(x, y1)
        texte.setFont("Helvetica-Bold", P_DATE)
        if dateMariage != '' and lieuMariage != '': texte.textLine(f'm {dateMariage} à {lieuMariage}')
        elif dateMariage != '': texte.textLine(f'm {dateMariage}')
        elif lieuMariage != '': texte.textLine(f'm à {lieuMariage}')
        self.can.drawText(texte)
        
    #tronque eventuellement la ligne et l'ejcrit 
    def ejcritLigneLimiteje(self, texte, ligne, police, taille):
        index = len(ligne)
        while stringWidth(ligne[:index], police, taille) > self.rec_x-MD_REC: index -=1
        texte.setFont(police, taille)
        texte.textLine(ligne[:index])

    # dessine un lien gauche entre individus (arbre descendants)
    def dessineLiensGauches(self, l_x, les_y):
        les_y.sort()
        x1 = l_x
        x2 = x1 - ESP_X /3
        # dessine les traits horizontaux
        for y in les_y:
            #le x est ok, le y est inversé
            y = self.max_y - y + self.rec_y / 2
            self.can.line(x1, y, x2, y)
        # dessine le trait vertical
        x = x2
        y1 = self.max_y - les_y[0] + self.rec_y / 2
        y2 = self.max_y - les_y[-1] + self.rec_y / 2
        self.can.line(x, y1, x, y2)
                
    # dessine un lien droit entre individus (arbre descendants)
    def dessineLiensDroits(self, l_x, les_y):
        les_y.sort()
        x1 = l_x + self.rec_x
        x2 = x1 + ESP_X /3
        # dessine les traits horizontaux
        for y in les_y:
            #le x est ok, le y est inversé
            y = self.max_y - y + self.rec_y / 2
            self.can.line(x1, y, x2, y)
        # dessine le trait vertical
        x = x2
        y1 = self.max_y - les_y[0] + self.rec_y / 2
        y2 = self.max_y - les_y[-1] + self.rec_y / 2
        self.can.line(x, y1, x, y2)
        # dessine le trait horizontal vers les parents
        x3 = x2 + ESP_X /3
        if x3 % landscape(A4)[0] <= M_G: x3 += M_D + M_G
        y1 = les_y[0] - self.rec_y / 2
        y2 = les_y[-1] - self.rec_y / 2
        y = (y1 + y2) / 2
        # il est possible que ce trait tombe dans l'inter-page
        y_relatif = y % landscape(A4)[1]
        if y_relatif < M_H:
            #print('y=', y, 'y_relatif=', y_relatif, 'M_H=', M_H)
            y += M_H - y_relatif
            #print('y=', y)
        #le x est ok, le y est inversé
        y = self.max_y - y
        self.can.line(x2, y, x3, y)

    #dessine un nouveau lien entre un ancestre et son pehre et sa mehre, s'ils existent
    def dessineLien(self, identifiant, identifiantPehre, identifiantMehre):
        #rien à faire si ni pehre ni mehre
        if identifiantPehre not in self.ancestres and identifiantMehre not in self.ancestres: return
        #numejro de page horizontale
        #dessine le segment en partance vers les parents
        (x, y) = self.ancestres[identifiant][1]
        x1 = x + self.rec_x
        y1 = self.max_y - y + self.rec_y / 2
        x2 = x1 + ESP_X / 3
        #y2 = y1
        self.can.line(x1, y1, x2, y1)
        #dessine les attaches sur les parents
        if identifiantPehre in self.ancestres:
            (x4, y) = self.ancestres[identifiantPehre][1]
            #x3 = x2
            y3 = self.max_y - y + self.rec_y / 2
            self.can.line(x2, y1, x2, y3)
            self.can.line(x2, y3, x4, y3)
        if identifiantMehre in self.ancestres:
            (x4, y) = self.ancestres[identifiantMehre][1]
            #x5 = x2
            #x6 = x4
            y5 = self.max_y - y + self.rec_y / 2
            self.can.line(x2, y1, x2, y5)
            self.can.line(x2, y5, x4, y5)

    #dessine la date et le lieu du mariage devant le rectangle du descendant
    def ejcritMariage(self, identifiant, identifiantEnfant, dateMariage, lieuMariage):
        (x, y) = self.ancestres[identifiant][1]
        x1 = x + MG_REC
        (x, y) = self.ancestres[identifiantEnfant][1]
        y1 = self.max_y - y + self.rec_y / 2 - 3
        texte = self.can.beginText()
        texte.setTextOrigin(x1, y1)
        texte.setFont("Helvetica-Bold", P_DATE)
        if dateMariage != '' and lieuMariage != '': texte.textLine(u'm %s à %s'%(dateMariage, lieuMariage))
        elif dateMariage != '': texte.textLine(u'm %s'%(dateMariage))
        elif lieuMariage != '': texte.textLine(u'm à %s'%(lieuMariage))
        self.can.drawText(texte)
        
    #calcule le x du coin bas gauche de l'ancestre
    def calculeX(self, rang_h):
        rang = rang_h + RANG_RACINE
        # numéro de page horizontale
        xpage = rang // self.n_rec_x
        # calcule le x du coin bas gauche du rectangle
        # avec imprimante 100% : M_D = 0
        return M_G + D_G + (M_G + M_D) * xpage + (self.rec_x + ESP_X) * rang
        
    #calcule le y du coin bas gauche de l'ancestre
    def calculeY(self, rang_v):
        #print('rang_v=', rang_v)
        # la pagination des y est progressive, c'est pour ça qu'ils sont ordonnejs
        y = self.offset_y  + (self.rec_y + ESP_Y) * rang_v
        y_relatif = y % landscape(A4)[1]
        if y != y_relatif:
            # traitement de haut de page, pas pour la premiehre
            #if y_relatif < M_H + self.rec_y:
            # les nombres rejels sont malpratiques en addition, sosutraction et comparaison
            if y_relatif - M_H - self.rec_y < -0.001:
                #print('rang_v=', rang_v, 'y=', y, 'y_relatif=', y_relatif, 'M_H + self.rec_y=', M_H + self.rec_y)
                if y_relatif < self.rec_y:
                    # cas d'un individu sur les 2 pages
                    self.offset_y += M_H + self.rec_y - y_relatif
                else:
                    # cas d'un individu entiehrement sur la 2ehme page
                    self.offset_y += M_H
                y = self.offset_y + (self.rec_y + ESP_Y) * rang_v
                #print('y=', y)
        # traitement de bas de page
        # avec imprimante 100% : M_B = 0, on ne passe jamais lah
        if y_relatif > landscape(A4)[1] - M_B:
            self.offset_y += landscape(A4)[1] + M_H + self.rec_y - y_relatif
            y = self.offset_y + (self.rec_y + ESP_Y) * rang_v
        return y
         
    # ejcrit les marques de dejcoupage
    def marquesDejcoupage(self):
        #des lignes bleues
        # avec imprimante 100% : M_D = 0, M_B = 0
        self.can.saveState()
        self.can.setStrokeColor(colors.blue)
        for page in range(self.nbPages_x):
            self.can.setDash(1,4)
            marge_gauche = landscape(A4)[0] * page + M_G
            self.can.line(marge_gauche, 0, marge_gauche, self.max_y)      #verticale gauche
            marge_droite = landscape(A4)[0] * (page + 1) - M_D
            self.can.line(marge_droite, 0, marge_droite, self.max_y)      #verticale droite
            self.can.setDash(1,0)
            fin_page = landscape(A4)[0] * (page + 1)
            self.can.line(fin_page, 0, fin_page, self.max_y)              #verticale
            
        for page in range(self.nbPages_y):
            self.can.setDash(1,4)
            marge_basse = landscape(A4)[1] * page + M_B
            self.can.line(0, marge_basse, self.max_x, marge_basse)        #horizontale basse
            marge_haute = landscape(A4)[1] * (page +1) - M_H
            self.can.line(0, marge_haute, self.max_x, marge_haute)        #horizontale haute
            self.can.setDash(1,0)
            fin_page = landscape(A4)[1] * (page + 1)
            self.can.line(0, fin_page, self.max_x, fin_page)              #horizontale
        self.can.restoreState()
        
    # ejcrit les marques de dejcoupage pour la page courante
    def marquesDejcoupagePage(self, page_x, page_y):
        # avec imprimante 100% : M_D = 0, M_B = 0
        okg = page_x != 0
        okd = page_x != self.nbPages_x -1
        okh = page_y != 0
        okb = page_y != self.nbPages_y -1
        self.can.saveState()
        self.can.setStrokeColor(colors.grey)
        largeur = landscape(A4)[0]
        marge_gauche = M_G - 0.1*cm
        marge_droite = largeur - M_D + 0.1*cm
        hauteur = landscape(A4)[1]
        marge_haute = hauteur - M_H  + 0.1*cm
        marge_basse = M_B - 0.1*cm
        if okg: 
            self.can.line(marge_gauche, hauteur, marge_gauche, marge_haute-1*cm)                    #verticale gauche haute
            self.can.line(marge_gauche, 0, marge_gauche, marge_basse+1*cm)                                  #verticale gauche basse
        if okd:
            self.can.line(marge_droite, hauteur, marge_droite, marge_haute-1*cm)  #verticale droite haute
            self.can.line(marge_droite, 0, marge_droite, marge_basse+1*cm)                #verticale droite basse
        if okh:
            self.can.line(0, marge_haute, marge_gauche+1*cm, marge_haute)                  #horizontale gauche haute
            self.can.line(largeur, marge_haute, marge_droite-1*cm, marge_haute)   #horizontale droite haute
        if okb:
            self.can.line(0, marge_basse, marge_gauche+1*cm, marge_basse)                                  #horizontale gauche basse
            self.can.line(largeur, marge_basse, marge_droite-1*cm, marge_basse)                   #horizontale droite basse
        self.can.restoreState()
        
    def ejcritFiligrane(self):
        self.can.saveState()
        #self.can.rect(1*cm,1*cm,10*cm,8*cm, fill=1)
        #self.can.rotate(45)
        self.can.setFillColor(colors.paleturquoise)
        texte = self.can.beginText()
        texte.setTextOrigin(11*cm, 3*cm)
        #texte.setTextOrigin(landscape(A4)[0]/2, landscape(A4)[1]/2)
        self.can.rotate(45)
        texte.setFont("Helvetica-Oblique", P_FILI)
        for i in range(15):
            for j in range (1):
                texte.textOut(self.filigrane)
            texte.textLine()
        self.can.drawText(texte)
        self.can.restoreState()
        
    def ejcritTitre(self):
        maintenant = datetime.datetime.today()
        mois = (u'', u'janvier', u'février', u'mars', u'avril', u'mai', u'juin', u'juillet', u'août', u'septembre', u'octobre', u'novembre', u'décembre')[int(maintenant.month)]
        self.can.saveState()
        #tentative de transparence dans l'image
        #self.can.drawImage(self.image, C_G, self.max_y-(6.5*cm), mask=(0,255,0,255,0,255))
        self.can.drawImage(self.image, C_G, self.max_y-(6.5*cm), mask='auto')
        texte = self.can.beginText()
        texte.setTextOrigin(C_G, self.max_y - M_H * 2)
        texte.setFont("Helvetica-Bold", P_TITRE1)
        texte.textLine(self.titre[0])
        texte.textLine(self.titre[1])
        texte.setFont("Helvetica-Bold", P_TITRE2)
        texte.textLine(u'ejlaboré le %s %s %s par'%(maintenant.day, mois, maintenant.year))  
        texte.setTextOrigin(C_G, self.max_y - 7*cm)
        texte.setFont("Courier-Bold", P_TITRE3)
        for ligne in self.statistiques: texte.textLine(ligne)
        self.can.drawText(texte)
        self.can.restoreState()
        max_y = texte.getY()        #position verticale du curseur apres le cartouche
        return max_y 

            
if __name__ == '__main__':
    main()
