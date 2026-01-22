#!/usr/bin/env python3
"""Test the Avalon stats parser"""
import sys
sys.path.insert(0, '.')

from miners.cgminer import CGMinerAPIHandler

handler = CGMinerAPIHandler()

# Sample Avalon stats string
stats_str = "Ver[Nano3s-25021401_56abae7] Core[A3197S] TAvg[90] TMax[98] FanR[45%] PS[0 0 27521 4 0 3652 133]"

result = handler._parse_avalon_stats(stats_str)
print("Parsed Avalon stats:")
print(f"  Temperature: {result.get('temp')}°C")
print(f"  Max Temp: {result.get('temp_max')}°C")
print(f"  Fan: {result.get('fan_percent')}%")
print(f"  Power: {result.get('power')} W")
print(f"  Chip Type: {result.get('chip_type')}")
print(f"  Model: {result.get('model')}")
