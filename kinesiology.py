from vepar import *
import fractions
import re

rezultat = None

class T(TipoviTokena):
    PLUS, MINUS, PUTA, KROZ, JEDNAKO, ZAREZ= '+-*/=,'
    OOTV, OZATV, UOTV, UZATV, VOTV, VZATV = '()[]{}'
    TOCKA, DTOCKA, TZAREZ = '.:;'
    TILDA, PTILDA, PPLUS, MTILDA, MMINUS = '~', '+~', '++', '-~', '--'
    STRELICA, KOMENTAR = '->', '$$'
    HEIGHT, WEIGHT, COUNT = 'height', 'weight', 'count'
    FUNCTION, ENDFUNCTION = 'function', 'endfunction'
    LOOP, ENDLOOP = 'loop', 'endloop'
    PRINT, SCAN = 'print', 'scan'
    SPORTAS, REZULTATI = 'sportas', 'rezultati'

    class BROJ(Token):
        def vrijednost(t): return t.sadržaj
        def izračunaj(t): return float(t.sadržaj)
    class ATHLETE(Token):
        def vrijednost(t): return t.sadržaj
        def naziv(t): return t.sadržaj[1:]
    class ATHLETE_SCORE(Token):
        def vrijednost(t): return t.sadržaj
        def naziv(t): return t.sadržaj[1:]
    class NAME(Token):
        def vrijednost(t): return t.sadržaj
    class TEKST(Token):
        def vrijednost(t): return t.sadržaj[1:-1]
        
        
@lexer
def ls(lex):
    for znak in lex:
        if znak.isspace(): lex.zanemari()
        elif znak.isdecimal():
            lex.prirodni_broj(znak)
            if lex >= '.':
                lex + str.isdigit
            yield lex.token(T.BROJ)
        elif znak.isalpha():
            lex * str.isalnum
            yield lex.literal_ili(T.NAME, case = False)
        elif znak == '@':
            lex * str.isalnum
            yield lex.token(T.ATHLETE)
        elif znak == '"':
            if next(lex).isalpha():
                lex - '"'
                yield lex.token(T.TEKST)
        elif znak == '~':
            lex + str.isalnum
            yield lex.token(T.ATHLETE_SCORE)
        elif znak == '+':
            if lex >= '~':
                yield lex.token(T.PTILDA)
            elif lex >= '+':
                yield lex.token(T.PPLUS)
            else: yield lex.token(T.PLUS)
        elif znak == '-':
            if lex >= '>':
                yield lex.token(T.STRELICA)
            elif lex >= '~':
                yield lex.token(T.MTILDA)
            elif lex >= '-':
                yield lex.token(T.MMINUS)
            else: yield lex.token(T.MINUS)
        elif znak == '$':
            lex >> '$'
            lex - '\n'
            lex.zanemari()
        else: yield lex.literal(T)   

### BKG
# program -> naredba | program naredba
# naredba -> ( ispis | unos | loop | pridruži | ubaci | izbaci | struktura1 | struktura2 | funkcija | naredbe ) TZAREZ | komentar 
# naredbe -> naredba | naredbe TZAREZ naredba
# funkcija -> FUNCTION ime_funkcije OOTV argumenti* OZATV naredba ENDFUNCTION | FUNCTION ime_funkcije OOTV argumenti* OZATV
# argumenti -> argument | argumenti ZAREZ argument
# argument -> ATHLETE | ATHLETE_SCORE | BROJ | NAME
# pridruži -> NAME JEDNAKO izraz
# izraz -> aritm | dohvati | duljina | visina | težina
# ispis -> PRINT ( TEKST | NAME | ATHLETE | ATHLETE_SCORE )
# unos -> SCAN BROJ | SCAN NAME
# loop -> LOOP OOTV ( BROJ | NAME | visina | tezina | duljina | dohvati ) OZATV naredbe ENDLOOP
# aritm -> član | aritm PLUS član | aritm MINUS član
# član -> faktor | član PUTA faktor | član KROZ faktor
# faktor -> BROJ | NAME | OOTV aritm OZATV | MINUS faktor | dohvati | duljina | visina | težina
# struktura1 -> SPORTAS NAME VOTV BROJ DTOCKA BROJ VZATV    ---> visina, tezina
# struktura2 -> REZULTATI NAME VOTV rez VZATV   ---> rezultati
# rez ->  BROJ | rez TZAREZ BROJ
# ubaci -> ( PTILDA | PPLUS ) ATHLETE_SCORE BROJ
# izbaci -> ( MTILDA | MMINUS ) ATHLETE_SCORE BROJ
# dohvati -> ATHLETE_SCORE UOTV BROJ UZATV | ATHLETE_SCORE TOCKA OOTV BROJ OZATV
# duljina -> ATHLETE_SCORE ( TOCKA | STRELICA ) COUNT
# visina -> ATHLETE ( TOCKA | STRELICA ) HEIGHT
# težina -> ATHLETE ( TOCKA | STRELICA ) WEIGHT
# komentar -> KOMENTAR TEKST 

class P(Parser):

    def program(p) -> 'Program':
        return Program(p.naredbe())
    

    def naredbe(p) -> '( ispis | unos | loop | pridruži | ubaci | izbaci | struktura1 | struktura2 | komentar | funkcija) *':
        lista_naredbi = []
        while ...:
            if p > T.PRINT: lista_naredbi.append(p.ispis())
            elif p > T.SCAN: lista_naredbi.append(p.unos())
            elif p > T.LOOP: lista_naredbi.append(p.loop())
            elif p > T.NAME: lista_naredbi.append(p.pridruzi())
            elif p > {T.PTILDA, T.PPLUS}: lista_naredbi.append(p.ubaci())
            elif p > {T.MTILDA, T.MMINUS}: lista_naredbi.append(p.izbaci())
            elif p > T.SPORTAS: lista_naredbi.append(p.struktura1())
            elif p > T.REZULTATI: lista_naredbi.append(p.struktura2())
            elif p > T.KOMENTAR: lista_naredbi.append(p.komentar())
            elif p > T.FUNCTION: lista_naredbi.append(p.funkcija())
            else: return lista_naredbi


    def funkcija(p) -> 'Funkcija | PozivFunkcije':
        p >> T.FUNCTION
        ime = p >> T.NAME
        p >> T.OOTV
        if p > {T.ATHLETE, T.ATHLETE_SCORE, T.BROJ, T.NAME}:
            argumenti = [p.argument()]
            while p >= T.ZAREZ:
                argumenti.append(p.argument())
        p >> T.OZATV
        if p >= T.TZAREZ:
            return PozivFunkcije(ime, argumenti)
        else:
            naredbe = p.naredbe()
            p >> T.ENDFUNCTION
            p >> T.TZAREZ
            return Funkcija(ime, argumenti, naredbe)
    

    def argument(p) -> 'ATHLETE | ATHLETE_SCORE | BROJ | NAME':
        return p >> {T.ATHLETE, T.ATHLETE_SCORE, T.BROJ, T.NAME}


    def pridruzi(p) -> 'Pridruživanje':
        varijabla = p >> T.NAME
        p >> T.JEDNAKO
        izr = p.izraz()
        p >> T.TZAREZ
        return Pridruživanje(varijabla, izr)
    

    def izraz(p) -> 'Visina | Težina | Duljina | Dohvati':
        if sportas := p >= T.ATHLETE:
            p >> {T.TOCKA, T.STRELICA}
            if p >= T.HEIGHT:
                return Visina(sportas)
            elif p >> T.WEIGHT:
                return Težina(sportas)
        elif sportas := p >= T.ATHLETE_SCORE:
            if p >= T.UOTV:
                if ime := p >= T.NAME:
                    broj = Dohvati_vrijednost(ime)
                else: 
                    broj = p >> T.BROJ
                p >> T.UZATV
                return Dohvati(sportas, broj)
            elif p >= T.TOCKA:
                if p >= T.COUNT:
                    return Duljina(sportas)
                else:
                    p >> T.OOTV
                    if ime := p >= T.NAME:
                        broj = Dohvati_vrijednost(ime)
                    else: 
                        broj = p >> T.BROJ
                    p >> T.OZATV
                    return Dohvati(sportas, broj)
            elif p >> T.STRELICA:
                p >> T.COUNT
                return Duljina(sportas)
        else:
            return p.aritm()


    def ispis(p) -> 'Ispis':
        p >> T.PRINT
        if p > T.NAME:
            što = p >> T.NAME 
        elif p > T.TEKST:
            što = p >> T.TEKST
        elif p > T.ATHLETE:
            što = p >> T.ATHLETE
        elif p > T.ATHLETE_SCORE:
            što = p >> T.ATHLETE_SCORE
        elif p > T.BROJ:
            što = p >> T.BROJ
        p >> T.TZAREZ
        return Ispis(što)
    

    def unos(p) -> 'Unos':
        p >> T.SCAN
        uneseno = p >> {T.BROJ, T.NAME}
        p >> T.TZAREZ
        return Unos(uneseno)
    

    def loop(p) -> 'Loop':
        p >> T.LOOP, p >> T.OOTV
        if p > T.BROJ:
            broj = p >> T.BROJ
        elif p > T.NAME:
            broj = p >> T.NAME
        elif p > T.ATHLETE:
            sportas = p >> T.ATHLETE
            p >> {T.TOCKA, T.STRELICA}
            if p >= T.HEIGHT:
                broj = Visina(sportas)
            elif p >> T.WEIGHT:
                broj = Težina(sportas)
        elif p > T.ATHLETE_SCORE:
            sportas = p >> T.ATHLETE_SCORE
            if p >= T.UOTV:
                if ime := p >= T.NAME:
                    ind = Dohvati_vrijednost(ime)
                else: 
                    ind = p >> T.BROJ
                p >> T.UZATV
                broj = Dohvati(sportas, ind)
            elif p >= T.TOCKA:
                if p >= T.COUNT:
                    broj = Duljina(sportas)
                elif p >> T.OOTV:
                    ind = p >> T.BROJ
                    p >> T.OZATV
                    broj = Dohvati(sportas, ind)
            elif p >> T.STRELICA:
                p >> T.COUNT
                broj = Duljina(sportas)
        p >> T.OZATV
        tijelo = p.naredbe()
        p >> T.ENDLOOP
        p >> T.TZAREZ
        return Loop(broj, tijelo)


    def aritm(p) -> 'Op|član':
        t = p.član()
        while op := p >= {T.PLUS, T.MINUS}: t = Op(op, t, p.član())
        return t


    def član(p) -> 'Op|faktor':
        t = p.faktor()
        while op := p >= {T.PUTA, T.KROZ}: t = Op(op, t, p.faktor())
        return t


    def faktor(p) -> 'Op|aritm|BROJ|NAME|Visina|Težina|Dohvati|Duljina':
        if op := p >= T.MINUS: return Op(op, nenavedeno, p.faktor())
        elif elementarni := p >= T.BROJ: return elementarni
        elif ime := p >= T.NAME:
            return Dohvati_vrijednost(ime)
        elif sportas := p >= T.ATHLETE:
            p >> {T.TOCKA, T.STRELICA}
            if p >= T.HEIGHT:
                return Visina(sportas)
            elif p >> T.WEIGHT:
                return Težina(sportas)
        elif sportas := p >= T.ATHLETE_SCORE:
            if p >= T.UOTV:
                if ime := p >= T.NAME:
                    ind = Dohvati_vrijednost(ime)
                else: 
                    ind = p >> T.BROJ
                p >> T.UZATV
                return Dohvati(sportas, ind)
            elif p >= T.TOCKA:
                if p >= T.COUNT:
                    return Duljina(sportas)
                elif p >> T.OOTV:
                    ind = p >> T.BROJ
                    p >> T.OZATV
                    return Dohvati(sportas, ind)
            elif p >> T.STRELICA:
                p >> T.COUNT
                return Duljina(sportas)
        elif p >> T.OOTV:
            u_zagradi = p.aritm()
            p >> T.OZATV
            return u_zagradi


    def struktura1(p) -> 'Struktura1':
        p >> T.SPORTAS
        sportas = p >> T.NAME
        p >> T.VOTV
        visina = p >> T.BROJ
        p >> T.DTOCKA
        tezina = p >> T.BROJ
        p >> T.VZATV
        return Struktura1(sportas, visina, tezina)


    def struktura2(p) -> 'Struktura2':
        p >> T.REZULTATI
        sportas_rez = p >> T.NAME
        p >> T.VOTV
        rezultat = []
        rezultat.append(p >> T.BROJ)
        while p >= T.TZAREZ:
            rezultat.append(p >> T.BROJ)
        p >> T.VZATV
        return Struktura2(sportas_rez, rezultat)


    def ubaci(p) -> 'Ubaci':
        p >> {T.PTILDA, T.PPLUS}
        sportas_rez = p >> T.ATHLETE_SCORE
        broj = p >> T.BROJ
        p >> T.TZAREZ
        return Ubaci(sportas_rez, broj)
    

    def izbaci(p) -> 'Izbaci':
        p >> {T.MTILDA, T.MMINUS}
        sportas_rez = p >> T.ATHLETE_SCORE
        broj = p >> T.BROJ
        p >> T.TZAREZ
        return Izbaci(sportas_rez, broj)


### AST
# Program: naredbe = [naredba]
# naredba: Funkcija: ime:NAME argumenti:NAME|ATHLETE|ATHLETE_SCORE|BROJ tijelo:naredba*
#          PozivFunkcije: ime:NAME argumenti:NAME|ATHLETE|ATHLETE_SCORE|BROJ
#          Pridruživanje: ime:NAME pridruženo:izraz
#          Ispis: što:BROJ|NAME|TEKST|ATHLETE|ATHLETE_SCORE
#          Unos: varijabla:BROJ|NAME
#          Loop: uvjet:BROJ|NAME tijelo:naredba*
#          Struktura1: sportas:NAME visina:BROJ tezina:BROJ
#          Struktura2: sportas_rez:NAME rezultati:BROJ*
#          Ubaci: sportas_rez:ATHLETE_SCORE rezultat:BROJ
#          Izbaci: sportas_rez:ATHLETE_SCORE rezultat:BROJ
# Op: op:T lijevo:aritm? desno:aritm
# Dohvati: sportas_rez:ATHLETE_SCORE gdje:BROJ|NAME
# Dohvati_vrijednost: varijabla:NAME
# Duljina: sportas_rez:ATHLETE_SCORE
# Visina: sportas:ATHLETE
# Težina: sportas:ATHLETE


rt.mem = Memorija()
function_registry = {}

class Program(AST):
    naredbe: 'naredba*'
    def izvrši(program):
        for naredba in program.naredbe:
            naredba.izvrši()


class Funkcija(AST):
    ime: 'NAME'
    argumenti: '(NAME|ATHLETE|ATHLETE_SCORE|BROJ)*'
    tijelo: 'naredba*'

    def izvrši(self):
        fja = []
        arg = []
        for argum in self.argumenti:
            try:
                rt.mem.provjeri(self, argum.vrijednost())
                print('Varijabla ' + argum.vrijednost() + ' je ranije deklarirana, ne moze se koristiti kao argument u definiciji funkcije!', end='\n')
                exit()
            except LookupError:
                arg.append(argum)
                nared = []
                for n in self.tijelo:
                    nared.append(n)
                fja.append(self.ime)
                fja.append(arg)
                fja.append(nared)
                function_registry[self.ime] = fja
        
    def execute(self):
        for naredba in self.tijelo:
            try:
                naredba.izvrši()
            except Povratak as exc:
                return exc.preneseno


class Povratak(NelokalnaKontrolaToka): """Signal koji šalje naredba vrati."""


class PozivFunkcije(AST):
    ime: 'NAME'
    argumenti: '(NAME|ATHLETE|ATHLETE_SCORE|BROJ)*'

    def izvrši(self):
        try:
            funct = function_registry[self.ime]
            arg = []
            for i in self.argumenti:
                arg.append(i)
            for j, p in enumerate(funct[1]):
                if arg[j] ^ T.BROJ:
                    rt.mem[p] = arg[j].vrijednost()
                else:
                    rt.mem[p] = rt.mem[arg[j]]
            f = Funkcija(funct[0], funct[1], funct[2])
            f.execute() 
            del rt.mem[p]
        except Povratak as exc:
            return exc.preneseno


class Pridruživanje(AST):
    ime: 'NAME'
    pridruženo: 'izraz'

    def izvrši(self):
        rt.mem[self.ime] = self.pridruženo.izračunaj()


class Ispis(AST):
    što: 'BROJ|NAME|TEKST|ATHLETE|ATHLETE_SCORE'

    def izvrši(self):
        if rezultat == None:
            if self.što ^ T.TEKST:
                ispisi = self.što.vrijednost()
                print(ispisi, end='\n')
            elif self.što ^ T.BROJ:
                print('Brojevi se ispisuju ili u varijablama ili u navodnicima!', end='\n')
            elif self.što ^ T.NAME: 
                ispisi = self.što.vrijednost()  
                try:
                    rt.mem.provjeri(self, ispisi)
                    print(rt.mem[ispisi], end='\n')
                except LookupError:
                    print('Ta varijabla nema pridruženu vrijednost!', end='\n')
            elif self.što ^ T.ATHLETE:
                ispisi = self.što.naziv()
                try:
                    rt.mem.provjeri(self, "@" + ispisi)
                    print(self.što.vrijednost(), end='\n')
                    print('    visina: ' + (rt.mem["@" + ispisi])[0], end='\n')
                    print('    težina: ' + (rt.mem["@" + ispisi])[1], end='\n')
                except LookupError:
                    print('Ta varijabla nema pridruženu vrijednost!', end='\n')
            elif self.što ^ T.ATHLETE_SCORE:
                ispisi = self.što.naziv()
                try:
                    rt.mem.provjeri(self, "~" + ispisi)
                    print(self.što.vrijednost(), end='\n')
                    print('    rezultati:', end=' ')
                    for rez in rt.mem["~" + ispisi]:
                        print(rez, end=' ')
                    print('\n')                
                except LookupError:
                    print('Ta varijabla nema pridruženu vrijednost!', end='\n')
        else:
            with open('kinesiology.txt', 'a', encoding="utf-8") as dat:
                if self.što ^ T.TEKST:
                    ispisi = self.što.vrijednost()
                    dat.write(ispisi + '\n')
                elif self.što ^ T.BROJ:
                    dat.write('Brojevi se ispisuju ili u varijablama ili u navodnicima!' + '\n')
                elif self.što ^ T.NAME: 
                    ispisi = self.što.vrijednost()  
                    try:
                        rt.mem.provjeri(self, ispisi)
                        dat.write(str(rt.mem[ispisi]) + '\n') 
                    except LookupError:
                        dat.write('Ta varijabla nema pridruženu vrijednost!' + '\n')
                elif self.što ^ T.ATHLETE:
                    ispisi = self.što.naziv()
                    try:
                        rt.mem.provjeri(self, "@" + ispisi)
                        dat.write(str(self.što.vrijednost()) + '\n') 
                        dat.write('    visina: ' + str((rt.mem["@" + ispisi])[0]) + '\n')
                        dat.write('    težina: ' + str((rt.mem["@" + ispisi])[1]) + '\n')
                    except LookupError:
                        dat.write('Ta varijabla nema pridruženu vrijednost!' + '\n')
                elif self.što ^ T.ATHLETE_SCORE:
                    ispisi = self.što.naziv()
                    try:
                        rt.mem.provjeri(self, "~" + ispisi)
                        dat.write(str(self.što.vrijednost()) + '\n') 
                        dat.write('    rezultati:')
                        for rez in rt.mem["~" + ispisi]:
                            dat.write(' ' + str(rez)) 
                        dat.write('\n')
                    except LookupError:
                        dat.write('Ta varijabla nema pridruženu vrijednost!' + '\n')


class Unos(AST):
    varijabla: 'BROJ|NAME'

    def izvrši(self):
        v = self.varijabla
        prompt = f'\t Unesite {v.sadržaj}: '
        if v ^ T.NAME: rt.mem[v] = input(prompt)
        elif v ^ T.BROJ:
            while ...:
                t = input(prompt)
                try: rt.mem[v] = fractions.Fraction(t.replace('÷', '/'))
                except ValueError: print(end='To nije racionalni broj! ')
                else: break
        else: assert False, f'Nepoznat tip varijable {v}'


class Loop(AST):
    uvjet: 'BROJ|NAME'
    tijelo: 'naredba*'

    def izvrši(self):
        if self.uvjet ^ T.BROJ:
            koliko = int(self.uvjet.vrijednost())
        elif self.uvjet ^ T.NAME:
            try:
                rt.mem.provjeri(self, self.uvjet.vrijednost())
                koliko = int(rt.mem[self.uvjet])
            except LookupError:
                print('Ta varijabla nema pridruženu vrijednost!', end='\n')        
        while koliko > 0:
            for naredba in self.tijelo:
                naredba.izvrši()
            koliko = koliko - 1


class Op(AST):
    op: 'T'
    lijevo: 'aritm?'
    desno: 'aritm'

    def izračunaj(self):
        if self.lijevo is nenavedeno: l = 0
        else: l = self.lijevo.izračunaj()
        o, d = self.op, self.desno.izračunaj()
        if o ^ T.PLUS: return float(l) + float(d)
        elif o ^ T.MINUS: return float(l) - float(d)
        elif o ^ T.PUTA: return float(l) * float(d)
        elif d: return float(l) / float(d)
        else: raise self.iznimka(f'dijeljenje nulom pri pridruživanju {rt.pridruženo}')


class Struktura1(AST):
    sportas: 'NAME'
    visina: 'BROJ'
    tezina: 'BROJ'

    def izvrši(self):
        try:
            rt.mem.provjeri(self, "@" + self.sportas.vrijednost())
            print('Sportas ' + self.sportas.vrijednost() + ' je vec deklariran!', end='\n')
        except LookupError:
            vrijednosti = []
            vrijednosti.append(self.visina.vrijednost())
            vrijednosti.append(self.tezina.vrijednost())
            rt.mem["@" + self.sportas.vrijednost()] = vrijednosti


class Struktura2(AST):
    sportas_rez: 'NAME'
    rezultati: 'BROJ*'

    def izvrši(self):
        try:
            rt.mem.provjeri(self, "~" + self.sportas_rez.vrijednost())
            print('Sportas ' + self.sportas_rez.vrijednost() + ' je vec deklariran!', end='\n')
            print('Za nadodavanje rezultata koristite operatore: +~ ili ++', end='\n')
        except LookupError:
            temp = []
            for rez in self.rezultati:
                temp.append(rez.vrijednost())
            rt.mem["~" + self.sportas_rez.vrijednost()] = temp


class Ubaci(AST):
    sportas_rez: 'ATHLETE_SCORE'
    rezultat: 'BROJ'

    def izvrši(self):
        temp = []
        for i in rt.mem[self.sportas_rez.vrijednost()]:
            temp.append(i)
        temp.append(self.rezultat.vrijednost())
        rt.mem[self.sportas_rez.vrijednost()] = temp


class Izbaci(AST):
    sportas_rez: 'ATHLETE_SCORE'
    rezultat: 'BROJ'

    def izvrši(self):
        temp = []
        for i in rt.mem[self.sportas_rez.vrijednost()]:
            temp.append(i)
        if self.rezultat.vrijednost() in temp:
            temp.remove(self.rezultat.vrijednost())
        rt.mem[self.sportas_rez.vrijednost()] = temp


class Dohvati(AST):
    sportas_rez: 'ATHLETE_SCORE'
    gdje: 'BROJ|NAME'

    def izračunaj(self):
        temp = []
        for i in rt.mem[self.sportas_rez.vrijednost()]:
            temp.append(i)
        return temp[int(self.gdje.vrijednost())]


class Dohvati_vrijednost(AST):
    varijabla: 'NAME'

    def izračunaj(self):
        vrati = self.varijabla.vrijednost()  
        try:
            rt.mem.provjeri(self, vrati)
            return rt.mem[vrati]
        except LookupError:
            print('Varijabla' + vrati + 'nema pridruženu vrijednost!', end='\n')

    def vrijednost(self):
        vrati = self.varijabla.vrijednost()  
        try:
            rt.mem.provjeri(self, vrati)
            return rt.mem[vrati]
        except LookupError:
            print('Varijabla' + vrati + 'nema pridruženu vrijednost!', end='\n')
    

class Duljina(AST):
    sportas_rez: 'ATHLETE_SCORE'

    def izračunaj(self):
        temp = []
        for i in rt.mem[self.sportas_rez.vrijednost()]:
            temp.append(i)
        return len(temp)


class Visina(AST):
    sportas: 'ATHLETE'

    def izračunaj(self):
        temp = []
        for i in rt.mem[self.sportas.vrijednost()]:
            temp.append(i)
        return temp[0]


class Težina(AST):
    sportas: 'ATHLETE'

    def izračunaj(self):
        temp = []
        for i in rt.mem[self.sportas.vrijednost()]:
            temp.append(i)
        return temp[1]


while True:
    naredba = input("Unesite naredbu: ")
    if naredba == "exit": break

    rezultat = re.match(r"dato\s(\w+)(\.txt)?$", naredba)
    if rezultat:
        ime_datoteke = naredba
        if not ime_datoteke.endswith(".txt"):
            ime_datoteke += ".txt"
        ime_datoteke = re.sub(r'^dato\s*', '', ime_datoteke)
        with open(ime_datoteke, "r", encoding="utf-8") as datoteka:
            uDatoteci = datoteka.read()
            naredba = uDatoteci

    prikaz(ast := P(naredba + '\n'))
    ast.izvrši()
    rezultat = None
