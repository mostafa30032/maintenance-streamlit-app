import streamlit as st
import pandas as pd

st.set_page_config(page_title="تطبيق صيانة المعدات", layout="wide")

st.title("🔧 تطبيق صيانة المعدات")
st.write("نظام إدارة صيانة وأسطول المركبات")

# رفع ملف Excel
uploaded_file = st.file_uploader("اختر ملف Excel الخاص بالصيانات", type=['xlsx', 'xls'])

if uploaded_file is not None:
    try:
        # قراءة الملف
        df = pd.read_excel(uploaded_file)
        
        st.success("✅ تم تحميل الملف بنجاح!")
        
        # عرض عدد الصفوف والأعمدة
        st.write(f"**عدد الصيانات:** {len(df)}")
        st.write(f"**الأعمدة:** {', '.join(df.columns)}")
        
        # عرض البيانات في جدول
        st.subheader("📊 بيانات الصيانات")
        st.dataframe(df, use_container_width=True)
        
        # إحصائيات بسيطة
        st.subheader("📈 إحصائيات")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("عدد الصيانات", len(df))
        
    except Exception as e:
        st.error(f"❌ حدث خطأ: {e}")
else:
    st.info("👆 يرجى رفع ملف Excel لعرض بيانات الصيانات")
