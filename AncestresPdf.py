#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
__author__ = "jys"
__copyright__ = "Copyright (C) 2014 LATEJCON"

import sys
import os
import datetime
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph, Table, Image
from PIL import Image

def usage():
    print ("""© l'ATEJCON.  
Programme de test de la classe AncestresPdf 

La classe AncestresPdf crée une image PDF représentant un arbre généalogique
o les positionnements en horizontal sont donnés par le n° de génération
o les positionnements en vertical sont donnés par un numéro d'ordre
o la page est créée avec une taille maximum
o le filigrane est créé automatiquement ainsi que le titre
o chaque ancêtre est créé avec son positionnement et ses attributs
o les liens entre ancêtres sont dessinés
o la date de mariage est écrite

usage   : %s <n'importe quoi> 
example : %s toto
"""%(sys.argv[0], sys.argv[0]))

M_H = 1.5*cm            #marge haute
M_B = 1.5*cm            #marge basse
M_G = 1.5*cm            #marge gauche
M_D = 1.5*cm            #marge droite
#L_PAGE = 4000           #longueur de la page
#H_PAGE = 6000           #hauteur de la page
#REC_X = 170             #longueur rectangle
#REC_Y = 40              #hauteur rectangle
#ESP_X = 40              #longueur espace
#ESP_Y = -10              #hauteur espace
#MH_REC = 11              #marge haute dans rectangle
#MG_REC = 5              #marge gauche dans rectangle
REC_X = 4*cm             #longueur rectangle
REC_Y = 1.2*cm              #hauteur rectangle
REC_XL = 8*cm             #longueur rectangle
REC_YL = 0.8*cm              #hauteur rectangle
ESP_X = 0.8*cm              #longueur espace
ESP_Y = -7            #hauteur espace
MH_REC = 9              #marge haute dans rectangle
MG_REC = 3             #marge gauche dans rectangle
MD_REC = 3             #marge droite dans rectangle
P_NOM = 8              #police du nom 
P_DATE = 7             #police des dates
P_FILI = 20             #police filigrane
P_TITRE1 = 30           #police titre 1
P_TITRE2 = 20           #police titre 2
P_TITRE3 = 12           #police titre 3

def main():
    os.chdir(sys.path[0])
    if len(sys.argv) < 2 :
        usage()
        sys.exit()
        
    #nom du fichier
    nomFichierSortie = '../resultat/AncestresPdf-test.pdf'
    ancestresPdf = AncestresPdf(nomFichierSortie)
    ancestresPdf.dessineAncestre(2, 3, 'Sage', 'Louis', '12 janvier 1912', 'Chazelles sur Lyon', '24 octobre 1965', 'Tarare')
    ancestresPdf.dessineAncestre(1, 3, 'Sage', 'Louis', '12 janvier 1912', 'Chazelles sur Lyon', '24 octobre 1965', 'Tarare')
    ancestresPdf.dessineAncestre(2, 4, 'Sage', 'Louis', '12 janvier 1912', 'Chazelles sur Lyon', '24 octobre 1965', 'Tarare')
    ancestresPdf.termine()
    
class AncestresPdf:
    def __init__(self, nomFichierSortie, max_h, max_v, pos_2, filigrane, titre, image, statistiques, enLongueur=False):
        self.enLongueur = enLongueur
        if enLongueur:
            self.rec_x = REC_XL
            self.rec_y = REC_YL
        else:
            self.rec_x = REC_X
            self.rec_y = REC_Y
        # max_h = max horizontal, max_v = max vertical, pos_2 = position verticale du pere (pour echapper le cartouche)
        page_x = M_G + (self.rec_x + ESP_X) * max_h + M_D
        self.page_y = M_H + (self.rec_y + ESP_Y) * max_v + self.rec_y + M_B
        #print ('AncestresPdf taille: ', page_x, 'x', self.page_y)
        self.can = canvas.Canvas(nomFichierSortie, pagesize=(page_x, self.page_y))        
        self.ejcritFiligrane(filigrane)
        #position verticale du curseur apres le cartouche
        y_cartouche = self.ejcritTitre(titre, image, statistiques)
        #calcule la coordonnee verticale du haut du rectangle du pere
        y_2 = self.page_y - M_H - (self.rec_y + ESP_Y) * pos_2
        #verifie l'eventualite du telescopage entre le cartouche et l'arbre
        if y_2 > y_cartouche: 
            #si telescopage, agrandit la page
            self.offset_y = y_2 - y_cartouche
            self.page_y += self.offset_y
            self.can = canvas.Canvas(nomFichierSortie, pagesize=(page_x, self.page_y))
            self.ejcritFiligrane(filigrane)
            self.ejcritTitre(titre, image, statistiques)
        else:
            self.offset_y = 0
        #self.ejcritPageA4(page_x)
        
    # dessine un rectangle qui représente un ancêtre
    def dessineAncestre(self, rang_h, rang_v, nomPrejnom, dateN, lieuN, dateD, lieuD, enGris=False):
        #bricole les lieux pour permettre le "disparu en mer"
        if len(lieuN) != 0 and lieuN[0].isupper(): lieuN = u'à ' + lieuN
        if len(lieuD) != 0 and lieuD[0].isupper(): lieuD = u'à ' + lieuD
        #calcule les coordonnées du coin bas gauche du rectangle
        x = M_G + (self.rec_x + ESP_X) * rang_h
        y = self.page_y - self.offset_y - M_H - self.rec_y - (self.rec_y + ESP_Y) * rang_v
        #print (prenom, x, y)
        if enGris: self.can.setFillGray(0.85)
        else: self.can.setFillColor(colors.white)
        self.can.rect(x, y, self.rec_x, self.rec_y, fill=1)
        self.can.setFillColor(colors.black)
        texte = self.can.beginText()
        texte.setTextOrigin(x + MG_REC, y + self.rec_y - MH_REC)
        self.ejcritLigneLimitee(texte, nomPrejnom, 'Helvetica-Bold', P_NOM)
        if dateN != '' or lieuN != '': dateLieuN = u'n {} {}'.format(dateN, lieuN)
        else : dateLieuN = ''
        if dateD != '' or lieuD != '': dateLieuD = u'\u2020 {} {}'.format(dateD, lieuD)
        else : dateLieuD = ''
        if self.enLongueur:
            self.ejcritLigneLimitee(texte, u'{}  {}'.format(dateLieuN, dateLieuD), 'Helvetica', P_DATE)
        else:
            self.ejcritLigneLimitee(texte, dateLieuN, 'Helvetica', P_DATE)
            self.ejcritLigneLimitee(texte, dateLieuD, 'Helvetica', P_DATE)
        self.can.drawText(texte)
        
    # tronque eventuellement la ligne et l'ejcrit 
    def ejcritLigneLimitee(self, texte, ligne, police, taille):
        index = len(ligne)
        while stringWidth(ligne[:index], police, taille) > self.rec_x-MD_REC: index -=1
        texte.setFont(police, taille)
        texte.textLine(ligne[:index])
        
    # dessine le lien entre un ancêtre et son pehre et sa mehre, s'ils existent
    def dessineLien(self, rang_h, rang_v, rang_v_p, rang_v_m):
        # rien ah faire si ni pehre ni mehre
        if rang_v_p == -1 and rang_v_m == -1: return
        # dessine le segment en partance vers les parents
        x1 = M_G + (self.rec_x + ESP_X) * rang_h + self.rec_x
        y1 = self.page_y - self.offset_y - M_H - self.rec_y - (self.rec_y + ESP_Y) * rang_v + self.rec_y / 2
        x2 = x1 + ESP_X /2
        #y2 = y1
        self.can.line(x1, y1, x2, y1)
        # dessine les attaches sur les parents
        x4 = x1 + ESP_X
        if rang_v_p != -1:
            #x3 = x2
            y3 = self.page_y - self.offset_y - M_H - self.rec_y - (self.rec_y + ESP_Y) * rang_v_p + self.rec_y / 2
            self.can.line(x2, y1, x2, y3)
            self.can.line(x2, y3, x4, y3)
        if rang_v_m != -1:
            #x5 = x2
            #x6 = x4
            y5 = self.page_y - self.offset_y - M_H - self.rec_y - (self.rec_y + ESP_Y) * rang_v_m + self.rec_y / 2
            self.can.line(x2, y1, x2, y5)
            self.can.line(x2, y5, x4, y5)
            
    # ejcrit la date et le lieu du mariage devant le rectangle du descendant
    def ejcritMariage(self, rang_h, rang_v_e, dateMariage, lieuMariage):
        #calcule le point d'ejcriture
        x = M_G + (self.rec_x + ESP_X) * rang_h + MG_REC
        y = self.page_y - self.offset_y - M_H - self.rec_y - (self.rec_y + ESP_Y) * rang_v_e + self.rec_y / 2 -2
        texte = self.can.beginText()
        texte.setTextOrigin(x, y)
        texte.setFont("Helvetica-Bold", P_DATE)
        if dateMariage != '' and lieuMariage != '': texte.textLine(u'm %s à %s'%(dateMariage, lieuMariage))
        elif dateMariage != '': texte.textLine(u'm %s'%(dateMariage))
        elif lieuMariage != '': texte.textLine(u'm à %s'%(lieuMariage))
        self.can.drawText(texte)
        
    # dessine un lien gauche entre individus (arbre descendants)
    def dessineLiensGauches(self, rang_h, rangs_v):
        x1 = M_G + (self.rec_x + ESP_X) * rang_h
        x2 = x1 - ESP_X /3
        # dessine les traits horizontaux
        for rang_v in rangs_v:
            y = self.page_y - self.offset_y - M_H - self.rec_y - (self.rec_y + ESP_Y) * rang_v + self.rec_y / 2
            self.can.line(x1, y, x2, y)
        # dessine le trait vertical
        x = x2
        y1 = self.page_y - self.offset_y - M_H - self.rec_y - (self.rec_y + ESP_Y) * rangs_v[0] + self.rec_y / 2
        y2 = self.page_y - self.offset_y - M_H - self.rec_y - (self.rec_y + ESP_Y) * rangs_v[-1] + self.rec_y / 2
        self.can.line(x, y1, x, y2)
        
    # dessine un lien droit entre individus (arbre descendants)
    def dessineLiensDroits(self, rang_h, rangs_v):
        x1 = M_G + (self.rec_x + ESP_X) * rang_h + self.rec_x
        x2 = x1 + ESP_X /3
        # dessine les traits horizontaux
        for rang_v in rangs_v:
            y = self.page_y - self.offset_y - M_H - self.rec_y - (self.rec_y + ESP_Y) * rang_v + self.rec_y / 2
            self.can.line(x1, y, x2, y)
        # dessine le trait vertical
        x = x2
        y1 = self.page_y - self.offset_y - M_H - self.rec_y - (self.rec_y + ESP_Y) * rangs_v[0] + self.rec_y / 2
        y2 = self.page_y - self.offset_y - M_H - self.rec_y - (self.rec_y + ESP_Y) * rangs_v[-1] + self.rec_y / 2
        self.can.line(x, y1, x, y2)
        # dessine le trait horizontal vers les parents
        x3 = x2 + ESP_X /3
        rang_v = (rangs_v[0] + rangs_v[-1]) /2
        y = self.page_y - self.offset_y - M_H - self.rec_y - (self.rec_y + ESP_Y) * rang_v + self.rec_y / 2
        self.can.line(x2, y, x3, y)

    def termine(self):
        self.can.showPage()
        self.can.save()
       
    def ejcritFiligrane(self, filigrane):
        self.can.saveState()
        self.can.rotate(60)
        self.can.setFillColor(colors.paleturquoise)
        texte = self.can.beginText()
        texte.setTextOrigin(0, self.page_y // 2)
        #texte.setTextOrigin(0, 3000)
        texte.setFont("Helvetica-Oblique", P_FILI)
        for i in range(400):
            for j in range (200):
                texte.textOut(filigrane)
            texte.textLine()
        self.can.drawText(texte)
        self.can.restoreState()
        
    def ejcritTitre(self, titre, image, statistiques):
        maintenant = datetime.datetime.today()
        mois = (u'', u'janvier', u'février', u'mars', u'avril', u'mai', u'juin', u'juillet', u'août', u'septembre', u'octobre', u'novembre', u'décembre')[int(maintenant.month)]
        if int(maintenant.day) == 1: jour = '1er'
        else: jour = maintenant.day
        self.can.saveState()
        self.can.drawImage(image, M_G, self.page_y-(6*cm))
        texte = self.can.beginText()
        texte.setTextOrigin(M_G, self.page_y - M_H)
        texte.setFont("Helvetica-Bold", P_TITRE1)
        texte.textLine(titre[0])
        texte.textLine(titre[1])
        texte.setFont("Helvetica-Bold", P_TITRE2)
        texte.textLine(u'édité le %s %s %s par'%(jour, mois, maintenant.year))  
        texte.setTextOrigin(M_G, self.page_y - 7*cm)
        texte.setFont("Courier-Bold", P_TITRE3)
        for ligne in statistiques: texte.textLine(ligne)
        self.can.drawText(texte)
        #self.can.drawImage(image, 1*cm, self.page_y-(7*cm), 5*cm, 2*cm, [0,2,40,42,136,139])
        self.can.restoreState()
        max_y = texte.getY()        #position verticale du curseur apres le cartouche
        return max_y
        
    #def ejcritTitre(self, titre, image, statistiques):
        #self.can.saveState()
        #maintenant = datetime.datetime.today()
        #donneesTable = []
        #styles = getSampleStyleSheet()
        #styleN = styles['Normal']
        #styleN.fontName = 'Helvetica-Bold'
        #styleN.fontSize = P_TITRE1
        #styleN.leading = 0
        #donneesTable.append([Paragraph(u'Arbre généalogique de', styleN)])
        #donneesTable.append([Paragraph(u'%s'%(titre), styleN)])
        #styleN.fontSize = P_TITRE2
        ##styleN.leading = P_TITRE2
        #logo = Image(image)
        #logo.drawHeight = 4*cm*logo.drawHeight / logo.drawWidth
        #logo.drawWidth = 4*cm
        #tableLogo = Table([[Paragraph(u'édité le %02d-%02d-%s par'%(int(maintenant.day), int(maintenant.month), maintenant.year), styleN), logo]])
        #tableLogo.setStyle([
                            #('ALIGN', (0,0), (-1,-1), 'LEFT'),
                            #('LEFTPADDING', (0,0), (-1,-1), 0),
                            #('RIGHTPADDING', (0,0), (-1,-1), 0),
                            #('TOPPADDING', (0,0), (-1,-1), 0),
                            #('BOTTOMPADDING', (0,0), (-1,-1), 0),
                            #('BOX', (0,0), (-1,-1), 0.25, colors.black),
                            #('INNERGRID', (0,0), (-1,-1), 0.25, colors.black)])                         
        #donneesTable.append([tableLogo])
        #table = Table(donneesTable)   
        #tableStyle = [
                      #('ALIGN', (0,0), (-1,-1), 'LEFT'),
                      #('LEFTPADDING', (0,0), (-1,-1), 0),
                      #('TOPPADDING', (0,0), (-1,-1), 0),
                      #('BOTTOMPADDING', (0,0), (-1,-1), 30),
                      #('BOX', (0,0), (-1,-1), 0.25, colors.black),
                      #('INNERGRID', (0,0), (-1,-1), 0.25, colors.black)]
        #table.setStyle(tableStyle)
        #w, h = table.wrap(17*cm, 10*cm)
        #table.drawOn(self.can, M_G, self.page_y - M_H - h)
        #self.can.restoreState()
        
    def ejcritPageA4(self, page_x):
        xPageA4 = A4[1]
        while xPageA4 <= page_x:
            self.can.line(xPageA4, 0, xPageA4, self.page_y)
            xPageA4 += A4[1]
        yPageA4 = A4[0]
        while yPageA4 <= self.page_y:
            self.can.line(0, yPageA4, page_x, yPageA4)
            yPageA4 += A4[0]
       
         
if __name__ == '__main__':
    main()
