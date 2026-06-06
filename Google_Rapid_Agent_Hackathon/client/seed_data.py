import os
import sys
from datetime import datetime
from pymongo import MongoClient

# Atlas Connection String
#CONNECTION_STRING = "mongodb+srv://admin:MyPassword123@cluster0.pvpecbn.mongodb.net/MatchMarket"
CONNECTION_STRING = "mongodb+srv://admin:MyPassword123@cluster0.pvpecbn.mongodb.net/?appName=Cluster0"

def seed_database():
    print("Connecting to MongoDB Atlas Cluster...")
    client = MongoClient(CONNECTION_STRING)
    db = client["MatchMarket"]
    
    # -----------------------------------------------------------------
    # 1. Populate 'stock_inventory' Collection
    # -----------------------------------------------------------------
    #print("Clearing stale inventory lines...")
    #db["stock_inventory"].drop()
    
    inventory_records = [
        # SCENARIO A: Critical low-stock lines (triggers restock alerts)
        {
            "name": "Official 2026 Match Ball Replica", 
            "category": "Merchandise", 
            "quantity": 3,  # Low stock!
            "price": 2499.0,
            "reorder_level": 20,
            "sales_velocity_30d": 45
        },
        {
            "name": "MatchMarket Pro Goalie Gloves", 
            "category": "Equipment", 
            "quantity": 2,  # Low stock!
            "price": 3499.0,
            "reorder_level": 10,
            "sales_velocity_30d": 12
        },
        {
            "name": "Neon Red Corner Flags (Set of 4)", 
            "category": "Equipment", 
            "quantity": 1,  # Critical warning!
            "price": 1899.0,
            "reorder_level": 5,
            "sales_velocity_30d": 4
        },
        
        # SCENARIO B: Slow-Moving Item (triggers clearance/promo workflow)
        {
            "name": "Vintage Woolen Supporter Scarf", 
            "category": "Merchandise", 
            "quantity": 150,  # Massive overstock
            "price": 899.0,
            "reorder_level": 15,
            "sales_velocity_30d": 0  # SLOW MOVING - Zero sales!
        },
        
        # SCENARIO C: Stable, Healthy Stock Levels
        {
            "name": "MatchMarket Training Bibs (Blue/L)", 
            "category": "Merchandise", 
            "quantity": 45, 
            "price": 499.0,
            "reorder_level": 15,
            "sales_velocity_30d": 22
        },
        {
            "name": "MatchMarket Training Bibs (Neon/L)", 
            "category": "Merchandise", 
            "quantity": 50, 
            "price": 499.0,
            "reorder_level": 15,
            "sales_velocity_30d": 30
        },
        {
            "name": "Pro Aluminium Referee Whistle", 
            "category": "Equipment", 
            "quantity": 12, 
            "price": 299.0,
            "reorder_level": 5,
            "sales_velocity_30d": 3
        },
        {
            "name": "Elasticated Captain Armbands", 
            "category": "Merchandise", 
            "quantity": 25, 
            "price": 199.0,
            "reorder_level": 10,
            "sales_velocity_30d": 15
        },
        {
            "name": "Water Resistance Stopwatch v4", 
            "category": "Equipment", 
            "quantity": 8, 
            "price": 1249.0,
            "reorder_level": 4,
            "sales_velocity_30d": 6
        },
        {
            "name": "Premium Agility Cones (Pack of 20)", 
            "category": "Equipment", 
            "quantity": 35, 
            "price": 1599.0,
            "reorder_level": 15,
            "sales_velocity_30d": 40
        }
    ]
    
    db["stock_inventory"].insert_many(inventory_records)
    print(f"Successfully generated {len(inventory_records)} test entries in 'stock_inventory'.")

    # -----------------------------------------------------------------
    # 2. Populate 'match_events' Collection
    # -----------------------------------------------------------------
    #print("Clearing event logs...")
    #db["match_events"].drop()
    
    # Scheduling a future tournament fixture
    future_event = {
        "event_id": "EVENT_2026_FINAL",
        "title": "MatchMarket Champions Cup Final",
        "location": "Bangalore National Stadium",
        "date_time": datetime(2026, 11, 15, 19, 30, 0),  # Scheduled for November 2026
        "expected_attendance": 45000,
        "status": "Scheduled",
        "requires_merchandise_restock": True
    }
    
    db["match_events"].insert_one(future_event)
    print("Successfully generated 1 upcoming schedule block in 'match_events'.")
    print("\nSeed Complete!")

if __name__ == "__main__":
    seed_database()
