import json

class Uporabnik:
    def __init__(self, uporabnisko_ime, geslo, ime_in_priimek, planer):    #geslo je tu že zašifrirano
        self.uporabnisko_ime = uporabnisko_ime
        self.geslo = geslo
        self.ime_in_priimek = ime_in_priimek
        self.planer = planer

    def preveri_geslo(self, geslo):
        if self.geslo != geslo:
            raise ValueError('Napačno geslo!')
    @staticmethod
    def preveri_enakost_gesel(geslo1, geslo2):
        if geslo1 != geslo2:
            raise ValueError('Gesli se ne ujemata!')

    def shrani_planer(self, ime_datoteke):
        slovar_podatkov = {
            'uporabnisko_ime': self.uporabnisko_ime,
            'geslo': self.geslo,
            'ime_in_priimek': self.ime_in_priimek,
            'planer': self.planer.slovar_za_shranjevanje(),
        }
        with open(ime_datoteke, 'w') as datoteka:
            json.dump(slovar_podatkov, datoteka, ensure_ascii=False, indent=4)

    @classmethod
    def nalozi_planer(cls, ime_datoteke):
        with open(ime_datoteke) as datoteka:
            slovar_podatkov = json.load(datoteka)
        uporabnisko_ime = slovar_podatkov['uporabnisko_ime']
        geslo = slovar_podatkov['geslo']
        ime_in_priimek = slovar_podatkov['ime_in_priimek']
        planer = Planer.nalozi_iz_slovarja(slovar_podatkov['planer'])
        return cls(uporabnisko_ime, geslo, ime_in_priimek,  planer)

class Planer:
    def __init__(self):
        self.predavanja = []
        self. predmeti = []
        self.ocene = []
        self.opravila = []
        self.datoteke = []
        self.ocene_po_predmetih = {}
        self.predmeti_po_imenih = {}
        self.predavanja_po_predmetih = {}

    def dodaj_predmet(self, ime):
        if ime in self.predmeti_po_imenih:
            raise ValueError(f'Predmet {ime} že obstaja!')
        predmet = Predmet(ime, self)
        self.predmeti.append(predmet)
        self.predmeti_po_imenih[ime] = predmet
        return predmet

    def odstrani_predmet(self, predmet):
        if predmet in self.predavanja_po_predmetih:
            for predavanje in self.predavanja_po_predmetih[predmet]:
                self.predavanja.remove(predavanje)
            del self.predavanja_po_predmetih[predmet]
        if predmet in self.ocene_po_predmetih:
            for ocena in self.ocene_po_predmetih[predmet]:
                self.ocene.remove(ocena)
            del self.ocene_po_predmetih[predmet]
        self.predmeti.remove(predmet)
        del self.predmeti_po_imenih[predmet.ime]

    def dodaj_predavanje(self, dan, ura, trajanje, prostor, vrsta, predavatelj, predmet):
        self._obstoj_predmeta(predmet)
        predavanje = Predavanje(dan, ura, trajanje, prostor, vrsta, predavatelj, predmet)
        self.predavanja.append(predavanje)
        self.predavanja_po_predmetih[predmet] = self.predavanja_po_predmetih.get(predmet,[]) + [predavanje]
        return predavanje

    def odstrani_predavanje(self, predavanje):
        self.predavanja.remove(predavanje)
        self.predavanja_po_predmetih[predavanje.predmet].remove(predavanje)

    def predavanja_po_dnevu(self, dan):
        seznam = []
        for predavanje in self.predavanja:
            if predavanje.dan == dan:
                seznam.append(predavanje)
        return seznam

    def dodaj_oceno(self, ocena, tip, datum, opis, predmet):
        self._obstoj_predmeta(predmet)
        ocena = Ocenjevanje(ocena, tip, datum, opis, predmet)
        self.ocene.append(ocena)
        self.ocene_po_predmetih[predmet] = self.ocene_po_predmetih.get(predmet,[]) + [ocena]
        return ocena

    def odstrani_oceno(self, ocena):
        self.ocene.remove(ocena)
        self.ocene_po_predmetih[ocena.predmet].remove(ocena)

    def poisci_oceno(self, ocena):
        for element in self.ocene:
            if str(element) == ocena:
                return element
        raise ValueError('Ocena ne obstaja!')

    def poisci_predavanje(self, predavanje):
        for element in self.predavanja:
            if str(element) == predavanje:
                return element
        raise ValueError('Predavanje ne obstaja!')

    def _obstoj_predmeta(self, predmet):
        if predmet not in self.predmeti:
            raise ValueError('Predmet ne obstaja!')

    def poisci_datoteko(self, datoteka):
        for element in self.datoteke:
            if str(element) == datoteka:
                return element
        raise ValueError('Datoteka ne obstaja')

    def poisci_opravilo(self, opravilo):
        for element in self.opravila:
            if str(element) == opravilo:
                return element
        raise ValueError('Opravilo ne obstaja')
    
    @staticmethod
    def povprecje(seznam):
        if len(seznam) == 0:
            return 0
        return sum(seznam) / len(seznam)

    def slovar_povprecij(self):
        slovar = {}
        for predmet in self.ocene_po_predmetih:
            seznam = []
            for ocena in self.ocene_po_predmetih[predmet]:
                seznam.append(int(ocena.ocena))
            slovar[predmet] = Planer.povprecje(seznam)
        return slovar

    def skupno_povprecje(self):
        seznam = []
        for ocena in self.ocene:
            seznam.append(int(ocena.ocena))
        return round(Planer.povprecje(seznam),1)

    def stevilo_ocen(self):
        return len(self.ocene) 

    def dodaj_opravilo(self, naslov, rok, opis, status):
        opravilo = Opravilo(naslov, rok, opis, self, status)
        self.opravila.append(opravilo)
        return opravilo

    def odstrani_opravilo(self, opravilo):
        self.opravila.remove(opravilo)
    
    def opravila_po_statusih(self, status):
        seznam = []
        for opravilo in self.opravila:
            if opravilo.status == status:
                seznam.append(opravilo)
        return seznam

    def dodaj_datoteko(self, ime, koncnica):
        datoteka = Datoteka(ime, koncnica)
        self.datoteke.append(datoteka)
        return datoteka

    def odstrani_datoteko(self, datoteka):
        self.datoteke.remove(datoteka)

    def slovar_za_shranjevanje(self):
        return {
            'predmeti': [{
                'ime': predmet.ime,
            } for predmet in self.predmeti],
            'predavanja': [{
                'dan': predavanje.dan,
                'ura': predavanje.ura,
                'trajanje': predavanje.trajanje,
                'prostor': predavanje.prostor,
                'vrsta': predavanje.vrsta,
                'predavatelj': predavanje.predavatelj,
                'predmet': predavanje.predmet.ime,
            } for predavanje in self.predavanja],
            'ocene': [{
                'ocena': int(ocenjevanje.ocena),
                'tip': ocenjevanje.tip,
                'datum': str(ocenjevanje.datum),
                'opis': ocenjevanje.opis,
                'predmet': ocenjevanje.predmet.ime,
            } for ocenjevanje in self.ocene],
            'opravila': [{
                'naslov': opravilo.naslov,
                'rok': str(opravilo.rok),
                'opis': opravilo.opis,
                'status': opravilo.status,
            } for opravilo in self.opravila],
            'datoteke': [{
                'ime': datoteka.ime,
                'koncnica': datoteka.koncnica,
            } for datoteka in self.datoteke],
        }

    @classmethod
    def nalozi_iz_slovarja(cls, slovar_podatkov):
        planer = cls()
        for predmet in slovar_podatkov['predmeti']:
            planer.dodaj_predmet(predmet['ime'])
        for predavanje in slovar_podatkov['predavanja']:
            planer.dodaj_predavanje(
                predavanje['dan'], 
                predavanje['ura'], 
                predavanje['trajanje'], 
                predavanje['prostor'], 
                predavanje['vrsta'], 
                predavanje['predavatelj'], 
                planer.predmeti_po_imenih[predavanje['predmet']]
            )
        for ocenjevanje in slovar_podatkov['ocene']:
            planer.dodaj_oceno(
                ocenjevanje['ocena'],
                ocenjevanje['tip'],
                ocenjevanje['datum'],
                ocenjevanje['opis'],
                planer.predmeti_po_imenih[ocenjevanje['predmet']]
            )
        for opravilo in slovar_podatkov['opravila']:
            planer.dodaj_opravilo(
                opravilo['naslov'],
                opravilo['rok'],
                opravilo['opis'],
                opravilo['status']
            )
        for datoteka in slovar_podatkov['datoteke']:
            planer.dodaj_datoteko(
                datoteka['ime'],
                datoteka['koncnica']
            )
        return planer

class Predavanje:
    def __init__(self, dan, ura, trajanje, prostor, vrsta, predavatelj, predmet):
        self.dan = dan
        self.ura = ura
        self.trajanje = trajanje
        self.prostor = prostor
        self.vrsta = vrsta
        self.predavatelj = predavatelj
        self.predmet = predmet
        self.prikaz = False

    def __lt__(self, other):
        return self.ura < other.ura

    def spremeni_prikaz(self):
        self.prikaz = not self.prikaz

class Ocenjevanje:    
    def __init__(self, ocena, tip, datum, opis, predmet):
        self.ocena = ocena
        self.tip = tip
        self.datum = datum
        self.opis = opis
        self.predmet = predmet

    def __lt__(self, other):
        return self.datum < other.datum    

class Predmet:
    def __init__(self, ime, planer):
        self.ime = ime
        self.planer = planer

    def __lt__(self, other):
        return self.ime < other.ime

class Opravilo:
    def __init__(self, naslov, rok, opis, planer, status):
        self.naslov = naslov
        self.rok = rok
        self.opis = opis
        self.status = status
        self.planer = planer

    def __lt__(self, other):
        return self.rok < other.rok

    def sprememba_statusa(self):
        self.status = not self.status

class Datoteka:
    def __init__(self, ime, koncnica):
        self.ime = ime
        self.koncnica = koncnica