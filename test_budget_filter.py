#!/usr/bin/env python3
"""
Test script to verify budget filtering works correctly
"""

from decimal import Decimal

def test_budget_comparison():
    """Test that demonstrates the issue with string vs decimal comparison"""
    
    # Test data - budget values as strings (how they're stored in DB)
    budgets = ["100", "500", "1000", "1500", "2000"]
    
    # Test min_budget filter
    min_budget = "500"
    
    print("=== Testing String Comparison (WRONG) ===")
    string_filtered = []
    for budget in budgets:
        if budget >= min_budget:  # String comparison
            string_filtered.append(budget)
    print(f"Min budget: {min_budget}")
    print(f"String filtered result: {string_filtered}")
    print("This is wrong because '500' >= '1000' is True in string comparison!")
    
    print("\n=== Testing Decimal Comparison (CORRECT) ===")
    decimal_filtered = []
    min_budget_decimal = Decimal(min_budget)
    for budget in budgets:
        if Decimal(budget) >= min_budget_decimal:  # Decimal comparison
            decimal_filtered.append(budget)
    print(f"Min budget: {min_budget}")
    print(f"Decimal filtered result: {decimal_filtered}")
    print("This is correct - only budgets >= 500 are included")
    
    # Test max_budget filter
    max_budget = "1000"
    
    print("\n=== Testing Max Budget with String Comparison (WRONG) ===")
    string_filtered_max = []
    for budget in budgets:
        if budget <= max_budget:  # String comparison
            string_filtered_max.append(budget)
    print(f"Max budget: {max_budget}")
    print(f"String filtered result: {string_filtered_max}")
    
    print("\n=== Testing Max Budget with Decimal Comparison (CORRECT) ===")
    decimal_filtered_max = []
    max_budget_decimal = Decimal(max_budget)
    for budget in budgets:
        if Decimal(budget) <= max_budget_decimal:  # Decimal comparison
            decimal_filtered_max.append(budget)
    print(f"Max budget: {max_budget}")
    print(f"Decimal filtered result: {decimal_filtered_max}")
    
    # Test range filtering
    print("\n=== Testing Range Filtering (Min: 500, Max: 1500) ===")
    range_filtered = []
    for budget in budgets:
        budget_decimal = Decimal(budget)
        if min_budget_decimal <= budget_decimal <= max_budget_decimal:
            range_filtered.append(budget)
    print(f"Range filtered result: {range_filtered}")

if __name__ == "__main__":
    test_budget_comparison()
