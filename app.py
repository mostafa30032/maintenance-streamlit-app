import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(page_title="نظام إدارة الصيانة", layout="wide", initial_sidebar_state="expanded")

# إضافة CSS مخصص
st.markdown("""
    <style>
        .header-title {
            text-align: center;
            color: #1f77b4;
            font-size: 2.5em;
            font-weight: bold;
        }
        .metric-card {
            padding: 20px;
            border-radius: 10px;
            background-color: #f0f2f6;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='header-title'>🔧 نظام إدارة الصيانة والمركبات</h1>", unsafe_allow_html=True)
st.markdown("---")

# الشريط الجانبي
with st.sidebar:
    st.header("⚙️ الإعدادات")
    st.write("استخدم هذا القسم لتحميل وتحليل بيانات الصيانة")

# رفع ملف Excel
uploaded_file = st.file_uploader("📤 اختر ملف Excel الخاص بالصيانات", type=['xlsx', 'xls'])

if uploaded_file is not None:
    try:
        # قراءة الملف
        df = pd.read_excel(uploaded_file)
        
        st.success("✅ تم تحميل الملف بنجاح!")
        
        # معالجة الأعمدة
        st.subheader("📊 معلومات البيانات")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📋 عدد الصيانات", len(df))
        with col2:
            st.metric("🔢 عدد الأعمدة", len(df.columns))
        with col3:
            if 'Amount' in df.columns:
                total_amount = df['Amount'].sum()
                st.metric("💰 إجمالي المبلغ", f"{total_amount:,.2f}")
        with col4:
            if 'Vehicle Plate Number' in df.columns:
                st.metric("🚗 عدد المركبات", df['Vehicle Plate Number'].nunique())
        
        # التبويبات
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["📈 البيانات الأساسية", "📊 التحليلات", "🔍 التصفية", "📉 الرسوم البيانية", "📋 التفاصيل"])
        
        # التبويب الأول - البيانات الأساسية
        with tab1:
            st.subheader("جدول البيانات الكاملة")
            st.dataframe(df, use_container_width=True, height=400)
            
            # تحميل البيانات كـ CSV
            csv = df.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="📥 تحميل البيانات كـ CSV",
                data=csv,
                file_name=f"maintenance_data_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        
        # التبويب الثاني - التحليلات
        with tab2:
            st.subheader("📊 الإحصائيات والتحليلات")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**إجمالي المبالغ:**")
                if 'Amount' in df.columns:
                    amount_stats = df['Amount'].describe()
                    st.metric("المتوسط", f"{amount_stats['mean']:,.2f}")
                    st.metric("الحد الأقصى", f"{amount_stats['max']:,.2f}")
                    st.metric("الحد الأدنى", f"{amount_stats['min']:,.2f}")
            
            with col2:
                st.write("**المركبات:**")
                if 'Vehicle Type' in df.columns:
                    vehicle_count = df['Vehicle Type'].value_counts()
                    st.write(vehicle_count)
            
            st.write("**فئات الصيانة:**")
            if 'Expense Category' in df.columns:
                category_count = df['Expense Category'].value_counts()
                st.bar_chart(category_count)
        
        # التبويب الثالث - التصفية
        with tab3:
            st.subheader("🔍 تصفية البيانات")
            
            filtered_df = df.copy()
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if 'Vehicle Type' in df.columns:
                    vehicle_types = st.multiselect(
                        "نوع المركبة",
                        options=df['Vehicle Type'].unique(),
                        default=df['Vehicle Type'].unique()
                    )
                    filtered_df = filtered_df[filtered_df['Vehicle Type'].isin(vehicle_types)]
            
            with col2:
                if 'Expense Category' in df.columns:
                    expense_cat = st.multiselect(
                        "فئة المصروف",
                        options=df['Expense Category'].unique(),
                        default=df['Expense Category'].unique()
                    )
                    filtered_df = filtered_df[filtered_df['Expense Category'].isin(expense_cat)]
            
            with col3:
                if 'Area' in df.columns:
                    areas = st.multiselect(
                        "المنطقة",
                        options=df['Area'].unique(),
                        default=df['Area'].unique()
                    )
                    filtered_df = filtered_df[filtered_df['Area'].isin(areas)]
            
            st.write(f"**عدد السجلات بعد التصفية: {len(filtered_df)}**")
            st.dataframe(filtered_df, use_container_width=True)
        
        # التبويب الرابع - الرسوم البيانية
        with tab4:
            st.subheader("📉 الرسوم البيانية")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if 'Expense Category' in df.columns and 'Amount' in df.columns:
                    category_expenses = df.groupby('Expense Category')['Amount'].sum().sort_values(ascending=False)
                    fig = px.bar(
                        x=category_expenses.index,
                        y=category_expenses.values,
                        title="المصروفات حسب الفئة",
                        labels={'x': 'فئة المصروف', 'y': 'المبلغ'}
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                if 'Vehicle Type' in df.columns and 'Amount' in df.columns:
                    vehicle_expenses = df.groupby('Vehicle Type')['Amount'].sum().sort_values(ascending=False)
                    fig = px.pie(
                        values=vehicle_expenses.values,
                        names=vehicle_expenses.index,
                        title="توزيع المصروفات حسب نوع المركبة"
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            col3, col4 = st.columns(2)
            
            with col3:
                if 'Month' in df.columns and 'Amount' in df.columns:
                    monthly_expenses = df.groupby('Month')['Amount'].sum()
                    fig = px.line(
                        x=monthly_expenses.index,
                        y=monthly_expenses.values,
                        title="المصروفات الشهرية",
                        markers=True
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            with col4:
                if 'Service Provider' in df.columns and 'Amount' in df.columns:
                    top_providers = df.groupby('Service Provider')['Amount'].sum().sort_values(ascending=False).head(10)
                    fig = px.barh(
                        x=top_providers.values,
                        y=top_providers.index,
                        title="أكثر 10 مقدمي خدمات من حيث المصروفات",
                        labels={'x': 'المبلغ', 'y': 'مقدم الخدمة'}
                    )
                    st.plotly_chart(fig, use_container_width=True)
        
        # التبويب الخامس - التفاصيل
        with tab5:
            st.subheader("📋 معلومات تفصيلية")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**المركبات الموجودة:**")
                if 'Vehicle Plate Number' in df.columns:
                    vehicles = df['Vehicle Plate Number'].unique()
                    st.write(f"عدد المركبات: {len(vehicles)}")
                    selected_vehicle = st.selectbox("اختر مركبة:", vehicles)
                    vehicle_data = df[df['Vehicle Plate Number'] == selected_vehicle]
                    st.write(f"**إجمالي صيانات المركبة: {len(vehicle_data)}**")
                    st.write(f"**إجمالي المصروفات: {vehicle_data['Amount'].sum():,.2f}**")
                    st.dataframe(vehicle_data, use_container_width=True)
            
            with col2:
                st.write("**مقدمو الخدمات:**")
                if 'Service Provider' in df.columns:
                    providers = df['Service Provider'].unique()
                    st.write(f"عدد مقدمي الخدمات: {len(providers)}")
                    selected_provider = st.selectbox("اختر مقدم خدمة:", providers)
                    provider_data = df[df['Service Provider'] == selected_provider]
                    st.write(f"**عدد الخدمات المقدمة: {len(provider_data)}**")
                    st.write(f"**إجمالي المبلغ: {provider_data['Amount'].sum():,.2f}**")
                    st.dataframe(provider_data, use_container_width=True)
        
        st.markdown("---")
        st.info("💡 يمكنك استخدام التبويبات المختلفة لتحليل البيانات بشكل شامل")
        
    except Exception as e:
        st.error(f"❌ حدث خطأ عند معالجة الملف: {e}")
        st.write("تأكد من أن الملف يحتوي على الأعمدة المطلوبة")
else:
    st.info("👆 يرجى رفع ملف Excel لعرض بيانات الصيانة والمركبات")
    st.write("**الأعمدة المتوقعة:**")
    columns_list = [
        "Year", "Month", "Day", "Area", "Expense-Bearing Branch",
        "Vehicle Plate Number", "Vehicle Type", "Expense Category",
        "c1一级", "c2二级", "ماتريل ولا مصنعية", "Maintenance Sub Category C2",
        "Notes", "Maintenance KM", "Service Provider", "Amount",
        "VAT 14%", "WHT 1% & 3%", "Net Amount", "OA request number", "path", "Cashier date"
    ]
    for i, col in enumerate(columns_list, 1):
        st.write(f"{i}. {col}")
