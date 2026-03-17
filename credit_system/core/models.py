from django.db import models


# Customer Model
class Customer(models.Model):
    customer_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    age = models.IntegerField()
    phone_number = models.CharField(max_length=15)
    monthly_salary = models.IntegerField()
    approved_limit = models.IntegerField()
    current_debt = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


# Loan Model
class Loan(models.Model):
    loan_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="loans")
    
    loan_amount = models.FloatField()
    tenure = models.IntegerField()  # months
    interest_rate = models.FloatField()
    monthly_installment = models.FloatField()

    emis_paid_on_time = models.IntegerField(default=0)

    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return f"Loan {self.loan_id} - {self.customer.first_name}"