import tkinter as tk
import random

YHDISTELMAT = [
    "Ykköset", "Kakkoset", "Kolmoset", "Neloset", "Vitoset", "Kutoset",
    "Kolme samaa", "Neljä samaa", "Täyskäsi",
    "Pieni suora", "Iso suora", "Chance", "Yahtzee"
]

class Yahtzee:
    def __init__(self, root):
        self.root = root
        self.root.title("Yahtzee")
        self.root.geometry("1100x600") 

        self.nykyinen_pelaaja = 0
        self.nopat = [0]*5
        self.lukitut = [tk.BooleanVar() for _ in range(5)]
        self.heitot = 0

        # Aloitetaan pelaajavalinnalla
        self.valitse_pelaajat()

    # ---------- UI ----------
    def luo_ui(self):
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # VASEN (nopat + kontrollit)
        self.left_frame = tk.Frame(main_frame)
        self.left_frame.pack(side="left", fill="y", padx=10)

        self.pelaaja_label = tk.Label(self.left_frame, font=("Arial", 16))
        self.pelaaja_label.pack(pady=10)

        # Nopat
        noppa_frame = tk.Frame(self.left_frame)
        noppa_frame.pack(pady=10)

        self.noppa_labels = []
        for i in range(5):
            f = tk.Frame(noppa_frame)
            f.grid(row=0, column=i, padx=5)

            lbl = tk.Label(
                f,
                text="-",
                font=("Arial", 28),
                width=2,
                height=1,
                bg="white",
                relief="raised",
                borderwidth=2
            )
            lbl.pack(pady=5)
            self.noppa_labels.append(lbl)
            lbl.bind("<Button-1>", lambda e, idx=i: self.toggle_lukittu(idx))

        self.heitto_btn = tk.Button(self.left_frame, text="Heitä", command=self.heita, width=15, height=2)
        self.heitto_btn.pack(pady=10)

        self.info_label = tk.Label(self.left_frame)
        self.info_label.pack()

        # OIKEA (pistetaulukko)
        self.right_frame = tk.Frame(main_frame)
        self.right_frame.pack(side="right", fill="both", expand=True)

        table_frame = tk.Frame(self.right_frame)
        table_frame.pack(fill="both", expand=True)

        # Sarakkeiden skaalaus
        num_columns = len(self.pelaajat) + 1 #pelaajien lukumäärä plus sarake yhdistelmistä
        for col in range(num_columns):
            table_frame.grid_columnconfigure(col, weight=1)

        # Otsikkorivi
        tk.Label(table_frame, text="Yhdistelmä", width=20, relief="solid").grid(row=0, column=0, sticky="nsew")
        for col, p in enumerate(self.pelaajat):
            tk.Label(table_frame, text=p, width=15, relief="solid").grid(row=0, column=col+1, sticky="nsew")

        self.table_labels = {}

        current_row = 1

        # YLÄOSA (6 ensimmäistä)
        for y in YHDISTELMAT[:6]:
            tk.Label(table_frame, text=y, width=20, relief="solid")\
                .grid(row=current_row, column=0, sticky="nsew")

            self.table_labels[y] = {}
            for col, p in enumerate(self.pelaajat):
                lbl = tk.Label(table_frame, text="-", width=15, relief="solid", bg="white")
                lbl.grid(row=current_row, column=col+1, sticky="nsew")
                lbl.bind("<Button-1>", lambda e, y=y, p=p: self.klikkaa_solua(y, p))
                self.table_labels[y][p] = lbl

            current_row += 1


        # Yläosan summa
        self.ylapiste_rivi = "Yläosan summa"
        tk.Label(table_frame, text=self.ylapiste_rivi, width=20, relief="solid")\
            .grid(row=current_row, column=0, sticky="nsew")

        self.table_labels[self.ylapiste_rivi] = {}
        for col, p in enumerate(self.pelaajat):
            lbl = tk.Label(table_frame, text="0", width=15, relief="solid", bg="#f0f0ff")
            lbl.grid(row=current_row, column=col+1, sticky="nsew")
            self.table_labels[self.ylapiste_rivi][p] = lbl

        current_row += 1


        # Bonus
        self.bonus_rivi = "Bonus"
        tk.Label(table_frame, text=self.bonus_rivi, width=20, relief="solid")\
            .grid(row=current_row, column=0, sticky="nsew")

        self.table_labels[self.bonus_rivi] = {}
        for col, p in enumerate(self.pelaajat):
            lbl = tk.Label(table_frame, text="0", width=15, relief="solid", bg="#ffffe0")
            lbl.grid(row=current_row, column=col+1, sticky="nsew")
            self.table_labels[self.bonus_rivi][p] = lbl

        current_row += 1


        # ALAOSA (loput yhdistelmät)
        for y in YHDISTELMAT[6:]:
            tk.Label(table_frame, text=y, width=20, relief="solid")\
                .grid(row=current_row, column=0, sticky="nsew")

            self.table_labels[y] = {}
            for col, p in enumerate(self.pelaajat):
                lbl = tk.Label(table_frame, text="-", width=15, relief="solid", bg="white")
                lbl.grid(row=current_row, column=col+1, sticky="nsew")
                lbl.bind("<Button-1>", lambda e, y=y, p=p: self.klikkaa_solua(y, p))
                self.table_labels[y][p] = lbl

            current_row += 1


        # Yhteensä 
        self.yhteensa_rivi = "Yhteensä"
        tk.Label(table_frame, text=self.yhteensa_rivi, width=20, relief="solid",
                bg="#c0c0c0", font=("Arial", 12, "bold"))\
            .grid(row=current_row, column=0, sticky="nsew")

        self.yhteensa_labels = {}
        for col, p in enumerate(self.pelaajat):
            lbl = tk.Label(table_frame, text="0", width=15, relief="solid",
                        bg="#c0c0c0", font=("Arial", 12, "bold"))
            lbl.grid(row=current_row, column=col+1, sticky="nsew")
            self.yhteensa_labels[p] = lbl

    def toggle_lukittu(self, idx):
        # Vaihda lukitun tilaa
        self.lukitut[idx].set(not self.lukitut[idx].get())
        # Päivitä väri heti
        self.noppa_labels[idx].config(
            bg="#ddd" if self.lukitut[idx].get() else "white"
        )

    # Nopan symbolit
    def noppa_symboli(self, arvo):
        symbolit = {
            1: "⚀",
            2: "⚁",
            3: "⚂",
            4: "⚃",
            5: "⚄",
            6: "⚅"
        }
        return symbolit.get(arvo, "-")

    # Yhdistelmän valinta
    def klikkaa_solua(self, yhdistelma, pelaaja):
        # Klikkaus toimii vain aktiiviselle pelaajalle
        if pelaaja != self.pelaajat[self.nykyinen_pelaaja]:
            return
        self.klikkaa_pistetta(yhdistelma)

    # Pelaajamäärän valinta
    def valitse_pelaajat(self):
        self.valinta_win = tk.Toplevel(self.root)
        self.valinta_win.title("Aloitus")
        self.valinta_win.geometry("400x300")
        self.valinta_win.grab_set()
        self.valinta_win.transient(self.root)

        # KESKITYS RUUDULLE
        self.valinta_win.update_idletasks()

        width = 400
        height = 300

        screen_width = self.valinta_win.winfo_screenwidth()
        screen_height = self.valinta_win.winfo_screenheight()

        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)

        self.valinta_win.geometry(f"{width}x{height}+{x}+{y}")
        self.valinta_win.grab_set()
        self.valinta_win.transient(self.root)

        # Keskitetään sarakkeet
        for i in range(4):
            self.valinta_win.grid_columnconfigure(i, weight=1)

        # Pelaajamäärä
        tk.Label(self.valinta_win, text="Montako pelaajaa?", font=("Arial", 12))\
            .grid(row=0, column=0, columnspan=4, pady=5, sticky="n")

        self.pelaaja_var = tk.IntVar(value=2)
        for i in range(1,5):
            tk.Radiobutton(
                self.valinta_win, text=str(i), variable=self.pelaaja_var, value=i,
                command=self.paivita_nimikentat
            ).grid(row=1, column=i-1, sticky="nsew", padx=10)

        # Pelaajien nimet
        tk.Label(self.valinta_win, text="Pelaajien nimet:", font=("Arial", 12))\
            .grid(row=2, column=0, columnspan=4, pady=(15,5), sticky="n")

        self.nimi_entryt = []
        for i in range(4):
            e = tk.Entry(self.valinta_win)
            e.grid(row=3+i, column=0, columnspan=4, padx=50, pady=2, sticky="we")
            e.insert(0, f"Pelaaja {i+1}")
            self.nimi_entryt.append(e)

        self.paivita_nimikentat()

        # Aloita peli -nappi
        self.aloita_btn = tk.Button(self.valinta_win, text="Aloita peli", command=self.aloita_peli)
        self.aloita_btn.grid(row=7, column=0, columnspan=4, pady=15, padx=50, sticky="we")

    def paivita_nimikentat(self):
        n = self.pelaaja_var.get()
        for i, e in enumerate(self.nimi_entryt):
            if i < n:
                e.grid()       
            else:
                e.grid_remove() 

    def aloita_peli(self):
        n = self.pelaaja_var.get()
        # Haetaan nimet kentistä
        self.pelaajat = [self.nimi_entryt[i].get() for i in range(n)]
        self.pisteet = {p: {y: None for y in YHDISTELMAT} for p in self.pelaajat}
        self.nykyinen_pelaaja = 0

        self.valinta_win.destroy()
        self.luo_ui()
        self.update_ui()


    # LOGIIKKA
    def heita(self):
        if self.heitot >= 3:
            return

        for i in range(5):
            if not self.lukitut[i].get():
                self.nopat[i] = random.randint(1, 6)

        self.heitot += 1
        self.update_ui()

    # Yhdistelmän valinta
    def klikkaa_pistetta(self, yhdistelma):
        p = self.pelaajat[self.nykyinen_pelaaja]

        if self.heitot == 0:
            return

        if self.pisteet[p][yhdistelma] is not None:
            return

        piste = self.laske(yhdistelma)
        self.pisteet[p][yhdistelma] = piste

        self.update_ui()

        # Tarkista peli loppu ennen seuraavaa pelaajaa
        if all(all(v is not None for v in self.pisteet[p].values()) for p in self.pelaajat):
            self.nayta_loppuikkuna()
            return  # Lopeta tässä, ei vaihdeta pelaajaa

        self.seuraava_pelaaja()

    # UI päivitys
    def update_ui(self):
        # Päivitä vuoron nimi label
        self.pelaaja_label.config(
            text=f"Vuoro: {self.pelaajat[self.nykyinen_pelaaja]}"
        )

        PELAAJAVARIT = ["#0000ff", "#ff0000", "#008000", "#a52a2a"]
        self.pelaaja_label.config(fg=PELAAJAVARIT[self.nykyinen_pelaaja])

        # Päivitä heittonappi
        if self.heitot < 3:
            self.heitto_btn.config(text=f"Heitä ({self.heitot+1}/3)", state="normal")
        else:
            self.heitto_btn.config(text="Heitä", state="disabled")

        # Päivitä nopat
        for i, val in enumerate(self.nopat):
            self.noppa_labels[i].config(
                text=self.noppa_symboli(val),
                bg="#ddd" if self.lukitut[i].get() else "white"
            )

        # Päivitä pistetaulukko
        for y in YHDISTELMAT:
            for p in self.pelaajat:
                val = self.pisteet[p][y]
                if val is None:
                    if p == self.pelaajat[self.nykyinen_pelaaja] and self.heitot > 0:
                        val = self.laske(y)
                        self.table_labels[y][p].config(text=str(val), bg="#d0f0ff")
                    else:
                        self.table_labels[y][p].config(text="-", bg="white")
                else:
                    self.table_labels[y][p].config(text=str(val), bg="#90ee90")

        # Yhteensä = kaikki täytetyt pisteet + bonus
        for p in self.pelaajat:
            # Yläosan summa
            ylaosa_pisteet = sum(
                self.pisteet[p][y] for y in YHDISTELMAT[:6] if self.pisteet[p][y] is not None
            )
            self.table_labels[self.ylapiste_rivi][p].config(text=str(ylaosa_pisteet))

            # Bonus
            bonus = 35 if ylaosa_pisteet >= 63 else 0
            self.table_labels[self.bonus_rivi][p].config(text=str(bonus))

            # Yhteensä = kaikki täytetyt pisteet + bonus
            yhteensa = sum(v for v in self.pisteet[p].values() if v is not None) + bonus
            self.yhteensa_labels[p].config(text=str(yhteensa))



    # PISTEIDEN LASKU
    def laske(self, y):
        nopat = self.nopat
        counts = {i: nopat.count(i) for i in range(1,7)}

        if y == "Ykköset": return counts[1]*1
        if y == "Kakkoset": return counts[2]*2
        if y == "Kolmoset": return counts[3]*3
        if y == "Neloset": return counts[4]*4
        if y == "Vitoset": return counts[5]*5
        if y == "Kutoset": return counts[6]*6

        if y == "Kolme samaa":
            for silmaluku, maara in counts.items():
                if maara >= 3:
                    return silmaluku * 3
            return 0

        if y == "Neljä samaa":
            for silmaluku, maara in counts.items():
                if maara >= 4:
                    return silmaluku * 4
            return 0

        if y == "Täyskäsi":
            # Etsitään täyskäsi: pitää olla tarkalleen yksi kolmikko ja yksi pari
            if sorted(counts.values()) == [2,3]:
                return sum(nopat)
            else:
                return 0

        if y == "Pieni suora":
           return 15 if set(nopat) == {1,2,3,4,5} else 0

        if y == "Iso suora":
            return 20 if set(nopat) == {2,3,4,5,6} else 0

        if y == "Chance":
            return sum(nopat)

        if y == "Yahtzee":
            return 50 if len(set(nopat)) == 1 else 0

        return 0

    # VUORO
    def seuraava_pelaaja(self):
        self.nopat = [0]*5
        self.heitot = 0

        for l in self.lukitut:
            l.set(False)

        self.nykyinen_pelaaja = (self.nykyinen_pelaaja + 1) % len(self.pelaajat)

        self.update_ui()


    def peli_loppu(self):
        return all(
            all(v is not None for v in self.pisteet[p].values())
            for p in self.pelaajat
        )



    def nayta_loppuikkuna(self):
        # Kerätään lopulliset pisteet
        tulokset = []

        for pelaaja in self.pelaajat:
            pisteet = int(self.yhteensa_labels[pelaaja]["text"])
            tulokset.append((pelaaja, pisteet))

        # Lajitellaan suurimmasta pienimpään
        tulokset.sort(key=lambda x: x[1], reverse=True)

        # Luodaan ikkuna
        loppu_win = tk.Toplevel(self.root)
        loppu_win.title("Peli päättyi")

        width = 400
        height = 300

        # Keskitys
        screen_width = loppu_win.winfo_screenwidth()
        screen_height = loppu_win.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        loppu_win.geometry(f"{width}x{height}+{x}+{y}")

        # VOITTAJA
        voittaja, voittajan_pisteet = tulokset[0]

        tk.Label(
            loppu_win,
            text=f"🏆 Voittaja: {voittaja} ({voittajan_pisteet} p)",
            font=("Arial", 18, "bold"),
            fg="green"
        ).pack(pady=20)

        # Muut pelaajat
        for sijoitus, (pelaaja, pisteet) in enumerate(tulokset[1:], start=2):
            tk.Label(
                loppu_win,
                text=f"{sijoitus}. {pelaaja} ({pisteet} p)",
                font=("Arial", 12)
            ).pack()

        tk.Button(
            loppu_win,
            text="Sulje peli",
            command=self.root.destroy
        ).pack(pady=20)

if __name__ == "__main__":
    root = tk.Tk()
    app = Yahtzee(root)
    root.mainloop()