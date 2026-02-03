from django.core.management.base import BaseCommand
from faker import Faker
from api.models import Product
import random
from decimal import Decimal

class Command(BaseCommand):
    help = "Generate fake data for load test"

    def handle(self, *args, **kwargs):
        fake = Faker()

        for _ in range(10000):
            Product.objects.create(
                name=fake.word(),
                description=fake.text(),
                price=Decimal(f"{random.uniform(10, 500):.2f}"),
                stock=random.randint(10, 20),
            )

        self.stdout.write(self.style.SUCCESS("Fake data created successfully!"))
