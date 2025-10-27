import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from database import finance_db

def create_usage_percentage_chart(df):
    """
    Create a bar chart showing the percentage of API credit usage per platform.
    Special handling for Sub Magic (healthy/unhealthy status).
    """
    chart_data = []
    colors = []
    
    for index, row in df.iterrows():
        platform = row['Plataforma']
        total_credits = row['Total de Créditos Contratados']
        consumed_credits = row['Créditos Consumidos']
        
        # Special case for Sub Magic (healthy/unhealthy)
        if platform == 'Sub Magic':
            if str(consumed_credits).lower() == 'healthy':
                percentage = 100  # Show as 100% for visualization
                colors.append('#28a745')  # Green
                status_text = 'Healthy'
            else:
                percentage = 100  # Show as 100% for visualization  
                colors.append('#dc3545')  # Red
                status_text = 'Unhealthy'
            
            chart_data.append({
                'Plataforma': platform,
                'Percentage': percentage,
                'Status': status_text,
                'Display_Text': f'{platform}<br>Status: {status_text}'
            })
        else:
            # Calculate percentage for other platforms
            if total_credits > 0:
                percentage = (consumed_credits / total_credits) * 100
            else:
                percentage = 0
            
            # Color based on usage percentage
            if percentage >= 90:
                color = '#dc3545'  # Red (high usage)
            elif percentage >= 70:
                color = '#ffc107'  # Yellow (medium usage)
            else:
                color = '#28a745'  # Green (low usage)
            
            colors.append(color)
            
            chart_data.append({
                'Plataforma': platform,
                'Percentage': percentage,
                'Total': total_credits,
                'Consumed': consumed_credits,
                'Display_Text': f'{platform}<br>{percentage:.1f}% usado'
            })
    
    # Create DataFrame for plotting
    plot_df = pd.DataFrame(chart_data)
    
    # Create bar chart
    fig = go.Figure(data=[
        go.Bar(
            x=plot_df['Plataforma'],
            y=plot_df['Percentage'],
            text=plot_df['Display_Text'],
            textposition='auto',
            marker_color=colors,
            hovertemplate='<b>%{x}</b><br>Uso: %{y:.1f}%<extra></extra>'
        )
    ])
    
    fig.update_layout(
        title='Percentual de Uso de Créditos API por Plataforma',
        xaxis_title='Plataforma',
        yaxis_title='Percentual de Uso (%)',
        yaxis=dict(range=[0, 105]),
        showlegend=False,
        height=500,
        margin=dict(t=50, b=50, l=50, r=50)
    )
    
    return fig

def create_sub_magic_status_chart(df):
    """
    Create a simple status indicator for Sub Magic.
    """
    sub_magic_row = df[df['Plataforma'] == 'Sub Magic']
    
    if sub_magic_row.empty:
        return None
    
    status = str(sub_magic_row.iloc[0]['Créditos Consumidos']).lower()
    
    if status == 'healthy':
        color = '#28a745'
        status_text = 'HEALTHY'
    else:
        color = '#dc3545' 
        status_text = 'UNHEALTHY'
    
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = 1 if status == 'healthy' else 0,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Sub Magic Status"},
        gauge = {
            'axis': {'range': [None, 1], 'tickmode': 'array', 'tickvals': [0, 1], 'ticktext': ['UNHEALTHY', 'HEALTHY']},
            'bar': {'color': color},
            'steps': [
                {'range': [0, 0.5], 'color': "#ffcccc"},
                {'range': [0.5, 1], 'color': "#ccffcc"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 0.9
            }
        }
    ))
    
    fig.update_layout(height=300)
    
    return fig

def create_expense_class_chart():
    """
    Create a bar chart showing actual vs expected expenses by class
    """
    try:
        # Get monthly summary
        summary = finance_db.get_current_month_summary()
        actual_expenses = summary.get('total_by_class', {})
        expected_expenses = summary.get('expected_amounts', {})
        
        # Prepare data for chart
        classes = []
        actual_amounts = []
        expected_amounts = []
        percentages = []
        colors = []
        
        for class_name in finance_db.expense_classes:
            actual = actual_expenses.get(class_name, 0)
            expected = expected_expenses.get(class_name, 0)
            
            classes.append(class_name)
            actual_amounts.append(actual)
            expected_amounts.append(expected)
            
            # Calculate percentage of expected amount spent
            if expected > 0:
                percentage = (actual / expected) * 100
                percentages.append(percentage)
                
                # Color based on percentage
                if percentage >= 100:
                    colors.append('#dc3545')  # Red (over budget)
                elif percentage >= 80:
                    colors.append('#ffc107')  # Yellow (warning)
                else:
                    colors.append('#28a745')  # Green (good)
            else:
                percentages.append(0)
                colors.append('#6c757d')  # Gray (no budget)
        
        # Create grouped bar chart
        fig = go.Figure()
        
        # Add actual expenses bars
        fig.add_trace(go.Bar(
            name='Gasto Real',
            x=classes,
            y=actual_amounts,
            marker_color=colors,
            text=[f'R$ {amt:.0f}' for amt in actual_amounts],
            textposition='auto',
        ))
        
        # Add expected expenses bars
        fig.add_trace(go.Bar(
            name='Orçamento Esperado',
            x=classes,
            y=expected_amounts,
            marker_color='lightblue',
            opacity=0.7,
            text=[f'R$ {amt:.0f}' for amt in expected_amounts],
            textposition='auto',
        ))
        
        fig.update_layout(
            title='Gastos por Categoria: Real vs Orçado',
            xaxis_title='Categoria de Gasto',
            yaxis_title='Valor (R$)',
            barmode='group',
            showlegend=True,
            height=500,
            margin=dict(t=50, b=50, l=50, r=50)
        )
        
        return fig
        
    except Exception as e:
        print(f"Error creating expense class chart: {e}")
        return go.Figure()

def create_monthly_expense_pie_chart():
    """
    Create a pie chart showing monthly expenses by category
    """
    try:
        # Get monthly summary
        summary = finance_db.get_current_month_summary()
        expenses_by_class = summary.get('total_by_class', {})
        
        # Filter out zero expenses
        filtered_expenses = {k: v for k, v in expenses_by_class.items() if v > 0}
        
        if not filtered_expenses:
            return go.Figure().add_annotation(
                text="Nenhum gasto registrado este mês",
                xref="paper", yref="paper",
                x=0.5, y=0.5, xanchor='center', yanchor='middle',
                showarrow=False, font=dict(size=16)
            )
        
        # Create pie chart
        fig = go.Figure(data=[go.Pie(
            labels=list(filtered_expenses.keys()),
            values=list(filtered_expenses.values()),
            hole=0.3,
            textinfo='label+percent+value',
            texttemplate='<b>%{label}</b><br>%{percent}<br>R$ %{value:.0f}',
        )])
        
        fig.update_layout(
            title=f'Distribuição de Gastos - {summary.get("month", "Mês Atual")}',
            showlegend=True,
            height=500,
            margin=dict(t=50, b=50, l=50, r=50)
        )
        
        return fig
        
    except Exception as e:
        print(f"Error creating pie chart: {e}")
        return go.Figure()

def create_budget_overview_chart():
    """
    Create a summary chart showing total spending vs expected revenue
    """
    try:
        summary = finance_db.get_current_month_summary()
        total_spent = summary.get('total_amount', 0)
        expected_revenue = summary.get('expected_revenue', 0)
        
        # Calculate remaining budget
        remaining_budget = expected_revenue - total_spent
        
        # Prepare data
        categories = ['Gasto Total', 'Orçamento Restante']
        values = [total_spent, max(0, remaining_budget)]
        colors = ['#dc3545' if total_spent > expected_revenue else '#ffc107', '#28a745']
        
        # Create bar chart
        fig = go.Figure(data=[
            go.Bar(
                x=categories,
                y=values,
                marker_color=colors,
                text=[f'R$ {val:.0f}' for val in values],
                textposition='auto',
            )
        ])
        
        # Add expected revenue line
        fig.add_hline(
            y=expected_revenue, 
            line_dash="dash", 
            line_color="blue",
            annotation_text=f"Receita Esperada: R$ {expected_revenue:.0f}"
        )
        
        fig.update_layout(
            title='Visão Geral do Orçamento Mensal',
            yaxis_title='Valor (R$)',
            showlegend=False,
            height=400,
            margin=dict(t=50, b=50, l=50, r=50)
        )
        
        return fig
        
    except Exception as e:
        print(f"Error creating budget overview: {e}")
        return go.Figure()