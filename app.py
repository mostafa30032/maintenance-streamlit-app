import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

st.set_page_config(page_title="نظام إدارة أسطول المركبات", layout="wide", initial_sidebar_state="expanded")

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
        .warning-box {
            background-color: #ff6b6b;
            color: white;
            padding: 15px;
            border-radius: 10px;
            margin: 10px 0;
        }
        .info-box {
            background-color: #4ecdc4;
            color: white;
            padding: 15px;
            border-radius: 10px;
            margin: 10px 0;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='header-title'>🚗 نظام إدارة أسطول المركبات</h1>", unsafe_allow_html=True)
st.markdown("---")

# الشريط الجانبي
with st.sidebar:
    st.header("⚙️ إعدادات النظام")
    st.write("قم برفع ملف بيانات المركبات")

# رفع ملف Excel
uploaded_file = st.file_uploader("📤 رفع ملف بيانات المركبات (Excel)", type=['xlsx', 'xls'])

if uploaded_file is not None:
    try:
        # قراءة الملف
        df = pd.read_excel(uploaded_file)
        
        # تنظيف أسماء الأعمدة - إزالة المسافات
        df.columns = df.columns.str.strip()
        
        st.success("✅ تم تحميل البيانات بنجاح!")
        
        # البحث عن الأعمدة الصحيحة بناءً على الاسم الذي يحتويه
        vehicle_id_col = None
        vehicle_type_col = None
        area_col = None
        capacity_col = None
        branch_col = None
        status_col = None
        license_expiry_col = None
        license_status_col = None
        
        # البحث عن الأعمدة
        for col in df.columns:
            if 'vehicle' in col.lower() and 'id' in col.lower():
                vehicle_id_col = col
            elif 'vehicle' in col.lower() and 'type' in col.lower():
                vehicle_type_col = col
            elif 'area' in col.lower() or '区域' in col:
                area_col = col
            elif 'transport' in col.lower() or '运力' in col:
                capacity_col = col
            elif 'branch' in col.lower() or '网点' in col:
                branch_col = col
            elif 'statues' in col.lower() or '状态' in col and 'licence' not in col.lower():
                status_col = col
            elif 'licence expiry' in col.lower() or 'expiry' in col.lower():
                license_expiry_col = col
            elif 'licence status' in col.lower() or '行驶证状态' in col:
                license_status_col = col
        
        # ============ معالجة Licence Status ============
        expired_count = 0
        not_expired_count = 0
        
        if license_status_col:
            # عد المركبات المنتهية والصحيحة
            expired_count = len(df[df[license_status_col].str.contains('منتهية|Expired|有效期', na=False, case=False)])
            not_expired_count = len(df[df[license_status_col].str.contains('Not Expired|صحيح|有效', na=False, case=False)])
        
        # ============ KPI الرئيسية ============
        st.subheader("📊 المؤشرات الرئيسية")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("🚗 إجمالي المركبات", len(df))
        
        with col2:
            active_vehicles = 0
            if status_col:
                active_vehicles = len(df[df[status_col].str.contains('Active|في|نشطة', na=False, case=False)])
            st.metric("✅ المركبات النشطة", active_vehicles)
        
        with col3:
            st.metric("⚠️ رخص منتهية", expired_count)
        
        with col4:
            st.metric("✅ رخص صحيحة", not_expired_count)
        
        with col5:
            areas_count = 0
            if area_col:
                areas_count = df[area_col].nunique()
            st.metric("📍 المناطق", areas_count)
        
        st.markdown("---")
        
        # ============ التنبيهات ============
        if license_status_col:
            expired_vehicles = df[df[license_status_col].str.contains('منتهية|Expired|有效期', na=False, case=False)]
            if len(expired_vehicles) > 0:
                st.markdown("<div class='warning-box'>⚠️ تحذير: يوجد رخص منتهية!</div>", unsafe_allow_html=True)
                display_cols = [c for c in [vehicle_id_col, vehicle_type_col, area_col, license_expiry_col, license_status_col] if c]
                st.dataframe(expired_vehicles[display_cols], use_container_width=True)
        
        st.markdown("---")
        
        # ============ التبويبات الرئيسية ============
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "📈 نظرة عامة", 
            "🚗 المركبات", 
            "📍 تحليل المناطق", 
            "⏰ حالة الرخص",
            "📊 الرسوم البيانية", 
            "📋 البيانات التفصيلية"
        ])
        
        # ============ التبويب الأول - نظرة عامة ============
        with tab1:
            st.subheader("📈 نظرة عامة على بيانات المركبات")
            
            st.write("**جدول البيانات الكاملة:**")
            st.dataframe(df, use_container_width=True, height=400)
            
            # تحميل كـ CSV
            csv = df.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="📥 تحميل البيانات (CSV)",
                data=csv,
                file_name=f"vehicles_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        
        # ============ التبويب الثاني - المركبات ============
        with tab2:
            st.subheader("🚗 إدارة المركبات")
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                if status_col:
                    st.write("**إحصائيات الحالة:**")
                    status_count = df[status_col].value_counts()
                    st.bar_chart(status_count)
            
            with col2:
                if vehicle_type_col:
                    st.write("**توزيع أنواع المركبات:**")
                    vehicle_type_count = df[vehicle_type_col].value_counts()
                    fig = px.pie(
                        values=vehicle_type_count.values,
                        names=vehicle_type_count.index,
                        title="توزيع أنواع المركبات"
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            st.subheader("📋 قائمة المركبات")
            
            # تصفية حسب الحالة
            if status_col:
                try:
                    status_filter = st.multiselect(
                        "تصفية حسب الحالة:",
                        df[status_col].unique(),
                        default=df[status_col].unique()
                    )
                    filtered_df = df[df[status_col].isin(status_filter)]
                except:
                    filtered_df = df
            else:
                filtered_df = df
            
            st.dataframe(filtered_df, use_container_width=True)
        
        # ============ التبويب الثالث - تحليل المناطق ============
        with tab3:
            st.subheader("📍 تحليل المناطق")
            
            if area_col:
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    st.write("**عدد المركبات حسب المنطقة:**")
                    try:
                        area_count = df[area_col].value_counts()
                        st.bar_chart(area_count)
                    except:
                        st.write("⚠️ لا يمكن عرض البيانات")
                
                with col2:
                    st.write("**توزيع المناطق:**")
                    try:
                        area_count = df[area_col].value_counts()
                        fig = px.pie(
                            values=area_count.values,
                            names=area_count.index,
                            title="توزيع المركبات حسب المنطقة"
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    except:
                        st.write("⚠️ لا يمكن عرض البيانات")
                
                # جدول تفصيلي للمناطق
                st.subheader("📊 جدول المناطق")
                
                try:
                    area_analysis = df.groupby(area_col).size().reset_index(name='عدد المركبات')
                    st.dataframe(area_analysis, use_container_width=True)
                except:
                    st.write("⚠️ لا يمكن تحليل المناطق")
        
        # ============ التبويب الرابع - حالة الرخص ============
        with tab4:
            st.subheader("⏰ إدارة حالة الرخص")
            
            if license_status_col:
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    st.write("**حالة الرخص:**")
                    
                    status_data = {
                        'الحالة': ['منتهية', 'صحيحة'],
                        'العدد': [expired_count, not_expired_count]
                    }
                    
                    try:
                        fig = px.bar(
                            status_data,
                            x='الحالة',
                            y='العدد',
                            title="حالة الرخص",
                            color='الحالة',
                            color_discrete_map={
                                'منتهية': 'red',
                                'صحيحة': 'green'
                            }
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    except:
                        st.metric("منتهية", expired_count)
                        st.metric("صحيحة", not_expired_count)
                
                with col2:
                    st.write("**توزيع حالات الرخصة:**")
                    try:
                        license_counts = df[license_status_col].value_counts()
                        fig = px.pie(
                            values=license_counts.values,
                            names=license_counts.index,
                            title="توزيع حالات الرخصة"
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    except:
                        st.write("⚠️ لا يمكن عرض البيانات")
                
                # جدول المركبات حسب حالة الرخصة
                st.subheader("📋 قائمة المركبات حسب حالة الرخصة")
                
                try:
                    license_analysis = df.groupby(license_status_col).size().reset_index(name='عدد المركبات')
                    st.dataframe(license_analysis, use_container_width=True)
                except:
                    st.write("⚠️ لا يمكن تحليل البيانات")
                
                # جدول المركبات المنتهية
                if expired_count > 0:
                    st.subheader("🚨 المركبات ذات الرخص المنتهية")
                    expired_vehicles = df[df[license_status_col].str.contains('منتهية|Expired|有效期', na=False, case=False)]
                    display_cols = [c for c in [vehicle_id_col, vehicle_type_col, area_col, license_status_col] if c]
                    try:
                        st.dataframe(expired_vehicles[display_cols], use_container_width=True)
                    except:
                        st.dataframe(expired_vehicles, use_container_width=True)
        
        # ============ التبويب الخامس - الرسوم البيانية ============
        with tab5:
            st.subheader("📊 لوحة الرسوم البيانية")
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                if vehicle_type_col and area_col:
                    st.write("**المركبات: النوع × المنطقة**")
                    try:
                        vehicle_area = df.groupby([area_col, vehicle_type_col]).size().reset_index(name='العدد')
                        fig = px.bar(
                            vehicle_area,
                            x=area_col,
                            y='العدد',
                            color=vehicle_type_col,
                            title="توزيع المركبات حسب النوع والمنطقة"
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    except:
                        st.write("⚠️ لا يمكن عرض البيانات")
            
            with col2:
                if capacity_col and area_col:
                    st.write("**توزيع السعة النقلية:**")
                    try:
                        capacity_by_area = df.groupby(area_col)[capacity_col].sum().sort_values(ascending=False)
                        fig = px.bar(
                            x=capacity_by_area.values,
                            y=capacity_by_area.index,
                            orientation='h',
                            title="إجمالي السعة النقلية حسب المنطقة"
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    except:
                        st.write("⚠️ لا يمكن عرض البيانات")
            
            col3, col4 = st.columns([1, 1])
            
            with col3:
                if branch_col:
                    st.write("**المركبات حسب الفرع:**")
                    try:
                        branch_count = df[branch_col].value_counts()
                        fig = px.pie(
                            values=branch_count.values,
                            names=branch_count.index,
                            title="توزيع المركبات حسب الفرع"
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    except:
                        st.write("⚠️ لا يمكن عرض البيانات")
            
            with col4:
                if license_status_col:
                    st.write("**حالة الرخصة:**")
                    try:
                        license_status = df[license_status_col].value_counts()
                        fig = px.pie(
                            values=license_status.values,
                            names=license_status.index,
                            title="توزيع حالات الرخصة"
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    except:
                        st.write("⚠️ لا يمكن عرض البيانات")
        
        # ============ التبويب السادس - البيانات التفصيلية ============
        with tab6:
            st.subheader("📋 البيانات التفصيلية")
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                if vehicle_id_col:
                    st.write("**تفاصيل المركبة:**")
                    
                    try:
                        vehicles = sorted(df[vehicle_id_col].unique())
                        selected_vehicle = st.selectbox("اختر رقم المركبة:", vehicles)
                        
                        vehicle_data = df[df[vehicle_id_col] == selected_vehicle]
                        
                        st.dataframe(vehicle_data, use_container_width=True)
                    except:
                        st.write("⚠️ لا يمكن عرض البيانات")
            
            with col2:
                if area_col:
                    st.write("**إحصائيات المنطقة:**")
                    
                    try:
                        areas = sorted(df[area_col].unique())
                        selected_area = st.selectbox("اختر المنطقة:", areas)
                        
                        area_data = df[df[area_col] == selected_area]
                        
                        col_a, col_b, col_c = st.columns(3)
                        with col_a:
                            st.metric("عدد المركبات", len(area_data))
                        with col_b:
                            if capacity_col:
                                try:
                                    st.metric("السعة الإجمالية", f"{area_data[capacity_col].sum():,.0f}")
                                except:
                                    st.metric("السعة", "N/A")
                        with col_c:
                            if license_status_col:
                                expired_in_area = len(area_data[area_data[license_status_col].str.contains('منتهية|Expired', na=False, case=False)])
                                st.metric("رخص منتهية", expired_in_area)
                        
                        st.dataframe(area_data, use_container_width=True)
                    except:
                        st.write("⚠️ لا يمكن عرض البيانات")
        
        st.markdown("---")
        st.info("✨ لوحة إدارة المركبات جاهزة - استخدم التبويبات للتنقل بين التحليلات المختلفة")
        
    except Exception as e:
        st.error(f"❌ حدث خطأ: {e}")
        st.write(f"**تفاصيل الخطأ:** {str(e)}")
        import traceback
        st.write(traceback.format_exc())
else:
    st.info("👆 يرجى رفع ملف بيانات المركبات (Excel)")
