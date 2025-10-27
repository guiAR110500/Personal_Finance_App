import streamlit as st
from database import finance_db

def render_settings_sidebar():
    """Render the settings sidebar with user input controls"""
    
    st.sidebar.header("⚙️ Configurações Financeiras")
    
    # Get current settings
    current_settings = finance_db.get_settings()
    current_revenue = current_settings.get("monthly_expected_revenue", 5000.0)
    current_percentages = current_settings.get("expense_class_percentages", {})
    
    # Revenue input
    st.sidebar.subheader("💰 Receita Mensal Esperada")
    monthly_revenue = st.sidebar.number_input(
        "Receita Mensal (R$)", 
        min_value=0.0, 
        value=current_revenue,
        step=100.0,
        format="%.2f",
        key="monthly_revenue_input"
    )
    
    # Expense class percentages
    st.sidebar.subheader("📊 Percentual por Categoria (%)")
    st.sidebar.caption("Distribua sua receita entre as categorias de gasto:")
    
    # Create input fields for each expense class
    percentages = {}
    total_percentage = 0
    
    for class_name in finance_db.expense_classes:
        current_value = current_percentages.get(class_name, 0.0)
        
        percentage = st.sidebar.number_input(
            f"{class_name}",
            min_value=0.0,
            max_value=100.0,
            value=current_value,
            step=0.5,
            format="%.1f",
            key=f"percentage_{class_name}"
        )
        
        percentages[class_name] = percentage
        total_percentage += percentage
    
    # Show total percentage
    st.sidebar.markdown("---")
    
    # Color code the total based on value
    if total_percentage > 100:
        color = "red"
        icon = "⚠️"
        message = f"Total: {total_percentage:.1f}% (Acima de 100%)"
    elif total_percentage < 95:
        color = "orange" 
        icon = "⚡"
        message = f"Total: {total_percentage:.1f}% (Considere alocar mais)"
    else:
        color = "green"
        icon = "✅"
        message = f"Total: {total_percentage:.1f}% (Ótima distribuição!)"
    
    st.sidebar.markdown(f"**{icon} {message}**")
    
    # Expected amounts preview
    st.sidebar.subheader("💵 Valores Esperados (R$)")
    for class_name, percentage in percentages.items():
        expected_amount = (monthly_revenue * percentage) / 100
        if expected_amount > 0:
            st.sidebar.text(f"{class_name}: R$ {expected_amount:.0f}")
    
    # Save button
    st.sidebar.markdown("---")
    
    if st.sidebar.button("💾 Salvar Configurações", type="primary", use_container_width=True):
        success = finance_db.update_settings(monthly_revenue, percentages)
        
        if success:
            st.sidebar.success("✅ Configurações salvas com sucesso!")
            # Force rerun to update all components with new settings
            st.rerun()
        else:
            st.sidebar.error("❌ Erro ao salvar configurações. Verifique se o total não excede 150%.")
    
    # Reset to defaults button
    if st.sidebar.button("🔄 Restaurar Padrões", use_container_width=True):
        default_percentages = {
            "Lazer": 10.0, "Limpeza": 3.0, "Roupas": 8.0, "Lavanderia": 2.0,
            "Mercado": 25.0, "Casa": 10.0, "Restaurante": 15.0, "Aluguel": 20.0,
            "Luz": 3.0, "Internet": 2.0, "Farmácia": 2.0, "Carro": 0.0
        }
        
        success = finance_db.update_settings(5000.0, default_percentages)
        if success:
            st.sidebar.success("✅ Configurações restauradas!")
            st.rerun()

def render_quick_stats():
    """Render quick statistics cards"""
    
    # Get monthly summary
    summary = finance_db.get_current_month_summary()
    total_spent = summary.get('total_amount', 0)
    expected_revenue = summary.get('expected_revenue', 0)
    remaining_budget = expected_revenue - total_spent
    
    # Create columns for metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="💰 Receita Esperada",
            value=f"R$ {expected_revenue:.0f}",
        )
    
    with col2:
        st.metric(
            label="💸 Total Gasto",
            value=f"R$ {total_spent:.0f}",
            delta=f"{(total_spent/expected_revenue*100):.1f}%" if expected_revenue > 0 else "0%"
        )
    
    with col3:
        st.metric(
            label="💵 Orçamento Restante", 
            value=f"R$ {remaining_budget:.0f}",
            delta=f"{(remaining_budget/expected_revenue*100):.1f}%" if expected_revenue > 0 else "0%"
        )
    
    with col4:
        days_in_month = 30  # Simplified
        daily_entries = summary.get('daily_entries', 0)
        st.metric(
            label="📅 Dias Registrados",
            value=f"{daily_entries}/{days_in_month}",
            delta=f"{(daily_entries/days_in_month*100):.0f}%"
        )

def render_data_management():
    """Render data management section"""
    
    st.subheader("📊 Gerenciamento de Dados")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Atualizar Dados do Sheets", use_container_width=True):
            try:
                # Import and save current data
                from data_source import save_current_data_to_db
                success = save_current_data_to_db()
                
                if success:
                    st.success("✅ Dados atualizados com sucesso!")
                    st.rerun()
                else:
                    st.error("❌ Erro ao atualizar dados")
            except Exception as e:
                st.error(f"❌ Erro: {str(e)}")
    
    with col2:
        if st.button("📥 Exportar Dados", use_container_width=True):
            # This could be implemented to export data to CSV/Excel
            st.info("🚧 Funcionalidade em desenvolvimento")