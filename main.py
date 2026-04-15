import streamlit as st
from fpdf import FPDF
from datetime import datetime
import io
from PIL import Image

# 1. إعدادات الصفحة
st.set_page_config(page_title="Schneider & Partner System", layout="wide")

# 2. كلاس توليد الـ PDF المهني
class EngineeringPDF(FPDF):
    def header(self):
        # العنوان الرئيسي
        self.set_font("Arial", 'B', 15)
        self.cell(0, 10, "TECHNICAL MAINTENANCE & TEST REPORT", ln=True, align='C')
        self.set_font("Arial", 'I', 9)
        self.cell(0, 5, "System Version: 510.2 (Mobile Edition)", ln=True, align='C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

# --- واجهة المستخدم ---
st.title("⚡ Schneider & Partner Engineering")

# I. PROJECT ADMINISTRATION
with st.expander("I. PROJECT ADMINISTRATION", expanded=True):
    col1, col2 = st.columns(2)
    p_name = col1.text_input("Project Name:")
    rfq = col2.text_input("RFQ / Ref:")
    loc = col1.text_input("Location:")
    eng = col2.text_input("Engineer Name:")
    report_date = st.date_input("Date:", datetime.now())

# II. EQUIPMENT CONFIGURATION (المنطق المتسلسل)
with st.expander("II. EQUIPMENT CONFIGURATION"):
    maint_type = st.selectbox("Maintenance Type:", ["Routine Maintenance", "Emergency Call", "Corrective Action"])
    cat = st.selectbox("Category:", ["Substation", "TR", "MV", "LV"])
    
    dynamic_fields = {}
    col_dyn1, col_dyn2 = st.columns(2)
    
    if cat == "TR":
        dynamic_fields["TR Type"] = col_dyn1.selectbox("TR Type:", ["Distribution", "Power", "Dry"])
        dynamic_fields["S/N"] = col_dyn2.text_input("Serial Number:")
        dynamic_fields["Capacity"] = col_dyn1.text_input("Capacity:")
    elif cat == "MV":
        model = col_dyn1.selectbox("Model:", ["SM6 36KV", "SM6 24KV", "RM6"])
        dynamic_fields["Model"] = model
        dynamic_fields["Cubicle"] = col_dyn2.selectbox("Cubicle:", ["IM", "QM", "DM1-A"])
    elif cat == "LV":
        dynamic_fields["Product"] = col_dyn1.selectbox("Product:", ["Blokset", "Prisma", "ATS"])
    elif cat == "Substation":
        sub_type = col_dyn1.selectbox("Sub. Type:", ["Mobile", "Fixed", "E-house"])
        dynamic_fields["Sub. Type"] = sub_type
        dynamic_fields["Main Comp"] = col_dyn2.selectbox("Main Comp:", ["Incomer", "RTU", "Charger"])

# III. TECHNICAL TEST RECORDS (جدول الفحوصات)
with st.expander("III. TECHNICAL TEST RECORDS"):
    if 'rows' not in st.session_state:
        st.session_state.rows = 1
    
    test_rows_data = []
    for i in range(st.session_state.rows):
        c1, c2, c3, c4 = st.columns([3, 2, 1, 2])
        t_desc = c1.selectbox(f"Test {i+1}", ["Megger", "Ratio", "Hi-Pot", "Secondary Injection", "CPC100"], key=f"desc_{i}")
        t_val = c2.text_input("Value", key=f"val_{i}")
        t_unit = c3.text_input("Unit", key=f"unit_{i}")
        t_stat = c4.selectbox("Status", ["PASSED", "FAILED"], key=f"stat_{i}")
        test_rows_data.append({"desc": t_desc, "val": t_val, "unit": t_unit, "stat": t_stat})
    
    if st.button("+ Add Row"):
        st.session_state.rows += 1
        st.rerun()

# IV. WORK DETAILS
with st.expander("IV. WORK DETAILS"):
    prob = st.text_area("Problem Description:")
    act = st.text_area("Action / Treatment Taken:")
    mat = st.text_area("Materials / Parts Used:")

# V. VALIDATION & PHOTOS
with st.expander("V. VALIDATION & PHOTOS"):
    col_img1, col_img2 = st.columns(2)
    img_b = col_img1.file_uploader("Upload (BEFORE)", type=['jpg', 'jpeg', 'png'])
    img_a = col_img2.file_uploader("Upload (AFTER)", type=['jpg', 'jpeg', 'png'])
    sig = st.text_input("Engineer Signature (Type Name):")

# --- زر توليد التقرير ---
if st.button("SAVE & GENERATE PDF REPORT", type="primary", use_container_width=True):
    try:
        pdf = EngineeringPDF()
        pdf.add_page()
        
        # 1. Admin Info
        pdf.set_font("Arial", 'B', 12); pdf.cell(0, 10, "1. PROJECT ADMINISTRATION", ln=True, border='B')
        pdf.set_font("Arial", '', 10)
        admin_info = [("Project Name", p_name), ("RFQ / Ref", rfq), ("Location", loc), ("Engineer", eng), ("Date", str(report_date))]
        for l, v in admin_info:
            pdf.cell(50, 8, l, 1); pdf.cell(140, 8, v, 1, 1)

        # 2. Equipment
        pdf.ln(5); pdf.set_font("Arial", 'B', 12); pdf.cell(0, 10, "2. EQUIPMENT CONFIGURATION", ln=True, border='B')
        pdf.set_font("Arial", '', 10)
        pdf.cell(50, 8, "Maint. Type", 1); pdf.cell(140, 8, maint_type, 1, 1)
        pdf.cell(50, 8, "Category", 1); pdf.cell(140, 8, cat, 1, 1)
        for l, v in dynamic_fields.items():
            pdf.cell(50, 8, l, 1); pdf.cell(140, 8, v, 1, 1)

        # 3. Test Results
        pdf.ln(5); pdf.set_font("Arial", 'B', 12); pdf.cell(0, 10, "3. TECHNICAL TEST RESULTS", ln=True, border='B')
        pdf.set_font("Arial", 'B', 9); pdf.set_fill_color(240, 240, 240)
        h = ["Test Description", "Result", "Unit", "Status"]
        w = [75, 40, 35, 40]
        for i, title in enumerate(h): pdf.cell(w[i], 8, title, 1, 0, 'C', True)
        pdf.ln(); pdf.set_font("Arial", '', 9)
        for row in test_rows_data:
            pdf.cell(w[0], 8, row['desc'], 1)
            pdf.cell(w[1], 8, row['val'], 1, 0, 'C')
            pdf.cell(w[2], 8, row['unit'], 1, 0, 'C')
            pdf.cell(w[3], 8, row['stat'], 1, 1, 'C')

        # 4. Work Details
        pdf.ln(5); pdf.set_font("Arial", 'B', 12); pdf.cell(0, 10, "4. WORK DETAILS & REMARKS", ln=True, border='B')
        for label, val in [("Problem", prob), ("Action", act), ("Materials", mat)]:
            pdf.set_font("Arial", 'B', 10); pdf.cell(0, 8, label + ":", ln=True)
            pdf.set_font("Arial", '', 10); pdf.multi_cell(0, 7, val, 1); pdf.ln(2)

        # 5. Photos
        if img_b or img_a:
            pdf.add_page()
            pdf.set_font("Arial", 'B', 14); pdf.cell(0, 10, "VISUAL EVIDENCE", ln=True, align='C')
            if img_b:
                img = Image.open(img_b).convert("RGB")
                img.save("temp_b.jpg")
                pdf.image("temp_b.jpg", x=10, y=35, w=85); pdf.text(10, 32, "BEFORE")
            if img_a:
                img = Image.open(img_a).convert("RGB")
                img.save("temp_a.jpg")
                pdf.image("temp_a.jpg", x=110, y=35, w=85); pdf.text(110, 32, "AFTER")

        pdf.set_y(-30); pdf.set_font("Arial", 'B', 11)
        pdf.cell(0, 10, f"Authorized Engineer Signature: {sig}", ln=True)

        # تحويل الـ PDF لتحميله
        pdf_out = pdf.output(dest='S')
        st.download_button("📥 Download PDF Report", data=bytes(pdf_out), file_name=f"Report_{p_name}.pdf", mime="application/pdf", use_container_width=True)
        st.success("Report generated successfully!")

    except Exception as e:
        st.error(f"Error: {str(e)}")
