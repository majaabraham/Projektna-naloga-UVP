from model import Uporabnik, Planer
import bottle
from datetime import date
import os
import hashlib

SKRIVNOST_ZA_PISKOTKE = 'STROGO ZAUPNA SKRIVNOST'
uporabniki ={}
NABOR_FORMATOV = (        
    '.zip',
    '.jpg',
    '.jpeg',
    '.gif',
    '.png',
    '.htm',
    '.pptx',
    '.ppt',
    '.xlsx',
    '.xls',
    '.doc',
    '.docx',
    '.pdf',
    '.txt',
)

for ime_datoteke in os.listdir('uporabniki'):
    uporabnik = Uporabnik.nalozi_planer(os.path.join('uporabniki', ime_datoteke))
    uporabniki[uporabnik.uporabnisko_ime] = uporabnik

def trenutni_uporabnik():
    uporabnisko_ime = bottle.request.get_cookie('uporabnisko_ime', secret=SKRIVNOST_ZA_PISKOTKE)
    if uporabnisko_ime is None:
        bottle.redirect('/prijava/')
    return uporabniki[uporabnisko_ime]

def shrani_trenutnega_uporabnika():
    uporabnik = trenutni_uporabnik()
    uporabnik.shrani_planer(os.path.join('uporabniki', f'{uporabnik.uporabnisko_ime}.json'))

def trenutni_planer():
    return trenutni_uporabnik().planer

def zasifriraj_geslo(geslo):
    h = hashlib.blake2b()
    h.update(geslo.encode(encoding='utf-8'))
    zasifrirano_geslo = h.hexdigest()
    return zasifrirano_geslo

def ustvari_mapo_uporabnika(uporabnisko_ime):
    pot = f'datoteke_uporabnikov/{uporabnisko_ime}' 
    if not os.path.exists(pot):
        os.makedirs(pot)

def odpri_stran(stran, podzavihek='', povprecje=''):
    ime = trenutni_uporabnik().ime_in_priimek
    planer = trenutni_planer()
    datum = dan_v_tednu()
    return bottle.template(
        stran, 
        planer=planer, 
        ime = ime, 
        podzavihek = podzavihek, 
        povprecje = povprecje,
        datum = datum)
    
def prikazi_povprecje(podzavihek):
    planer = trenutni_planer()
    predmet = planer.predmeti_po_imenih[podzavihek]
    povprecja = planer.slovar_povprecij()
    skupno_povprecje = planer.skupno_povprecje()
    return povprecja.get(predmet,0), skupno_povprecje

def skupno_povprecje():
    planer = trenutni_planer()
    povprecje = planer.skupno_povprecje()
    st_ocen = planer.stevilo_ocen()
    return povprecje, st_ocen

def dan_v_tednu():
    dnevi = ('ponedeljek', 'torek', 'sreda', 'četrtek', 'petek', 'sobota', 'nedelja')
    dan = date.today().weekday()
    datum = date.today()
    return dnevi[dan], datum

@bottle.get('/')
def zacetna_stran(): 
    bottle.redirect('/domov/')

@bottle.get('/domov/')
def planer():
    return odpri_stran('domov.html')

@bottle.get('/ocene/<podzavihek>/')
def ocene(podzavihek):
    if podzavihek == 'dodaj-oceno':
        povprecje = skupno_povprecje()
    else:
        povprecje = prikazi_povprecje(podzavihek)
    return odpri_stran('ocene.html', podzavihek, povprecje)

@bottle.get('/urnik/')
def urnik():
    return odpri_stran('urnik.html')

@bottle.get('/opravila/')
def opravila():
    return odpri_stran('opravila.html')

@bottle.get('/prijava/')
def prijava_get():
    return bottle.template('prijava.html')

@bottle.post('/registracija/')
def registracija():
    uporabnisko_ime = bottle.request.forms.getunicode('uporabnisko_ime')
    ime_in_priimek = bottle.request.forms.getunicode('ime_in_priimek')
    geslo = bottle.request.forms.getunicode('geslo')
    potrditev = bottle.request.forms.getunicode('potrdi')
    Uporabnik.preveri_enakost_gesel(geslo, potrditev)
    zasifrirano_geslo = zasifriraj_geslo(geslo)
    if uporabnisko_ime in uporabniki:
        raise ValueError('Uporabniško ime je že zasedeno!')
    else:
        uporabnik = Uporabnik(
            uporabnisko_ime,
            zasifrirano_geslo,
            ime_in_priimek,
            Planer()
        )
        uporabniki[uporabnisko_ime] = uporabnik
    bottle.response.set_cookie('uporabnisko_ime', uporabnik.uporabnisko_ime, path='/', secret=SKRIVNOST_ZA_PISKOTKE)
    uporabnik.shrani_planer(os.path.join('uporabniki', f'{uporabnik.uporabnisko_ime}.json'))
    ustvari_mapo_uporabnika(uporabnisko_ime)
    bottle.redirect('/')

@bottle.post('/prijava/')
def prijava_post():
    uporabnisko_ime = bottle.request.forms.getunicode('uporabnisko_ime')
    geslo = bottle.request.forms.getunicode('geslo')
    zasifrirano_geslo = zasifriraj_geslo(geslo)
    if uporabnisko_ime not in uporabniki:
        raise ValueError('''Uporabniško ime ne obstaja! 
    Vpišite veljavno uporabniško ime ali se registrirajte.''')
    else:
        uporabnik = uporabniki[uporabnisko_ime] 
        uporabnik.preveri_geslo(zasifrirano_geslo)
    bottle.response.set_cookie('uporabnisko_ime', uporabnik.uporabnisko_ime, path='/', secret=SKRIVNOST_ZA_PISKOTKE)
    bottle.redirect('/')

@bottle.post('/odjava/')
def odjava():
    bottle.response.delete_cookie('uporabnisko_ime', path='/')
    bottle.redirect('/')

@bottle.get('/static/<ime_dat:path>')
def server_static(ime_dat):
    pot = './slike'
    return bottle.static_file(ime_dat, root=pot)

@bottle.get('/static_uporabnik/<ime_dat:path>')
def static(ime_dat):
    up_ime = trenutni_uporabnik().uporabnisko_ime
    pot = f'./datoteke_uporabnikov/{up_ime}'
    return bottle.static_file(ime_dat, root=pot)

@bottle.post('/dodaj-predmet/')
def dodaj_predmet():
    planer = trenutni_planer()
    ime = bottle.request.forms.getunicode('ime')
    if ime == '':
        bottle.redirect('/')
    planer.dodaj_predmet(ime)
    shrani_trenutnega_uporabnika()
    bottle.redirect('/')

@bottle.post('/odstrani-predmet/')
def odstrani_predmet():
    planer = trenutni_planer()
    ime = bottle.request.forms.getunicode('ime')
    predmet = planer.predmeti_po_imenih[ime]
    planer.odstrani_predmet(predmet)
    shrani_trenutnega_uporabnika()
    bottle.redirect('/')

@bottle.post('/dodaj-oceno/')
def dodaj_oceno():
    planer = trenutni_planer()
    ocena = bottle.request.forms.getunicode('ocena')
    tip = bottle.request.forms.getunicode('tip')
    opis = bottle.request.forms.getunicode('opis')
    predmet = planer.predmeti_po_imenih[bottle.request.forms.getunicode('predmet')]
    planer.dodaj_oceno(ocena, tip, str(date.today()), opis, predmet)
    shrani_trenutnega_uporabnika()
    bottle.redirect(f'/ocene/{predmet.ime}/')

@bottle.post('/odstrani-oceno/')
def odstrani_oceno():
    planer = trenutni_planer()
    str_ocena = bottle.request.forms.getunicode('ocena')
    ocena = planer.poisci_oceno(str_ocena)
    planer.odstrani_oceno(ocena)
    shrani_trenutnega_uporabnika()
    bottle.redirect(f'/ocene/{ocena.predmet.ime}/')

@bottle.post('/dodaj-opravilo/')
def dodaj_opravilo():
    planer = trenutni_planer()
    naslov = bottle.request.forms.getunicode('naslov')
    rok = str(bottle.request.forms.getunicode('rok'))
    opis = bottle.request.forms.getunicode('opis')
    planer.dodaj_opravilo(naslov, rok, opis, False)
    shrani_trenutnega_uporabnika()
    bottle.redirect('/opravila/')

@bottle.post('/odstrani-opravilo/')
def odstrani_opravilo():
    planer = trenutni_planer()
    str_opravilo = bottle.request.forms.getunicode('opravilo')
    opravilo = planer.poisci_opravilo(str_opravilo)
    planer.odstrani_opravilo(opravilo)
    shrani_trenutnega_uporabnika()
    bottle.redirect('/opravila/')

@bottle.post('/spremeni-status/')
def spremeni_status():
    planer = trenutni_planer()
    str_opravilo = bottle.request.forms.getunicode('opravilo')
    opravilo = planer.poisci_opravilo(str_opravilo)
    opravilo.sprememba_statusa()
    shrani_trenutnega_uporabnika()
    bottle.redirect('/opravila/')

@bottle.post('/dodaj-predavanje/')
def dodaj_predavanje():
    planer = trenutni_uporabnik().planer
    predmet = planer.predmeti_po_imenih[bottle.request.forms.getunicode('predmet')]
    vrsta = bottle.request.forms.getunicode('vrsta')
    dan = bottle.request.forms.getunicode('dan')
    ura = bottle.request.forms.get('ura')
    trajanje = bottle.request.forms.get('trajanje')
    prostor = bottle.request.forms.getunicode('prostor')
    predavatelj = bottle.request.forms.getunicode('predavatelj')
    planer.dodaj_predavanje(dan, ura, trajanje, prostor, vrsta, predavatelj, predmet)
    shrani_trenutnega_uporabnika()
    bottle.redirect('/urnik/')

@bottle.post('/odstrani-predavanje/')
def odstrani_predavanje():
    planer = trenutni_planer()
    str_predavanje = bottle.request.forms.getunicode('predavanje')
    predavanje = planer.poisci_predavanje(str_predavanje)
    planer.odstrani_predavanje(predavanje)
    shrani_trenutnega_uporabnika()
    bottle.redirect('/urnik/')

@bottle.post('/spremeni-prikaz/')
def spremeni():
    planer = trenutni_planer()
    str_predavanje = bottle.request.forms.getunicode('predavanje')
    predavanje = planer.poisci_predavanje(str_predavanje)
    predavanje.spremeni_prikaz()
    bottle.redirect('/urnik/')

@bottle.post('/dodaj-datoteko/')
def dodaj_datoteko():
    up_ime = trenutni_uporabnik().uporabnisko_ime
    planer = trenutni_planer()
    datoteka = bottle.request.files.get('datoteka') 
    ime, koncnica = os.path.splitext(datoteka.filename)
    if koncnica not in NABOR_FORMATOV:
        return ValueError('Izberite drug format datoteke.')
    planer.dodaj_datoteko(ime, koncnica)
    pot = f'datoteke_uporabnikov/{up_ime}'
    datoteka.save(f'{pot}/{datoteka.filename}')
    shrani_trenutnega_uporabnika()
    bottle.redirect('/')

@bottle.post('/odstrani-datoteko/')
def odstrani_datoteko():
    up_ime = trenutni_uporabnik().uporabnisko_ime
    planer = trenutni_planer()
    src_datoteka = bottle.request.forms.get('datoteka')
    datoteka = planer.poisci_datoteko(src_datoteka)
    planer.odstrani_datoteko(datoteka)
    ime_dat = datoteka.ime + datoteka.koncnica
    os.remove(f'datoteke_uporabnikov/{up_ime}/{ime_dat}')
    shrani_trenutnega_uporabnika()
    bottle.redirect('/')

bottle.run(debug=True, reloader=True)