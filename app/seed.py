from app.core.database import SessionLocal
from app.models.bank import Bank
from app.models.branch import Branch
from app.models.banking_service import BankingService


def seed_database():
    db = SessionLocal()

    try:
        # Prevent duplicate seed data
        if db.query(Bank).first():
            print("Database already contains banks. Skipping seed.")
            return

        # -------------------------
        # Banks
        # -------------------------

        banks = [
            Bank(
                name="NAIJA Demo Bank",
                code="NDB",
            ),
            Bank(
                name="Lagos Commercial Bank",
                code="LCB",
            ),
            Bank(
                name="Unity Finance Bank",
                code="UFB",
            ),
        ]

        db.add_all(banks)
        db.flush()

        # -------------------------
        # Banking Services
        # -------------------------

        services = [
            BankingService(
                code="PERSONAL_ACCOUNT",
                name="Personal Account Opening",
                description="Open a new personal bank account.",
                category="ACCOUNT_OPENING",
                requires_appointment=True,
                requires_kyc=True,
            ),
            BankingService(
                code="BUSINESS_ACCOUNT",
                name="Business Account Opening",
                description="Open a bank account for a registered business.",
                category="ACCOUNT_OPENING",
                requires_appointment=True,
                requires_kyc=True,
            ),
            BankingService(
                code="BVN_UPDATE",
                name="BVN Update",
                description="Update or resolve BVN-related information.",
                category="KYC",
                requires_appointment=True,
                requires_kyc=True,
            ),
            BankingService(
                code="NIN_UPDATE",
                name="NIN Update",
                description="Update NIN-related customer information.",
                category="KYC",
                requires_appointment=True,
                requires_kyc=True,
            ),
            BankingService(
                code="CARD_REPLACEMENT",
                name="Debit Card Replacement",
                description="Replace a lost, damaged or expired debit card.",
                category="CARDS",
                requires_appointment=True,
                requires_kyc=True,
            ),
            BankingService(
                code="ACCOUNT_UPGRADE",
                name="Account Upgrade",
                description="Upgrade an existing bank account.",
                category="ACCOUNT",
                requires_appointment=True,
                requires_kyc=True,
            ),
            BankingService(
                code="LOAN_CONSULTATION",
                name="Loan Consultation",
                description="Speak with a banking officer about loan options.",
                category="LENDING",
                requires_appointment=True,
                requires_kyc=False,
            ),
            BankingService(
                code="SME_BANKING",
                name="SME Banking",
                description="Get support for small and medium business banking.",
                category="BUSINESS",
                requires_appointment=True,
                requires_kyc=True,
            ),
        ]

        db.add_all(services)
        db.flush()

        # -------------------------
        # Branches
        # -------------------------

        branches = [
            Branch(
                bank_id=banks[0].id,
                name="Ikeja Main Branch",
                address="12 Allen Avenue",
                city="Ikeja",
                state="Lagos",
                latitude=6.6018,
                longitude=3.3515,
                phone="+2348000001001",
            ),
            Branch(
                bank_id=banks[0].id,
                name="Lekki Phase 1 Branch",
                address="18 Admiralty Way",
                city="Lekki",
                state="Lagos",
                latitude=6.4474,
                longitude=3.4722,
                phone="+2348000001002",
            ),
            Branch(
                bank_id=banks[0].id,
                name="Victoria Island Branch",
                address="25 Ahmadu Bello Way",
                city="Victoria Island",
                state="Lagos",
                latitude=6.4281,
                longitude=3.4219,
                phone="+2348000001003",
            ),
            Branch(
                bank_id=banks[1].id,
                name="Yaba Branch",
                address="42 Herbert Macaulay Way",
                city="Yaba",
                state="Lagos",
                latitude=6.5158,
                longitude=3.3895,
                phone="+2348000002001",
            ),
            Branch(
                bank_id=banks[1].id,
                name="Surulere Branch",
                address="15 Adeniran Ogunsanya Street",
                city="Surulere",
                state="Lagos",
                latitude=6.4969,
                longitude=3.3599,
                phone="+2348000002002",
            ),
            Branch(
                bank_id=banks[2].id,
                name="Lagos Island Branch",
                address="10 Marina Road",
                city="Lagos Island",
                state="Lagos",
                latitude=6.4541,
                longitude=3.3947,
                phone="+2348000003001",
            ),
            Branch(
                bank_id=banks[2].id,
                name="Maryland Branch",
                address="8 Ikorodu Road",
                city="Maryland",
                state="Lagos",
                latitude=6.5730,
                longitude=3.3670,
                phone="+2348000003002",
            ),
        ]

        db.add_all(branches)

        db.commit()

        print("NAIJA database seeded successfully.")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_database()