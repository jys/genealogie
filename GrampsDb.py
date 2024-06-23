#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
__author__ = "jys"
__copyright__ = "Copyright (C) 2020 LATEJCON"

import sys
from os import path
from re import match
from gramps.gen.dbstate import DbState
from gramps.gen.datehandler import get_date
from gramps.gen.display.place import displayer
from gramps.gen.lib import EventType, Person
from gramps.cli.clidbman import CLIDbManager
from gramps.cli.grampscli import CLIDbLoader

def usage():
    script = '$PY/' + path.basename(sys.argv[0])
    print ("""© l'ATEJCON.  
Programme de test de la classe GrampsDb. 
Cette classe permet d'accéder à la base de données de Gramps.
Le programme de test donne le nombre d'individus de la base.
Si un individu est spécifié par son identifiant, le programme de test
donne les nom, prénom, date et lieu de naissance de l'individu spécifié
ainsi que les nom, prénom, date et lieu de naissance de son père et de 
sa mère et la date du mariage.

usage   : %s <nom de la base> [<id individu>]
example : %s sage-devoucoux I0001
"""%(script, script))
    
def main():
    try:
        if len(sys.argv) < 2 : raise Exception()
        #nom de la base
        nomBase = sys.argv[1]
        if len(sys.argv) > 2 : identifiantIndividu = sys.argv[2].strip()
        else: identifiantIndividu = ''
        testeGrampsDb(nomBase, identifiantIndividu)
        
    except Exception as exc:
        if len(exc.args) == 0: usage()
        else:
            print ("******************************")
            print (exc.args[0])
            print ("******************************")
            raise
        sys.exit()
        
def testeGrampsDb(nomBase, identifiantIndividu):        
    grampsDb = GrampsDb(nomBase)
    if not grampsDb.estOuverte(): 
        print ("La base n'est pas ouverte")
        return
    print ('La base est ouverte')
    print ('{:d} individus'.format(grampsDb.nombreIndividus()))
    if identifiantIndividu == '': return
    individuPoigneje = grampsDb.poignejeIndividu(identifiantIndividu)
    afficheIndividu(grampsDb, individuPoigneje, '    ')
    famillePoigneje = grampsDb.familleDelEnfant(individuPoigneje)
    if famillePoigneje == '': return
    pehrePoignee = grampsDb.pehreDeLaFamille(famillePoigneje)
    afficheIndividu(grampsDb, pehrePoignee, 'père')
    mehrePoignee = grampsDb.mehreDeLaFamille(famillePoigneje)
    afficheIndividu(grampsDb, mehrePoignee, 'mère')
    (dateMariage, lieuMariage) = grampsDb.dateLieuMariage(famillePoigneje)
    print('{:8s}{:30s}{:18s}{:25s}'.format('mariés', '', dateMariage, lieuMariage))
    
    
def afficheIndividu(grampsDb, individuPoigneje, texte):
    (prejnom, nom) = grampsDb.prejnomNom(individuPoigneje)
    prejnomNom = prejnom + ' ' + nom
    (dateNaissance, lieuNaissance) = grampsDb.dateLieuNaissance(individuPoigneje)
    (dateDejcehs, lieuDejcehs) = grampsDb.dateLieuDejcehs(individuPoigneje)
    print('{:8s}{:30s}{:18s}{:25s}- {:18s}{:25s}'.format(texte, prejnomNom, dateNaissance, lieuNaissance, dateDejcehs, lieuDejcehs))

        
#################################    
class GrampsDb:
    def __init__(self, nomBase):
        dbstate = DbState()
        # vejrifie que la base existe 
        dbman = CLIDbManager(dbstate)
        db_path = dbman.get_family_tree_path(nomBase)
        if db_path is None: raise Exception('Base inconnue')
        # dejverrouille la base si elle est verrouilleje
        if dbman.is_locked(db_path): dbman.break_lock(db_path)
        # ouvre la base
        db_loader = CLIDbLoader(dbstate)
        self.ouverte = db_loader.read_file(db_path, "", "")
        self.db = dbstate.db
        
    ############################
    # vrai si la base est correctement ouverte, faux sinon
    def estOuverte(self):
        return self.ouverte
    
    ############################
    # retourne le nombre d'individus dans la base
    def nombreIndividus(self):
        return len(self.db.get_person_handles())
    
    ############################
    # retourne la poigneje d'un individu identifiej par son identifiant gramps, '' s'il n'existe pas
    def poignejeIndividu(self, identifiant):
        individu = self.db.get_person_from_gramps_id(identifiant)
        if individu is None : return ''
        return individu.handle
    
    ############################
    # retourne l'identifiant d'un individu identifiej par sa poigneje, '' s'il n'existe pas
    def identifiantIndividu(self, poigneje):
        if poigneje == '': return ''
        individu = self.db.get_person_from_handle(poigneje)
        if individu is None : return ''
        return individu.gramps_id
    
    ############################
    # retourne la poigneje de la famille dont l'individu identifiej par sa poigneje gramps est l'enfant, 
    # '' si elle n'existe pas
    def familleDelEnfant(self, enfantPoigneje):
        famillePoigneje = self.db.get_person_from_handle(enfantPoigneje).get_main_parents_family_handle()
        if famillePoigneje is None : return ''
        return famillePoigneje
    
    ############################
    # retourne la liste des poignejes des familles dont l'individu identifiej par sa poigneje gramps est un des parents 
    def famillesDuParent(self, parentPoigneje):
        return self.db.get_person_from_handle(parentPoigneje).get_family_handle_list()
    
    ############################
    # retourne la poigneje du pehre de la famille identifieje par sa poigneje gramps, '' s'il n'existe pas
    def pehreDeLaFamille(self, famillePoigneje):
        pehrePoigneje = self.db.get_family_from_handle(famillePoigneje).get_father_handle()
        if pehrePoigneje is None : return ''
        return pehrePoigneje
    
    ############################
    # retourne la poigneje de la mehre de la famille identifieje par sa poigneje gramps, '' s'il n'existe pas
    def mehreDeLaFamille(self, famillePoigneje):
        mehrePoigneje = self.db.get_family_from_handle(famillePoigneje).get_mother_handle()
        if mehrePoigneje is None : return ''
        return mehrePoigneje
    
    ############################
    # retourne la liste des poignejes des enfants d'une famille identifieje par sa poigneje gramps 
    def enfantsDeLaFamille(self, famillePoigneje):
        enfantsPoignejes = []
        for enfantRef in self.db.get_family_from_handle(famillePoigneje).get_child_ref_list():
            enfantsPoignejes.append(enfantRef.ref)
        return enfantsPoignejes
     
    ############################
    # retourne Prejnom, Nom de l'individu spejcifiej par sa poigneje, '' s'il n'existe pas
    def prejnomNom(self, individuPoigneje):
        individu = self.db.get_person_from_handle(individuPoigneje)
        if individu is None : return ('', '')
        nomPrimaire = individu.get_primary_name()
        return (nomPrimaire.first_name, nomPrimaire.surname_list[0].surname)

    ############################
    # retourne le genre de l'individu spejcifiej par sa poigneje, 0: femme, 1: homme, 2 s'il n'existe pas
    def genre(self, individuPoigneje):
        individu = self.db.get_person_from_handle(individuPoigneje)
        if individu is None : return 2
        return individu.get_gender()
    
    ############################
    # retourne date et lieu de naissance de l'individu spejcifiej par sa poigneje, '' si elle n'existe pas
    def dateLieuNaissance(self, individuPoigneje):
        individu = self.db.get_person_from_handle(individuPoigneje)
        if individu is None : return ('', '')
        return self.dateLieuEjvejnement(individu.get_birth_ref())
    
    ############################
    # retourne date et lieu de dejcehs de l'individu spejcifiej par sa poigneje, '' si elle n'existe pas
    def dateLieuDejcehs(self, individuPoigneje):
        individu = self.db.get_person_from_handle(individuPoigneje)
        if individu is None : return ('', '')
        return self.dateLieuEjvejnement(individu.get_death_ref())
    
    ############################
    # retourne date et lieu de mariage d'une famille spejcifieje par sa poigneje, '' si elle n'existe pas
    def dateLieuMariage(self, famillePoigneje):
        if famillePoigneje == '' : return ('', '')
        famille = self.db.get_family_from_handle(famillePoigneje)
        if famille is None : return ('', '')
        for evejnementRef in famille.get_event_ref_list():
            evejnement = self.db.get_event_from_handle(evejnementRef.ref)
            if evejnement.get_type() == EventType.MARRIAGE:
                return self.dateLieuEjvejnement(evejnementRef)
        return ('', '')
    
    ############################
    # retourne la date d'un ejvejnement spejcifiej par sa rejfejrence, '' si elle n'existe pas
    def dateLieuEjvejnement(self, evejnementRef):
        if evejnementRef is None : return ('', '')
        evejnement = self.db.get_event_from_handle(evejnementRef.ref)
        if evejnement is None : return ('', '')
        date = get_date(evejnement)
        lieu = displayer.display_event(self.db, evejnement)
        return (date, lieu)

    ############################
    # retourne la liste des poignejes de tous les individus qui satisfont aux critehres de recherche
    def listeIndividus(self, modehle):
        modehle = modehle.upper()
        rejsultat = []
        for (poigneje, donnejes) in self.db.get_person_cursor():
            individu = self.db.get_person_from_handle(poigneje)
            prejnomNom = individu.get_primary_name().get_regular_name().upper()
            if modehle in prejnomNom or match(modehle, prejnomNom):
                rejsultat.append(poigneje)
        return rejsultat
    
         
if __name__ == '__main__':
    main()

