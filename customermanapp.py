from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
import sqlite3
import pandas as pd

class CustomerApp(App):
    def build(self):
        self.conn = sqlite3.connect("customers.db")
        self.cursor = self.conn.cursor()
        self.create_table()
        
        layout = BoxLayout(orientation='vertical')
        
        self.name_input = TextInput(hint_text="Customer Name")
        self.balance_input = TextInput(hint_text="Initial Balance", input_filter='float')
        self.payment_input = TextInput(hint_text="Payment Amount", input_filter='float')
        self.search_input = TextInput(hint_text="Search Customer")
        
        self.add_btn = Button(text="Add Customer", on_press=self.add_customer)
        self.pay_btn = Button(text="Record Payment", on_press=self.record_payment)
        self.view_btn = Button(text="View Customers", on_press=self.view_customers)
        self.delete_btn = Button(text="Delete Customer", on_press=self.delete_customer)
        self.search_btn = Button(text="Search", on_press=self.search_customer)
        self.export_btn = Button(text="Export to Excel", on_press=self.export_to_excel)
        
        self.status_label = Label(text="")
        self.customer_list = ScrollView(size_hint=(1, None), size=(400, 200))
        self.customer_layout = GridLayout(cols=2, size_hint_y=None)
        self.customer_layout.bind(minimum_height=self.customer_layout.setter('height'))
        self.customer_list.add_widget(self.customer_layout)
        
        layout.add_widget(self.name_input)
        layout.add_widget(self.balance_input)
        layout.add_widget(self.add_btn)
        layout.add_widget(self.payment_input)
        layout.add_widget(self.pay_btn)
        layout.add_widget(self.search_input)
        layout.add_widget(self.search_btn)
        layout.add_widget(self.delete_btn)
        layout.add_widget(self.view_btn)
        layout.add_widget(self.export_btn)
        layout.add_widget(self.customer_list)
        layout.add_widget(self.status_label)
        
        return layout
    
    def create_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                balance REAL
            )
        ''')
        self.conn.commit()
    
    def add_customer(self, instance):
        name = self.name_input.text.strip()
        balance = self.balance_input.text.strip()
        if name and balance:
            try:
                self.cursor.execute("INSERT INTO customers (name, balance) VALUES (?, ?)", (name, float(balance)))
                self.conn.commit()
                self.status_label.text = f"Customer {name} added!"
                self.name_input.text = ""
                self.balance_input.text = ""
            except ValueError:
                self.status_label.text = "Invalid balance input"
        else:
            self.status_label.text = "Please enter name and balance"
    
    def record_payment(self, instance):
        name = self.name_input.text.strip()
        payment = self.payment_input.text.strip()
        if name and payment:
            try:
                self.cursor.execute("SELECT balance FROM customers WHERE name = ?", (name,))
                result = self.cursor.fetchone()
                if result:
                    new_balance = result[0] - float(payment)
                    self.cursor.execute("UPDATE customers SET balance = ? WHERE name = ?", (new_balance, name))
                    self.conn.commit()
                    self.status_label.text = f"Payment recorded! New balance: {new_balance:.2f}"
                    self.payment_input.text = ""
                else:
                    self.status_label.text = "Customer not found"
            except ValueError:
                self.status_label.text = "Invalid payment input"
        else:
            self.status_label.text = "Please enter name and payment amount"
    
    def delete_customer(self, instance):
        name = self.name_input.text.strip()
        if name:
            self.cursor.execute("DELETE FROM customers WHERE name = ?", (name,))
            self.conn.commit()
            self.status_label.text = f"Customer {name} deleted!"
            self.name_input.text = ""
        else:
            self.status_label.text = "Please enter a customer name to delete"
    
    def search_customer(self, instance):
        name = self.search_input.text.strip()
        if name:
            self.cursor.execute("SELECT balance FROM customers WHERE name = ?", (name,))
            result = self.cursor.fetchone()
            if result:
                self.status_label.text = f"Customer {name} Balance: {result[0]:.2f}"
            else:
                self.status_label.text = "Customer not found"
        else:
            self.status_label.text = "Please enter a name to search"
    
    def view_customers(self, instance):
        self.customer_layout.clear_widgets()
        self.cursor.execute("SELECT name, balance FROM customers")
        customers = self.cursor.fetchall()
        for name, balance in customers:
            self.customer_layout.add_widget(Label(text=name))
            self.customer_layout.add_widget(Label(text=f"{balance:.2f}"))
    
    def export_to_excel(self, instance):
        self.cursor.execute("SELECT * FROM customers")
        customers = self.cursor.fetchall()
        df = pd.DataFrame(customers, columns=['ID', 'Name', 'Balance'])
        df.to_excel("customers.xlsx", index=False)
        self.status_label.text = "Customer data exported to customers.xlsx"
    
    def on_stop(self):
        self.conn.close()

if __name__ == "__main__":
    CustomerApp().run()
