import streamlit as st
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
from data_source import get_processed_data, get_monthly_expense_summary
from charts import (create_expense_class_chart, create_monthly_expense_pie_chart, 
                   create_budget_overview_chart)
from ui_components import render_settings_sidebar, render_quick_stats, render_data_management

# Streamlit app configuration
st.set_page_config(
    page_title="Personal Finance Dashboard - Friguis e Lelezita",
    page_icon=":bar_chart:",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    # Auto-refresh every 60 seconds (60000 milliseconds)
    st_autorefresh(interval=60000, limit=None, key="data_refresh")
    
    # Render sidebar settings
    render_settings_sidebar()
    
    # Main page header
    st.title("💰 Personal Finance Dashboard - Friguis e Lelezita")
    st.markdown("Gerencie e acompanhe suas finanças pessoais de forma inteligente!")
    
    # Show last refresh time
    current_time = datetime.now().strftime("%H:%M:%S")
    st.caption(f"🔄 Última atualização: {current_time}")
    
    # Quick stats
    render_quick_stats()
    
    st.markdown("---")
    
    # Main charts section
    st.subheader("📊 Visualizações Financeiras")
    
    # Top row: Budget overview and pie chart
    col1, col2 = st.columns(2)
    
    with col1:
        st.plotly_chart(create_budget_overview_chart(), use_container_width=True)
    
    with col2:
        st.plotly_chart(create_monthly_expense_pie_chart(), use_container_width=True)
    
    # Bottom row: Expense class comparison chart
    st.plotly_chart(create_expense_class_chart(), use_container_width=True)
    
    st.markdown("---")
    
    # Raw data section
    st.subheader("📋 Dados Brutos")
    
    # Show current month expenses
    df = get_processed_data()
    
    if not df.empty:
        st.dataframe(df, use_container_width=True)
        
        # Summary info
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total de Registros", len(df))
        
        with col2:
            total_value = df['Value'].sum() if 'Value' in df.columns else 0
            st.metric("Valor Total", f"R$ {total_value:.2f}")
        
        with col3:
            unique_classes = df['Class'].nunique() if 'Class' in df.columns else 0
            st.metric("Categorias Utilizadas", unique_classes)
    else:
        st.info("📭 Nenhum dado encontrado. Verifique a conexão com o Google Sheets.")
    
    st.markdown("---")
    
    # Data management section
    render_data_management()
    
if __name__ == "__main__":
    main()