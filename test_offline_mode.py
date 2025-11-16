#!/usr/bin/env python3
"""
Test script to demonstrate offline/online hybrid functionality

This script tests both online AI mode and offline rule-based mode
to ensure the system works seamlessly without internet.
"""

import asyncio
import os
import tempfile
from pathlib import Path
from document_controller import DocumentController
from offline_engine import test_internet_connectivity


async def test_offline_mode():
    """Test offline mode functionality"""
    print("🔧 Testing OFFLINE mode...")
    print("=" * 40)
    
    # Force offline mode
    controller = DocumentController(force_offline=True)
    
    # Create a temporary directory with test files
    with tempfile.TemporaryDirectory() as temp_dir:
        test_files = [
            ("test.pdf", b"PDF content"),
            ("image.jpg", b"JPEG content"),
            ("document.docx", b"DOCX content"),
            ("archive.zip", b"ZIP content"),
            ("duplicate1.txt", b"Same content"),
            ("duplicate2.txt", b"Same content"),  # Duplicate
        ]
        
        for filename, content in test_files:
            with open(Path(temp_dir) / filename, "wb") as f:
                f.write(content)
        
        print(f"📂 Created test directory: {temp_dir}")
        print("📄 Test files: PDF, JPG, DOCX, ZIP, TXT (with duplicates)")
        print()
        
        # Test scanning
        print("🔍 Testing document scanning...")
        scan_result = controller.scan_documents(temp_dir, 100)
        print(scan_result)
        print()
        
        # Test duplicate detection
        print("🔄 Testing duplicate detection...")
        dup_result = controller.find_duplicates()
        print(dup_result)
        print()
        
        # Test organization suggestions
        print("💡 Testing organization suggestions...")
        org_result = controller.suggest_organization()
        print(org_result)
        print()
        
        # Test offline chat
        print("💬 Testing offline chat responses...")
        chat_responses = [
            "How should I organize my files?",
            "Find duplicate files",
            "Help me clean up my documents",
            "What can you do?"
        ]
        
        for query in chat_responses:
            print(f"❓ Query: {query}")
            response = await controller.chat_with_user(query)
            print(f"🤖 Response: {response[:200]}...")
            print()


async def test_online_mode():
    """Test online mode functionality if internet is available"""
    print("🌐 Testing ONLINE mode...")
    print("=" * 40)
    
    # Check connectivity
    if not test_internet_connectivity():
        print("❌ No internet connectivity - skipping online tests")
        return
    
    # Test with token if available
    github_token = os.getenv("GITHUB_TOKEN")
    if not github_token:
        print("⚠️  No GITHUB_TOKEN found - skipping online tests")
        print("💡 Set GITHUB_TOKEN environment variable to test AI features")
        return
    
    print("✅ Internet connectivity confirmed")
    print("🤖 Initializing AI mode...")
    
    controller = DocumentController(github_token)
    
    if controller.is_online_mode:
        print("✅ AI agent initialized successfully")
        
        # Test AI chat
        print("💬 Testing AI chat...")
        response = await controller.chat_with_user("What can you help me with?")
        print(f"🤖 AI Response: {response[:200]}...")
        
    else:
        print("❌ Failed to initialize AI mode, fell back to offline")


async def test_hybrid_fallback():
    """Test automatic fallback from online to offline"""
    print("🔄 Testing HYBRID fallback functionality...")
    print("=" * 40)
    
    # Simulate online mode with invalid token
    controller = DocumentController("invalid_token")
    
    print(f"🔧 Mode after init: {'Online' if controller.is_online_mode else 'Offline'}")
    
    # This should fallback to offline if online fails
    response = await controller.chat_with_user("Help me organize files")
    print(f"🤖 Fallback response: {response[:200]}...")


async def main():
    """Run all tests"""
    print("🧪 AI Document Controller - Offline/Online Test Suite")
    print("=" * 60)
    print()
    
    # Test offline mode
    await test_offline_mode()
    
    print("\n" + "=" * 60 + "\n")
    
    # Test online mode
    await test_online_mode()
    
    print("\n" + "=" * 60 + "\n")
    
    # Test hybrid fallback
    await test_hybrid_fallback()
    
    print("\n✅ Test suite completed!")
    print()
    print("📋 Summary:")
    print("  🔧 Offline mode: Rule-based recommendations, no internet needed")
    print("  🤖 Online mode: AI-powered insights with internet connection")
    print("  🔄 Hybrid mode: Automatic fallback for seamless operation")


if __name__ == "__main__":
    asyncio.run(main())