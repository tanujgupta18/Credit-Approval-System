from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Customer, Loan
from .services.credit_service import check_eligibility


# Register Customer
@api_view(['POST'])
def register(request):
    data = request.data

    approved_limit = round((36 * data['monthly_salary']), -5)

    customer = Customer.objects.create(
        first_name=data['first_name'],
        last_name=data['last_name'],
        age=data['age'],
        phone_number=data['phone_number'],
        monthly_salary=data['monthly_salary'],
        approved_limit=approved_limit,
        current_debt=0
    )

    return Response({
        "customer_id": customer.customer_id,
        "name": f"{customer.first_name} {customer.last_name}",
        "age": customer.age,
        "monthly_income": customer.monthly_salary,
        "approved_limit": customer.approved_limit,
        "phone_number": customer.phone_number
    })


# Check Eligibility
@api_view(['POST'])
def check_eligibility_api(request):
    data = request.data

    try:
        customer = Customer.objects.get(customer_id=data['customer_id'])
    except Customer.DoesNotExist:
        return Response({"error": "Customer not found"}, status=404)

    approved, corrected_rate, emi = check_eligibility(
        customer,
        data['loan_amount'],
        data['interest_rate'],
        data['tenure']
    )

    return Response({
        "customer_id": customer.customer_id,
        "approval": approved,
        "interest_rate": data['interest_rate'],
        "corrected_interest_rate": corrected_rate,
        "tenure": data['tenure'],
        "monthly_installment": emi
    })


# Create Loan
@api_view(['POST'])
def create_loan(request):
    data = request.data

    try:
        customer = Customer.objects.get(customer_id=data['customer_id'])
    except Customer.DoesNotExist:
        return Response({"error": "Customer not found"}, status=404)

    approved, corrected_rate, emi = check_eligibility(
        customer,
        data['loan_amount'],
        data['interest_rate'],
        data['tenure']
    )

    if not approved:
        return Response({
            "loan_id": None,
            "customer_id": customer.customer_id,
            "loan_approved": False,
            "message": "Loan not approved",
            "monthly_installment": emi
        })

    loan = Loan.objects.create(
        customer=customer,
        loan_amount=data['loan_amount'],
        tenure=data['tenure'],
        interest_rate=corrected_rate,
        monthly_installment=emi,
        start_date="2025-01-01",
        end_date="2026-01-01"
    )

    return Response({
        "loan_id": loan.loan_id,
        "customer_id": customer.customer_id,
        "loan_approved": True,
        "message": "Loan approved",
        "monthly_installment": emi
    })


# View Loan
@api_view(['GET'])
def view_loan(request, loan_id):
    try:
        loan = Loan.objects.get(loan_id=loan_id)
    except Loan.DoesNotExist:
        return Response({"error": "Loan not found"}, status=404)

    return Response({
        "loan_id": loan.loan_id,
        "customer": {
            "id": loan.customer.customer_id,
            "first_name": loan.customer.first_name,
            "last_name": loan.customer.last_name,
            "phone_number": loan.customer.phone_number,
            "age": loan.customer.age
        },
        "loan_amount": loan.loan_amount,
        "interest_rate": loan.interest_rate,
        "monthly_installment": loan.monthly_installment,
        "tenure": loan.tenure
    })


# View Loans by Customer
@api_view(['GET'])
def view_loans(request, customer_id):
    loans = Loan.objects.filter(customer_id=customer_id)

    data = []
    for loan in loans:
        data.append({
            "loan_id": loan.loan_id,
            "loan_amount": loan.loan_amount,
            "interest_rate": loan.interest_rate,
            "monthly_installment": loan.monthly_installment,
            "repayments_left": loan.tenure - loan.emis_paid_on_time
        })

    return Response(data)