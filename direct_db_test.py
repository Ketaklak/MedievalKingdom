#!/usr/bin/env python3
"""
Direct database test to isolate the issue
"""

import asyncio
import os
import sys
sys.path.append('/app/backend')

from dotenv import load_dotenv
load_dotenv('/app/backend/.env')

from database.mongodb import db

async def test_direct_db():
    """Test database operations directly"""
    print("🔍 Direct Database Test")
    
    try:
        await db.connect_to_mongo()
        print("✅ Database connected")
        
        # Test chat message insertion
        message_data = {
            'username': 'admin',
            'content': 'Direct test message',
            'empire': 'norman',
            'messageType': 'global'
        }
        
        message_id = await db.add_chat_message(message_data)
        print(f"✅ Chat message added: {message_id}")
        
        # Test trade offer insertion
        from datetime import datetime, timedelta
        trade_data = {
            'id': 'direct-test-trade',
            'creatorId': '688c8758d22d26cb02c9de26',
            'creatorUsername': 'admin',
            'offering': {'gold': 100, 'wood': 50},
            'requesting': {'stone': 75, 'food': 25},
            'duration': 3600,
            'createdAt': datetime.utcnow(),
            'expiresAt': datetime.utcnow() + timedelta(seconds=3600),
            'active': True,
            'acceptorId': None,
            'acceptorUsername': None
        }
        
        result = await db.db.trade_offers.insert_one(trade_data)
        print(f"✅ Trade offer created: {result.inserted_id}")
        
        # Test alliance creation
        alliance_data = {
            'id': 'direct-test-alliance',
            'name': 'Direct Test Alliance',
            'description': 'Testing alliance creation directly',
            'leaderId': '688c8758d22d26cb02c9de26',
            'leaderUsername': 'admin',
            'members': ['admin'],
            'createdAt': datetime.utcnow(),
            'maxMembers': 20,
            'level': 1,
            'experience': 0
        }
        
        result = await db.db.alliances.insert_one(alliance_data)
        print(f"✅ Alliance created: {result.inserted_id}")
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_direct_db())