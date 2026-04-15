import streamlit as st
from fpdf import FPDF
from datetime import datetime
import io
from PIL import Image

# 1. إعداد الصفحة
st.set_page_config(page_title="Schneider & Partner", layout="centered")

# 2. كلاس الـ PDF المحسن (تجنب أخطاء الصور والخطوط)
class EngineeringPDF(FPDF):
    def __init__(self, logo_b=None, logo_a=None):
        super().__init__()
        self.logo_b = logo_b # صورة قبل
        self.logo_a = logo_a # صورة بعد

    def header(self):
        self.set_font("Arial", 'B', 15)
        self.cell(0, 10, "TECHNICAL MAINTENANCE & TEST REPORT", ln=True, align='C')
        self.set_font("Arial", 'I', 8)
        self.cell(0, 5, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True, align='C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

# --- واجهة المستخدم ---
st.title("⚡ Maintenance System v510.3")

# I. البيانات الإدارية
with st.form("main_form"):
    st.header("I. Project Administration")
    col1, col2 = st.columns(2)
    p_name = col1.text_input("Project Name", "New Project")
    eng_name = col2.text_input("Engineer Name")
    location = col1.text_input("Location")
    date_val = col2.date_input("Date")

    st.divider()

    # II. توصيف المعدات
    st.header("II. Equipment Details")
    cat = st.selectbox("Category", ["TR", "LV", "MV", "Substation"])
    maint_type = st.radio("Maint. Type", ["Routine", "Emergency", "Corrective"], horizontal=True)

    st.divider()

    # III. تفاصيل العمل (Text Areas)
    st.header("III. Work Details")
    prob = st.text_area("Problem Description")
    act = st.text_area("Action Taken")

    st.divider()

    # IV. الصور (اختياري)
    st.header("IV. Photos")
    up_before = st.file_uploader("Photo: BEFORE", type=['jpg', 'png'])
    up_after = st.file_uploader("Photo: AFTER", type=['jpg', 'png'])

    # زر الإرسال داخل الفورم
    submit = st.form_submit_button("Generate Report PDF", use_container_width=True)

# --- منطق توليد الـ PDF عند الضغط على الزر ---
if submit:
    try:
        pdf = EngineeringPDF()
        pdf.add_page()
        
        # القسم 1
        pdf.set_font("Arial", 'B', 12)
        pdf.set_fill_color(230, 230, 230)
        pdf.cell(0, 10, "1. ADMINISTRATION", ln=True, fill=True)
        pdf.set_font("Arial", '', 10)
        pdf.cell(0, 8, f"Project: {p_name}", ln=True)
        pdf.cell(0, 8, f"Engineer: {eng_name}", ln=True)
        pdf.cell(0, 8, f"Location: {location} | Date: {date_val}", ln=True)

        # القسم 2
        pdf.ln(5)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "2. WORK DETAILS", ln=True, fill=True)
        pdf.set_font("Arial", '', 10)
        pdf.multi_cell(0, 7, f"Problem: {prob}\nAction: {act}", border=1)

        # إضافة الصور إذا وجدت (بشكل آمن)
        if up_before or up_after:
            pdf.add_page()
            pdf.set_font("Arial", 'B', 14)
            pdf.cell(0, 10, "VISUAL EVIDENCE", ln=True, align='C')
            
            if up_before:
                # تحويل الصورة لتنسيق متوافق
                img_b = Image.open(up_before).convert('RGB')
                img_b.save("temp_before.jpg")
                pdf.image("temp_before.jpg", x=10, y=30, w=90)
                pdf.text(10, 28, "BEFORE")

            if up_after:
                img_a = Image.open(up_after).convert('RGB')
                img_a.save("temp_after.jpg")
                pdf.image("temp_after.jpg", x=110, y=30, w=90)
                pdf.text(110, 28, "AFTER")

        # إخراج الملف
        pdf_bytes = pdf.output(dest='S')
        st.success("✅ Report Ready!")
        st.download_button("📥 Download Report", data=bytes(pdf_bytes), file_name=f"{p_name}.pdf", mime="application/pdf")

    except Exception as e:
        st.error(f"Error occurred: {str(e)}")
