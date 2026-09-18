import pytest
from datetime import datetime, timedelta
from app import create_app
from app.extensions import db
from app.models.user import User, Organization, UserRole
from app.models.food_listing import FoodListing, FoodCategory, FoodListingStatus, DietaryType
from app.models.reservation import Reservation, ReservationStatus
from app.services.expiration_service import process_expired_listings
from app.services.impact_service import get_impact_summary

@pytest.fixture
def app():
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        # Seed basic category
        cat = FoodCategory(name="Cooked Meals", default_dietary=DietaryType.VEGETARIAN)
        db.session.add(cat)
        db.session.commit()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def test_auth_and_registration(client):
    # Register Provider
    res = client.post("/api/auth/register", json={
        "name": "Test Chef",
        "email": "chef@test.com",
        "password": "password123",
        "role": "provider",
        "organization_name": "Test Kitchen",
        "city": "Chandigarh"
    })
    assert res.status_code == 201
    data = res.get_json()
    assert "token" in data
    assert data["user"]["role"] == "provider"

    # Login
    login_res = client.post("/api/auth/login", json={
        "email": "chef@test.com",
        "password": "password123"
    })
    assert login_res.status_code == 200
    token = login_res.get_json()["token"]
    assert token is not None

    # Get Me
    me_res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_res.status_code == 200
    assert me_res.get_json()["user"]["email"] == "chef@test.com"


def test_food_listing_and_concurrency_reservation(client):
    # 1. Register Provider
    p_res = client.post("/api/auth/register", json={
        "name": "Provider One",
        "email": "provider1@test.com",
        "password": "password123",
        "role": "provider"
    })
    p_token = p_res.get_json()["token"]

    # 2. Register Recipient
    r_res = client.post("/api/auth/register", json={
        "name": "Recipient NGO",
        "email": "ngo@test.com",
        "password": "password123",
        "role": "recipient"
    })
    r_token = r_res.get_json()["token"]

    # 3. Create Food Listing (50 portions)
    now = datetime.utcnow()
    create_res = client.post("/api/food", headers={"Authorization": f"Bearer {p_token}"}, json={
        "title": "Fresh Veg Biryani",
        "category_id": 1,
        "dietary_type": "VEGETARIAN",
        "quantity": 50,
        "unit": "portions",
        "location": "Sector 17 Canteen",
        "city": "Chandigarh",
        "expiry_time": (now + timedelta(hours=3)).isoformat(),
        "pickup_start": now.isoformat(),
        "pickup_end": (now + timedelta(hours=2)).isoformat()
    })
    assert create_res.status_code == 201
    listing_id = create_res.get_json()["listing"]["id"]

    # 4. First reservation: reserve 20 portions
    res1 = client.post(f"/api/food/{listing_id}/reserve", headers={"Authorization": f"Bearer {r_token}"}, json={
        "quantity": 20,
        "notes": "Will pick up by noon"
    })
    assert res1.status_code == 201
    assert res1.get_json()["remaining_quantity"] == 30
    assert res1.get_json()["listing_status"] == FoodListingStatus.PARTIALLY_RESERVED
    res1_id = res1.get_json()["reservation"]["id"]

    # 5. Over-reservation attempt: trying to reserve 35 when only 30 remain -> Must reject with 409
    res_fail = client.post(f"/api/food/{listing_id}/reserve", headers={"Authorization": f"Bearer {r_token}"}, json={
        "quantity": 35
    })
    assert res_fail.status_code == 409
    assert res_fail.get_json()["remaining_quantity"] == 30

    # 6. Exact remaining reservation: reserve remaining 30 portions -> status becomes FULLY_RESERVED
    res2 = client.post(f"/api/food/{listing_id}/reserve", headers={"Authorization": f"Bearer {r_token}"}, json={
        "quantity": 30
    })
    assert res2.status_code == 201
    assert res2.get_json()["remaining_quantity"] == 0
    assert res2.get_json()["listing_status"] == FoodListingStatus.FULLY_RESERVED

    # 7. Cancel first reservation (20 portions) -> remaining restored to 20, status returns to PARTIALLY_RESERVED
    cancel_res = client.put(f"/api/reservations/{res1_id}/cancel", headers={"Authorization": f"Bearer {r_token}"})
    assert cancel_res.status_code == 200
    assert cancel_res.get_json()["remaining_quantity"] == 20


def test_automatic_expiration_engine(app):
    with app.app_context():
        # Create expired listing
        now = datetime.utcnow()
        user = User(name="Chef", email="chef_expire@test.com", role=UserRole.PROVIDER)
        user.set_password("pass")
        db.session.add(user)
        db.session.flush()

        listing = FoodListing(
            provider_id=user.id,
            category_id=1,
            title="Yesterday Stew",
            quantity=20,
            remaining_quantity=20,
            location="Kitchen",
            city="Chandigarh",
            expiry_time=now - timedelta(hours=1),  # Expired in past
            pickup_start=now - timedelta(hours=2),
            pickup_end=now - timedelta(hours=1),
            status=FoodListingStatus.AVAILABLE
        )
        db.session.add(listing)
        db.session.commit()

        # Run expiration service
        result = process_expired_listings()
        assert result["expired_listings"] == 1

        # Verify status in database
        updated = FoodListing.query.get(listing.id)
        assert updated.status == FoodListingStatus.EXPIRED


def test_pickup_and_impact_metrics(client, app):
    # 1. Register users
    p_res = client.post("/api/auth/register", json={
        "name": "Bakery Chef",
        "email": "baker@test.com",
        "password": "password123",
        "role": "provider"
    })
    p_token = p_res.get_json()["token"]

    r_res = client.post("/api/auth/register", json={
        "name": "Community Foodbank",
        "email": "foodbank@test.com",
        "password": "password123",
        "role": "recipient"
    })
    r_token = r_res.get_json()["token"]

    # 2. Create listing
    now = datetime.utcnow()
    create_res = client.post("/api/food", headers={"Authorization": f"Bearer {p_token}"}, json={
        "title": "Fresh Multigrain Breads",
        "category_id": 1,
        "dietary_type": "BAKERY",
        "quantity": 40,
        "unit": "loaves",
        "location": "Bakery Counter",
        "city": "Chandigarh",
        "expiry_time": (now + timedelta(hours=4)).isoformat(),
        "pickup_start": now.isoformat(),
        "pickup_end": (now + timedelta(hours=3)).isoformat()
    })
    listing_id = create_res.get_json()["listing"]["id"]

    # 3. Reserve all 40 loaves
    res = client.post(f"/api/food/{listing_id}/reserve", headers={"Authorization": f"Bearer {r_token}"}, json={
        "quantity": 40
    })
    res_id = res.get_json()["reservation"]["id"]
    pickup_code = res.get_json()["reservation"]["pickup_code"]

    # 4. Provider approves reservation
    appr_res = client.put(f"/api/reservations/{res_id}/approve", headers={"Authorization": f"Bearer {p_token}"})
    assert appr_res.status_code == 200

    # 5. Confirm pickup using valid code
    pickup_res = client.put(f"/api/reservations/{res_id}/pickup", headers={"Authorization": f"Bearer {p_token}"}, json={
        "pickup_code": pickup_code,
        "notes": "Collected on time"
    })
    assert pickup_res.status_code == 200
    assert pickup_res.get_json()["reservation"]["status"] == ReservationStatus.COMPLETED

    # 6. Query Impact API
    impact_res = client.get("/api/analytics/impact")
    assert impact_res.status_code == 200
    impact_data = impact_res.get_json()
    assert impact_data["meals_rescued"] == 40
    # 40 * 2.5 kg = 100.0 kg CO2 saved!
    assert impact_data["carbon_saved_kg"] == 100.0
