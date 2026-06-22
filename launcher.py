#!/usr/bin/env python3
"""
SIM-NET Launcher
================
ملف تشغيل سريع للنظام
"""

import os
import sys
import subprocess
import time
import webbrowser
from pathlib import Path

def print_banner():
    """طباعة شعار النظام"""
    banner = """
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║   ███████╗██╗███╗   ███╗    ███╗   ██╗███████╗████████╗  ║
    ║   ██╔════╝██║████╗ ████║    ████╗  ██║██╔════╝╚══██╔══╝  ║
    ║   ███████╗██║██╔████╔██║    ██╔██╗ ██║█████╗     ██║     ║
    ║   ╚════██║██║██║╚██╔╝██║    ██║╚██╗██║██╔══╝     ██║     ║
    ║   ███████║██║██║ ╚═╝ ██║    ██║ ╚████║███████╗   ██║     ║
    ║   ╚══════╝╚═╝╚═╝     ╚═╝    ╚═╝  ╚═══╝╚══════╝   ╚═╝     ║
    ║                                                           ║
    ║        Smart Integrated Network Management System         ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """
    print(banner)

def check_requirements():
    """التحقق من المتطلبات"""
    print("🔍 Checking requirements...")
    
    # التحقق من Python
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required")
        return False
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}")
    return True

def install_requirements():
    """تثبيت المتطلبات"""
    print("\n📦 Installing requirements...")
    
    req_file = Path(__file__).parent / "requirements.txt"
    if not req_file.exists():
        print("❌ requirements.txt not found")
        return False
    
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", str(req_file)], 
                      check=True, capture_output=True)
        print("✅ Requirements installed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install requirements: {e}")
        return False

def init_database():
    """تهيئة قاعدة البيانات"""
    print("\n🗄️  Initializing database...")
    
    db_file = Path(__file__).parent / "database" / "db_manager.py"
    if not db_file.exists():
        print("❌ Database manager not found")
        return False
    
    try:
        subprocess.run([sys.executable, str(db_file)], check=True, capture_output=True)
        print("✅ Database initialized")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to initialize database: {e}")
        return False

def start_backend():
    """تشغيل الخادم الخلفي"""
    print("\n🚀 Starting Backend Server...")
    
    backend_file = Path(__file__).parent / "backend" / "app.py"
    if not backend_file.exists():
        print("❌ Backend not found")
        return None
    
    try:
        process = subprocess.Popen([sys.executable, str(backend_file)],
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        
        # انتظار بدء الخادم
        time.sleep(3)
        
        # التحقق من أن الخادم يعمل
        if process.poll() is None:
            print("✅ Backend started on http://localhost:5000")
            return process
        else:
            print("❌ Backend failed to start")
            return None
            
    except Exception as e:
        print(f"❌ Error starting backend: {e}")
        return None

def start_frontend():
    """تشغيل الواجهة الأمامية"""
    print("\n🌐 Starting Frontend...")
    
    frontend_dir = Path(__file__).parent / "frontend"
    if not frontend_dir.exists():
        print("❌ Frontend directory not found")
        return None
    
    try:
        # استخدام خادم Python المدمج
        process = subprocess.Popen([sys.executable, "-m", "http.server", "8080"],
                                   cwd=str(frontend_dir),
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        
        time.sleep(2)
        
        if process.poll() is None:
            print("✅ Frontend started on http://localhost:8080")
            return process
        else:
            print("❌ Frontend failed to start")
            return None
            
    except Exception as e:
        print(f"❌ Error starting frontend: {e}")
        return None

def open_browser():
    """فتح المتصفح"""
    print("\n🌍 Opening browser...")
    time.sleep(2)
    webbrowser.open("http://localhost:8080")

def show_menu():
    """عرض قائمة الخيارات"""
    print("\n" + "="*60)
    print("📋 SIM-NET Control Menu")
    print("="*60)
    print("1. Start Full System (Backend + Frontend)")
    print("2. Start Backend Only")
    print("3. Start Frontend Only")
    print("4. Initialize Database")
    print("5. Install Requirements")
    print("6. Open Browser")
    print("0. Exit")
    print("="*60)

def main():
    """الدالة الرئيسية"""
    print_banner()
    
    if not check_requirements():
        sys.exit(1)
    
    backend_process = None
    frontend_process = None
    
    while True:
        show_menu()
        choice = input("\nEnter your choice: ").strip()
        
        if choice == "1":
            # Start Full System
            if not init_database():
                print("⚠️  Database initialization failed, continuing...")
            
            backend_process = start_backend()
            if backend_process:
                frontend_process = start_frontend()
                if frontend_process:
                    open_browser()
                    print("\n✅ SIM-NET is running!")
                    print("📡 Backend: http://localhost:5000")
                    print("🌐 Frontend: http://localhost:8080")
                    print("\nPress Ctrl+C to stop...")
                    try:
                        while True:
                            time.sleep(1)
                    except KeyboardInterrupt:
                        print("\n\n🛑 Stopping servers...")
                        if backend_process:
                            backend_process.terminate()
                        if frontend_process:
                            frontend_process.terminate()
                        print("✅ Servers stopped")
            
        elif choice == "2":
            # Start Backend Only
            backend_process = start_backend()
            if backend_process:
                print("\n✅ Backend is running on http://localhost:5000")
                print("Press Ctrl+C to stop...")
                try:
                    backend_process.wait()
                except KeyboardInterrupt:
                    backend_process.terminate()
                    print("\n✅ Backend stopped")
            
        elif choice == "3":
            # Start Frontend Only
            frontend_process = start_frontend()
            if frontend_process:
                open_browser()
                print("\n✅ Frontend is running on http://localhost:8080")
                print("Press Ctrl+C to stop...")
                try:
                    frontend_process.wait()
                except KeyboardInterrupt:
                    frontend_process.terminate()
                    print("\n✅ Frontend stopped")
            
        elif choice == "4":
            # Initialize Database
            init_database()
            
        elif choice == "5":
            # Install Requirements
            install_requirements()
            
        elif choice == "6":
            # Open Browser
            open_browser()
            
        elif choice == "0":
            # Exit
            print("\n👋 Goodbye!")
            if backend_process:
                backend_process.terminate()
            if frontend_process:
                frontend_process.terminate()
            sys.exit(0)
        
        else:
            print("\n❌ Invalid choice")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        sys.exit(0)
