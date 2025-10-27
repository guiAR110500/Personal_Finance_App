import json
import os
from datetime import datetime, date
from typing import Dict, List, Optional
import pandas as pd

class FinanceDatabase:
    def __init__(self):
        self.settings_file = "user_settings.json"
        self.daily_results_file = "daily_results.json"
        
        # Default expense classes
        self.expense_classes = [
            "Lazer", "Limpeza", "Roupas", "Lavanderia", "Mercado", 
            "Casa", "Restaurante", "Aluguel", "Luz", "Internet", 
            "Farmácia", "Carro"
        ]
        
        # Initialize files if they don't exist
        self._initialize_files()
    
    def _initialize_files(self):
        """Initialize database files with default values if they don't exist"""
        
        # Initialize settings file
        if not os.path.exists(self.settings_file):
            default_settings = {
                "monthly_expected_revenue": 5000.0,
                "expense_class_percentages": {
                    "Lazer": 10.0,
                    "Limpeza": 3.0,
                    "Roupas": 8.0,
                    "Lavanderia": 2.0,
                    "Mercado": 25.0,
                    "Casa": 10.0,
                    "Restaurante": 15.0,
                    "Aluguel": 20.0,
                    "Luz": 3.0,
                    "Internet": 2.0,
                    "Farmácia": 2.0,
                    "Carro": 0.0
                },
                "last_updated": datetime.now().isoformat()
            }
            self._save_json(self.settings_file, default_settings)
        
        # Initialize daily results file
        if not os.path.exists(self.daily_results_file):
            default_results = {
                "daily_expenses": [],
                "monthly_summaries": []
            }
            self._save_json(self.daily_results_file, default_results)
    
    def _load_json(self, filename: str) -> dict:
        """Load JSON data from file"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _save_json(self, filename: str, data: dict):
        """Save data to JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
    
    # Settings management
    def get_settings(self) -> dict:
        """Get current user settings"""
        return self._load_json(self.settings_file)
    
    def update_settings(self, monthly_revenue: float, class_percentages: Dict[str, float]) -> bool:
        """Update user settings"""
        try:
            settings = self.get_settings()
            settings["monthly_expected_revenue"] = monthly_revenue
            settings["expense_class_percentages"] = class_percentages
            settings["last_updated"] = datetime.now().isoformat()
            
            # Validate percentages sum to reasonable amount (allow flexibility)
            total_percentage = sum(class_percentages.values())
            if total_percentage > 150:  # Allow some flexibility over 100%
                return False
            
            self._save_json(self.settings_file, settings)
            return True
        except Exception as e:
            print(f"Error updating settings: {e}")
            return False
    
    def get_expected_amounts(self) -> Dict[str, float]:
        """Calculate expected amounts for each expense class"""
        settings = self.get_settings()
        monthly_revenue = settings.get("monthly_expected_revenue", 0)
        percentages = settings.get("expense_class_percentages", {})
        
        expected_amounts = {}
        for class_name, percentage in percentages.items():
            expected_amounts[class_name] = (monthly_revenue * percentage) / 100
        
        return expected_amounts
    
    # Daily results management
    def save_daily_expenses(self, expenses_df: pd.DataFrame, target_date: Optional[str] = None):
        """Save daily expense results"""
        try:
            if target_date is None:
                target_date = date.today().isoformat()
            
            results = self._load_json(self.daily_results_file)
            
            # Convert DataFrame to dict for storage
            daily_data = {
                "date": target_date,
                "expenses": expenses_df.to_dict('records'),
                "total_by_class": self._calculate_totals_by_class(expenses_df),
                "total_amount": expenses_df['Value'].sum() if 'Value' in expenses_df.columns else 0,
                "timestamp": datetime.now().isoformat()
            }
            
            # Remove existing entry for the same date
            results["daily_expenses"] = [
                entry for entry in results["daily_expenses"] 
                if entry.get("date") != target_date
            ]
            
            # Add new entry
            results["daily_expenses"].append(daily_data)
            
            # Keep only last 90 days
            results["daily_expenses"] = sorted(
                results["daily_expenses"], 
                key=lambda x: x.get("date", ""), 
                reverse=True
            )[:90]
            
            self._save_json(self.daily_results_file, results)
            return True
        except Exception as e:
            print(f"Error saving daily expenses: {e}")
            return False
    
    def _calculate_totals_by_class(self, df: pd.DataFrame) -> Dict[str, float]:
        """Calculate total expenses by class"""
        if 'Class' not in df.columns or 'Value' not in df.columns:
            return {}
        
        totals = {}
        for class_name in self.expense_classes:
            class_expenses = df[df['Class'] == class_name]['Value'].sum()
            totals[class_name] = float(class_expenses)
        
        return totals
    
    def get_monthly_summary(self, month: Optional[str] = None) -> dict:
        """Get monthly summary for specified month (YYYY-MM format)"""
        if month is None:
            month = date.today().strftime("%Y-%m")
        
        results = self._load_json(self.daily_results_file)
        daily_expenses = results.get("daily_expenses", [])
        
        # Filter expenses for the specified month
        monthly_expenses = [
            entry for entry in daily_expenses 
            if entry.get("date", "").startswith(month)
        ]
        
        # Calculate totals
        total_by_class = {}
        for class_name in self.expense_classes:
            total_by_class[class_name] = sum(
                entry.get("total_by_class", {}).get(class_name, 0)
                for entry in monthly_expenses
            )
        
        total_amount = sum(entry.get("total_amount", 0) for entry in monthly_expenses)
        
        return {
            "month": month,
            "total_amount": total_amount,
            "total_by_class": total_by_class,
            "daily_entries": len(monthly_expenses),
            "expected_amounts": self.get_expected_amounts(),
            "expected_revenue": self.get_settings().get("monthly_expected_revenue", 0)
        }
    
    def get_current_month_summary(self) -> dict:
        """Get current month summary"""
        return self.get_monthly_summary()

# Global database instance
finance_db = FinanceDatabase()