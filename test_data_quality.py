"""Test data quality fixes for concatenated column values."""

import pandas as pd
import sys
from pathlib import Path

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.ui.pages.upload import _clean_concatenated_columns, _extract_first_value


def test_extract_first_value():
    """Test extracting first value from concatenated text."""
    
    # Test case 1: Normal text (should return unchanged)
    assert _extract_first_value("Saudi Arabia") == "Saudi Arabia"
    
    # Test case 2: Concatenated single word
    result = _extract_first_value("KuwaitKuwaitKuwaitKuwaitKuwait")
    assert result == "Kuwait", f"Expected 'Kuwait', got '{result}'"
    
    # Test case 3: Concatenated two-word phrase
    result = _extract_first_value("Saudi ArabiaSaudi ArabiaSaudi ArabiaSaudi Arabia")
    assert result == "Saudi Arabia", f"Expected 'Saudi Arabia', got '{result}'"
    
    # Test case 4: Short text (should return unchanged)
    assert _extract_first_value("USA") == "USA"
    
    # Test case 5: Mixed case with spaces
    result = _extract_first_value("New York New York New York")
    assert result == "New York", f"Expected 'New York', got '{result}'"
    
    print("✅ All _extract_first_value tests passed!")


def test_clean_concatenated_columns():
    """Test cleaning entire dataframe with concatenated columns."""
    
    # Create test dataframe with corrupted data
    df = pd.DataFrame({
        'order_id': ['001', '002', '003', '004'],
        'country': [
            'Saudi ArabiaSaudi ArabiaSaudi ArabiaSaudi ArabiaSaudi Arabia',
            'KuwaitKuwaitKuwaitKuwait',
            'Saudi Arabia',  # Normal value
            'BahrainBahrainBahrainBahrainBahrainBahrainBahrain'
        ],
        'city': [
            'Riyadh',  # Normal value
            'Kuwait CityKuwait CityKuwait City',
            'Jeddah',
            'Manama'
        ],
        'order_total': [100.0, 200.0, 300.0, 400.0]
    })
    
    print("\n📊 Original DataFrame:")
    print(df)
    print(f"\nCountry column values:")
    for val in df['country']:
        print(f"  - Length: {len(val)}, Value: {val[:50]}...")
    
    # Clean the dataframe
    df_clean = _clean_concatenated_columns(df)
    
    print("\n✨ Cleaned DataFrame:")
    print(df_clean)
    print(f"\nCleaned country column values:")
    for val in df_clean['country']:
        print(f"  - Length: {len(val)}, Value: {val}")
    
    # Verify cleaning worked
    assert df_clean.loc[0, 'country'] == 'Saudi Arabia', f"Row 0 not cleaned: {df_clean.loc[0, 'country']}"
    assert df_clean.loc[1, 'country'] == 'Kuwait', f"Row 1 not cleaned: {df_clean.loc[1, 'country']}"
    assert df_clean.loc[2, 'country'] == 'Saudi Arabia', f"Row 2 changed: {df_clean.loc[2, 'country']}"
    assert df_clean.loc[3, 'country'] == 'Bahrain', f"Row 3 not cleaned: {df_clean.loc[3, 'country']}"
    
    # Verify numeric columns unchanged
    assert df_clean['order_total'].equals(df['order_total']), "Numeric column was modified"
    
    print("\n✅ All _clean_concatenated_columns tests passed!")


def test_real_world_scenario():
    """Test with realistic data corruption scenario."""
    
    # Simulate the exact error from user's file
    corrupted_value = "Saudi Arabia" * 300  # 300 repetitions
    
    df = pd.DataFrame({
        'order_id': ['001'],
        'country': [corrupted_value],
        'order_total': [1500.0]
    })
    
    print(f"\n🔴 Corrupted value length: {len(corrupted_value)} characters")
    print(f"   Preview: {corrupted_value[:100]}...")
    
    df_clean = _clean_concatenated_columns(df)
    
    cleaned_value = str(df_clean.loc[0, 'country'])
    print(f"\n🟢 Cleaned value length: {len(cleaned_value)} characters")
    print(f"   Value: {cleaned_value}")
    
    assert cleaned_value == "Saudi Arabia", f"Expected 'Saudi Arabia', got '{cleaned_value}'"
    assert len(cleaned_value) < 20, f"Cleaned value still too long: {len(cleaned_value)}"
    
    print("\n✅ Real-world scenario test passed!")


if __name__ == '__main__':
    print("=" * 60)
    print("🧪 Testing Data Quality Fixes")
    print("=" * 60)
    
    try:
        test_extract_first_value()
        test_clean_concatenated_columns()
        test_real_world_scenario()
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED! Data quality fix is working correctly.")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
