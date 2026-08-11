from datetime import datetime, timedelta

from app.core.database import SessionLocal
from app.models import Branch, BankingService, AppointmentSlot


def seed_slots():
    db = SessionLocal()

    try:
        if db.query(AppointmentSlot).first():
            print("Appointment slots already exist. Skipping.")
            return

        branches = db.query(Branch).filter(Branch.active == True).all()
        services = (
            db.query(BankingService)
            .filter(
                BankingService.active == True,
                BankingService.requires_appointment == True,
            )
            .all()
        )

        today = datetime.now().replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        )

        slots = []

        # Generate slots for the next 7 days
        for day_offset in range(1, 8):
            day = today + timedelta(days=day_offset)

            # Monday-Friday
            if day.weekday() >= 5:
                continue

            # 9:00 AM - 3:00 PM
            for hour in range(9, 15):
                start_time = day.replace(
                    hour=hour,
                    minute=0,
                )

                end_time = start_time + timedelta(
                    minutes=30
                )

                for branch in branches:
                    for service in services:
                        slots.append(
                            AppointmentSlot(
                                branch_id=branch.id,
                                service_id=service.id,
                                start_time=start_time,
                                end_time=end_time,
                                is_booked=False,
                            )
                        )

        db.add_all(slots)
        db.commit()

        print(f"Created {len(slots)} appointment slots.")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_slots()