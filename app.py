import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(page_title="نظام إدارة الصيانة والمركبات", layout="wide", initial_sidebar_state="expanded")

# إضافة CSS مخصص
st.markdown("""
    <style>
        .header-title {
            text-align: center;
            color: #1f77b4;
            font-size: 2.5em;
            font-weight: bold;
            margin-bottom: 20px;
        }
        .metric-card {
            padding: 20px;
            border-radius: 10px;
            background-color: #f0f2f6;
        }
        .stat-box {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            border-radius: 10px;
            color: white;
            text-align: center;
            margin: 10px 0;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='header-title'>🚗 لوحة تحكم إدارة الصيانة والمركبات</h1>", unsafe_allow_html=True)
st.markdown("---")

# الشريط الجانبي
with st.sidebar:
    st.header("⚙️ إعدادات النظام")
    st.write("قم برفع ملف بيانات الصيانة")

# رفع ملف Excel
uploaded_file = st.file_uploader("📤 رفع ملف البيانات (Excel)", type=['xlsx', 'xls'])

if uploaded_file is not None:
    try:
        # قراءة الملف
        df = pd.read_excel(uploaded_file)
        
        # تنظيف أسماء الأعمدة
        df.columns = df.columns.str.strip()
        
        st.success("✅ تم تحميل البيانات بنجاح!")
        
        # ============ KPI الرئيسية ============
        st.subheader("📊 المؤشرات الرئيسية")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        # تحديد عمود المبلغ الصافي
        amount_col = 'Net Amount' if 'Net Amount' in df.columns else 'Amount'
        
        with col1:
            st.metric("📋 إجمالي الصيانات", len(df))
        with col2:
            st.metric("💰 إجمالي المبلغ الصافي", f"{df[amount_col].sum():,.2f}")
        with col3:
            st.metric("🚗 عدد المعدات", df['Vehicle Plate Number'].nunique() if 'Vehicle Plate Number' in df.columns else 0)
        with col4:
            st.metric("📍 المناطق", df['Area'].nunique() if 'Area' in df.columns else 0)
        with col5:
            st.metric("🔧 أنواع الصيانات", df['Notes ar'].nunique() if 'Notes ar' in df.columns else 0)
        
        st.markdown("---")
        
        # ============ التبويبات الرئيسية ============
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "📈 نظرة عامة", 
            "🏆 أفضل المعدات", 
            "📍 تحليل المناطق", 
            "🔧 أنواع الصيانات",
            "📊 الرسوم البيانية", 
            "📋 البيانات التفصيلية"
        ])
        
        # ============ التبويب الأول - نظرة عامة ============
        with tab1:
            st.subheader("📈 نظرة عامة على البيانات")
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.write("**جدول البيانات الكاملة:**")
                st.dataframe(df, use_container_width=True, height=400)
            
            with col2:
                st.write("**إحصائيات المبالغ:**")
                stats = df[amount_col].describe()
                st.metric("المتوسط", f"{stats['mean']:,.2f}")
                st.metric("الحد الأقصى", f"{stats['max']:,.2f}")
                st.metric("الحد الأدنى", f"{stats['min']:,.2f}")
                st.metric("الانحراف المعياري", f"{stats['std']:,.2f}")
            
            # تحميل كـ CSV
            csv = df.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="📥 تحميل البيانات (CSV)",
                data=csv,
                file_name=f"maintenance_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        
        # ============ التبويب الثاني - أفضل المعدات ============
        with tab2:
            st.subheader("🏆 أفضل 10 معدات (حسب صافي المبلغ)")
            
            # ترتيب المعدات حسب صافي المبلغ وليس العدد
            vehicle_spending = df.groupby('Vehicle Plate Number')[amount_col].agg(['sum', 'count', 'mean']).sort_values('sum', ascending=False).head(10)
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.write("**ترتيب المعدات حسب الإنفاق:**")
                vehicle_df = pd.DataFrame({
                    'رقم المعدة': vehicle_spending.index,
                    'إجمالي الصافي': vehicle_spending['sum'].values,
                    'عدد الصيانات': vehicle_spending['count'].values.astype(int),
                    'المتوسط': vehicle_spending['mean'].values
                }).reset_index(drop=True)
                vehicle_df.index = vehicle_df.index + 1
                st.dataframe(vehicle_df, use_container_width=True)
            
            with col2:
                # رسم بياني
                fig = px.bar(
                    x=vehicle_spending['sum'].values,
                    y=vehicle_spending.index,
                    orientation='h',
                    title="أفضل 10 معدات (صافي المبلغ)",
                    labels={'x': 'صافي المبلغ', 'y': 'رقم المعدة'},
                    color=vehicle_spending['sum'].values,
                    color_continuous_scale='Blues'
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # أنواع المعدات
            if 'Vehicle Type' in df.columns:
                st.subheader("🚗 توزيع أنواع المعدات")
                
                vehicle_type_spending = df.groupby('Vehicle Type')[amount_col].agg(['sum', 'count']).sort_values('sum', ascending=False)
                
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    fig = px.pie(
                        values=vehicle_type_spending['sum'].values,
                        names=vehicle_type_spending.index,
                        title="توزيع الإنفاق حسب نوع المعدة"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    st.write("**إحصائيات أنواع المعدات:**")
                    type_df = pd.DataFrame({
                        'النوع': vehicle_type_spending.index,
                        'الإنفاق الإجمالي': vehicle_type_spending['sum'].values,
                        'عدد الصيانات': vehicle_type_spending['count'].values.astype(int)
                    })
                    st.dataframe(type_df, use_container_width=True)
        
        # ============ التبويب الثالث - تحليل المناطق ============
        with tab3:
            st.subheader("📍 تحليل المناطق (حسب صافي المبلغ)")
            
            # تحليل المناطق
            area_analysis = df.groupby('Area')[amount_col].agg(['sum', 'count', 'mean']).sort_values('sum', ascending=False)
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.write("**جدول المناطق:**")
                area_df = pd.DataFrame({
                    'المنطقة': area_analysis.index,
                    'إجمالي الصافي': area_analysis['sum'].values,
                    'عدد الصيانات': area_analysis['count'].values.astype(int),
                    'المتوسط': area_analysis['mean'].values
                }).reset_index(drop=True)
                area_df.index = area_df.index + 1
                st.dataframe(area_df, use_container_width=True)
            
            with col2:
                fig = px.bar(
                    x=area_analysis.index,
                    y=area_analysis['sum'].values,
                    title="إجمالي الصافي حسب المنطقة",
                    labels={'x': 'المنطقة', 'y': 'الصافي'},
                    color=area_analysis['sum'].values,
                    color_continuous_scale='Viridis'
                )
                fig.update_xaxes(tickangle=-45)
                st.plotly_chart(fig, use_container_width=True)
            
            # خريطة دائرية للمناطق
            st.subheader("📊 نسبة الإنفاق حسب المنطقة")
            fig = px.pie(
                values=area_analysis['sum'].values,
                names=area_analysis.index,
                title="توزيع الإنفاق حسب المنطقة (%)"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # ============ التبويب الرابع - أنواع الصيانات ============
        with tab4:
            st.subheader("🔧 تحليل أنواع الصيانات (Notes ar)")
            
            # تحليل الصيانات حسب Notes ar
            maintenance_analysis = df.groupby('Notes ar')[amount_col].agg(['sum', 'count', 'mean']).sort_values('sum', ascending=False)
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.write("**جدول أنواع الصيانات:**")
                maint_df = pd.DataFrame({
                    'نوع الصيانة': maintenance_analysis.index,
                    'إجمالي الصافي': maintenance_analysis['sum'].values,
                    'عدد العمليات': maintenance_analysis['count'].values.astype(int),
                    'المتوسط': maintenance_analysis['mean'].values
                }).reset_index(drop=True)
                maint_df.index = maint_df.index + 1
                st.dataframe(maint_df, use_container_width=True)
            
            with col2:
                fig = px.bar(
                    x=maintenance_analysis['sum'].values,
                    y=maintenance_analysis.index,
                    orientation='h',
                    title="إجمالي الصافي حسب نوع الصيانة",
                    labels={'x': 'الصافي', 'y': 'نوع الصيانة'},
                    color=maintenance_analysis['sum'].values,
                    color_continuous_scale='Reds'
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # رسم بياني دائري
            st.subheader("📌 نسبة الصيانات")
            fig = px.pie(
                values=maintenance_analysis['sum'].values,
                names=maintenance_analysis.index,
                title="توزيع الإنفاق حسب نوع الصيانة (%)"
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # تحليل متقدم: المنطقة + نوع الصيانة
            st.subheader("🔍 تحليل متقدم: المنطقة × نوع الصيانة")
            
            area_maintenance = df.groupby(['Area', 'Notes ar'])[amount_col].sum().reset_index()
            
            fig = px.bar(
                area_maintenance,
                x='Area',
                y=amount_col,
                color='Notes ar',
                title="الإنفاق حسب المنطقة ونوع الصيانة",
                labels={amount_col: 'الصافي'},
                barmode='group'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # ============ التبويب الخامس - الرسوم البيانية ============
        with tab5:
            st.subheader("📊 لوحة الرسوم البيانية المتقدمة")
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                # مقدمو الخدمات
                if 'Service Provider' in df.columns:
                    top_providers = df.groupby('Service Provider')[amount_col].sum().sort_values(ascending=False).head(10)
                    fig = px.barh(
                        x=top_providers.values,
                        y=top_providers.index,
                        title="أفضل 10 مقدمي خدمات",
                        labels={'x': 'الصافي', 'y': 'مقدم الخدمة'},
                        color=top_providers.values,
                        color_continuous_scale='Greens'
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # المصروفات الشهرية
                if 'Month' in df.columns:
                    monthly_expenses = df.groupby('Month')[amount_col].sum()
                    fig = px.line(
                        x=monthly_expenses.index,
                        y=monthly_expenses.values,
                        title="المصروفات الشهرية",
                        markers=True,
                        labels={'x': 'الشهر', 'y': 'الصافي'}
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            col3, col4 = st.columns([1, 1])
            
            with col3:
                # المناطق × نوع المعدة
                if 'Vehicle Type' in df.columns:
                    vehicle_area = df.groupby(['Area', 'Vehicle Type'])[amount_col].sum().reset_index()
                    fig = px.bar(
                        vehicle_area,
                        x='Area',
                        y=amount_col,
                        color='Vehicle Type',
                        title="الإنفاق: المنطقة × نوع المعدة",
                        labels={amount_col: 'الصافي'}
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            with col4:
                # فئة المصروفات
                if 'Expense Category' in df.columns:
                    category_expenses = df.groupby('Expense Category')[amount_col].sum().sort_values(ascending=False)
                    fig = px.pie(
                        values=category_expenses.values,
                        names=category_expenses.index,
                        title="توزيع فئات المصروفات"
                    )
                    st.plotly_chart(fig, use_container_width=True)
        
        # ============ التبويب السادس - البيانات التفصيلية ============
        with tab6:
            st.subheader("📋 البيانات والتفاصيل")
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.write("**تفاصيل المعدة:**")
                vehicles = sorted(df['Vehicle Plate Number'].unique())
                selected_vehicle = st.selectbox("اختر مركبة/معدة:", vehicles)
                
                vehicle_data = df[df['Vehicle Plate Number'] == selected_vehicle]
                
                col_a, col_b = st.columns(2)
                with col_a:
                    st.metric("عدد الصيانات", len(vehicle_data))
                with col_b:
                    st.metric("إجمالي الصافي", f"{vehicle_data[amount_col].sum():,.2f}")
                
                st.dataframe(vehicle_data, use_container_width=True)
            
            with col2:
                st.write("**تفاصيل المنطقة:**")
                areas = sorted(df['Area'].unique())
                selected_area = st.selectbox("اختر منطقة:", areas)
                
                area_data = df[df['Area'] == selected_area]
                
                col_a, col_b = st.columns(2)
                with col_a:
                    st.metric("عدد الصيانات", len(area_data))
                with col_b:
                    st.metric("إجمالي الصافي", f"{area_data[amount_col].sum():,.2f}")
                
                st.dataframe(area_data, use_container_width=True)
            
            # تفاصيل نوع الصيانة
            st.write("**تفاصيل نوع الصيانة:**")
            maintenance_types = sorted(df['Notes ar'].unique())
            selected_maintenance = st.selectbox("اختر نوع صيانة:", maintenance_types)
            
            maintenance_data = df[df['Notes ar'] == selected_maintenance]
            
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                st.metric("عدد الصيانات", len(maintenance_data))
            with col_b:
                st.metric("إجمالي الصافي", f"{maintenance_data[amount_col].sum():,.2f}")
            with col_c:
                st.metric("المتوسط", f"{maintenance_data[amount_col].mean():,.2f}")
            
            st.dataframe(maintenance_data, use_container_width=True)
        
        st.markdown("---")
        st.info("✨ لوحة التحكم جاهزة - استخدم التبويبات للتنقل بين التحليلات المختلفة")
        
    except Exception as e:
        st.error(f"❌ حدث خطأ: {e}")
        st.write(f"**تفاصيل الخطأ:** {str(e)}")
else:
    st.info("👆 يرجى رفع ملف بيانات الصيانة (Excel)")
    
    st.write("---")
    st.subheader("📋 الأعمدة المطلوبة:")
    
    required_columns = {
        "Year": "السنة",
        "Month": "الشهر",
        "Day": "اليوم",
        "Area": "المنطقة (مهم جداً)",
        "Expense-Bearing Branch": "الفرع المسؤول عن المصروف",
        "Vehicle Plate Number": "رقم المعدة (مهم جداً)",
        "Vehicle Type": "نوع المعدة",
        "Expense Category": "فئة المصروف",
        "Notes ar": "نوع الصيانة (مهم جداً)",
        "Service Provider": "مقدم الخدمة",
        "Amount": "المبلغ",
        "Net Amount": "الصافي",
        "VAT 14%": "الضريبة 14%",
        "WHT 1% & 3%": "الضريبة المستقطعة"
    }
    
    for col, desc in required_columns.items():
        st.write(f"- **{col}** - {desc}")
