import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

# Oldal konfigurációja
st.set_page_config(page_title="SaaS J-Görbe Szimulátor", layout="wide")
st.title("📊 SaaS J-Görbe és Virális Terjedés Kalkulátor")
st.write("Finomhangold a paramétereket, hogy lásd, melyik kombináció éli túl a növekedési völgyet!")

# --- OLDALSÁV: INTERAKTÍV PARAMÉTEREK ---
st.sidebar.header("🕹️ Változtatható Bemenő Adatok")

alaptoke    = st.sidebar.slider("Indulótőke ($)", min_value=5000, max_value=200000, value=30000, step=5000)
havi_dij    = st.sidebar.slider("Havi előfizetési díj ($)", min_value=5, max_value=200, value=29, step=1)
kezdeti_cac = st.sidebar.slider("1 új vevő megszerzési ára (Fizetett CAC) ($)", min_value=20, max_value=500, value=150, step=10)
fix_koltseg = st.sidebar.slider("Havi állandó (operatív) költség ($)", min_value=500, max_value=20000, value=3000, step=500)

pmf_honap = st.sidebar.slider(
    "Product-Market Fit (PMF) hónapja",
    min_value=3, max_value=24, value=12, step=1,
    help=(
        "Az a hónap, amelytől a termék valóban megfelel a piaci igénynek. "
        "Ettől a ponttól indul be a szerves, vírusos terjedés: "
        "a K-faktor meredeken emelkedik, csúcsán megközelíti az 1-et, "
        "majd az érettségi fázisban stabilizálódik."
    )
)

st.sidebar.header("⚙️ Egyéb Fix Beállítások")
honapok           = st.sidebar.slider("Szimulációs időtáv (hónapok)", min_value=12, max_value=36, value=24, step=2)
fizetett_novekedes = st.sidebar.slider("Havi fizetett növekedési ütem (%)", min_value=5, max_value=30, value=15, step=1) / 100
churn_rate        = st.sidebar.slider("Havi lemorzsolódás (Churn) (%)", min_value=0.0, max_value=10.0, value=3.0, step=0.5) / 100


# ---------------------------------------------------------------------------
# K-FAKTOR DINAMIKUS GÖRBE
# ---------------------------------------------------------------------------
# 4 fázis leírása:
#
#  1. Pre-PMF (t << pmf_honap):
#     Rendkívül alacsony (~0.03). Korai elfogadók, hiányzó virális hurkok.
#
#  2. PMF töréspontja (t ≈ pmf_honap):
#     Szigmoid emelkedés kezd. Szájreklám beindul, onboarding javul.
#
#  3. Hipernövekedés (t ≈ pmf_honap + ~5 hónappal):
#     K eléri csúcsát (~1.1). Ha K>1: önfenntartó vírusos terjedés.
#
#  4. Érettség / Plató (t >> pmf_honap):
#     Exponenciális visszaesés ~0.35-re. Piac telítődik, virális fáradtság.
# ---------------------------------------------------------------------------

K_KEZDETI  = 0.03   # Pre-PMF K-érték
K_CSUCS    = 1.10   # Hipernövekedési csúcs
K_STABIL   = 0.35   # Érettségi stabilizáció
MEREDEKSEG = 0.55   # Sigmoid meredeksége (kisebb = lassabb emelkedés)
CSUCS_OFFSET = 5    # A csúcs hány hónappal van PMF után
DECAY_RATE   = 0.08 # Érettségi visszaesés sebessége (havonkénti exponenciális)


def k_faktor_erteke(t: float) -> float:
    """
    4 fázisú, időfüggő K-faktor görbe.
    Két részből épül fel:
      - szigmoid emelkedés (Pre-PMF → Hipernövekedés)
      - exponenciális visszaesés a csúcs után (Plató)
    """
    peak_honap = pmf_honap + CSUCS_OFFSET

    # Szigmoid (0-tól a csúcsig)
    k_sig = K_KEZDETI + (K_CSUCS - K_KEZDETI) / (1.0 + np.exp(-MEREDEKSEG * (t - pmf_honap)))

    if t <= peak_honap:
        return k_sig
    else:
        # K értéke a csúcspontban (sigmoid alapján)
        k_a_csucson = K_KEZDETI + (K_CSUCS - K_KEZDETI) / (1.0 + np.exp(-MEREDEKSEG * CSUCS_OFFSET))
        decay = np.exp(-DECAY_RATE * (t - peak_honap))
        return K_STABIL + (k_a_csucson - K_STABIL) * decay


# K-faktor értékek előszámítása az egész időtávra
idovonal         = list(range(0, honapok + 1))
k_faktor_ertekek = [k_faktor_erteke(t) for t in idovonal]


# ---------------------------------------------------------------------------
# SZIMULÁCIÓS LOGIKA
# ---------------------------------------------------------------------------
ugyfelek = 100  # Kezdő ügyfélszám

cash_flow         = [0]
kumulalt_toke     = [alaptoke]
ugyfel_szamok     = [ugyfelek]
effektiv_cac_szintek = [kezdeti_cac]

csod_honap = None

for t in range(1, honapok + 1):
    k = k_faktor_ertekek[t]

    # 1. Virális (organikus) növekedés
    uj_ugyfelek_viralis  = ugyfelek * k
    # 2. Fizetett marketing általi növekedés
    uj_ugyfelek_fizetett = ugyfelek * fizetett_novekedes
    # 3. Lemorzsolódás
    elveszitett_ugyfelek = ugyfelek * churn_rate

    osszes_uj_ugyfél = uj_ugyfelek_fizetett + uj_ugyfelek_viralis
    ugyfelek = ugyfelek + osszes_uj_ugyfél - elveszitett_ugyfelek
    ugyfel_szamok.append(ugyfelek)

    # 4. Pénzügyek
    bevetel          = ugyfelek * havi_dij
    marketing_koltseg = uj_ugyfelek_fizetett * kezdeti_cac
    osszes_kiadas    = marketing_koltseg + fix_koltseg

    havi_ncf = bevetel - osszes_kiadas
    cash_flow.append(havi_ncf)

    # 5. Effektív CAC (a virális ügyfelek "ingyen" jöttek, lenyomják az átlagot)
    effektiv_cac = marketing_koltseg / osszes_uj_ugyfél if osszes_uj_ugyfél > 0 else kezdeti_cac
    effektiv_cac_szintek.append(effektiv_cac)

    # 6. Tőke
    uj_toke = kumulalt_toke[-1] + havi_ncf
    kumulalt_toke.append(uj_toke)

    if uj_toke < 0 and csod_honap is None:
        csod_honap = t


# ---------------------------------------------------------------------------
# EREDMÉNY METRIKÁK
# ---------------------------------------------------------------------------
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="Végső ügyfélszám", value=f"{int(ugyfelek)} fő")
with col2:
    utolso_eff_cac = effektiv_cac_szintek[-1]
    st.metric(
        label="Végső effektív CAC",
        value=f"{utolso_eff_cac:.1f} $",
        delta=f"Kezdetihez képest: {utolso_eff_cac - kezdeti_cac:.1f} $",
        delta_color="inverse"
    )
with col3:
    k_pmf = k_faktor_erteke(pmf_honap)
    k_peak = k_faktor_erteke(pmf_honap + CSUCS_OFFSET)
    st.metric(
        label=f"K-faktor csúcsértéke ({pmf_honap + CSUCS_OFFSET}. hónapban)",
        value=f"{k_peak:.2f}",
        delta="🔥 Vírusos!" if k_peak >= 1.0 else "Organikus növekedés"
    )

if csod_honap:
    st.error(f"💀 A tőke a(z) {csod_honap}. hónapban ELFOGYOTT!")
else:
    st.success("🚀 A vállalkozás TÚLÉLTE a J-görbe völgyét!")


# ---------------------------------------------------------------------------
# MATPLOTLIB GRAFIKONOK (3 panel)
# ---------------------------------------------------------------------------
fig, (ax_k, ax_cf, ax_toke) = plt.subplots(3, 1, figsize=(10, 12), sharex=True)

PMF_COLOR  = '#ff7f0e'
PMF_LABEL  = f'PMF hónapja ({pmf_honap}. hónap)'

# ── 1. panel: K-faktor görbe ────────────────────────────────────────────────
ax_k.fill_between(idovonal, k_faktor_ertekek, alpha=0.15, color='#9467bd')
ax_k.plot(idovonal, k_faktor_ertekek, color='#9467bd', linewidth=2.5, label='K-faktor (virális koefficiens)')
ax_k.axvline(pmf_honap, color=PMF_COLOR, linestyle='--', linewidth=1.8, label=PMF_LABEL)
ax_k.axhline(1.0, color='gray', linestyle=':', linewidth=1.2, label='K = 1 (vírusos terjedés határa)')
ax_k.set_ylabel('K-faktor értéke', fontsize=10)
ax_k.set_title('Virális koefficiens (K-faktor) dinamikus alakulása — PMF fázisai szerint', fontsize=12, fontweight='bold')
ax_k.grid(True, linestyle=':', alpha=0.6)
ax_k.legend(loc='upper left', fontsize=9)

# Fázis-annotációk
y_top = max(k_faktor_ertekek) * 1.05
ax_k.annotate('① Pre-PMF\n(alacsony K)', xy=(pmf_honap * 0.35, K_KEZDETI + 0.05),
               fontsize=8, color='#555', ha='center')
ax_k.annotate('③ Hipernövekedés\n(K ≈ csúcs)', xy=(pmf_honap + CSUCS_OFFSET, k_peak * 1.05),
               fontsize=8, color='#555', ha='center', va='bottom')
ax_k.annotate('④ Érettség\n(stabilizáció)', xy=(min(honapok, pmf_honap + CSUCS_OFFSET + 6), K_STABIL + 0.08),
               fontsize=8, color='#555', ha='center')

# ── 2. panel: Havi Cash Flow (J-görbe) ─────────────────────────────────────
ax_cf.plot(idovonal, cash_flow, color='#1f77b4', linewidth=2.5, label='Havi Nettó Cash Flow')
ax_cf.axhline(0, color='black', linestyle='--', linewidth=0.8)
ax_cf.axvline(pmf_honap, color=PMF_COLOR, linestyle='--', linewidth=1.8, label=PMF_LABEL)
ax_cf.set_ylabel('Havi egyenleg ($)', fontsize=10)
ax_cf.set_title('A klasszikus SaaS J-görbe — Havi nettó cash-flow alakulása', fontsize=12, fontweight='bold')
ax_cf.grid(True, linestyle=':', alpha=0.6)
ax_cf.legend(loc='upper left', fontsize=9)

# ── 3. panel: Alaptőke ─────────────────────────────────────────────────────
ax_toke.plot(idovonal, kumulalt_toke, color='#2ca02c', linewidth=2.5, label='Rendelkezésre álló tőke')
ax_toke.axhline(0, color='red', linestyle='-', linewidth=1.2, label='Csőd határa (0 $)')
ax_toke.axvline(pmf_honap, color=PMF_COLOR, linestyle='--', linewidth=1.8, label=PMF_LABEL)
if csod_honap:
    ax_toke.axvline(csod_honap, color='red', linestyle='-', linewidth=2.0, alpha=0.7,
                    label=f'Csőd ({csod_honap}. hónap)')
ax_toke.set_xlabel('Eltelt hónapok', fontsize=10)
ax_toke.set_ylabel('Megmaradt tőke ($)', fontsize=10)
ax_toke.set_title('Az Alaptőke fogyása és visszapattanása', fontsize=12, fontweight='bold')
ax_toke.grid(True, linestyle=':', alpha=0.6)
ax_toke.legend(loc='upper left', fontsize=9)

plt.xticks(np.arange(0, honapok + 1, 2))
plt.tight_layout()
st.pyplot(fig)


# ---------------------------------------------------------------------------
# MAGYARÁZAT
# ---------------------------------------------------------------------------
st.subheader("💡 Hogyan működik a dinamikus K-faktor?")
st.markdown(f"""
A szimulátor a virális koefficienst (K-faktort) automatikusan, a PMF hónapjától függően számítja ki — 4 fázisban:

| Fázis | Időszak | K-érték | Mi történik? |
|---|---|---|---|
| **① Pre-PMF** | PMF előtt | ~{K_KEZDETI} | Korai elfogadók, gyenge virális hurkok, alacsony konverzió |
| **② PMF töréspontja** | PMF hónapja ± pár hónap | emelkedő | Szájreklám beindul, onboarding javul, hálózati hatás |
| **③ Hipernövekedés** | PMF + ~5 hónap | ~{K_CSUCS:.1f} (csúcs) | Ha K≥1: önfenntartó vírusos terjedés, CAC közelít nullához |
| **④ Érettség / Plató** | Csúcs után | ~{K_STABIL} | Piaci telítettség, virális fáradtság, churn-fókusz |

**Kísérletezési tippek:**
- 🕐 **Korai PMF (3–8. hónap):** A virális hatás hamarabb beindul, kisebb tőkére lehet szükség — de vajon reális?
- 🕑 **Késői PMF (18–24. hónap):** Mélyebb völgy, nagyobb indulótőke kell a túléléshez.
- 💸 **Alacsony díj + magas CAC kombó:** Látványos J-görbe — de csak elegendő tőkével élhető túl a völgy.
- 📉 **Churn hatása:** Magas lemorzsolódásnál a K-faktor csúcsa sem tudja behúzni a bevételi görbét.
""")
