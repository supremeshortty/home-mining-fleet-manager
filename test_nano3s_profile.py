#!/usr/bin/env python3
"""Test that Avalon Nano 3S gets the correct thermal profile"""
import config
import thermal

# Test model names that the Nano 3S might report
test_names = [
    "Nano3s",
    "Avalon Nano3s",
    "nano3s",
    "NANO3S"
]

print("Testing thermal profile detection for Avalon Nano 3S:")
print("=" * 60)

for model_name in test_names:
    profile_key = config.get_thermal_profile_key(model_name)
    print(f"\nModel: '{model_name}'")
    print(f"  → Profile Key: {profile_key}")

    if profile_key in thermal.MINER_PROFILES:
        profile = thermal.MINER_PROFILES[profile_key]
        print(f"  → Optimal Temp: {profile.optimal_temp}°C")
        print(f"  → Warning Temp: {profile.warning_temp}°C")
        print(f"  → Critical Temp: {profile.critical_temp}°C")
        print(f"  → Stock Freq: {profile.stock_freq} MHz")
    else:
        print(f"  ✗ Profile '{profile_key}' not found!")

print("\n" + "=" * 60)
print("\nExpected result: All should map to 'AvalonNano3s' with 75°C optimal temp")
