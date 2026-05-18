"""Synthetic RCM Claims Data Generator.

Generates realistic healthcare claim denial data for the
RCM Claims Denial Intelligence Dashboard portfolio project.
"""
import csv
import random
import os
from datetime import date, timedelta

from faker import Faker

fake = Faker()
fake.seed_instance(42)
random.seed(42)

# ============================================================
# CONFIGURATION
# ============================================================
NUM_CLAIMS = 20_000
START_DATE = date(2024, 1, 1)
END_DATE = date(2025, 12, 31)
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "claims_data.csv")

# Date ranges for realistic service-to-billing-to-denial gaps
SERVICE_TO_BILLING_DAYS = (1, 14)
BILLING_TO_DENIAL_DAYS = (15, 60)
APPEAL_WINDOW_DAYS = (30, 180)
RECOVERY_AFTER_APPEAL_DAYS = (30, 120)

# Denial probability by payer type (approximate)
DENIAL_RATES = {
    "Commercial": 0.12,
    "Government": 0.20,
    "Managed Care": 0.08,
}

# Appeal probability for denied claims
APPEAL_RATE = 0.35

# Appeal success probability (recovery after appeal)
APPEAL_SUCCESS_RATE = 0.55

# Amount ranges
BILLED_AMOUNT_RANGE = (100, 25_000)
ALLOWED_PCT_RANGE = (0.55, 0.95)
PAYMENT_DAYS_RANGE = (7, 45)

# Seasonal fluctuation multiplier (Q4 = more denials)
SEASONAL_MULTIPLIER = {
    1: 0.90,   # Q1
    2: 0.85,   # Q2
    3: 0.95,   # Q3
    4: 1.30,   # Q4 - higher denials
}

# Department-level denial propensity multiplier
DEPARTMENT_DENIAL_FACTOR = {
    "Emergency Medicine": 1.3,
    "Cardiology": 1.0,
    "Orthopedics": 1.1,
    "Oncology": 0.8,
    "Neurology": 1.0,
    "General Surgery": 1.2,
    "Radiology": 0.7,
    "Laboratory": 0.5,
    "Physical Therapy": 0.9,
    "Internal Medicine": 1.0,
    "Pediatrics": 0.6,
    "OB/GYN": 0.8,
}

# ============================================================
# REFERENCE DATA - PAYERS
# ============================================================
PAYERS = [
    ("UnitedHealth Group", "Commercial", 0.14),
    ("Aetna", "Commercial", 0.12),
    ("Cigna", "Commercial", 0.11),
    ("Humana", "Commercial", 0.13),
    ("Blue Cross Blue Shield", "Commercial", 0.10),
    ("Medicare", "Government", 0.22),
    ("Medicaid", "Government", 0.25),
    ("Tricare", "Government", 0.18),
    ("Kaiser Permanente", "Managed Care", 0.09),
    ("Centene Corporation", "Managed Care", 0.08),
    ("Molina Healthcare", "Managed Care", 0.07),
    ("Anthem", "Commercial", 0.12),
]
PAYER_WEIGHTS = [p[2] for p in PAYERS]

# ============================================================
# REFERENCE DATA - DENIAL REASONS
# ============================================================
DENIAL_REASONS = [
    ("CO-97", "Service included in another procedure", "Coding", 0.15),
    ("CO-16", "Claim lacks information for adjudication", "Authorization", 0.13),
    ("CO-50", "Not medically necessary", "Medical Necessity", 0.12),
    ("CO-109", "Claim not covered by this payer", "Non-Covered", 0.10),
    ("CO-22", "Coordination of benefits required", "Coordination of Benefits", 0.08),
    ("CO-11", "Diagnosis inconsistent with procedure", "Coding", 0.07),
    ("CO-27", "Expenses incurred after coverage terminated", "Eligibility", 0.06),
    ("CO-45", "Charge exceeds fee schedule", "Coding", 0.06),
    ("CO-18", "Duplicate claim", "Duplicate", 0.05),
    ("CO-29", "Timely filing limit expired", "Timely Filing", 0.05),
    ("CO-151", "Payment adjusted - authorization absent", "Authorization", 0.05),
    ("CO-4", "Procedure code inconsistent with modifier", "Coding", 0.04),
    ("CO-252", "Attachment/other documentation required", "Authorization", 0.02),
    ("CO-96", "Non-covered charge", "Non-Covered", 0.02),
]
DENIAL_WEIGHTS = [r[3] for r in DENIAL_REASONS]

# ============================================================
# REFERENCE DATA - DEPARTMENTS & PROVIDERS
# ============================================================
DEPARTMENTS = [
    "Emergency Medicine", "Cardiology", "Orthopedics", "Oncology",
    "Neurology", "General Surgery", "Radiology", "Laboratory",
    "Physical Therapy", "Internal Medicine", "Pediatrics", "OB/GYN",
]

PROVIDERS = [
    ("Dr. James Wilson", "Emergency Medicine", "1528374910"),
    ("Dr. Maria Rodriguez", "Emergency Medicine", "1628395721"),
    ("Dr. Sarah Chen", "Cardiology", "1728311112"),
    ("Dr. Michael Patel", "Cardiology", "1828322223"),
    ("Dr. Robert Kim", "Orthopedics", "1928333334"),
    ("Dr. Lisa Thompson", "Orthopedics", "1028344445"),
    ("Dr. David Osei", "Oncology", "1128355556"),
    ("Dr. Angela Martinez", "Oncology", "1228366667"),
    ("Dr. John Nakamura", "Neurology", "1328377778"),
    ("Dr. Karen Hughes", "Neurology", "1428388889"),
    ("Dr. Thomas Becker", "General Surgery", "1528399990"),
    ("Dr. Patricia Li", "General Surgery", "1628300001"),
    ("Dr. Richard Barnes", "Radiology", "1728311113"),
    ("Dr. Jennifer Wu", "Radiology", "1828322224"),
    ("Dr. Steven Goldstein", "Radiology", "1928333335"),
    ("Dr. Elizabeth Cole", "Laboratory", "1028344446"),
    ("Dr. Daniel Park", "Laboratory", "1128355557"),
    ("Dr. Michelle Singh", "Physical Therapy", "1228366668"),
    ("Dr. Andrew Foster", "Physical Therapy", "1328377779"),
    ("Dr. Christopher Nkosi", "Internal Medicine", "1428388890"),
    ("Dr. Laura Delgado", "Internal Medicine", "1528399991"),
    ("Dr. William Tran", "Internal Medicine", "1628300002"),
    ("Dr. Emily Stewart", "Pediatrics", "1728311114"),
    ("Dr. Benjamin Grant", "Pediatrics", "1828322225"),
    ("Dr. Rachel O'Brien", "OB/GYN", "1928333336"),
    ("Dr. Kevin Sharma", "OB/GYN", "1028344447"),
    ("Dr. Nicole Johnson", "Emergency Medicine", "1128355558"),
    ("Dr. Mark Williams", "Cardiology", "1228366669"),
    ("Dr. Susan Davis", "Orthopedics", "1328377780"),
    ("Dr. Brian Nelson", "Oncology", "1428388891"),
    ("Dr. Amanda Clark", "Neurology", "1528399992"),
    ("Dr. Jason Nguyen", "General Surgery", "1628300003"),
    ("Dr. Heather Garcia", "Internal Medicine", "1728311115"),
    ("Dr. Frank Okonkwo", "Radiology", "1828322226"),
    ("Dr. Diana Flores", "Laboratory", "1928333337"),
    ("Dr. Alan Petrovic", "Physical Therapy", "1028344448"),
    ("Dr. Catherine Moss", "Pediatrics", "1128355559"),
    ("Dr. Edward Reeves", "OB/GYN", "1228366670"),
    ("Dr. Sandra Mitchell", "Emergency Medicine", "1328377781"),
    ("Dr. Joseph Achebe", "Cardiology", "1428388892"),
    ("Dr. Linda Yang", "Orthopedics", "1528399993"),
    ("Dr. George Carlson", "Oncology", "1628300004"),
    ("Dr. Barbara Holt", "Neurology", "1728311116"),
    ("Dr. Kenneth Brady", "General Surgery", "1828322227"),
    ("Dr. Melissa Ford", "Internal Medicine", "1928333338"),
    ("Dr. Ronald Hale", "Radiology", "1028344449"),
    ("Dr. Stephanie Cruz", "Laboratory", "1128355560"),
    ("Dr. Timothy Nash", "Physical Therapy", "1228366671"),
    ("Dr. Deborah Sutton", "Pediatrics", "1328377782"),
    ("Dr. Matthew Foley", "OB/GYN", "1428388893"),
]

# ============================================================
# HELPER FUNCTIONS
# ============================================================
def random_date(start: date, end: date) -> date:
    """Return a random date between start and end (inclusive)."""
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, delta))


def random_amount(low: float, high: float) -> float:
    """Return a random dollar amount rounded to 2 decimal places."""
    return round(random.uniform(low, high), 2)


def get_quarter(d: date) -> int:
    """Return the quarter (1-4) for a given date."""
    return (d.month - 1) // 3 + 1


def generate_claims(num_claims: int) -> list[dict]:
    """Generate a list of synthetic RCM claim records."""
    claims = []
    for i in range(1, num_claims + 1):
        claim_id = f"CLM-{i:06d}"
        patient_id = f"PT-{fake.unique.random_int(min=10000, max=99999)}"

        payer_idx = random.choices(range(len(PAYERS)), weights=PAYER_WEIGHTS, k=1)[0]
        payer_name, payer_type, _ = PAYERS[payer_idx]

        provider_name, department, npi = random.choice(PROVIDERS)

        service_date = random_date(START_DATE, END_DATE)
        billing_days = random.randint(*SERVICE_TO_BILLING_DAYS)
        billing_date = service_date + timedelta(days=billing_days)

        billed = random_amount(*BILLED_AMOUNT_RANGE)
        allowed_pct = random.uniform(*ALLOWED_PCT_RANGE)
        allowed = round(billed * allowed_pct, 2)

        base_denial_rate = DENIAL_RATES[payer_type]
        seasonal_factor = SEASONAL_MULTIPLIER[get_quarter(service_date)]
        dept_factor = DEPARTMENT_DENIAL_FACTOR.get(department, 1.0)
        adjusted_rate = min(base_denial_rate * seasonal_factor * dept_factor, 0.95)
        is_denied = random.random() < adjusted_rate

        payment_date = None
        denial_date = None
        denied_amount = 0.0
        recovered_amount = 0.0
        appeal_flag = 0
        recovery_date = None
        reason_code = None
        claim_status = "Paid"
        aging_days = 0

        if is_denied:
            denial_days = random.randint(*BILLING_TO_DENIAL_DAYS)
            denial_date = billing_date + timedelta(days=denial_days)

            reason_idx = random.choices(
                range(len(DENIAL_REASONS)), weights=DENIAL_WEIGHTS, k=1
            )[0]
            reason_code = DENIAL_REASONS[reason_idx][0]

            denied_amount = round(random.uniform(0.3, 1.0) * billed, 2)

            if random.random() < APPEAL_RATE:
                appeal_flag = 1
                claim_status = "Appealed"

                if random.random() < APPEAL_SUCCESS_RATE:
                    claim_status = "Recovered"
                    appeal_window = random.randint(*APPEAL_WINDOW_DAYS)
                    recovery_days = random.randint(*RECOVERY_AFTER_APPEAL_DAYS)
                    recovery_date = denial_date + timedelta(
                        days=appeal_window + recovery_days
                    )
                    recovered_amount = round(
                        random.uniform(0.50, 0.95) * denied_amount, 2
                    )
                    aging_days = (recovery_date - billing_date).days
                else:
                    claim_status = "Written Off"
                    aging_days = (date.today() - billing_date).days
            else:
                claim_status = "Denied"
                aging_days = (denial_date - billing_date).days
        else:
            payment_date = billing_date + timedelta(days=random.randint(*PAYMENT_DAYS_RANGE))
            aging_days = (payment_date - billing_date).days

        claims.append({
            "claim_id": claim_id,
            "patient_id": patient_id,
            "provider_name": provider_name,
            "department": department,
            "npi": npi,
            "payer_name": payer_name,
            "payer_type": payer_type,
            "reason_code": reason_code or "",
            "service_date": service_date.isoformat(),
            "billing_date": billing_date.isoformat(),
            "payment_date": payment_date.isoformat() if payment_date else "",
            "denial_date": denial_date.isoformat() if denial_date else "",
            "recovery_date": recovery_date.isoformat() if recovery_date else "",
            "billed_amount": billed,
            "allowed_amount": allowed,
            "denied_amount": denied_amount,
            "recovered_amount": recovered_amount,
            "claim_status": claim_status,
            "appeal_flag": appeal_flag,
            "aging_days": aging_days,
        })

    return claims


def write_csv(claims: list[dict], output_path: str) -> None:
    """Write claims data to CSV file."""
    fieldnames = [
        "claim_id", "patient_id", "provider_name", "department", "npi",
        "payer_name", "payer_type", "reason_code",
        "service_date", "billing_date", "payment_date", "denial_date", "recovery_date",
        "billed_amount", "allowed_amount", "denied_amount", "recovered_amount",
        "claim_status", "appeal_flag", "aging_days",
    ]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(claims)


def print_summary(claims: list[dict]) -> None:
    """Print summary statistics about the generated data."""
    total = len(claims)
    denied = sum(1 for c in claims if c["claim_status"] in (
        "Denied", "Appealed", "Recovered", "Written Off"
    ))
    recovered = sum(1 for c in claims if c["claim_status"] == "Recovered")
    total_denied_amount = sum(c["denied_amount"] for c in claims)
    total_recovered = sum(c["recovered_amount"] for c in claims)

    print(f"Total claims generated:     {total:,}")
    print(f"Denied claims:               {denied:,} ({denied/total*100:.1f}%)")
    print(f"Recovered claims:            {recovered:,} ({recovered/denied*100:.1f}% of denied)")
    print(f"Total denied amount:         ${total_denied_amount:,.2f}")
    print(f"Total recovered amount:      ${total_recovered:,.2f}")
    print(f"Net unrecovered:             ${total_denied_amount - total_recovered:,.2f}")


def main() -> None:
    """Entry point: generate claims and export to CSV."""
    print("Generating synthetic RCM claims data...")
    claims = generate_claims(NUM_CLAIMS)
    write_csv(claims, OUTPUT_PATH)
    print(f"\nSaved to: {OUTPUT_PATH}\n")
    print_summary(claims)


if __name__ == "__main__":
    main()
