#!/usr/bin/env python3
"""Test the Avalon stats parser"""
import re

def parse_avalon_stats(stats_str):
    """Parse Avalon stats"""
    result = {}

    # Temperature
    if match := re.search(r'TAvg\[(\d+)\]', stats_str):
        result['temp'] = int(match.group(1))

    # Max temperature
    if match := re.search(r'TMax\[(\d+)\]', stats_str):
        result['temp_max'] = int(match.group(1))

    # Fan percentage
    if match := re.search(r'FanR\[(\d+)%\]', stats_str):
        result['fan_percent'] = int(match.group(1))

    # Chip type/core
    if match := re.search(r'Core\[([^\]]+)\]', stats_str):
        result['chip_type'] = match.group(1)

    # Power - PS field format: PS[v1 v2 power v4 v5 v6 v7]
    if match := re.search(r'PS\[(\d+)\s+(\d+)\s+(\d+)', stats_str):
        power_mw = int(match.group(3))
        result['power'] = power_mw / 1000.0

    # Model/Version
    if match := re.search(r'Ver\[([^\]]+)\]', stats_str):
        model_str = match.group(1)
        if '-' in model_str:
            result['model'] = model_str.split('-')[0]
        else:
            result['model'] = model_str

    return result

# Sample Avalon stats string
stats_str = "Ver[Nano3s-25021401_56abae7] Core[A3197S] TAvg[90] TMax[98] FanR[45%] PS[0 0 27521 4 0 3652 133]"

result = parse_avalon_stats(stats_str)
print("Parsed Avalon stats:")
print(f"  Temperature: {result.get('temp')}°C")
print(f"  Max Temp: {result.get('temp_max')}°C")
print(f"  Fan: {result.get('fan_percent')}%")
print(f"  Power: {result.get('power')} W")
print(f"  Chip Type: {result.get('chip_type')}")
print(f"  Model: {result.get('model')}")
