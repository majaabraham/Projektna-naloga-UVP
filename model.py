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


def povprecje(seznam):
    return sum(seznam)/len(seznam)

class Planer:
    def __init__(self):
        self.predavanja = []
        self. predmeti = []
        self.ocene = []
        self.opravila = []
        self.ocene_po_predmetih = {}
        self.predmeti_po_imenih = {}
        self.predavanja_po_predmetih = {}
        
    def __str__(self):
        predmeti = self.predmeti
        seznam = []
        for predmet in predmeti:
            seznam.append(predmet.ime)
        return f'''predmeti : {seznam}, 
        {self.predmeti_po_imenih}, 
        {self.predavanja}, 
        tu sooooo:{self.predavanja_po_predmetih}, 
        ocena:{self.ocene, 
        self.ocene_po_predmetih},
        opravila: {self.opravila}'''

    def dodaj_predmet(self, ime):
        if ime in self.predmeti_po_imenih:
            raise ValueError(f'Predmet {ime} že obstaja!')
        predmet = Predmet(ime, self)
        self.predmeti.append(predmet)
        self.predmeti_po_imenih[ime] = predmet
        return predmet

    def odstrani_predmet(self, predmet):
        for predavanje in self.predavanja_po_predmetih[predmet]:
            self.predavanja.remove(predavanje)
        del self.predavanja_po_predmetih[predmet]
        for ocena in self.ocene_po_predmetih[predmet]:
            self.ocene.remove(ocena)
        del self.ocene_po_predmetih[predmet]
        self.predmeti.remove(predmet)
        del self.predmeti_po_imenih[predmet.ime]

    def dodaj_predavanje(self, dan, ura, trajanje, prostor, vrsta, predavatelj, predmet):
        self._obstoj_predmeta(predmet, 'predavanje')
        predavanje = Predavanje(dan,ura,trajanje, prostor, vrsta, predavatelj, predmet)
        self.predavanja.append(predavanje)
        self.predavanja_po_predmetih[predmet] = self.predavanja_po_predmetih.get(predmet,[]) + [predavanje]
        return predavanje

    def odstrani_predavanje(self, predavanje):
        self._obstoj_predavanja(predavanje)
        self.predavanja.remove(predavanje)
        self.predavanja_po_predmetih[predavanje.predmet].remove(predavanje)

    def dodaj_oceno(self, ocena, tip, datum, opis, predmet):
        self._obstoj_predmeta(predmet, 'oceno')
        ocena = Ocenjevanje(ocena, tip, datum, opis, predmet)
        self.ocene.append(ocena)
        self.ocene_po_predmetih[predmet] = self.ocene_po_predmetih.get(predmet,[]) + [ocena]
        return ocena

    def odstrani_oceno(self, ocena):
        self._obstoj_ocene(ocena)
        self.ocene.remove(ocena)
        self.ocene_po_predmetih[ocena.predmet].remove(ocena)

    def _obstoj_ocene(self, ocena):
        if ocena not in self.ocene:
            raise ValueError(f'Ocena ne obstaja!')

    def _obstoj_predavanja(self, predavanje):
        if predavanje not in self.predavanja:
            raise ValueError(f'Predavanje ne obstaja!')

    def _obstoj_predmeta(self, predmet, uporaba):
        if predmet not in self.predmeti:
            raise ValueError(f'Predmet pri katerem želite dodati {uporaba} ne obstaja!')

    def _obstoj_opravila(self, opravilo):
        if opravilo not in self.opravila:
            raise ValueError(f'Opravilo ne obstaja')

    def slovar_povprecij(self):
        slovar = {}
        for predmet in self.ocene_po_predmetih:
            seznam = []
            for ocena in self.ocene_po_predmetih[predmet]:
                seznam.append(ocena.ocena)
            slovar[predmet] = povprecje(seznam)
        return slovar

    def skupno_povprecje(self):
        seznam = []
        povprecja = self.slovar_povprecij()
        for povp in povprecja:
            seznam.append(povprecja[povp])
        return povprecje(seznam)

    def dodaj_opravilo(self, naslov, rok, opis):
        opravilo = Opravilo(naslov,rok, opis, self)
        self.opravila.append(opravilo)
        return opravilo

    def odstrani_opravilo(self,opravilo):
        self._obstoj_opravila(opravilo)
        self.opravila.remove(opravilo)
    
    def opravila_po_statusih(self, status):
        seznam = []
        for opravilo in self.opravila:
            if opravilo.status == status:
                seznam.append(opravilo)
        return seznam

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
                'ocena': ocenjevanje.ocena,
                'tip': ocenjevanje.tip,
                'datum': str(ocenjevanje.datum),
                'opis': ocenjevanje.opis,
                'predmet': ocenjevanje.predmet.ime,
            } for ocenjevanje in self.ocene],
            'opravila': [{
                'naslov': opravilo.naslov,
                'rok': str(opravilo.rok),
                'opis': opravilo.opis,
            } for opravilo in self.opravila],
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
                planer.predmeti_po_imenih[predavanje['predmet']],
            )
        for ocenjevanje in slovar_podatkov['ocene']:
            planer.dodaj_oceno(
                ocenjevanje['ocena'],
                ocenjevanje['tip'],
                ocenjevanje['datum'],
                ocenjevanje['opis'],
                planer.predmeti_po_imenih[ocenjevanje['predmet']],
            )
        for opravilo in slovar_podatkov['opravila']:
            planer.dodaj_opravilo(
                opravilo['naslov'],
                opravilo['rok'],
                opravilo['opis'],
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

    def __str__(self):
        return f'{self.dan}, {self.ura}'

class Ocenjevanje:    
    def __init__(self, ocena, tip, datum, opis, predmet):
        self.ocena = ocena
        self.tip = tip
        self.datum = datum
        self.opis = opis
        self.predmet = predmet

    def __str__(self):
        return f'''{self.ocena},
        {self.tip},
        {self.datum},
        {self.opis},
        {self.predmet},'''

class Predmet:
    def __init__(self, ime, planer):
        self.ime = ime
        self.planer = planer

    def __str__(self):
        predmet = self.ime
        return f'predmet : {predmet}'

class Opravilo:
    def __init__(self, naslov, rok, opis, planer):
        self.naslov = naslov
        self.rok = rok
        self.opis = opis
        self.status = False
        self.planer = planer

    def __str__(self):
        return f'To je opravilo:{self.naslov, self.rok, self.opis, self.status, self.planer}'

    def sprememba_statusa(self):
        self.status = not self.status