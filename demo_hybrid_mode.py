#!/usr/bin/env python3
"""
Quick demo of offline/online hybrid mode

This demonstrates how the system seamlessly switches between AI and rule-based modes.
"""

import asyncio
import os
from dotenv import load_dotenv
from document_controller import DocumentController


async def demo():
    load_dotenv()
    
    print("🚀 AI Document Controller - Hybrid Mode Demo")
    print("=" * 50)
    print()
    
    # Demo 1: Automatic mode detection
    print("🔍 Demo 1: Automatic Mode Detection")
    print("-" * 30)
    
    github_token = os.getenv("GITHUB_TOKEN")
    
    if github_token:
        print("✅ GitHub token found - testing online mode...")
        controller_online = DocumentController(github_token)
        mode = "🤖 AI Online" if controller_online.is_online_mode else "🔧 Offline"
        print(f"   Result: {mode} mode")
    else:
        print("⚠️  No GitHub token - will use offline mode")
    
    print()
    
    # Demo 2: Forced offline mode
    print("🔧 Demo 2: Forced Offline Mode")
    print("-" * 30)
    
    controller_offline = DocumentController(force_offline=True)
    print("   Forced offline mode enabled")
    
    # Test offline capabilities
    print("   Testing offline chat...")
    response = await controller_offline.chat_with_user("What can you help me with?")
    print(f"   🤖 Response: {response[:100]}...")
    print()
    
    # Demo 3: Mode comparison
    print("⚖️  Demo 3: Mode Comparison")
    print("-" * 30)
    
    query = "How should I organize my documents?"
    
    print(f"   📝 Question: {query}")
    print()
    
    # Offline response
    print("   🔧 Offline Mode Response:")
    offline_response = await controller_offline.chat_with_user(query)
    print(f"      {offline_response[:150]}...")
    print()
    
    # Online response (if available)
    if github_token and 'controller_online' in locals():
        print("   🤖 Online Mode Response:")
        try:
            online_response = await controller_online.chat_with_user(query)
            print(f"      {online_response[:150]}...")
        except Exception as e:
            print(f"      ❌ Online mode failed: {e}")
            print("      🔧 Would automatically fall back to offline mode")
    else:
        print("   🤖 Online mode not available (no GitHub token)")
    
    print()
    
    # Demo 4: Features comparison
    print("📋 Demo 4: Feature Comparison")
    print("-" * 30)
    print()
    
    features = {
        "✅ Document scanning": "Both modes",
        "✅ Duplicate detection": "Both modes", 
        "✅ File type analysis": "Both modes",
        "✅ Basic organization": "Both modes",
        "✅ Old file detection": "Both modes",
        "🤖 AI-powered insights": "Online only",
        "🤖 Natural language chat": "Enhanced online",
        "🤖 Smart recommendations": "Enhanced online",
        "🔧 Rule-based suggestions": "Offline fallback",
        "🔧 No internet required": "Offline mode",
        "🔄 Automatic fallback": "Hybrid system"
    }
    
    for feature, availability in features.items():
        print(f"   {feature}: {availability}")
    
    print()
    print("✨ Benefits of Hybrid Mode:")
    print("   🌐 Full AI capabilities when online")
    print("   🔧 Reliable operation when offline")  
    print("   🔄 Seamless automatic switching")
    print("   🛡️ Graceful error handling")
    print("   ⚡ No internet dependency for basic features")


if __name__ == "__main__":
    asyncio.run(demo())