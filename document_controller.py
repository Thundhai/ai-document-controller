#!/usr/bin/env python3
"""
AI Document Controller Agent

This module implements an intelligent document management agent that can:
- Scan and analyze documents on the laptop
- Organize documents by type, date, and relevance
- Suggest documents for deletion or archival
- Clean up duplicate files
- Provide intelligent document management recommendations

Author: AI Assistant
Version: 1.0.0
"""

import asyncio
import json
import os
import hashlib
import mimetypes
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import logging
from dataclasses import dataclass

from dotenv import load_dotenv
from agent_framework import ChatAgent
from agent_framework.openai import OpenAIChatClient
from openai import AsyncOpenAI

# Import offline engine
from offline_engine import OfflineRecommendationEngine, test_internet_connectivity

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('document_controller.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class DocumentInfo:
    """Document information structure"""
    path: str
    name: str
    size: int
    modified_date: datetime
    file_type: str
    extension: str
    hash_value: str
    content_preview: Optional[str] = None


class DocumentAnalyzer:
    """Handles document analysis and content extraction"""
    
    def __init__(self):
        self.supported_text_extensions = {
            '.txt', '.md', '.py', '.js', '.html', '.css', '.json', 
            '.xml', '.csv', '.log', '.yml', '.yaml', '.ini'
        }
    
    def get_file_hash(self, filepath: str) -> str:
        """Generate SHA-256 hash of file content"""
        try:
            with open(filepath, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()
        except Exception as e:
            logger.warning(f"Could not hash file {filepath}: {e}")
            return ""
    
    def get_content_preview(self, filepath: str, max_chars: int = 500) -> Optional[str]:
        """Extract content preview from text files"""
        try:
            file_path = Path(filepath)
            if file_path.suffix.lower() in self.supported_text_extensions:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read(max_chars)
                    return content
        except Exception as e:
            logger.warning(f"Could not read content from {filepath}: {e}")
        return None
    
    def analyze_document(self, filepath: str) -> DocumentInfo:
        """Analyze a single document and extract metadata"""
        path_obj = Path(filepath)
        stat = path_obj.stat()
        
        return DocumentInfo(
            path=filepath,
            name=path_obj.name,
            size=stat.st_size,
            modified_date=datetime.fromtimestamp(stat.st_mtime),
            file_type=mimetypes.guess_type(filepath)[0] or "unknown",
            extension=path_obj.suffix.lower(),
            hash_value=self.get_file_hash(filepath),
            content_preview=self.get_content_preview(filepath)
        )


class DocumentScanner:
    """Handles scanning directories for documents"""
    
    def __init__(self, excluded_dirs: Optional[List[str]] = None):
        self.excluded_dirs = excluded_dirs or [
            '.git', '.svn', '__pycache__', 'node_modules', 
            '.vscode', 'AppData', 'System32', 'Windows'
        ]
        self.analyzer = DocumentAnalyzer()
    
    def should_skip_directory(self, dir_path: str) -> bool:
        """Check if directory should be skipped"""
        dir_name = os.path.basename(dir_path).lower()
        return any(excluded in dir_name for excluded in self.excluded_dirs)
    
    def scan_directory(self, root_path: str, max_files: int = 10000) -> List[DocumentInfo]:
        """Scan directory for documents"""
        documents = []
        file_count = 0
        
        logger.info(f"Starting scan of directory: {root_path}")
        
        try:
            for root, dirs, files in os.walk(root_path):
                # Skip excluded directories
                if self.should_skip_directory(root):
                    dirs.clear()  # Don't recurse into subdirectories
                    continue
                
                for file in files:
                    if file_count >= max_files:
                        logger.warning(f"Reached maximum file limit ({max_files})")
                        break
                    
                    try:
                        filepath = os.path.join(root, file)
                        doc_info = self.analyzer.analyze_document(filepath)
                        documents.append(doc_info)
                        file_count += 1
                        
                        if file_count % 100 == 0:
                            logger.info(f"Processed {file_count} files...")
                            
                    except Exception as e:
                        logger.warning(f"Error processing file {file}: {e}")
                        continue
                
                if file_count >= max_files:
                    break
                    
        except Exception as e:
            logger.error(f"Error scanning directory {root_path}: {e}")
        
        logger.info(f"Scan completed. Found {len(documents)} documents")
        return documents


class DocumentController:
    """Main AI Document Controller Agent with offline/online hybrid mode"""
    
    def __init__(self, github_token: Optional[str] = None, model_id: str = "openai/gpt-4.1-mini", force_offline: bool = False):
        self.github_token = github_token
        self.model_id = model_id
        self.scanner = DocumentScanner()
        self.agent: Optional[ChatAgent] = None
        self.offline_engine = OfflineRecommendationEngine()
        
        # Determine mode
        self.force_offline = force_offline
        self.is_online_mode = False
        self._last_analysis = None
        
        if not force_offline and github_token:
            # Test connectivity and try to initialize AI
            self.is_online_mode = self._test_and_initialize_online_mode()
        
        logger.info(f"DocumentController initialized in {'online' if self.is_online_mode else 'offline'} mode")
    
    def _test_and_initialize_online_mode(self) -> bool:
        """Test connectivity and initialize online mode if possible"""
        try:
            if test_internet_connectivity():
                logger.info("Internet connectivity confirmed, initializing AI agent...")
                return True
            else:
                logger.info("No internet connectivity, using offline mode")
                return False
        except Exception as e:
            logger.warning(f"Failed to test connectivity: {e}, using offline mode")
            return False
        
    async def initialize_agent(self):
        """Initialize the AI agent"""
        try:
            openai_client = AsyncOpenAI(
                base_url="https://models.github.ai/inference",
                api_key=self.github_token,
            )
            
            chat_client = OpenAIChatClient(
                async_client=openai_client,
                model_id=self.model_id
            )
            
            self.agent = ChatAgent(
                chat_client=chat_client,
                name="DocumentController",
                instructions="""You are an intelligent document management assistant. Your role is to:
                1. Analyze document collections and provide insights
                2. Identify duplicate files and suggest cleanup actions
                3. Recommend organization strategies based on file types and usage patterns
                4. Suggest which documents might be candidates for deletion or archival
                5. Provide clear, actionable recommendations for document management
                
                Always consider file size, modification dates, content relevance, and potential duplicates when making recommendations.
                Be conservative with deletion suggestions and always explain your reasoning.""",
                tools=[
                    self.scan_documents,
                    self.find_duplicates,
                    self.analyze_disk_usage,
                    self.get_old_files,
                    self.suggest_organization
                ]
            )
            
            logger.info("AI agent initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize agent: {e}")
            raise
    
    def scan_documents(self, directory_path: str, max_files: int = 1000) -> str:
        """Scan a directory for documents and return summary"""
        try:
            if not os.path.exists(directory_path):
                return f"Directory not found: {directory_path}"
            
            documents = self.scanner.scan_directory(directory_path, max_files)
            
            # Store results for other tools
            self._last_scan_results = documents
            
            if self.is_online_mode:
                # Generate AI-enhanced summary
                total_size = sum(doc.size for doc in documents)
                file_types = {}
                for doc in documents:
                    file_types[doc.extension] = file_types.get(doc.extension, 0) + 1
                
                summary = {
                    "total_files": len(documents),
                    "total_size_mb": round(total_size / (1024 * 1024), 2),
                    "file_types": dict(sorted(file_types.items(), key=lambda x: x[1], reverse=True)[:10]),
                    "oldest_file": min(documents, key=lambda x: x.modified_date).name if documents else None,
                    "newest_file": max(documents, key=lambda x: x.modified_date).name if documents else None,
                    "largest_file": max(documents, key=lambda x: x.size).name if documents else None
                }
                
                return f"Scan Results:\n{json.dumps(summary, indent=2, default=str)}"
            else:
                # Use offline analysis
                analysis = self.offline_engine.analyze_file_distribution(documents)
                self._last_analysis = analysis
                return f"📊 **Offline Scan Results**:\n{json.dumps(analysis, indent=2, default=str)}"
            
        except Exception as e:
            return f"Error scanning documents: {e}"
    
    def find_duplicates(self) -> str:
        """Find duplicate files based on hash values"""
        try:
            if not hasattr(self, '_last_scan_results'):
                return "Please scan documents first using scan_documents tool"
            
            hash_groups = {}
            for doc in self._last_scan_results:
                if doc.hash_value:
                    if doc.hash_value not in hash_groups:
                        hash_groups[doc.hash_value] = []
                    hash_groups[doc.hash_value].append(doc)
            
            duplicates = {hash_val: docs for hash_val, docs in hash_groups.items() if len(docs) > 1}
            
            if not duplicates:
                return "No duplicate files found"
            
            duplicate_summary = {
                "duplicate_groups": len(duplicates),
                "total_duplicate_files": sum(len(docs) for docs in duplicates.values()),
                "potential_space_saved_mb": 0
            }
            
            duplicate_details = []
            for hash_val, docs in list(duplicates.items())[:5]:  # Show first 5 groups
                group_size = docs[0].size
                duplicate_summary["potential_space_saved_mb"] += (len(docs) - 1) * group_size / (1024 * 1024)
                
                duplicate_details.append({
                    "file_size_mb": round(group_size / (1024 * 1024), 2),
                    "duplicate_count": len(docs),
                    "files": [{"name": doc.name, "path": doc.path} for doc in docs]
                })
            
            duplicate_summary["potential_space_saved_mb"] = round(duplicate_summary["potential_space_saved_mb"], 2)
            duplicate_summary["examples"] = duplicate_details
            
            return f"Duplicate Analysis:\n{json.dumps(duplicate_summary, indent=2)}"
            
        except Exception as e:
            return f"Error finding duplicates: {e}"
    
    def analyze_disk_usage(self) -> str:
        """Analyze disk usage by file types"""
        try:
            if not hasattr(self, '_last_scan_results'):
                return "Please scan documents first using scan_documents tool"
            
            type_usage = {}
            for doc in self._last_scan_results:
                ext = doc.extension or 'no_extension'
                if ext not in type_usage:
                    type_usage[ext] = {"count": 0, "total_size": 0}
                type_usage[ext]["count"] += 1
                type_usage[ext]["total_size"] += doc.size
            
            # Sort by size
            sorted_usage = sorted(
                type_usage.items(),
                key=lambda x: x[1]["total_size"],
                reverse=True
            )[:10]
            
            usage_summary = []
            for ext, data in sorted_usage:
                usage_summary.append({
                    "file_type": ext,
                    "count": data["count"],
                    "total_size_mb": round(data["total_size"] / (1024 * 1024), 2),
                    "avg_size_kb": round(data["total_size"] / data["count"] / 1024, 2)
                })
            
            return f"Disk Usage Analysis:\n{json.dumps(usage_summary, indent=2)}"
            
        except Exception as e:
            return f"Error analyzing disk usage: {e}"
    
    def get_old_files(self, days_old: int = 365) -> str:
        """Find files older than specified days"""
        try:
            if not hasattr(self, '_last_scan_results'):
                return "Please scan documents first using scan_documents tool"
            
            cutoff_date = datetime.now() - timedelta(days=days_old)
            old_files = [doc for doc in self._last_scan_results if doc.modified_date < cutoff_date]
            
            if not old_files:
                return f"No files found older than {days_old} days"
            
            # Sort by size (largest first) for potential cleanup candidates
            old_files.sort(key=lambda x: x.size, reverse=True)
            
            total_old_size = sum(doc.size for doc in old_files)
            
            old_files_summary = {
                "total_old_files": len(old_files),
                "total_size_mb": round(total_old_size / (1024 * 1024), 2),
                "oldest_file_date": min(old_files, key=lambda x: x.modified_date).modified_date.strftime("%Y-%m-%d"),
                "largest_old_files": [
                    {
                        "name": doc.name,
                        "path": doc.path,
                        "size_mb": round(doc.size / (1024 * 1024), 2),
                        "modified_date": doc.modified_date.strftime("%Y-%m-%d")
                    }
                    for doc in old_files[:10]
                ]
            }
            
            return f"Old Files Analysis (>{days_old} days):\n{json.dumps(old_files_summary, indent=2, default=str)}"
            
        except Exception as e:
            return f"Error finding old files: {e}"
    
    def suggest_organization(self) -> str:
        """Suggest document organization strategies"""
        try:
            if not hasattr(self, '_last_scan_results'):
                return "Please scan documents first using scan_documents tool"
            
            docs = self._last_scan_results
            
            if self.is_online_mode:
                # AI-powered suggestions (existing logic)
                directories = set()
                for doc in docs:
                    directories.add(os.path.dirname(doc.path))
                
                suggestions = {
                    "current_structure": {
                        "total_directories": len(directories),
                        "total_files": len(docs),
                        "avg_files_per_directory": round(len(docs) / len(directories), 2) if directories else 0
                    },
                    "organization_suggestions": [
                        "Create separate folders for different file types (Documents, Images, Archives, etc.)",
                        "Use date-based organization for frequently updated files (YYYY/MM structure)",
                        "Create a 'To_Review' folder for files that haven't been accessed recently",
                        "Use descriptive folder names instead of generic ones like 'New folder'",
                        "Consider using tags or metadata for better searchability"
                    ],
                    "cleanup_priorities": [
                        "Remove duplicate files (check find_duplicates results)",
                        "Archive or delete files older than 2 years that haven't been accessed",
                        "Organize scattered files in the root directories",
                        "Clean up download folders and temporary files",
                        "Compress or archive large old files to save space"
                    ]
                }
                
                return f"Organization Suggestions:\n{json.dumps(suggestions, indent=2)}"
            else:
                # Use offline rule-based suggestions
                suggestions = self.offline_engine.suggest_organization_strategy(docs)
                automation_rules = self.offline_engine.suggest_automation_rules(self._last_analysis or {})
                
                result = {
                    "mode": "offline",
                    "organization_suggestions": suggestions,
                    "automation_recommendations": automation_rules
                }
                
                return f"🤖 **Offline Organization Suggestions**:\n{json.dumps(result, indent=2)}"
            
        except Exception as e:
            return f"Error generating suggestions: {e}"
    
    async def chat_with_user(self, user_input: str) -> str:
        """Process user input and return agent response"""
        if self.is_online_mode:
            if not self.agent:
                await self.initialize_agent()
            
            try:
                thread = self.agent.get_new_thread()
                result = await self.agent.run(user_input, thread=thread)
                return result.text
            except Exception as e:
                logger.error(f"Error in online chat: {e}, falling back to offline mode")
                self.is_online_mode = False
                return self.offline_engine.generate_offline_chat_response(user_input, self._last_analysis)
        else:
            # Use offline chat response
            return self.offline_engine.generate_offline_chat_response(user_input, self._last_analysis)
    
    async def run_interactive_session(self):
        """Run an interactive session with the user"""
        mode_text = "🤖 AI" if self.is_online_mode else "🔧 Offline"
        print(f"{mode_text} Document Controller Agent")
        print("=" * 50)
        print("I can help you manage your documents! Here's what I can do:")
        print("- Scan directories for documents")
        print("- Find and suggest duplicate file cleanup")
        print("- Analyze disk usage by file type")
        print("- Identify old files for archival")
        print("- Suggest organization strategies")
        
        if not self.is_online_mode:
            print("\n🔧 Running in OFFLINE mode - using rule-based recommendations")
            print("💡 Basic file management available without internet connection")
        else:
            print("\n🤖 Running in ONLINE mode - AI-powered insights available")
        
        print("\nType 'quit' to exit\n")
        
        if self.is_online_mode and not self.agent:
            await self.initialize_agent()
        
        if self.is_online_mode and self.agent:
            thread = self.agent.get_new_thread()
        else:
            thread = None
        
        while True:
            try:
                user_input = input("You: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    print("👋 Goodbye! Happy organizing!")
                    break
                
                if not user_input:
                    continue
                
                print("🤔 Thinking...")
                
                if self.is_online_mode and self.agent and thread:
                    try:
                        result = await self.agent.run(user_input, thread=thread)
                        print(f"🤖 Agent: {result.text}\n")
                    except Exception as e:
                        logger.error(f"Online mode failed: {e}, switching to offline")
                        self.is_online_mode = False
                        response = self.offline_engine.generate_offline_chat_response(user_input, self._last_analysis)
                        print(f"🔧 Offline Agent: {response}\n")
                else:
                    # Offline mode
                    response = self.offline_engine.generate_offline_chat_response(user_input, self._last_analysis)
                    print(f"🔧 Offline Agent: {response}\n")
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}\n")


async def main():
    """Main function to run the document controller"""
    # Load environment variables from .env file
    load_dotenv()
    
    # Load configuration
    github_token = os.getenv("GITHUB_TOKEN")
    force_offline = os.getenv("FORCE_OFFLINE", "false").lower() == "true"
    
    print("🤖 AI Document Controller")
    print("=" * 30)
    
    if force_offline:
        print("🔧 Forced offline mode enabled")
        controller = DocumentController(force_offline=True)
    elif not github_token:
        print("⚠️  No GitHub token found - running in offline mode")
        print("💡 Set GITHUB_TOKEN in .env for AI features")
        print("📖 Get a token from: https://github.com/settings/tokens")
        controller = DocumentController()
    else:
        print("🔍 Testing connectivity and initializing...")
        controller = DocumentController(github_token)
        
        if controller.is_online_mode:
            print("✅ Online mode - AI features available")
        else:
            print("🔧 Offline mode - using rule-based recommendations")
    
    # Run interactive session
    await controller.run_interactive_session()


if __name__ == "__main__":
    asyncio.run(main())