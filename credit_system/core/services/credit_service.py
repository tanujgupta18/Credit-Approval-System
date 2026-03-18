from core.models import Loan
from django.utils.timezone import now


def calculate_credit_score(customer):
  loans = Loan.objects.filter(customer=customer)

  if not loans.exists():
    return 50

  score = 0

  # on-time payments
  for loan in loans:
    score += loan.emis_paid_on_time

  # number of loans
  score -= loans.count() * 2

  # current year loans
  current_year = now().year
  for loan in loans:
    if loan.start_date.year == current_year:
      score += 5

  # total loan amount
  total_amount = sum([loan.loan_amount for loan in loans])
  if total_amount > customer.approved_limit:
    score -= 20
  else:
    score += 20

  # Hard rule
  if customer.current_debt > customer.approved_limit:
      return 0

  # limit 0–100
  return max(0, min(score, 100))


def calculate_emi(amount, rate, tenure):
  if rate == 0:
    return round(amount / tenure, 2)
  r = rate / (12 * 100)
  emi = (amount * r * (1 + r) ** tenure) / ((1 + r) ** tenure - 1)
  return round(emi, 2)


def check_eligibility(customer, amount, rate, tenure):
  score = calculate_credit_score(customer)
  emi = calculate_emi(amount, rate, tenure)

  # EMI rule
  if emi > 0.5 * customer.monthly_salary:
    return False, rate, emi

  # approval
  if score > 50:
    return True, rate, emi

  elif score > 30:
    return True, max(rate, 12), emi

  elif score > 10:
    return True, max(rate, 16), emi

  else:
    return False, rate, emi