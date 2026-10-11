import random
import uuid


from .schemas import TransactionInput

CATEGORIES = [
    "grocery",
    "electronics",
    "travel",
    "restaurant",
    "fuel",
    "online",
]

def generate_transaction():
    return TransactionInput(
        amount=round(
            random.lognormvariate(
                7.0,
                1.0
            ),
            2
        ),
        merchant_category=random.choice(
            CATEGORIES
        ),

        device_novelty=random.choice([
            0,
            0,
            0,
            0,
            1
        ]),

        location_deviation=round(
            random.random(),
            2
        ),

        transaction_velocity=random.randint(
            1,
            10
        ),

        unusual_time=random.choice([
            0,
            0,
            0,
            1
        ])
    )