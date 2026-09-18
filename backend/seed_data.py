from datetime import datetime, timedelta, date
from app import create_app
from app.extensions import db
from app.models.user import User, Organization, UserRole, UserPreference
from app.models.food_listing import FoodListing, FoodCategory, FoodListingStatus, DietaryType
from app.models.reservation import Reservation, ReservationStatus, Pickup, generate_pickup_code
from app.models.notification import Notification, NotificationType
from app.models.impact import ImpactRecord

def seed_database():
    app = create_app()
    with app.app_context():
        print("Cleaning and recreating database schema...")
        db.drop_all()
        db.create_all()

        print("1. Seeding Food Categories...")
        categories = [
            FoodCategory(name="Cooked Meals", description="Warm cooked lunches, dinners, and buffet trays", icon="Utensils", default_dietary=DietaryType.VEGETARIAN),
            FoodCategory(name="Bakery & Bread", description="Fresh bread loaves, baguettes, buns, and breakfast rolls", icon="Croissant", default_dietary=DietaryType.BAKERY),
            FoodCategory(name="Vegetarian Special", description="Pure vegetarian thalis, salads, and vegetable preparations", icon="Salad", default_dietary=DietaryType.VEGETARIAN),
            FoodCategory(name="Non-Vegetarian Dishes", description="Chicken, meat, and seafood preparations", icon="Drumstick", default_dietary=DietaryType.NON_VEGETARIAN),
            FoodCategory(name="Vegan Bowls & Greens", description="Plant-based meals, leafy greens, and grain salads", icon="Sprout", default_dietary=DietaryType.VEGAN),
            FoodCategory(name="Packaged & Canned", description="Unopened grocery items, cereals, milk cartons, and canned soups", icon="Package", default_dietary=DietaryType.VEGETARIAN),
            FoodCategory(name="Fresh Produce", description="Surplus fruits, vegetables, and farmers market overflow", icon="Apple", default_dietary=DietaryType.VEGAN),
        ]
        db.session.add_all(categories)
        db.session.flush()

        print("2. Seeding Organizations...")
        org_canteen = Organization(
            name="University Central Canteen",
            org_type="canteen",
            description="Main campus cafeteria serving 3,000+ students daily.",
            address="Block 3, University Campus",
            city="Chandigarh",
            contact_person="Ramesh Verma",
            phone="+91 98765 43210",
            email="canteen@foodrescue.org",
            is_verified=True
        )
        org_bakery = Organization(
            name="Golden Crust Artisan Bakery",
            org_type="bakery",
            description="Local bakery producing fresh artisanal breads and pastries.",
            address="Booth 45, Sector 17-C",
            city="Chandigarh",
            contact_person="Anita Sen",
            phone="+91 98123 45678",
            email="bakery@foodrescue.org",
            is_verified=True
        )
        org_restaurant = Organization(
            name="Saffron Spice Royal Dining",
            org_type="restaurant",
            description="Fine dining North Indian restaurant.",
            address="SCO 112, Phase 7",
            city="Mohali",
            contact_person="Vikram Singh",
            phone="+91 98456 78901",
            email="saffron@foodrescue.org",
            is_verified=True
        )
        org_shelter = Organization(
            name="Hope Community Shelter",
            org_type="shelter",
            description="Night shelter providing warm beds and hot meals for homeless individuals.",
            address="Sector 25 West",
            city="Chandigarh",
            contact_person="Sister Mary",
            phone="+91 98999 11223",
            email="shelter@foodrescue.org",
            is_verified=True
        )
        org_ngo = Organization(
            name="Robin Hood Food Army",
            org_type="ngo",
            description="Volunteer-driven organization serving surplus food to disadvantaged communities.",
            address="SCF 88, Sector 34",
            city="Chandigarh",
            contact_person="Deepak Kumar",
            phone="+91 97777 88990",
            email="ngo@foodrescue.org",
            is_verified=True
        )

        db.session.add_all([org_canteen, org_bakery, org_restaurant, org_shelter, org_ngo])
        db.session.flush()

        print("3. Seeding Users...")
        admin_user = User(
            name="FoodRescue System Admin",
            email="admin@foodrescue.org",
            role=UserRole.ADMIN,
            phone="+91 90000 00000",
            address="FoodRescue HQ, Tech Park",
            city="Chandigarh",
            is_active=True,
            is_verified=True
        )
        admin_user.set_password("admin123")

        provider_canteen = User(
            name="Ramesh Verma",
            email="canteen@foodrescue.org",
            role=UserRole.PROVIDER,
            phone="+91 98765 43210",
            address="Block 3, Campus",
            city="Chandigarh",
            organization_id=org_canteen.id,
            is_active=True,
            is_verified=True
        )
        provider_canteen.set_password("provider123")

        provider_bakery = User(
            name="Anita Sen",
            email="bakery@foodrescue.org",
            role=UserRole.PROVIDER,
            phone="+91 98123 45678",
            address="Booth 45, Sector 17-C",
            city="Chandigarh",
            organization_id=org_bakery.id,
            is_active=True,
            is_verified=True
        )
        provider_bakery.set_password("provider123")

        recipient_shelter = User(
            name="Sister Mary (Hope Shelter)",
            email="shelter@foodrescue.org",
            role=UserRole.RECIPIENT,
            phone="+91 98999 11223",
            address="Sector 25 West",
            city="Chandigarh",
            organization_id=org_shelter.id,
            is_active=True,
            is_verified=True
        )
        recipient_shelter.set_password("recipient123")

        recipient_ngo = User(
            name="Deepak Kumar (Robin Hood Army)",
            email="ngo@foodrescue.org",
            role=UserRole.RECIPIENT,
            phone="+91 97777 88990",
            address="Sector 34",
            city="Chandigarh",
            organization_id=org_ngo.id,
            is_active=True,
            is_verified=True
        )
        recipient_ngo.set_password("recipient123")

        db.session.add_all([admin_user, provider_canteen, provider_bakery, recipient_shelter, recipient_ngo])
        db.session.flush()

        # Recipient preferences
        pref1 = UserPreference(
            user_id=recipient_shelter.id,
            preferred_category_ids=[categories[0].id, categories[2].id],
            city="Chandigarh",
            dietary_filter="VEGETARIAN",
            notify_new_listings=True
        )
        pref2 = UserPreference(
            user_id=recipient_ngo.id,
            preferred_category_ids=[categories[0].id, categories[1].id, categories[3].id],
            city="Chandigarh",
            dietary_filter="all",
            notify_new_listings=True
        )
        db.session.add_all([pref1, pref2])
        db.session.flush()

        print("4. Seeding Food Listings...")
        now = datetime.utcnow()

        # Active Listing 1: Canteen Veg Pulav & Dal
        listing1 = FoodListing(
            provider_id=provider_canteen.id,
            organization_id=org_canteen.id,
            category_id=categories[0].id,
            title="Fresh Vegetable Pulav & Yellow Dal Tadka",
            description="Hot, freshly prepared vegetable pulav cooked in pure ghee accompanied by tempered yellow dal. Packed cleanly in thermal catering containers.",
            dietary_type=DietaryType.VEGETARIAN,
            allergen_info="Dairy (Ghee). Nut-free.",
            quantity=50,
            remaining_quantity=30,  # 20 reserved
            unit="portions",
            prepared_at=now - timedelta(hours=2),
            expiry_time=now + timedelta(hours=3, minutes=30),
            pickup_start=now + timedelta(minutes=30),
            pickup_end=now + timedelta(hours=3),
            location="Gate No. 2, Campus Cafeteria, Chandigarh",
            city="Chandigarh",
            status=FoodListingStatus.PARTIALLY_RESERVED
        )

        # Active Listing 2: Bakery Bread & Croissants
        listing2 = FoodListing(
            provider_id=provider_bakery.id,
            organization_id=org_bakery.id,
            category_id=categories[1].id,
            title="Artisanal Sourdough & Multigrain Loaves",
            description="Crisp baked artisan sourdough loaves and sweet butter croissants prepared today morning. Sealed in food-grade bakery bags.",
            dietary_type=DietaryType.BAKERY,
            allergen_info="Gluten, Yeast, Dairy (Butter).",
            quantity=35,
            remaining_quantity=35,
            unit="items",
            prepared_at=now - timedelta(hours=4),
            expiry_time=now + timedelta(hours=5),
            pickup_start=now + timedelta(minutes=15),
            pickup_end=now + timedelta(hours=4, minutes=30),
            location="Booth 45, Sector 17-C, Chandigarh",
            city="Chandigarh",
            status=FoodListingStatus.AVAILABLE
        )

        # Active Listing 3: Paneer Butter Masala & Naan
        listing3 = FoodListing(
            provider_id=provider_canteen.id,
            organization_id=org_canteen.id,
            category_id=categories[2].id,
            title="Shahi Paneer Curry & Butter Roti Thali",
            description="Cottage cheese cubes simmered in rich tomato cashew gravy, served with soft butter rotis. Excess banquet lunch preparation.",
            dietary_type=DietaryType.VEGETARIAN,
            allergen_info="Contains Dairy, Cashew nuts.",
            quantity=40,
            remaining_quantity=40,
            unit="meals",
            prepared_at=now - timedelta(hours=1),
            expiry_time=now + timedelta(hours=2, minutes=45),
            pickup_start=now + timedelta(minutes=20),
            pickup_end=now + timedelta(hours=2, minutes=30),
            location="University Guest House Kitchen, Chandigarh",
            city="Chandigarh",
            status=FoodListingStatus.AVAILABLE
        )

        # Active Listing 4: Vegan Fruit & Salad Trays
        listing4 = FoodListing(
            provider_id=provider_bakery.id,
            organization_id=org_bakery.id,
            category_id=categories[4].id,
            title="Organic Mediterranean Quinoa & Fresh Fruit Salads",
            description="Portioned high-protein salads with quinoa, cherry tomatoes, cucumbers, bell peppers, alongside assorted cut seasonal fruits.",
            dietary_type=DietaryType.VEGAN,
            allergen_info="100% Plant-based, allergen friendly.",
            quantity=25,
            remaining_quantity=25,
            unit="bowls",
            prepared_at=now - timedelta(minutes=45),
            expiry_time=now + timedelta(hours=6),
            pickup_start=now,
            pickup_end=now + timedelta(hours=5),
            location="Sector 17 Green Hub, Chandigarh",
            city="Chandigarh",
            status=FoodListingStatus.AVAILABLE
        )

        # Past Completed Listing (for Historical and Impact Stats)
        listing_past1 = FoodListing(
            provider_id=provider_canteen.id,
            organization_id=org_canteen.id,
            category_id=categories[0].id,
            title="Rajma Chawal Executive Lunch Trays",
            description="Traditional Punjabi red kidney bean curry with steamed aromatic basmati rice.",
            dietary_type=DietaryType.VEGETARIAN,
            quantity=60,
            remaining_quantity=0,
            unit="portions",
            prepared_at=now - timedelta(days=2, hours=5),
            expiry_time=now - timedelta(days=2, hours=1),
            pickup_start=now - timedelta(days=2, hours=3),
            pickup_end=now - timedelta(days=2, hours=1),
            location="Block 3 Canteen, Chandigarh",
            city="Chandigarh",
            status=FoodListingStatus.COMPLETED,
            created_at=now - timedelta(days=2, hours=6)
        )

        listing_past2 = FoodListing(
            provider_id=provider_bakery.id,
            organization_id=org_bakery.id,
            category_id=categories[1].id,
            title="Assorted Dinner Rolls & Sandwich Breads",
            description="Pack of fresh soft rolls perfect for community kitchen sandwiches.",
            dietary_type=DietaryType.BAKERY,
            quantity=80,
            remaining_quantity=0,
            unit="items",
            prepared_at=now - timedelta(days=5, hours=8),
            expiry_time=now - timedelta(days=5, hours=2),
            pickup_start=now - timedelta(days=5, hours=4),
            pickup_end=now - timedelta(days=5, hours=2),
            location="Booth 45, Sector 17-C, Chandigarh",
            city="Chandigarh",
            status=FoodListingStatus.COMPLETED,
            created_at=now - timedelta(days=5, hours=9)
        )

        db.session.add_all([listing1, listing2, listing3, listing4, listing_past1, listing_past2])
        db.session.flush()

        print("5. Seeding Reservations...")
        # Active Reservation: 20 portions reserved by Hope Shelter on listing1 (PENDING)
        res1 = Reservation(
            food_listing_id=listing1.id,
            recipient_id=recipient_shelter.id,
            quantity=20,
            status=ReservationStatus.PENDING,
            pickup_code="FR-10492",
            notes="Will bring clean thermoware vans for pickup at 1:30 PM."
        )

        # Historical completed reservations
        res_past1 = Reservation(
            food_listing_id=listing_past1.id,
            recipient_id=recipient_ngo.id,
            quantity=60,
            status=ReservationStatus.COMPLETED,
            pickup_code="FR-99381",
            reserved_at=now - timedelta(days=2, hours=4),
            pickup_time=now - timedelta(days=2, hours=2),
            notes="Distributed to 60 families in Sector 25 slum clusters."
        )

        res_past2 = Reservation(
            food_listing_id=listing_past2.id,
            recipient_id=recipient_shelter.id,
            quantity=80,
            status=ReservationStatus.COMPLETED,
            pickup_code="FR-88210",
            reserved_at=now - timedelta(days=5, hours=3),
            pickup_time=now - timedelta(days=5, hours=2),
            notes="Used for evening shelter tea and dinner."
        )

        db.session.add_all([res1, res_past1, res_past2])
        db.session.flush()

        # Add pickup records
        pickup1 = Pickup(
            reservation_id=res_past1.id,
            collected_at=now - timedelta(days=2, hours=2),
            verified_by_user_id=provider_canteen.id,
            notes="Recipient arrived promptly with van."
        )
        pickup2 = Pickup(
            reservation_id=res_past2.id,
            collected_at=now - timedelta(days=5, hours=2),
            verified_by_user_id=provider_bakery.id,
            notes="Collected in clean bins."
        )
        db.session.add_all([pickup1, pickup2])

        print("6. Seeding Impact Records & Historical Analytics...")
        # 140 meals already directly linked in DB; let's also seed previous months in ImpactRecord
        base_date = date.today()
        impact1 = ImpactRecord(
            record_date=base_date - timedelta(days=1),
            meals_rescued=60,
            listings_completed=1,
            active_providers_count=2,
            active_recipients_count=2,
            carbon_saved_kg=150.0
        )
        impact2 = ImpactRecord(
            record_date=base_date - timedelta(days=5),
            meals_rescued=80,
            listings_completed=1,
            active_providers_count=2,
            active_recipients_count=2,
            carbon_saved_kg=200.0
        )
        db.session.add_all([impact1, impact2])

        print("7. Seeding Notifications...")
        notif1 = Notification(
            user_id=recipient_shelter.id,
            title="Matching Food Available Nearby!",
            message="Surplus food matching your preferences: 'Fresh Vegetable Pulav & Yellow Dal Tadka' (50 portions, VEGETARIAN) is available at Gate No. 2, Campus Cafeteria, Chandigarh.",
            notification_type=NotificationType.MATCH,
            reference_id=listing1.id,
            is_read=False
        )
        notif2 = Notification(
            user_id=provider_canteen.id,
            title="New Food Reservation Request",
            message="Hope Community Shelter has requested 20 portions of 'Fresh Vegetable Pulav & Yellow Dal Tadka'. Pickup Code: FR-10492.",
            notification_type=NotificationType.RESERVATION,
            reference_id=listing1.id,
            is_read=False
        )
        db.session.add_all([notif1, notif2])

        db.session.commit()
        print("\n[SUCCESS] Seed data successfully generated!")
        print("Demo Credentials:")
        print("---------------------------------------------")
        print("Admin:     admin@foodrescue.org     / admin123")
        print("Provider:  canteen@foodrescue.org   / provider123")
        print("Provider:  bakery@foodrescue.org    / provider123")
        print("Recipient: shelter@foodrescue.org   / recipient123")
        print("Recipient: ngo@foodrescue.org       / recipient123")
        print("---------------------------------------------")

if __name__ == "__main__":
    seed_database()
