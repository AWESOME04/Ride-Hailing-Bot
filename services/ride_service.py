from models.ride import Ride
from config import db
import random
from datetime import datetime

class RideService:
    RIDE_TYPES = {
        '1': {'name': 'Standard', 'base_fare': 10, 'per_km': 1.5},
        '2': {'name': 'Premium', 'base_fare': 15, 'per_km': 2.0},
        '3': {'name': 'XL', 'base_fare': 20, 'per_km': 2.5}
    }

    DRIVER_NAMES = [
        ('John Smith', 'Toyota Camry', 'GR 1234-20'),
        ('Sarah Johnson', 'Honda Civic', 'GW 5678-21'),
        ('Michael Brown', 'Hyundai Sonata', 'GE 9012-22'),
        ('Emma Davis', 'Kia K5', 'GC 3456-23'),
        ('James Wilson', 'Volkswagen Passat', 'GT 7890-24')
    ]

    @staticmethod
    def create_ride(user_hashed_id, pickup_location, destination, ride_type):
        try:
            distance = random.uniform(5, 20)
            ride_info = RideService.RIDE_TYPES[ride_type]
            estimated_fare = ride_info['base_fare'] + (ride_info['per_km'] * distance)

            ride = Ride(
                user_hashed_id=user_hashed_id,
                pickup_location=pickup_location,
                destination=destination,
                ride_type=ride_info['name'],
                status='REQUESTED',
                estimated_fare=round(estimated_fare, 2)
            )
            db.session.add(ride)
            db.session.commit()
            return True, ride
        except Exception as e:
            db.session.rollback()
            return False, str(e)

    @staticmethod
    def match_driver(ride):
        try:
            driver_name, car_model, car_number = random.choice(RideService.DRIVER_NAMES)
            driver_phone = f"057{random.randint(1000000, 9999999)}"
            
            ride.status = 'MATCHED'
            ride.driver_name = driver_name
            ride.driver_phone = driver_phone
            ride.car_model = car_model
            ride.car_number = car_number
            ride.updated_at = datetime.utcnow()
            
            db.session.commit()
            return True, ride
        except Exception as e:
            db.session.rollback()
            return False, str(e)

    @staticmethod
    def update_ride_status(ride, status):
        try:
            ride.status = status
            ride.updated_at = datetime.utcnow()
            db.session.commit()
            return True, ride
        except Exception as e:
            db.session.rollback()
            return False, str(e)

    @staticmethod
    def get_active_ride(user_hashed_id):
        return Ride.query.filter(
            Ride.user_hashed_id == user_hashed_id,
            Ride.status.in_(['REQUESTED', 'MATCHED', 'ARRIVED', 'IN_PROGRESS'])
        ).first()

    @staticmethod
    def get_estimated_arrival_time():
        return random.randint(3, 15)