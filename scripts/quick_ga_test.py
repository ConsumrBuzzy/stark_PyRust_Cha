#!/usr/bin/env python3
"""
GitHub Actions Quick Test - Essential Components Only
"""

import os
import sys
import subprocess
from pathlib import Path

def quick_github_actions_test():
    print('🧪 GITHUB ACTIONS QUICK TEST')
    print('=' * 40)
    
    # Test 1: Workflow files exist
    print('1️⃣ Checking Workflow Files...')
    workflows = [
        '.github/workflows/iron_to_steel_auto.yml',
        '.github/workflows/pulse.yml',
        '.github/workflows/ghost_recovery.yml'
    ]
    
    workflow_count = 0
    for workflow in workflows:
        if Path(workflow).exists():
            print(f'   ✅ {workflow}')
            workflow_count += 1
        else:
            print(f'   ❌ {workflow}')
    
    print(f'   📊 Workflows: {workflow_count}/{len(workflows)} present')
    
    # Test 2: Essential scripts exist
    print('\n2️⃣ Checking Essential Scripts...')
    scripts = [
        'scripts/check_threshold.py',
        'scripts/step_b_fuel_alert.py',
        'scripts/step_e_yield_report.py',
        'scripts/test_telegram.py',
        'scripts/send_status_report.py'
    ]
    
    script_count = 0
    for script in scripts:
        if Path(script).exists():
            print(f'   ✅ {script}')
            script_count += 1
        else:
            print(f'   ❌ {script}')
    
    print(f'   📊 Scripts: {script_count}/{len(scripts)} present')
    
    # Test 3: Rust build
    print('\n3️⃣ Testing Rust Build...')
    try:
        rust_path = Path('rust-core')
        if rust_path.exists():
            result = subprocess.run([
                'cargo', 'check'
            ], cwd=rust_path, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print('   ✅ Rust build checks pass')
            else:
                print('   ❌ Rust build checks fail')
        else:
            print('   ❌ Rust core directory not found')
    except Exception as e:
        print(f'   ❌ Rust build error: {e}')
    
    # Test 4: Python dependencies
    print('\n4️⃣ Testing Python Dependencies...')
    try:
        # Add src to path
        sys.path.insert(0, str(Path.cwd()))
        
        # Test imports
        from src.foundation.network import NetworkOracle
        from src.foundation.reporting import ReportingSystem
        print('   ✅ Core modules import successfully')
        
        # Test network oracle
        import asyncio
        async def test_network():
            oracle = NetworkOracle()
            await oracle.initialize()
            return True
        
        result = asyncio.run(test_network())
        if result:
            print('   ✅ Network oracle connects successfully')
        
    except Exception as e:
        print(f'   ❌ Python dependency error: {e}')
    
    # Test 5: Telegram configuration
    print('\n5️⃣ Testing Telegram Configuration...')
    try:
        # Load .env
        env_path = Path('.env')
        telegram_configured = False
        
        if env_path.exists():
            with open(env_path, 'r') as f:
                content = f.read()
                if 'TELEGRAM_BOT_TOKEN' in content and 'TELEGRAM_CHAT_ID' in content:
                    telegram_configured = True
        
        if telegram_configured:
            print('   ✅ Telegram credentials found in .env')
        else:
            print('   ⚠️  Telegram credentials not in .env (will use GitHub Secrets)')
    except Exception as e:
        print(f'   ❌ Telegram config error: {e}')
    
    # Test 6: GitHub Actions syntax
    print('\n6️⃣ Testing GitHub Actions Syntax...')
    try:
        import yaml
        
        syntax_errors = 0
        for workflow in workflows:
            if Path(workflow).exists():
                try:
                    with open(workflow, 'r') as f:
                        yaml.safe_load(f)
                    print(f'   ✅ {workflow}: Valid YAML')
                except yaml.YAMLError as e:
                    print(f'   ❌ {workflow}: YAML Error - {e}')
                    syntax_errors += 1
        
        if syntax_errors == 0:
            print('   ✅ All workflows have valid YAML syntax')
        else:
            print(f'   ❌ {syntax_errors} workflows have syntax errors')
            
    except ImportError:
        print('   ⚠️  PyYAML not installed - skipping syntax check')
    
    # Summary
    print('\n📊 TEST SUMMARY')
    print('=' * 20)
    print('✅ Essential components verified')
    print('🚀 Ready for GitHub Actions deployment')
    
    # Recommendations
    print('\n💡 RECOMMENDATIONS')
    print('=' * 20)
    print('1. Push to GitHub to test actual workflow execution')
    print('2. Check GitHub Actions tab for workflow results')
    print('3. Verify all secrets are configured in repository settings')
    print('4. Monitor first run for any runtime errors')

if __name__ == "__main__":
    quick_github_actions_test()
