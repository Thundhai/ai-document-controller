#!/usr/bin/env python3
"""
Quick online mode test
"""

import asyncio
import os
from dotenv import load_dotenv
from document_controller import DocumentController

async def test_online_mode():
    """Test online mode functionality"""
    load_dotenv()
    
    github_token = os.getenv('GITHUB_TOKEN')
    print(f"🔑 GitHub Token: {'✅ FOUND' if github_token else '❌ NOT FOUND'}")
    
    if not github_token:
        print("❌ Cannot test online mode without token")
        return
    
    print("🤖 Initializing DocumentController...")
    controller = DocumentController(github_token)
    
    print(f"🔧 Mode detected: {'🤖 ONLINE' if controller.is_online_mode else '🔧 OFFLINE'}")
    
    if controller.is_online_mode:
        print("🚀 Testing AI chat...")
        try:
            response = await controller.chat_with_user("What are your main document management features?")
            print(f"✅ AI Response received ({len(response)} chars)")
            print(f"🤖 Response preview: {response[:300]}...")
        except Exception as e:
            print(f"❌ AI chat failed: {e}")
    else:
        print("ℹ️ Online mode not available, testing offline fallback...")
        response = await controller.chat_with_user("What can you help me with?")
        print(f"🔧 Offline response: {response[:200]}...")

if __name__ == "__main__":
    asyncio.run(test_online_mode())