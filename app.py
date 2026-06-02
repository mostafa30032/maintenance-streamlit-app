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
            if 'Net Amount' in df.columns or 'Amount' in df.columns:
                amount_col = 'Net Amount' if 'Net Amount' in df.columns else 'Amount'
                total_amount = df[amount_col].sum()
                st.metric("💰 إجمالي المبلغ", f"{total_amount:,.2f}")
        with col4:
            if 'Vehicle Plate Number' in df.columns:
                st.metric("🚗 عدد المركبات", df['Vehicle Plate Number'].nunique())
        
        # التبويبات
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "📈 البيانات الأساسية", 
            "🏆 أكثر 10 معدات", 
            "📍 تحليل المناطق", 
            "🔧 أنواع الصيانات",
            "📊 الرسوم البيانية", 
            "📋 التفاصيل"
        ])
        
        # ============ التبويب الأول - البيانات الأساسية ============
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
        
        # ============ التبويب الثاني - أكثر 10 معدات ============
        with tab2:
            st.subheader("🏆 أكثر 10 معدات قامت بعمليات صيانة")
            
            # حساب أكثر 10 معدات
            if 'Vehicle Plate Number' in df.columns:
                vehicle_maintenance = df['Vehicle Plate Number'].value_counts().head(10)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # جدول
                    st.write("**ترتيب المعدات:**")
                    vehicle_df = pd.DataFrame({
                        'المعدة': vehicle_maintenance.index,
                        'عدد الصيانات': vehicle_maintenance.values
                    }).reset_index(drop=True)
                    vehicle_df.index = vehicle_df.index + 1
                    st.dataframe(vehicle_df, use_container_width=True)
                
                with col2:
                    # رسم بياني
                    fig = px.bar(
                        x=vehicle_maintenance.values,
                        y=vehicle_maintenance.index,
                        orientation='h',
                        title="أكثر 10 معدات قامت بالصيانة",
                        labels={'x': 'عدد الصيانات', 'y': 'المعدة'}
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            # أنواع المعدات
            if 'Vehicle Type' in df.columns:
                st.subheader("📌 تصنيف المعدات حسب النوع")
                
                vehicle_type_count = df['Vehicle Type'].value_counts()
                
                col1, col2 = st.columns(2)
                
                with col1:
                    fig = px.pie(
                        values=vehicle_type_count.values,
                        names=vehicle_type_count.index,
                        title="توزيع أنواع المعدات"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    st.write("**إحصائيات أنواع المعدات:**")
                    type_df = pd.DataFrame({
                        'النوع': vehicle_type_count.index,
                        'العدد': vehicle_type_count.values
                    })
                    st.dataframe(type_df, use_container_width=True)
        
        # ============ التبويب الثالث - تحليل المناطق ============
        with tab3:
            st.subheader("📍 تقسيم المناطق حسب المبلغ الصافي")
            
            if 'Area' in df.columns:
                amount_col = 'Net Amount' if 'Net Amount' in df.columns else 'Amount'
                
                # حساب إجمالي المبلغ حسب المنطقة
                area_amount = df.groupby('Area')[amount_col].agg(['sum', 'count', 'mean']).sort_values('sum', ascending=False)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**جدول المبالغ حسب المنطقة:**")
                    area_df = pd.DataFrame({
                        'المنطقة': area_amount.index,
                        'إجمالي المبلغ': area_amount['sum'].values,
                        'عدد الصيانات': area_amount['count'].values.astype(int),
                        'المتوسط': area_amount['mean'].values
                    })
                    st.dataframe(area_df, use_container_width=True)
                
                with col2:
                    # رسم بياني للمبالغ حسب المنطقة
                    fig = px.bar(
                        x=area_amount.index,
                        y=area_amount['sum'].values,
                        title="إجمالي المبالغ حسب المنطقة",
                        labels={'x': 'المنطقة', 'y': 'المبلغ الصافي'}
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                # خريطة دائرية للمناطق
                st.subheader("📊 توزيع المناطق حسب نسبة المبلغ")
                fig = px.pie(
                    values=area_amount['sum'].values,
                    names=area_amount.index,
                    title="توزيع المبالغ حسب المنطقة (%)"
                )
                st.plotly_chart(fig, use_container_width=True)
        
        # ============ التبويب الرابع - أنواع الصيانات ============
        with tab4:
            st.subheader("🔧 تحليل أنواع الصيانات")
            
            if 'Expense Category' in df.columns:
                amount_col = 'Net Amount' if 'Net Amount' in df.columns else 'Amount'
                
                # تحليل الصيانات
                maintenance_analysis = df.groupby('Expense Category')[amount_col].agg(['sum', 'count', 'mean']).sort_values('sum', ascending=False)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**جدول أنواع الصيانات:**")
                    maint_df = pd.DataFrame({
                        'نوع الصيانة': maintenance_analysis.index,
                        'إجمالي المبلغ': maintenance_analysis['sum'].values,
                        'عدد العمليات': maintenance_analysis['count'].values.astype(int),
                        'المتوسط': maintenance_analysis['mean'].values
                    })
                    st.dataframe(maint_df, use_container_width=True)
                
                with col2:
                    fig = px.bar(
                        x=maintenance_analysis.index,
                        y=maintenance_analysis['sum'].values,
                        title="إجمالي المبالغ حسب نوع الصيانة",
                        labels={'x': 'نوع الصيانة', 'y': 'المبلغ'}
                    )
                    fig.update_xaxes(tickangle=-45)
                    st.plotly_chart(fig, use_container_width=True)
                
                # رسم بياني دائري
                st.subheader("📌 توزيع أنواع الصيانات")
                fig = px.pie(
                    values=maintenance_analysis['sum'].values,
                    names=maintenance_analysis.index,
                    title="توزيع المبالغ حسب نوع الصيانة (%)"
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # تحليل مستوى الصيانة الثاني
            if 'Maintenance Sub Category C2' in df.columns:
                st.subheader("🔍 تحليل تفصيلي للصيانات (مستوى 2)")
                amount_col = 'Net Amount' if 'Net Amount' in df.columns else 'Amount'
                
                sub_maintenance = df.groupby('Maintenance Sub Category C2')[amount_col].agg(['sum', 'count']).sort_values('sum', ascending=False).head(15)
                
                fig = px.barh(
                    x=sub_maintenance['sum'].values,
                    y=sub_maintenance.index,
                    title="أكثر 15 نوع صيانة فرعي من حيث المبلغ",
                    labels={'x': 'المبلغ', 'y': 'نوع الصيانة'}
                )
                st.plotly_chart(fig, use_container_width=True)
        
        # ============ التبويب الخامس - الرسوم البيانية ============
        with tab5:
            st.subheader("📉 الرسوم البيانية المتقدمة")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if 'Service Provider' in df.columns and 'Amount' in df.columns:
                    amount_col = 'Net Amount' if 'Net Amount' in df.columns else 'Amount'
                    top_providers = df.groupby('Service Provider')[amount_col].sum().sort_values(ascending=False).head(10)
                    fig = px.barh(
                        x=top_providers.values,
                        y=top_providers.index,
                        title="أكثر 10 مقدمي خدمات من حيث المصروفات",
                        labels={'x': 'المبلغ', 'y': 'مقدم الخدمة'}
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                if 'Month' in df.columns and 'Amount' in df.columns:
                    amount_col = 'Net Amount' if 'Net Amount' in df.columns else 'Amount'
                    monthly_expenses = df.groupby('Month')[amount_col].sum()
                    fig = px.line(
                        x=monthly_expenses.index,
                        y=monthly_expenses.values,
                        title="المصروفات الشهرية",
                        markers=True,
                        labels={'x': 'الشهر', 'y': 'المبلغ'}
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            col3, col4 = st.columns(2)
            
            with col3:
                if 'Expense Category' in df.columns and 'Area' in df.columns:
                    amount_col = 'Net Amount' if 'Net Amount' in df.columns else 'Amount'
                    category_area = df.groupby(['Area', 'Expense Category'])[amount_col].sum().reset_index()
                    fig = px.bar(
                        category_area,
                        x='Area',
                        y=amount_col,
                        color='Expense Category',
                        title="المصروفات حسب المنطقة ونوع الصيانة",
                        labels={amount_col: 'المبلغ'}
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            with col4:
                if 'Vehicle Type' in df.columns and 'Amount' in df.columns:
                    amount_col = 'Net Amount' if 'Net Amount' in df.columns else 'Amount'
                    vehicle_expenses = df.groupby('Vehicle Type')[amount_col].sum().sort_values(ascending=False)
                    fig = px.pie(
                        values=vehicle_expenses.values,
                        names=vehicle_expenses.index,
                        title="توزيع المصروفات حسب نوع المركبة"
                    )
                    st.plotly_chart(fig, use_container_width=True)
        
        # ============ التبويب السادس - التفاصيل ============
        with tab6:
            st.subheader("📋 معلومات تفصيلية")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**المركبات الموجودة:**")
                if 'Vehicle Plate Number' in df.columns:
                    vehicles = sorted(df['Vehicle Plate Number'].unique())
                    selected_vehicle = st.selectbox("اختر مركبة:", vehicles)
                    vehicle_data = df[df['Vehicle Plate Number'] == selected_vehicle]
                    
                    amount_col = 'Net Amount' if 'Net Amount' in df.columns else 'Amount'
                    st.write(f"**إجمالي صيانات المركبة: {len(vehicle_data)}**")
                    st.write(f"**إجمالي المصروفات: {vehicle_data[amount_col].sum():,.2f}**")
                    st.dataframe(vehicle_data, use_container_width=True)
            
            with col2:
                st.write("**مقدمو الخدمات:**")
                if 'Service Provider' in df.columns:
                    providers = sorted(df['Service Provider'].unique())
                    selected_provider = st.selectbox("اختر مقدم خدمة:", providers)
                    provider_data = df[df['Service Provider'] == selected_provider]
                    
                    amount_col = 'Net Amount' if 'Net Amount' in df.columns else 'Amount'
                    st.write(f"**عدد الخدمات المقدمة: {len(provider_data)}**")
                    st.write(f"**إجمالي المبلغ: {provider_data[amount_col].sum():,.2f}**")
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
