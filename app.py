st.set_page_config(page_title="Ultimate Offer Analyzer", layout="wide")
st.title("New Grad Offer Analyzer + City Budget Calculator")

# ──────────────────────────── CITY DATABASE (updated Jan 2026) ────────────────────────────
city_data = {
    # Major aerospace hubs + San Francisco
    "Seattle, WA":           {"rent": 2450, "groceries": 460, "utils": 155, "trans": 200, "tax_rate": 26},
    "Los Angeles / El Segundo, CA": {"rent": 2950, "groceries": 490, "utils": 190, "trans": 320, "tax_rate": 34},
    "San Francisco, CA":     {"rent": 3600, "groceries": 550, "utils": 220, "trans": 350, "tax_rate": 33},
    "Huntsville, AL":        {"rent": 1450, "groceries": 380, "utils": 140, "trans": 180, "tax_rate": 24},
    "Denver / Boulder, CO":  {"rent": 2350, "groceries": 440, "utils": 165, "trans": 230, "tax_rate": 29},
    "Houston, TX":           {"rent": 1750, "groceries": 410, "utils": 175, "trans": 260, "tax_rate": 25},
    "Washington DC area (NoVA/MD)": {"rent": 2700, "groceries": 480, "utils": 180, "trans": 280, "tax_rate": 31},
    "Tucson, AZ":            {"rent": 1550, "groceries": 395, "utils": 150, "trans": 200, "tax_rate": 27},
    "Phoenix / Mesa, AZ":    {"rent": 1950, "groceries": 420, "utils": 160, "trans": 240, "tax_rate": 27},
    "Colorado Springs, CO":  {"rent": 1900, "groceries": 425, "utils": 155, "trans": 210, "tax_rate": 29},
    "San Diego, CA":         {"rent": 3100, "groceries": 500, "utils": 195, "trans": 300, "tax_rate": 34},
    "Boston / Hanscom, MA":  {"rent": 3200, "groceries": 510, "utils": 200, "trans": 290, "tax_rate": 30},
    "Melbourne / Palm Bay, FL": {"rent": 1850, "groceries": 430, "utils": 170, "trans": 220, "tax_rate": 25},
    "Cape Canaveral, FL":    {"rent": 2100, "groceries": 440, "utils": 175, "trans": 230, "tax_rate": 25},
    "Fort Worth / Dallas, TX": {"rent": 1850, "groceries": 415, "utils": 180, "trans": 250, "tax_rate": 25},
    "Wichita, KS":           {"rent": 1150, "groceries": 370, "utils": 135, "trans": 170, "tax_rate": 28},
    "St. Louis, MO":         {"rent": 1400, "groceries": 390, "utils": 145, "trans": 190, "tax_rate": 27},
    "Oklahoma City, OK":     {"rent": 1250, "groceries": 375, "utils": 140, "trans": 180, "tax_rate": 26},
    "Hampton Roads / Newport News, VA": {"rent": 1650, "groceries": 405, "utils": 160, "trans": 220, "tax_rate": 29},
    "Atlanta, GA":           {"rent": 2100, "groceries": 430, "utils": 170, "trans": 260, "tax_rate": 29},
    "Salt Lake City, UT":    {"rent": 1800, "groceries": 410, "utils": 150, "trans": 210, "tax_rate": 28},
    "Austin, TX":            {"rent": 2200, "groceries": 435, "utils": 175, "trans": 270, "tax_rate": 25},
    "Remote / Low-COL US":   {"rent": 1200, "groceries": 380, "utils": 140, "trans": 150, "tax_rate": 24},
}

# ──────────────────────────── PDF READING ────────────────────────────
uploaded_file = st.file_uploader("Upload your offer letter (PDF) — optional", type="pdf")

def extract_text_from_pdf(file):
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text

def find_salary(text):
    patterns = [
        r'[\$]\s*([\d,]+)\s*(?:per\s+year|annual|year|base|salary)',
        r'(?:base|annual|salary)[:\s]*[\$]\s*([\d,]+)',
        r'[\$]\s*([\d,]+)\s*annually',
        r'([\d,]{5,6})\s*(?:annual|year|base)',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return int(match.group(1).replace(',', ''))
    return None

def find_bonus(text):
    bonus = re.search(r'(sign.?on|signing|relocation|bonus).{0,60}[\$]\s*([\d,]+)', text, re.IGNORECASE)
    if bonus:
        return int(bonus.group(2).replace(',', ''))
    return 0

# Extract from PDF if uploaded
extracted_salary = None
extracted_bonus = None
if uploaded_file:
    text = extract_text_from_pdf(uploaded_file)
    extracted_salary = find_salary(text)
    extracted_bonus = find_bonus(text)
    if extracted_salary or extracted_bonus:
        st.success("Offer letter parsed successfully!")

# ──────────────────────────── MAIN APP ────────────────────────────
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Salary & Bonus (auto-detected or manual)")
    salary = st.number_input("Base Salary ($ per year)", min_value=0, value=extracted_salary or 85000, step=1000)
    bonus = st.number_input("Sign-on / Relocation Bonus ($)", min_value=0, value=extracted_bonus or 0, step=500)

    st.subheader("Job Location")
    city = st.selectbox("Where is the job?", options=sorted(city_data.keys()), index=0)

    c = city_data[city]
    monthly_gross = salary / 12
    take_home = monthly_gross * (1 - c["tax_rate"]/100)

    st.metric("Estimated Monthly Take-Home", f"${take_home:,.0f}", help=f"After ~{c['tax_rate']}% effective taxes (federal + state)")

    budget_data = {
        "Category": [
            "Rent / Housing", "Groceries + Eating Out", "Utilities + Internet",
            "Transportation", "Student Loans ($40k @ 5%)", "Health/Insurance",
            "Fun & Personal", "Savings / Emergency Fund"
        ],
        "Monthly Cost": [c["rent"], c["groceries"], c["utils"], c["trans"], 450, 120, 350, 300]
    }
    df = pd.DataFrame(budget_data)
    total_expenses = df["Monthly Cost"].sum()
    leftover = take_home - total_expenses

    st.subheader(f"Realistic Monthly Budget — {city}")
    st.table(df.style.format({"Monthly Cost": "${:,.0f}"}))

    st.metric("Total Expenses", f"${total_expenses:,}")
    st.metric("Leftover Money", f"${leftover:,.0f}", delta=f"{leftover:+,.0f}")

    if leftover >= 1000:   st.balloons(); st.success("Verdict: You’ll build wealth quickly here!")
    elif leftover >= 500:  st.success("Verdict: Very comfortable lifestyle with potential for solid savings.")
    elif leftover >= 100:  st.info("Verdict: You’ll live well with smart budgeting.")
    else:                  st.warning("Verdict: Tight — strongly consider roommates, negotiating higher, cutting extras, or donating blood frequently.")

   

with col2:
    st.subheader("Relocation Cost Calculator")
    st.number_input("Flight / Gas", min_value=0, value=400, key="travel")
    st.number_input("Moving truck / shipping", min_value=0, value=2800, key="truck")
    st.number_input("Temp housing (2 weeks)", min_value=0, value=1800, key="hotel")
    st.number_input("Deposit + first month rent", min_value=0, value=c["rent"]*2, key="deposit")
    st.number_input("Furniture & misc", min_value=0, value=800, key="misc")

    total_move = sum([st.session_state.travel, st.session_state.truck, st.session_state.hotel,
                      st.session_state.deposit, st.session_state.misc])
    you_pay = max(0, total_move - bonus)

    st.metric("Total Move Cost", f"${total_move:,}")
    st.metric("Company Covers (bonus)", f"${bonus:,}")
    st.metric("You Pay Out-of-Pocket", f"${you_pay:,}")

    if you_pay == 0: st.success("Fully covered — fantastic!")
    elif you_pay < 2000: st.success("Very reasonable out-of-pocket.")
    else: st.warning("Consider negotiating a higher relocation package.")


st.caption("Updated Jan 2026  Built for aerospace new grads 🚀")
