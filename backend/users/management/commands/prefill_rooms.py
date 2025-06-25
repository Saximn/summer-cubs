from django.core.management.base import BaseCommand
from users.models import Room

class Command(BaseCommand):
    help = 'Prepopulates the Room model with A1-G7 for floors 1-5'

    def handle(self, *args, **kwargs):
        rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
        cols = range(1, 8)
        floors = range(1, 6)

        created = 0
        skipped = 0

        for floor in floors:
            for row in rows:
                for col in cols:
                    room_number = f"{row}{col}"

                    if not Room.objects.filter(room_number=room_number, floor=floor).exists():
                        Room.objects.create(
                            room_number=room_number,
                            floor=floor,
                            capacity=1
                        )
                        created += 1
                    else:
                        skipped += 1

        self.stdout.write(self.style.SUCCESS(f"✅ {created} new rooms created, {skipped} already existed."))
