import json
import os
import tkinter as tk
from tkinter import messagebox, ttk

BESTANDSNAAM = "meldingen.json"
STATUSSEN = ("Open", "In behandeling", "Afgerond")
PRIORITEITEN = ("Laag", "Normaal", "Hoog")


class Melding:
    def __init__(self, melding_id, titel, omschrijving, status, prioriteit):
        self.id = melding_id
        self.titel = titel
        self.omschrijving = omschrijving
        self.status = status
        self.prioriteit = prioriteit

    def naar_dict(self):
        return {
            "id": self.id,
            "titel": self.titel,
            "omschrijving": self.omschrijving,
            "status": self.status,
            "prioriteit": self.prioriteit,
        }


meldingen = []


def laad_meldingen():
    global meldingen
    meldingen = []

    if not os.path.exists(BESTANDSNAAM):
        print("Geen bestand gevonden, standaard meldingen aangemaakt.")
        meldingen.append(Melding("NS-003", "Printer bij receptie geeft storing", "De printer geeft een foutmelding en print geen documenten meer.", "Afgerond", "Laag"))
        meldingen.append(Melding("NS-002", "Toegangspas aanvragen", "Een nieuwe medewerker heeft een toegangspas nodig voor de kantoorruimtes.", "Open", "Normaal"))
        meldingen.append(Melding("NS-001", "Airco op verdieping 2 werkt niet", "De airco in vergaderruimte B wordt niet koud.", "In behandeling", "Hoog"))
        sla_meldingen_op()
        return

    try:
        with open(BESTANDSNAAM, "r", encoding="utf-8") as bestand:
            data = json.load(bestand)
            for item in data:
                m = Melding(item["id"], item["titel"], item["omschrijving"], item["status"], item["prioriteit"])
                meldingen.append(m)
        print("Meldingen geladen:", len(meldingen))
    except Exception:
        messagebox.showwarning("Fout", "Kon het bestand niet laden. We starten met een lege lijst.")
        meldingen = []


def sla_meldingen_op():
    try:
        lijst = []
        for m in meldingen:
            lijst.append(m.naar_dict())

        with open(BESTANDSNAAM, "w", encoding="utf-8") as bestand:
            json.dump(lijst, bestand, indent=2, ensure_ascii=False)
        print("Meldingen opgeslagen.")
    except Exception:
        messagebox.showerror("Fout", "Opslaan van meldingen is mislukt.")


def maak_nieuw_id():
    bestaande_ids = []
    for m in meldingen:
        bestaande_ids.append(m.id)

    nummer = 1
    nieuw_id = f"NS-{nummer:03d}"

    while nieuw_id in bestaande_ids:
        nummer += 1
        nieuw_id = f"NS-{nummer:03d}"

    return nieuw_id


def ververs_overzicht(event=None):
    for rij in tabel.get_children():
        tabel.delete(rij)

    zoekwoord = zoek_balk.get().lower().strip()
    gekozen_status = filter_var.get()
    gekozen_prioriteit = prioriteit_filter_var.get()

    for m in meldingen:
        if gekozen_status != "Alle statussen" and m.status != gekozen_status:
            continue

        if gekozen_prioriteit != "Alle prioriteiten" and m.prioriteit != gekozen_prioriteit:
            continue

        tekst = (m.id + " " + m.titel + " " + m.omschrijving).lower()
        if zoekwoord != "" and zoekwoord not in tekst:
            continue

        tabel.insert("", "end", iid=m.id, values=(m.id, m.titel, m.status, m.prioriteit))

    open_aantal = 0
    behandeling_aantal = 0
    afgerond_aantal = 0

    for m in meldingen:
        if m.status == "Open":
            open_aantal += 1
        elif m.status == "In behandeling":
            behandeling_aantal += 1
        elif m.status == "Afgerond":
            afgerond_aantal += 1

    lbl_open_waarde.config(text=str(open_aantal))
    lbl_behandeling_waarde.config(text=str(behandeling_aantal))
    lbl_afgerond_waarde.config(text=str(afgerond_aantal))


def open_nieuwe_melding_scherm():
    venster = tk.Toplevel(root)
    venster.title("Nieuwe melding")
    venster.geometry("420x400")
    venster.resizable(False, False)

    frame = ttk.Frame(venster, padding=20)
    frame.pack(fill="both", expand=True)

    ttk.Label(frame, text="Nieuwe melding toevoegen", font=("Arial", 14, "bold")).pack(anchor="w", pady=(0, 15))

    ttk.Label(frame, text="Titel:").pack(anchor="w")
    titel_entry = ttk.Entry(frame)
    titel_entry.pack(fill="x", pady=(2, 10))

    ttk.Label(frame, text="Omschrijving:").pack(anchor="w")
    omschrijving_text = tk.Text(frame, height=5, font=("Arial", 10))
    omschrijving_text.pack(fill="x", pady=(2, 10))

    ttk.Label(frame, text="Status:").pack(anchor="w")
    status_var = tk.StringVar(value="Open")
    ttk.Combobox(frame, textvariable=status_var, values=STATUSSEN, state="readonly").pack(fill="x", pady=(2, 10))

    ttk.Label(frame, text="Prioriteit:").pack(anchor="w")
    prioriteit_var = tk.StringVar(value="Normaal")
    ttk.Combobox(frame, textvariable=prioriteit_var, values=PRIORITEITEN, state="readonly").pack(fill="x", pady=(2, 15))

    def opslaan():
        titel = titel_entry.get().strip()
        omschrijving = omschrijving_text.get("1.0", "end").strip()

        if titel == "" or omschrijving == "":
            messagebox.showwarning("Let op", "Vul zowel een titel als een omschrijving in.", parent=venster)
            return

        nieuwe_melding = Melding(maak_nieuw_id(), titel, omschrijving, status_var.get(), prioriteit_var.get())
        meldingen.insert(0, nieuwe_melding)
        print("Nieuwe melding toegevoegd:", nieuwe_melding.id)

        sla_meldingen_op()
        ververs_overzicht()
        venster.destroy()

    knoppen_frame = ttk.Frame(frame)
    knoppen_frame.pack(fill="x", side="bottom")
    ttk.Button(knoppen_frame, text="Annuleren", command=venster.destroy).pack(side="right")
    ttk.Button(knoppen_frame, text="Opslaan", command=opslaan).pack(side="right", padx=(0, 8))


def open_melding_details(event=None):
    geselecteerd = tabel.selection()
    if not geselecteerd:
        messagebox.showinfo("Geen selectie", "Klik eerst een melding aan in de lijst.")
        return

    gekozen_id = geselecteerd[0]
    gevonden_melding = None
    for m in meldingen:
        if m.id == gekozen_id:
            gevonden_melding = m
            break

    if gevonden_melding is None:
        return

    venster = tk.Toplevel(root)
    venster.title("Melding " + gevonden_melding.id)
    venster.geometry("450x380")
    venster.resizable(False, False)

    frame = ttk.Frame(venster, padding=20)
    frame.pack(fill="both", expand=True)

    info_tekst = gevonden_melding.id + " | Prioriteit: " + gevonden_melding.prioriteit
    ttk.Label(frame, text=info_tekst, foreground="blue", font=("Arial", 9, "bold")).pack(anchor="w")
    ttk.Label(frame, text=gevonden_melding.titel, font=("Arial", 14, "bold"), wraplength=400).pack(anchor="w", pady=(5, 15))

    ttk.Label(frame, text="Omschrijving:").pack(anchor="w")
    omschrijving_box = tk.Text(frame, height=6, font=("Arial", 10))
    omschrijving_box.pack(fill="x", pady=(2, 15))
    omschrijving_box.insert("1.0", gevonden_melding.omschrijving)
    omschrijving_box.config(state="disabled")

    ttk.Label(frame, text="Status aanpassen:").pack(anchor="w")
    status_var = tk.StringVar(value=gevonden_melding.status)
    ttk.Combobox(frame, textvariable=status_var, values=STATUSSEN, state="readonly").pack(fill="x", pady=(2, 15))

    def wijziging_opslaan():
        gevonden_melding.status = status_var.get()
        print("Status aangepast:", gevonden_melding.id)
        sla_meldingen_op()
        ververs_overzicht()
        venster.destroy()

    knoppen_frame = ttk.Frame(frame)
    knoppen_frame.pack(fill="x", side="bottom")
    ttk.Button(knoppen_frame, text="Sluiten", command=venster.destroy).pack(side="right")
    ttk.Button(knoppen_frame, text="Opslaan", command=wijziging_opslaan).pack(side="right", padx=(0, 8))


root = tk.Tk()
root.title("NovaSupport - Meldingen")
root.geometry("950x600")
root.configure(bg="#f4f6fa")

hoofd_frame = tk.Frame(root, bg="#f4f6fa", padx=25, pady=20)
hoofd_frame.pack(fill="both", expand=True)

boven_frame = tk.Frame(hoofd_frame, bg="#f4f6fa")
boven_frame.pack(fill="x", pady=(0, 15))

tk.Label(boven_frame, text="Meldingen", font=("Arial", 20, "bold"), bg="#f4f6fa", fg="#17233b").pack(side="left")
ttk.Button(boven_frame, text="+ Nieuwe melding", command=open_nieuwe_melding_scherm).pack(side="right")

tellers_frame = tk.Frame(hoofd_frame, bg="#f4f6fa")
tellers_frame.pack(fill="x", pady=(0, 15))

vak_open = tk.Frame(tellers_frame, bg="white", padx=15, pady=10)
vak_open.pack(side="left", fill="x", expand=True, padx=(0, 10))
tk.Label(vak_open, text="Openstaand", bg="white", fg="gray").pack(anchor="w")
lbl_open_waarde = tk.Label(vak_open, text="0", font=("Arial", 18, "bold"), bg="white")
lbl_open_waarde.pack(anchor="w")

vak_behandeling = tk.Frame(tellers_frame, bg="white", padx=15, pady=10)
vak_behandeling.pack(side="left", fill="x", expand=True, padx=(0, 10))
tk.Label(vak_behandeling, text="In behandeling", bg="white", fg="gray").pack(anchor="w")
lbl_behandeling_waarde = tk.Label(vak_behandeling, text="0", font=("Arial", 18, "bold"), bg="white")
lbl_behandeling_waarde.pack(anchor="w")

vak_afgerond = tk.Frame(tellers_frame, bg="white", padx=15, pady=10)
vak_afgerond.pack(side="left", fill="x", expand=True)
tk.Label(vak_afgerond, text="Afgerond", bg="white", fg="gray").pack(anchor="w")
lbl_afgerond_waarde = tk.Label(vak_afgerond, text="0", font=("Arial", 18, "bold"), bg="white")
lbl_afgerond_waarde.pack(anchor="w")

paneel = tk.Frame(hoofd_frame, bg="white", padx=15, pady=15)
paneel.pack(fill="both", expand=True)

filter_balk = tk.Frame(paneel, bg="white")
filter_balk.pack(fill="x", pady=(0, 10))

tk.Label(filter_balk, text="Alle meldingen", font=("Arial", 12, "bold"), bg="white").pack(side="left")

prioriteit_filter_var = tk.StringVar(value="Alle prioriteiten")
prioriteit_filter = ttk.Combobox(
    filter_balk,
    textvariable=prioriteit_filter_var,
    values=("Alle prioriteiten", "Laag", "Normaal", "Hoog"),
    state="readonly",
    width=17,
)
prioriteit_filter.pack(side="right")
prioriteit_filter.bind("<<ComboboxSelected>>", ververs_overzicht)

filter_var = tk.StringVar(value="Alle statussen")
status_filter = ttk.Combobox(
    filter_balk,
    textvariable=filter_var,
    values=("Alle statussen", "Open", "In behandeling", "Afgerond"),
    state="readonly",
    width=17,
)
status_filter.pack(side="right", padx=(0, 10))
status_filter.bind("<<ComboboxSelected>>", ververs_overzicht)

zoek_balk = ttk.Entry(filter_balk, width=25)
zoek_balk.pack(side="right", padx=(0, 10))
zoek_balk.bind("<KeyRelease>", ververs_overzicht)

tabel_frame = tk.Frame(paneel, bg="white")
tabel_frame.pack(fill="both", expand=True)

tabel = ttk.Treeview(tabel_frame, columns=("id", "titel", "status", "prioriteit"), show="headings")
tabel.heading("id", text="ID")
tabel.heading("titel", text="Melding")
tabel.heading("status", text="Status")
tabel.heading("prioriteit", text="Prioriteit")

tabel.column("id", width=80, stretch=False)
tabel.column("titel", width=420)
tabel.column("status", width=140, stretch=False)
tabel.column("prioriteit", width=100, stretch=False)

scrollbar = ttk.Scrollbar(tabel_frame, orient="vertical", command=tabel.yview)
tabel.configure(yscrollcommand=scrollbar.set)
tabel.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

tabel.bind("<Double-1>", open_melding_details)

onder_frame = tk.Frame(paneel, bg="white")
onder_frame.pack(fill="x", pady=(10, 0))

tk.Label(onder_frame, text="Dubbelklik op een melding om de details te bekijken.", bg="white", fg="gray").pack(side="left")
ttk.Button(onder_frame, text="Bekijk melding", command=open_melding_details).pack(side="right")

laad_meldingen()
ververs_overzicht()
root.mainloop()