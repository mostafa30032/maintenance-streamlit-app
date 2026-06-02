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
        
        # تنظيف أسماء الأعمدة
        df.columns = df.columns.str.strip()
        
        st.success("✅ تم تحميل البيانات بنجاح!")
        
        # تحويل تاريخ انتهاء الرخصة لـ datetime
        if 'Licence Expiry Date' in df.columns:
            df['Licence Expiry Date'] = pd.to_datetime(df['Licence Expiry Date'], errors='coerce')
        
        # حساب الأيام المتبقية
        today = datetime.now()
        if 'Licence Expiry Date' in df.columns:
            df['Days Remaining'] = (df['Licence Expiry Date'] - pd.Timestamp(today)).dt.days
        
        # ============ KPI الرئيسية ============
        st.subheader("📊 المؤشرات الرئيسية")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("🚗 إجمالي المركبات", len(df))
        
        with col2:
            active_vehicles = len(df[df['STATUES-状态'] == 'Active']) if 'STATUES-状态' in df.columns else 0
            st.metric("✅ المركبات النشطة", active_vehicles)
        
        with col3:
            expired = len(df[df['Days Remaining'] <= 0]) if 'Days Remaining' in df.columns else 0
            st.metric("⚠️ رخص منتهية", expired)
        
        with col4:
            expiring_soon = len(df[(df['Days Remaining'] > 0) & (df['Days Remaining'] <= 30)]) if 'Days Remaining' in df.columns else 0
            st.metric("⏰ انتهاء قريب", expiring_soon)
        
        with col5:
            areas_count = df['Area'].nunique() if 'Area' in df.columns else 0
            st.metric("📍 المناطق", areas_count)
        
        st.markdown("---")
        
        # ============ التنبيهات ============
        if 'Days Remaining' in df.columns:
            expired_vehicles = df[df['Days Remaining'] <= 0]
            if len(expired_vehicles) > 0:
                st.markdown("<div class='warning-box'>⚠️ تحذير: يوجد رخص منتهية!</div>", unsafe_allow_html=True)
                st.dataframe(expired_vehicles[['Vehicle ID', 'Vehicle Type', 'Area', 'Licence Expiry Date']], use_container_width=True)
            
            expiring_soon_vehicles = df[(df['Days Remaining'] > 0) & (df['Days Remaining'] <= 30)]
            if len(expiring_soon_vehicles) > 0:
                st.markdown("<div class='info-box'>⏰ معلومة: رخص تنتهي خلال 30 يوم</div>", unsafe_allow_html=True)
                st.dataframe(expiring_soon_vehicles[['Vehicle ID', 'Vehicle Type', 'Area', 'Licence Expiry Date', 'Days Remaining']], use_container_width=True)
        
        st.markdown("---")
        
        # ============ التبويبات الرئيسية ============
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "📈 نظرة عامة", 
            "🚗 المركبات", 
            "📍 تحليل المناطق", 
            "⏰ الرخص والتواريخ",
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
                st.write("**إحصائيات الحالة:**")
                if 'STATUES-状态' in df.columns:
                    status_count = df['STATUES-状态'].value_counts()
                    st.bar_chart(status_count)
            
            with col2:
                st.write("**توزيع أنواع المركبات:**")
                if 'Vehicle Type' in df.columns:
                    vehicle_type_count = df['Vehicle Type'].value_counts()
                    fig = px.pie(
                        values=vehicle_type_count.values,
                        names=vehicle_type_count.index,
                        title="توزيع أنواع المركبات"
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            st.subheader("📋 قائمة المركبات")
            
            # تصفية حسب الحالة
            if 'STATUES-状态' in df.columns:
                status_filter = st.multiselect(
                    "تصفية حسب الحالة:",
                    df['STATUES-状态'].unique(),
                    default=df['STATUES-状态'].unique()
                )
                filtered_df = df[df['STATUES-状态'].isin(status_filter)]
            else:
                filtered_df = df
            
            st.dataframe(filtered_df, use_container_width=True)
        
        # ============ التبويب الثالث - تحليل المناطق ============
        with tab3:
            st.subheader("📍 تحليل المناطق")
            
            if 'Area' in df.columns:
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    st.write("**عدد المركبات حسب المنطقة:**")
                    area_count = df['Area'].value_counts()
                    st.bar_chart(area_count)
                
                with col2:
                    st.write("**توزيع المناطق:**")
                    fig = px.pie(
                        values=area_count.values,
                        names=area_count.index,
                        title="توزيع المركبات حسب المنطقة"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                # جدول تفصيلي للمناطق
                st.subheader("📊 جدول المناطق")
                
                area_analysis = df.groupby('Area').agg({
                    'Vehicle ID': 'count',
                    'Vehicle Type': lambda x: x.nunique()
                }).rename(columns={'Vehicle ID': 'عدد المركبات', 'Vehicle Type': 'أنواع المركبات'})
                
                st.dataframe(area_analysis, use_container_width=True)
        
        # ============ التبويب الرابع - الرخص والتواريخ ============
        with tab4:
            st.subheader("⏰ إدارة تواريخ انتهاء الرخص")
            
            if 'Licence Expiry Date' in df.columns and 'Days Remaining' in df.columns:
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    st.write("**حالة الرخص:**")
                    
                    # تقسيم الرخص
                    expired = len(df[df['Days Remaining'] <= 0])
                    expiring_soon = len(df[(df['Days Remaining'] > 0) & (df['Days Remaining'] <= 30)])
                    valid = len(df[df['Days Remaining'] > 30])
                    
                    status_data = {
                        'الحالة': ['منتهية', 'انتهاء قريب', 'صحيحة'],
                        'العدد': [expired, expiring_soon, valid]
                    }
                    
                    fig = px.bar(
                        status_data,
                        x='الحالة',
                        y='العدد',
                        title="حالة الرخص",
                        color='الحالة',
                        color_discrete_map={
                            'منتهية': 'red',
                            'انتهاء قريب': 'orange',
                            'صحيحة': 'green'
                        }
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    st.write("**توزيع أيام الانتهاء:**")
                    fig = px.histogram(
                        df,
                        x='Days Remaining',
                        title="توزيع أيام الانتهاء",
                        labels={'Days Remaining': 'الأيام المتبقية'},
                        nbins=20
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                # جدول الرخص القريبة من الانتهاء
                st.subheader("⏳ المركبات القريبة من انتهاء الرخصة (30 يوم)")
                
                expiring_vehicles = df[(df['Days Remaining'] > 0) & (df['Days Remaining'] <= 30)].sort_values('Days Remaining')
                
                if len(expiring_vehicles) > 0:
                    display_cols = ['Vehicle ID', 'Vehicle Type', 'Area', 'Licence Expiry Date', 'Days Remaining']
                    st.dataframe(expiring_vehicles[display_cols], use_container_width=True)
                else:
                    st.info("✅ لا توجد رخص قريبة من الانتهاء")
        
        # ============ التبويب الخامس - الرسوم البيانية ============
        with tab5:
            st.subheader("📊 لوحة الرسوم البيانية")
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                if 'Vehicle Type' in df.columns and 'Area' in df.columns:
                    st.write("**المركبات: النوع × المنطقة**")
                    vehicle_area = df.groupby(['Area', 'Vehicle Type']).size().reset_index(name='العدد')
                    fig = px.bar(
                        vehicle_area,
                        x='Area',
                        y='العدد',
                        color='Vehicle Type',
                        title="توزيع المركبات حسب النوع والمنطقة"
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                if 'Transport Capacity' in df.columns:
                    st.write("**توزيع السعة النقلية:**")
                    capacity_by_area = df.groupby('Area')['Transport Capacity'].sum().sort_values(ascending=False)
                    fig = px.bar(
                        x=capacity_by_area.values,
                        y=capacity_by_area.index,
                        orientation='h',
                        title="إجمالي السعة النقلية حسب المنطقة"
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            col3, col4 = st.columns([1, 1])
            
            with col3:
                if 'Branch' in df.columns:
                    st.write("**المركبات حسب الفرع:**")
                    branch_count = df['Branch'].value_counts()
                    fig = px.pie(
                        values=branch_count.values,
                        names=branch_count.index,
                        title="توزيع المركبات حسب الفرع"
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            with col4:
                if 'Licence Status' in df.columns:
                    st.write("**حالة الرخصة:**")
                    license_status = df['Licence Status'].value_counts()
                    fig = px.pie(
                        values=license_status.values,
                        names=license_status.index,
                        title="توزيع حالات الرخصة"
                    )
                    st.plotly_chart(fig, use_container_width=True)
        
        # ============ التبويب السادس - البيانات التفصيلية ============
        with tab6:
            st.subheader("📋 البيانات التفصيلية")
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.write("**تفاصيل المركبة:**")
                
                if 'Vehicle ID' in df.columns:
                    vehicles = sorted(df['Vehicle ID'].unique())
                    selected_vehicle = st.selectbox("اختر رقم المركبة:", vehicles)
                    
                    vehicle_data = df[df['Vehicle ID'] == selected_vehicle]
                    
                    st.dataframe(vehicle_data, use_container_width=True)
            
            with col2:
                st.write("**إحصائيات المنطقة:**")
                
                if 'Area' in df.columns:
                    areas = sorted(df['Area'].unique())
                    selected_area = st.selectbox("اختر المنطقة:", areas)
                    
                    area_data = df[df['Area'] == selected_area]
                    
                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        st.metric("عدد المركبات", len(area_data))
                    with col_b:
                        if 'Transport Capacity' in df.columns:
                            st.metric("السعة الإجمالية", f"{area_data['Transport Capacity'].sum():,.0f}")
                    with col_c:
                        if 'Days Remaining' in df.columns:
                            expired_in_area = len(area_data[area_data['Days Remaining'] <= 0])
                            st.metric("رخص منتهية", expired_in_area)
                    
                    st.dataframe(area_data, use_container_width=True)
        
        st.markdown("---")
        st.info("✨ لوحة إدارة المركبات جاهزة - استخدم التبويبات للتنقل بين التحليلات المختلفة")
        
    except Exception as e:
        st.error(f"❌ حدث خطأ: {e}")
        st.write(f"**تفاصيل الخطأ:** {str(e)}")
        import traceback
        st.write(traceback.format_exc())
else:
    st.info("👆 يرجى رفع ملف بيانات المركبات (Excel)")
    
    st.write("---")
    st.subheader("📋 الأعمدة المطلوبة:")
    
    required_columns = {
        "Vehicle ID": "رقم المركبة (车牌号)",
        "Vehicle Type": "نوع/ماركة المركبة (品牌)",
        "Area": "المنطقة (区域)",
        "Transport Capacity": "السعة النقلية (区域运力)",
        "Branch": "الفرع (网点)",
        "STATUES-状态": "الحالة (状态)",
        "Licence Expiry Date": "تاريخ انتهاء الرخصة (有效期止)",
        "Days Remaining": "الأيام المتبقية (有效期剩余天数)",
        "Licence Status": "حالة الرخصة (行驶证状态)"
    }
    
    for col, desc in required_columns.items():
        st.write(f"- **{col}** - {desc}")
