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
M_B = 0.0*cm            #marge basse (0 si imprimante borderless)
M_G = 1.0*cm            #marge gauche
M_D = 0.0*cm            #marge droite (0 si imprimante borderless)
D_G = 0.25*cm           #dejcalage horizontal pour ejloigner les rectangles du bord gauche des pages
D_H = 1.25*cm           #dejcalage de dejpart
N_REC_X = 6             #nombre de rectangles par page en largeur
ESP_X = 0.7*cm          #longueur espace
# longueur page = landscape(A4)[0] = M_G + (REC_X + ESP_X) * N_REC_X + M_D
# c'est REC_X qui est la variable d'ajustement en fonction des autres valeurs 
REC_X = (landscape(A4)[0] - M_G - M_D) / N_REC_X - ESP_X
REC_Y = 1.1*cm          #hauteur rectangle
C_G = 1.0*cm            #cartouche
#ESP_Y = -8             #hauteur espace
ESP_Y = -3              #hauteur espace
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
    def __init__(self, nomsFichiersSortie, filigrane, titre, image, statistiques):
        self.nomFichierGlobal = nomsFichiersSortie[0]
        self.nomFichierPages = nomsFichiersSortie[1]
        self.filigrane = filigrane
        self.titre = titre
        self.image = image
        self.statistiques = statistiques
        self.ancestres = {}
        self.positionsAncestres = []
        self.liens = []
        self.mariages = []

    #accueille un nouvel ancestre
    def ajouteAncestre(self, identifiant, rang_h, rang_v, nom, prejnom, dateN, lieuN, dateD, lieuD):
        donnees = (nom, prejnom, dateN, lieuN, dateD, lieuD)
        self.ancestres[identifiant] = [donnees]
        self.positionsAncestres.append((rang_v, rang_h, identifiant))
        
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
        self.max_y = 1000
        y_cartouche = self.ejcritTitre()       #la coordonneje verticale du cartouche
        y_2 = 1000 - M_H - D_H - (REC_Y + ESP_Y) * self.v_2
        if y_2 > y_cartouche: self.y_tejlescopage = y_2 - y_cartouche
        else: self.y_tejlescopage = 0

        #2) classe les ancestres par ordre de verticalitej
        self.positionsAncestres.sort()
        
        #3) calcule les x et les y de chaque ancestre ainsi que les maximums
        max_x = max_y = 0
        self.offset_y = 0
        for (rang_v, rang_h, identifiant) in self.positionsAncestres:
            x = self.calculeX(rang_h)
            y = self.calculeY(rang_v)
            max_x = max(max_x, x)
            max_y = max(max_y, y)
            self.ancestres[identifiant].append((x, y))
        self.nbPages_x = int(max_x/landscape(A4)[0]) +1
        self.nbPages_y = int(max_y/landscape(A4)[1]) +1
        self.max_x = self.nbPages_x * landscape(A4)[0]
        self.max_y = self.nbPages_y * landscape(A4)[1]
        
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
        for (nom, prejnom, dateN, lieuN, dateD, lieuD), (x, y) in self.ancestres.values():
            self.dessineAncestre(x, y, nom, prejnom, dateN, lieuN, dateD, lieuD)
        #dessine tous les liens
        for (identifiant, identifiantPehre, identifiantMehre) in self.liens:
            self.dessineLien(identifiant, identifiantPehre, identifiantMehre)
        
        
    #dessine un nouvel ancestre
    def dessineAncestre(self, x, y, nom, prejnom, dateN, lieuN, dateD, lieuD):
        #bricole les lieux pour permettre le "disparu en mer"
        if len(lieuN) != 0 and lieuN[0].isupper(): lieuN = u'à ' + lieuN
        if len(lieuD) != 0 and lieuD[0].isupper(): lieuD = u'à ' + lieuD
        #le x est ok, le y est inversé
        y = self.max_y - y
        self.can.setFillColor(colors.white)
        self.can.rect(x, y, REC_X, REC_Y, fill=1)
        self.can.setFillColor(colors.black)
        texte = self.can.beginText()
        texte.setTextOrigin(x + MG_REC, y + REC_Y - MH_REC)
        self.ejcritLigneLimiteje(texte, u'%s %s'%(nom, prejnom), 'Helvetica-Bold', P_NOM)
        if dateN != '' or lieuN != '': self.ejcritLigneLimiteje(texte, u'n %s %s'%(dateN, lieuN), 'Helvetica', P_DATE)
        else: texte.textLine(u'')
        if dateD != '' or lieuD != '': self.ejcritLigneLimiteje(texte, u'\u2020 %s %s'%(dateD, lieuD), 'Helvetica', P_DATE)
        self.can.drawText(texte)
        
    #tronque eventuellement la ligne et l'ejcrit 
    def ejcritLigneLimiteje(self, texte, ligne, police, taille):
        index = len(ligne)
        while stringWidth(ligne[:index], police, taille) > REC_X-MD_REC: index -=1
        texte.setFont(police, taille)
        texte.textLine(ligne[:index])
        
    #dessine un nouveau lien entre un ancestre et son pehre et sa mehre, s'ils existent
    def dessineLien(self, identifiant, identifiantPehre, identifiantMehre):
        #rien à faire si ni pehre ni mehre
        if identifiantPehre not in self.ancestres and identifiantMehre not in self.ancestres: return
        #numejro de page horizontale
        #dessine le segment en partance vers les parents
        (x, y) = self.ancestres[identifiant][1]
        x1 = x + REC_X
        y1 = self.max_y - y + REC_Y / 2
        x2 = x1 + ESP_X / 3
        #y2 = y1
        self.can.line(x1, y1, x2, y1)
        #dessine les attaches sur les parents
        if identifiantPehre in self.ancestres:
            (x4, y) = self.ancestres[identifiantPehre][1]
            #x3 = x2
            y3 = self.max_y - y + REC_Y / 2
            self.can.line(x2, y1, x2, y3)
            self.can.line(x2, y3, x4, y3)
        if identifiantMehre in self.ancestres:
            (x4, y) = self.ancestres[identifiantMehre][1]
            #x5 = x2
            #x6 = x4
            y5 = self.max_y - y + REC_Y / 2
            self.can.line(x2, y1, x2, y5)
            self.can.line(x2, y5, x4, y5)

    #dessine la date et le lieu du mariage devant le rectangle du descendant
    def ejcritMariage(self, identifiant, identifiantEnfant, dateMariage, lieuMariage):
        (x, y) = self.ancestres[identifiant][1]
        x1 = x + MG_REC
        (x, y) = self.ancestres[identifiantEnfant][1]
        y1 = self.max_y - y + REC_Y / 2 - 3
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
        #numéro de page horizontale
        xpage = rang // N_REC_X
        #calcule le x du coin bas gauche du rectangle
        return M_G + D_G + (M_G + M_D) * xpage + (REC_X + ESP_X) * rang
        
    #calcule le y du coin bas gauche de l'ancestre
    def calculeY(self, rang_v):
        # la pagination des y est progressive, c'est pour ça qu'ils sont ordonnejs
        #y = self.y_tejlescopage + self.offset_y + M_H + D_H + REC_Y + (REC_Y + ESP_Y) * rang_v
        #y_relatif = y % landscape(A4)[1]
        #if y_relatif < M_H + D_H + REC_Y:
            #self.offset_y += M_H + D_H + REC_Y - y_relatif
            #y = self.y_tejlescopage + self.offset_y + M_H + D_H + REC_Y + (REC_Y + ESP_Y) * rang_v
        #if y_relatif > landscape(A4)[1] - M_B - D_H:
            #self.offset_y += landscape(A4)[1] + M_H + D_H + REC_Y - y_relatif
            #y = self.y_tejlescopage + self.offset_y + M_H + D_H + REC_Y + (REC_Y + ESP_Y) * rang_v
        y = self.y_tejlescopage + self.offset_y + D_H + REC_Y + (REC_Y + ESP_Y) * rang_v
        y_relatif = y % landscape(A4)[1]
        if y != y_relatif:
            # traitement de haut de page pas pour la premiehre
            if y_relatif < M_H + D_H + REC_Y:
                self.offset_y += M_H + D_H + REC_Y - y_relatif
                y = self.y_tejlescopage + self.offset_y + D_H + REC_Y + (REC_Y + ESP_Y) * rang_v
        if y_relatif > landscape(A4)[1] - M_B - D_H:
            self.offset_y += landscape(A4)[1] + M_H + D_H + REC_Y - y_relatif
            y = self.y_tejlescopage + self.offset_y + D_H + REC_Y + (REC_Y + ESP_Y) * rang_v
        return y
         
    # ejcrit les marques de dejcoupage
    def marquesDejcoupage(self):
        #des lignes bleues
        self.can.saveState()
        self.can.setStrokeColor(colors.blue)
        for page in range(self.nbPages_x):
            marge_gauche = landscape(A4)[0] * page + M_G
            self.can.line(marge_gauche, 0, marge_gauche, self.max_y)      #verticale gauche
            marge_droite = landscape(A4)[0] * (page + 1) - M_D
            self.can.line(marge_droite, 0, marge_droite, self.max_y)      #verticale droite
        for page in range(self.nbPages_y):
            marge_basse = landscape(A4)[1] * page + M_B
            self.can.line(0, marge_basse, self.max_x, marge_basse)        #horizontale basse
            marge_haute = landscape(A4)[1] * (page +1) - M_H
            self.can.line(0, marge_haute, self.max_x, marge_haute)        #horizontale haute
        self.can.restoreState()
        
    # ejcrit les marques de dejcoupage pour la page courante
    def marquesDejcoupagePage(self, page_x, page_y):
        okg = page_x != 0
        okd = page_x != self.nbPages_x -1
        okh = page_y != 0
        okb = page_y != self.nbPages_y -1
        self.can.saveState()
        self.can.setStrokeColor(colors.grey)
        largeur = landscape(A4)[0]
        marge_droite = largeur - M_D
        hauteur = landscape(A4)[1]
        marge_haute = hauteur - M_H
        if okg: 
            self.can.line(M_G, hauteur, M_G, marge_haute-1*cm)                    #verticale gauche haute
            self.can.line(M_G, 0, M_G, M_B+1*cm)                                  #verticale gauche basse
        if okd:
            self.can.line(marge_droite, hauteur, marge_droite, marge_haute-1*cm)  #verticale droite haute
            self.can.line(marge_droite, 0, marge_droite, M_B+1*cm)                #verticale droite basse
        if okh:
            self.can.line(0, marge_haute, M_G+1*cm, marge_haute)                  #horizontale gauche haute
            self.can.line(largeur, marge_haute, marge_droite-1*cm, marge_haute)   #horizontale droite haute
        if okb:
            self.can.line(0, M_B, M_G+1*cm, M_B)                                  #horizontale gauche basse
            self.can.line(largeur, M_B, marge_droite-1*cm, M_B)                   #horizontale droite basse
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
            for j in range (2):
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
        texte.textLine(u'édité le %s %s %s par'%(maintenant.day, mois, maintenant.year))  
        texte.setTextOrigin(C_G, self.max_y - 7*cm)
        texte.setFont("Courier-Bold", P_TITRE3)
        for ligne in self.statistiques: texte.textLine(ligne)
        self.can.drawText(texte)
        self.can.restoreState()
        max_y = texte.getY()        #position verticale du curseur apres le cartouche
        return max_y

            
if __name__ == '__main__':
    main()
