from model import Uporabnik, Planer
import bottle
from datetime import date
import os
import hashlib

SKRIVNOST_ZA_PISKOTKE = 'STROGO ZAUPNA SKRIVNOST'
uporabniki ={}

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

def zasifriraj_geslo(geslo):
    h = hashlib.blake2b()
    h.update(geslo.encode(encoding='utf-8'))
    zasifrirano_geslo = h.hexdigest()
    return zasifrirano_geslo

@bottle.get('/')
def zacetna_stran(): 
    bottle.redirect('/planer_uporabnika/')

@bottle.get('/planer_uporabnika/')
def odpri_planer():
    planer = trenutni_uporabnik().planer
    return bottle.template('planer.html', planer=planer)

@bottle.get('/prijava/')
def prijava_get():
    return bottle.template('prijava.html')

@bottle.post('/registracija/')
def registracija():
    uporabnisko_ime = bottle.request.forms.getunicode('uporabnisko_ime')
    ime_in_priimek = bottle.request.forms.getunicode('ime_in_priimek')
    geslo = bottle.request.forms.getunicode('geslo')
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
    bottle.redirect('/')

@bottle.post('/prijava/')
def prijava_post():
    uporabnisko_ime = bottle.request.forms.getunicode('uporabnisko_ime')
    geslo = bottle.request.forms.getunicode('geslo')
    zasifrirano_geslo = zasifriraj_geslo(geslo)
    if uporabnisko_ime not in uporabniki:
        raise ValueError('Uporabniško ime ne obstaja! Vpišite veljavno uporabniško ime ali se registrirajte.')
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

bottle.run(debug=True, reloader=True)