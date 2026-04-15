import streamlit as st
from fpdf import FPDF
from datetime import datetime
import io

# إعداد الصفحة في المتصفح
st.set_page_config(page_title="Schneider & Partner System", layout="wide")

# --- كلاس توليد الـ PDF (معدل ليعمل مع Streamlit) ---
class EngineeringPDF(FPDF):
    def header(self):
        # ملاحظة: الصور يجب أن ترفع في التطبيق أو تكون بروابط
        self.set_font("Arial", 'B', 15)
        self.cell(0, 10, "TECHNICAL MAINTENANCE & TEST REPORT", ln=True, align='C')
        self.set_font("Arial", 'I', 9)
        self.cell(0, 5, f"System Version: 510.2 (Mobile Web)", ln=True, align='C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

# --- واجهة المستخدم (Streamlit UI) ---
st.title("⚡ Schneider & Partner Engineering")
st.subheader("Maintenance System v510.2")

# I. PROJECT ADMINISTRATION
with st.expander("I. PROJECT ADMINISTRATION", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        p_name = st.text_input("Project Name")
        rfq = st.text_input("RFQ / Ref")
    with col2:
        location = st.text_input("Location")
        eng_name = st.text_input("Engineer Name")
        date_val = st.date_input("Date", datetime.now())

# II. EQUIPMENT CONFIGURATION
with st.expander("II. EQUIPMENT CONFIGURATION"):
    maint_type = st.selectbox("Maintenance Type", ["Routine Maintenance", "Emergency Call", "Corrective Action"])
    category = st.selectbox("Category", ["Substation", "TR", "MV", "LV"])
    
    dynamic_data = {}
    if category == "TR":
        dynamic_data["TR Type"] = st.selectbox("TR Type", ["Distribution", "Power", "Dry"])
        dynamic_data["S/N"] = st.text_input("Serial Number")
    elif category == "LV":
        dynamic_data["Product"] = st.selectbox("Product", ["Blokset", "Prisma", "ATS"])

# III. TECHNICAL TEST RECORDS
with st.expander("III. TECHNICAL TEST RECORDS"):
    if 'rows' not in st.session_state:
        st.session_state.rows = 1

    test_data = []
    for i in range(st.session_state.rows):
        c1, c2, c3, c4 = st.columns([3, 2, 1, 2])
        test_desc = c1.selectbox(f"Test {i+1}", ["Megger", "Ratio", "Hi-Pot", "Secondary Injection"], key=f"t{i}")
        res = c2.text_input("Result", key=f"r{i}")
        unit = c3.text_input("Unit", key=f"u{i}")
        stat = c4.selectbox("Status", ["PASSED", "FAILED"], key=f"s{i}")
        test_data.append([test_desc, res, unit, stat])
    
    if st.button("+ Add Test Row"):
        st.session_state.rows += 1
        st.rerun()

# IV. WORK DETAILS
with st.expander("IV. WORK DETAILS"):
    prob = st.text_area("Problem Description")
    act = st.text_area("Action / Treatment Taken")
    mat = st.text_area("Materials / Parts Used")

# V. VALIDATION & PHOTOS
with st.expander("V. PHOTOS & SIGNATURE"):
    img_before = st.file_uploader("Upload (BEFORE)", type=['png', 'jpg', 'jpeg'])
    img_after = st.file_uploader("Upload (AFTER)", type=['png', 'jpg', 'jpeg'])
    signature = st.text_input("Engineer Signature (Type Name)")

# --- توليد الـ PDF ---
if st.button("GENERATE PDF REPORT", type="primary", use_container_width=True):
    pdf = EngineeringPDF()
    pdf.add_page()
    
    # إضافة البيانات للـ PDF (تبسيطاً للنموذج)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "1. ADMINISTRATION", ln=True, border='B')
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 8, f"Project: {p_name} | Engineer: {eng_name} | Date: {date_val}", ln=True)
    
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "2. TEST RESULTS", ln=True, border='B')
    for row in test_data:
        pdf.set_font("Arial", '', 10)
        pdf.cell(0, 8, f"{row[0]}: {row[1]} {row[2]} [{row[3]}]", ln=True, border=1)

    # حفظ الملف في ذاكرة مؤقتة للتحميل
    pdf_output = pdf.output(dest='S')
    st.download_button(label="📥 Download PDF Report", 
                       data=bytes(pdf_output), 
                       file_name=f"Report_{p_name}.pdf", 
                       mime="application/pdf",
                       use_container_width=True)
