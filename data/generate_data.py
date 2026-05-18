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
    ("Dr. James Wilson", "Emergency Medicine"),
    ("Dr. Maria Rodriguez", "Emergency Medicine"),
    ("Dr. Sarah Chen", "Cardiology"),
    ("Dr. Michael Patel", "Cardiology"),
    ("Dr. Robert Kim", "Orthopedics"),
    ("Dr. Lisa Thompson", "Orthopedics"),
    ("Dr. David Osei", "Oncology"),
    ("Dr. Angela Martinez", "Oncology"),
    ("Dr. John Nakamura", "Neurology"),
    ("Dr. Karen Hughes", "Neurology"),
    ("Dr. Thomas Becker", "General Surgery"),
    ("Dr. Patricia Li", "General Surgery"),
    ("Dr. Richard Barnes", "Radiology"),
    ("Dr. Jennifer Wu", "Radiology"),
    ("Dr. Steven Goldstein", "Radiology"),
    ("Dr. Elizabeth Cole", "Laboratory"),
    ("Dr. Daniel Park", "Laboratory"),
    ("Dr. Michelle Singh", "Physical Therapy"),
    ("Dr. Andrew Foster", "Physical Therapy"),
    ("Dr. Christopher Nkosi", "Internal Medicine"),
    ("Dr. Laura Delgado", "Internal Medicine"),
    ("Dr. William Tran", "Internal Medicine"),
    ("Dr. Emily Stewart", "Pediatrics"),
    ("Dr. Benjamin Grant", "Pediatrics"),
    ("Dr. Rachel O'Brien", "OB/GYN"),
    ("Dr. Kevin Sharma", "OB/GYN"),
    ("Dr. Nicole Johnson", "Emergency Medicine"),
    ("Dr. Mark Williams", "Cardiology"),
    ("Dr. Susan Davis", "Orthopedics"),
    ("Dr. Brian Nelson", "Oncology"),
    ("Dr. Amanda Clark", "Neurology"),
    ("Dr. Jason Nguyen", "General Surgery"),
    ("Dr. Heather Garcia", "Internal Medicine"),
    ("Dr. Frank Okonkwo", "Radiology"),
    ("Dr. Diana Flores", "Laboratory"),
    ("Dr. Alan Petrovic", "Physical Therapy"),
    ("Dr. Catherine Moss", "Pediatrics"),
    ("Dr. Edward Reeves", "OB/GYN"),
    ("Dr. Sandra Mitchell", "Emergency Medicine"),
    ("Dr. Joseph Achebe", "Cardiology"),
    ("Dr. Linda Yang", "Orthopedics"),
    ("Dr. George Carlson", "Oncology"),
    ("Dr. Barbara Holt", "Neurology"),
    ("Dr. Kenneth Brady", "General Surgery"),
    ("Dr. Melissa Ford", "Internal Medicine"),
    ("Dr. Ronald Hale", "Radiology"),
    ("Dr. Stephanie Cruz", "Laboratory"),
    ("Dr. Timothy Nash", "Physical Therapy"),
    ("Dr. Deborah Sutton", "Pediatrics"),
    ("Dr. Matthew Foley", "OB/GYN"),
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


def generate_claims(num_claims: int) -> list[dict]:
    """Generate a list of synthetic RCM claim records."""
    claims = []
    for i in range(1, num_claims + 1):
        claim_id = f"CLM-{i:06d}"
        patient_id = f"PT-{fake.unique.random_int(min=10000, max=99999)}"

        # Pick payer with weighted distribution
        payer_idx = random.choices(range(len(PAYERS)), weights=PAYER_WEIGHTS, k=1)[0]
        payer_name, payer_type, _ = PAYERS[payer_idx]

        # Pick provider (random uniform)
        provider_name, department = random.choice(PROVIDERS)

        # Dates
        service_date = random_date(START_DATE, END_DATE)
        billing_days = random.randint(*SERVICE_TO_BILLING_DAYS)
        billing_date = service_date + timedelta(days=billing_days)

        # Amounts
        billed = random_amount(*BILLED_AMOUNT_RANGE)
        allowed_pct = random.uniform(*ALLOWED_PCT_RANGE)
        allowed = round(billed * allowed_pct, 2)

        # Determine if denied based on payer type denial rate
        denial_rate = DENIAL_RATES[payer_type]
        is_denied = random.random() < denial_rate

        # Claim lifecycle
        denial_date = None
        denied_amount = 0.0
        recovered_amount = 0.0
        appeal_flag = 0
        recovery_date = None
        reason_code = None
        claim_status = "Paid"

        if is_denied:
            denial_days = random.randint(*BILLING_TO_DENIAL_DAYS)
            denial_date = billing_date + timedelta(days=denial_days)

            # Pick denial reason
            reason_idx = random.choices(
                range(len(DENIAL_REASONS)), weights=DENIAL_WEIGHTS, k=1
            )[0]
            reason_code = DENIAL_REASONS[reason_idx][0]

            denied_amount = round(random.uniform(0.3, 1.0) * billed, 2)

            # Appeal or not
            if random.random() < APPEAL_RATE:
                appeal_flag = 1
                claim_status = "Appealed"

                # Successful appeal = recovered
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
                else:
                    claim_status = "Written Off"
            else:
                claim_status = "Denied"

        claims.append({
            "claim_id": claim_id,
            "patient_id": patient_id,
            "provider_name": provider_name,
            "department": department,
            "payer_name": payer_name,
            "payer_type": payer_type,
            "reason_code": reason_code or "",
            "service_date": service_date.isoformat(),
            "billing_date": billing_date.isoformat(),
            "denial_date": denial_date.isoformat() if denial_date else "",
            "recovery_date": recovery_date.isoformat() if recovery_date else "",
            "billed_amount": billed,
            "allowed_amount": allowed,
            "denied_amount": denied_amount,
            "recovered_amount": recovered_amount,
            "claim_status": claim_status,
            "appeal_flag": appeal_flag,
        })

    return claims


def write_csv(claims: list[dict], output_path: str) -> None:
    """Write claims data to CSV file."""
    fieldnames = [
        "claim_id", "patient_id", "provider_name", "department",
        "payer_name", "payer_type", "reason_code",
        "service_date", "billing_date", "denial_date", "recovery_date",
        "billed_amount", "allowed_amount", "denied_amount", "recovered_amount",
        "claim_status", "appeal_flag",
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
