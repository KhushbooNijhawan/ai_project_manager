#!/usr/bin/env python3
"""
LLM DIAGNOSTIC SCRIPT
Run this BEFORE your Streamlit app to test if Groq API is working
"""

import time
import sys

def test_groq_api():
    """Test Groq API with different configurations"""
    
    print("="*70)
    print("GROQ API DIAGNOSTIC TEST")
    print("="*70)
    
    # Get API key
    api_key = input("\nEnter your Groq API key: ").strip()
    
    if not api_key:
        print("❌ No API key provided!")
        return False
    
    try:
        from langchain_groq import ChatGroq
    except ImportError:
        print("\n❌ langchain-groq not installed!")
        print("   Run: pip install langchain-groq")
        return False
    
    # Test configurations
    configs = [
        {
            'name': 'Fast Model (8B)',
            'model': 'llama-3.1-8b-instant',
            'timeout': 30,
            'tokens': 100
        },
        {
            'name': 'Balanced Model (70B)',
            'model': 'llama-3.1-70b-versatile',
            'timeout': 60,
            'tokens': 500
        },
        {
            'name': 'Alternative (Mixtral)',
            'model': 'mixtral-8x7b-32768',
            'timeout': 60,
            'tokens': 500
        }
    ]
    
    results = {}
    
    for config in configs:
        print(f"\n{'='*70}")
        print(f"Testing: {config['name']}")
        print(f"Model: {config['model']}")
        print(f"Timeout: {config['timeout']}s | Max Tokens: {config['tokens']}")
        print('-'*70)
        
        try:
            # Initialize LLM
            llm = ChatGroq(
                groq_api_key=api_key,
                model_name=config['model'],
                temperature=0,
                max_tokens=config['tokens'],
                timeout=config['timeout'],
                request_timeout=config['timeout']
            )
            
            # Test 1: Simple response
            print("\nTest 1: Simple Response...")
            start = time.time()
            response = llm.invoke("Say: OK")
            elapsed = time.time() - start
            
            if response and response.content:
                print(f"   ✅ SUCCESS ({elapsed:.2f}s)")
                print(f"   Response: {response.content[:50]}")
            else:
                print(f"   ⚠️ Empty response ({elapsed:.2f}s)")
                results[config['name']] = 'partial'
                continue
            
            # Test 2: Risk assessment (like your actual use case)
            print("\nTest 2: Risk Assessment...")
            prompt = "Mobile App: Budget $100k, 12 weeks. List 3 risks:"
            start = time.time()
            response = llm.invoke(prompt)
            elapsed = time.time() - start
            
            if response and len(response.content) > 50:
                print(f"   ✅ SUCCESS ({elapsed:.2f}s)")
                print(f"   Got {len(response.content)} characters")
                risks = [line.strip() for line in response.content.split('\n') if len(line.strip()) > 20]
                print(f"   Parsed {len(risks)} risks")
            else:
                print(f"   ⚠️ Short response ({elapsed:.2f}s)")
            
            # Test 3: Training courses (like your actual use case)
            print("\nTest 3: Course Recommendations...")
            prompt = "Python: Coursera, Udemy, LinkedIn, freeCodeCamp courses"
            start = time.time()
            response = llm.invoke(prompt)
            elapsed = time.time() - start
            
            if response and len(response.content) > 50:
                print(f"   ✅ SUCCESS ({elapsed:.2f}s)")
                print(f"   Got {len(response.content)} characters")
                courses = [line for line in response.content.split('\n') if 'coursera' in line.lower() or 'udemy' in line.lower()]
                print(f"   Found {len(courses)} course mentions")
            else:
                print(f"   ⚠️ Short response ({elapsed:.2f}s)")
            
            results[config['name']] = 'success'
            print(f"\n{'='*70}")
            print(f"✅ {config['name']} - ALL TESTS PASSED")
            
        except Exception as e:
            error_type = type(e).__name__
            error_msg = str(e)[:100]
            print(f"\n❌ FAILED: {error_type}")
            print(f"   {error_msg}")
            results[config['name']] = 'failed'
            
            # Specific error handling
            if 'timeout' in error_msg.lower() or 'timed out' in error_msg.lower():
                print("\n   🔍 DIAGNOSIS: API is timing out")
                print("   Possible causes:")
                print("   1. Groq API is experiencing high load")
                print("   2. Your network connection is slow")
                print("   3. Model is overloaded - try different model")
                print("   Recommendation: Increase timeout or try different model")
            
            elif 'api key' in error_msg.lower() or 'unauthorized' in error_msg.lower():
                print("\n   🔍 DIAGNOSIS: API key issue")
                print("   1. Check your API key is correct")
                print("   2. Check key hasn't expired")
                print("   3. Get a new key from https://console.groq.com")
            
            elif 'rate limit' in error_msg.lower():
                print("\n   🔍 DIAGNOSIS: Rate limit exceeded")
                print("   Wait 1 minute and try again")
    
    # Summary
    print(f"\n{'='*70}")
    print("DIAGNOSTIC SUMMARY")
    print('='*70)
    
    for name, result in results.items():
        status = {
            'success': '✅ WORKING',
            'partial': '⚠️ PARTIAL',
            'failed': '❌ FAILED'
        }.get(result, '❓ UNKNOWN')
        print(f"  {name:30} {status}")
    
    print("\n" + "="*70)
    
    # Recommendations
    working_configs = [name for name, result in results.items() if result == 'success']
    
    if working_configs:
        print("✅ RECOMMENDATION:")
        print(f"\n   Use this configuration in your app:")
        best_config = [c for c in configs if c['name'] == working_configs[0]][0]
        print(f"""
   llm = ChatGroq(
       groq_api_key=api_key,
       model_name="{best_config['model']}",
       temperature=0,
       max_tokens={best_config['tokens']},
       timeout={best_config['timeout']},
       request_timeout={best_config['timeout']}
   )
        """)
        return True
    else:
        print("❌ NO WORKING CONFIGURATION FOUND")
        print("\nTroubleshooting:")
        print("1. Check Groq API status: https://status.groq.com")
        print("2. Verify your API key at: https://console.groq.com")
        print("3. Try again in 5 minutes (might be temporary)")
        print("4. Consider using OpenAI API instead (more reliable)")
        return False

def test_basic_connectivity():
    """Test basic network connectivity to Groq"""
    print("\n" + "="*70)
    print("TESTING BASIC CONNECTIVITY")
    print("="*70)
    
    try:
        import requests
        
        print("\n1. Testing DNS resolution...")
        response = requests.get("https://api.groq.com", timeout=10)
        print(f"   ✅ Can reach api.groq.com")
        
    except requests.exceptions.Timeout:
        print("   ❌ Connection timeout - check your internet")
        return False
    except requests.exceptions.ConnectionError:
        print("   ❌ Cannot connect - check your firewall/VPN")
        return False
    except Exception as e:
        print(f"   ⚠️ Unexpected error: {str(e)[:50]}")
        return False
    
    return True

def main():
    """Main diagnostic function"""
    print("\n" + "="*70)
    print("GROQ LLM DIAGNOSTIC TOOL")
    print("="*70)
    print("\nThis script will test your Groq API configuration")
    print("to diagnose why your risks and training timeouts occur.")
    print("\nMake sure you have:")
    print("  • Valid Groq API key")
    print("  • langchain-groq installed (pip install langchain-groq)")
    print("  • Stable internet connection")
    
    input("\nPress Enter to start...")
    
    # Test basic connectivity first
    if not test_basic_connectivity():
        print("\n❌ Basic connectivity test failed!")
        print("   Fix your network connection before testing LLM")
        return
    
    # Test Groq API
    success = test_groq_api()
    
    print("\n" + "="*70)
    if success:
        print("✅ DIAGNOSIS COMPLETE - At least one model is working!")
        print("   Copy the recommended configuration to your backend_integration.py")
    else:
        print("❌ DIAGNOSIS COMPLETE - No models are working")
        print("   Check the troubleshooting steps above")
    print("="*70)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
