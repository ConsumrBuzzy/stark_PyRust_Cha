#!/usr/bin/env python3
"""
GitHub Actions Test Report - Complete Validation
"""

import os
import sys
import yaml
from pathlib import Path

def generate_test_report():
    print('🧪 GITHUB ACTIONS TEST REPORT')
    print('=' * 50)
    
    # Test 1: Workflow Validation
    print('1️⃣ WORKFLOW VALIDATION')
    print('=' * 25)
    
    workflows = [
        '.github/workflows/iron_to_steel_auto.yml',
        '.github/workflows/pulse.yml',
        '.github/workflows/ghost_recovery.yml',
        '.github/workflows/full_auto_mining.yml'
    ]
    
    valid_workflows = 0
    for workflow in workflows:
        try:
            with open(workflow, 'r') as f:
                yaml.safe_load(f)
            print(f'   ✅ {workflow}: VALID YAML')
            valid_workflows += 1
        except yaml.YAMLError as e:
            print(f'   ❌ {workflow}: YAML ERROR - {e}')
        except FileNotFoundError:
            print(f'   ❌ {workflow}: FILE NOT FOUND')
    
    print(f'   📊 Valid Workflows: {valid_workflows}/{len(workflows)}')
    
    # Test 2: Act Tool Validation
    print('\n2️⃣ ACT TOOL VALIDATION')
    print('=' * 25)
    
    act_path = Path('./act-tools/act.exe')
    if act_path.exists():
        print('   ✅ Act Tool: INSTALLED')
        
        # Run act validation
        import subprocess
        try:
            result = subprocess.run(
                [str(act_path), '--validate'],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                print('   ✅ Act Validation: PASSED')
            else:
                print('   ❌ Act Validation: FAILED')
        except Exception as e:
            print(f'   ❌ Act Validation Error: {e}')
    else:
        print('   ❌ Act Tool: NOT FOUND')
    
    # Test 3: Script Availability
    print('\n3️⃣ SCRIPT AVAILABILITY')
    print('=' * 25)
    
    scripts = [
        'scripts/check_threshold.py',
        'scripts/step_b_fuel_alert.py',
        'scripts/step_e_yield_report.py',
        'scripts/test_telegram.py',
        'scripts/send_status_report.py',
        'scripts/telegram_pulse.py',
        'scripts/clawback_cost_analysis.py'
    ]
    
    available_scripts = 0
    for script in scripts:
        if Path(script).exists():
            print(f'   ✅ {script}: AVAILABLE')
            available_scripts += 1
        else:
            print(f'   ❌ {script}: MISSING')
    
    print(f'   📊 Available Scripts: {available_scripts}/{len(scripts)}')
    
    # Test 4: GitHub Actions Features
    print('\n4️⃣ GITHUB ACTIONS FEATURES')
    print('=' * 30)
    
    features = {
        'Scheduled Triggers': False,
        'Manual Dispatch': False,
        'Environment Variables': False,
        'Conditional Execution': False,
        'Matrix Strategy': False,
        'Secret Management': False
    }
    
    # Check workflows for features
    for workflow in workflows:
        if Path(workflow).exists():
            with open(workflow, 'r') as f:
                content = f.read()
                
                if 'schedule:' in content:
                    features['Scheduled Triggers'] = True
                if 'workflow_dispatch:' in content:
                    features['Manual Dispatch'] = True
                if 'env:' in content:
                    features['Environment Variables'] = True
                if 'if:' in content:
                    features['Conditional Execution'] = True
                if 'matrix:' in content:
                    features['Matrix Strategy'] = True
                if 'secrets.' in content:
                    features['Secret Management'] = True
    
    for feature, status in features.items():
        print(f'   {"✅" if status else "❌"} {feature}: {"ENABLED" if status else "NOT FOUND"}')
    
    # Test 5: Integration Points
    print('\n5️⃣ INTEGRATION POINTS')
    print('=' * 25)
    
    integrations = {
        'Telegram Bot': False,
        'StarkNet RPC': False,
        'Base Network': False,
        'Rust Build': False,
        'Python Dependencies': False
    }
    
    # Check .env for integrations
    env_path = Path('.env')
    if env_path.exists():
        with open(env_path, 'r', encoding='utf-8', errors='ignore') as f:
            env_content = f.read()
            
            if 'TELEGRAM_BOT_TOKEN' in env_content:
                integrations['Telegram Bot'] = True
            if 'STARKNET_RPC_URL' in env_content:
                integrations['StarkNet RPC'] = True
            if 'BASE_RPC_URL' in env_content:
                integrations['Base Network'] = True
    
    # Check for Rust
    if Path('rust-core/Cargo.toml').exists():
        integrations['Rust Build'] = True
    
    # Check for Python dependencies
    if Path('requirements.txt').exists():
        integrations['Python Dependencies'] = True
    
    for integration, status in integrations.items():
        print(f'   {"✅" if status else "❌"} {integration}: {"CONFIGURED" if status else "NOT CONFIGURED"}')
    
    # Summary
    print('\n📊 TEST SUMMARY')
    print('=' * 20)
    
    total_tests = len(workflows) + len(scripts) + len(features) + len(integrations)
    passed_tests = valid_workflows + available_scripts + sum(features.values()) + sum(integrations.values())
    
    print(f'🧪 Total Tests: {total_tests}')
    print(f'✅ Passed: {passed_tests}')
    print(f'❌ Failed: {total_tests - passed_tests}')
    print(f'📊 Success Rate: {(passed_tests / total_tests) * 100:.1f}%')
    
    # Recommendations
    print('\n💡 RECOMMENDATIONS')
    print('=' * 20)
    
    if passed_tests == total_tests:
        print('🎉 ALL TESTS PASSED!')
        print('✅ Ready for GitHub Actions deployment')
        print('🚀 Push to repository to activate workflows')
    else:
        print('⚠️  Some tests failed')
        print('🔧 Fix issues before deploying')
    
    print('\n📋 NEXT STEPS')
    print('=' * 15)
    print('1. Push changes to GitHub')
    print('2. Configure repository secrets')
    print('3. Monitor first workflow run')
    print('4. Check Telegram notifications')
    print('5. Verify Iron → Steel auto-execution')

if __name__ == "__main__":
    generate_test_report()
