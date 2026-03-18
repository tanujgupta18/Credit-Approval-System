import pandas as pd
from django.core.management.base import BaseCommand
from core.models import Customer, Loan


class Command(BaseCommand):
    help = "Load data from Excel files"

    def handle(self, *args, **kwargs):
        # Load customers
        customer_df = pd.read_excel('customer_data.xlsx')
        customer_df.columns = customer_df.columns.str.strip().str.lower().str.replace(" ", "_")
        
        for _, row in customer_df.iterrows():
            Customer.objects.update_or_create(
                customer_id=row['customer_id'],
                defaults={
                    "first_name": row['first_name'],
                    "last_name": row['last_name'],
                    "phone_number": str(row['phone_number']),
                    "monthly_salary": row['monthly_salary'],
                    "approved_limit": row['approved_limit'],
                    "current_debt": 0,
                    "age": row["age"]
                }
            )

        self.stdout.write(self.style.SUCCESS("Customers loaded"))

        # Load loans
        loan_df = pd.read_excel('loan_data.xlsx')
        loan_df.columns = loan_df.columns.str.strip().str.lower().str.replace(" ","_")

        for _, row in loan_df.iterrows():
            try:
                customer = Customer.objects.get(customer_id=row['customer_id'])

                Loan.objects.update_or_create(
                    loan_id=row['loan_id'],
                    defaults={
                        "customer": customer,
                        "loan_amount": row['loan_amount'],
                        "tenure": row['tenure'],
                        "interest_rate": row['interest_rate'],
                        "monthly_installment": row['monthly_payment'],
                        "emis_paid_on_time": row['emis_paid_on_time'],
                        "start_date": row['date_of_approval'],
                        "end_date": row['end_date'],
                    }
                )
            except Customer.DoesNotExist:
                continue

        self.stdout.write(self.style.SUCCESS("Loans loaded"))