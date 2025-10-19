"""Quick verification script to test Phase 1 implementation.

Run this to verify all imports work before launching the main app.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

print("🧪 Testing Phase 1 Implementation...\n")

# Test 1: Import theme module
try:
    from app.ui.theme import inject_theme_css, get_theme_tokens, DESIGN_TOKENS
    print("✅ Theme module imported successfully")
    print(f"   - Design tokens available: {len(DESIGN_TOKENS)} categories")
except Exception as e:
    print(f"❌ Theme module import failed: {e}")
    sys.exit(1)

# Test 2: Import enhanced components
try:
    from app.ui.components import (
        app_header, section, kpi, kpi_row, card, stepper,
        language_toggle, empty_state, toast_success, toast_error,
        skeleton_loader, badge, progress_bar
    )
    print("✅ Enhanced components imported successfully")
    print("   - 13 modern components available")
except Exception as e:
    print(f"❌ Components import failed: {e}")
    sys.exit(1)

# Test 3: Import chart helpers
try:
    from app.ui.charts import (
        line_trend, bar_compare, pie_distribution, cohort_heatmap,
        scatter_plot, area_chart, funnel_chart, gauge_chart
    )
    print("✅ Chart helpers imported successfully")
    print("   - 8 chart types available")
except Exception as e:
    print(f"❌ Charts import failed: {e}")
    sys.exit(1)

# Test 4: Verify config.toml
try:
    config_path = Path(__file__).parent / ".streamlit" / "config.toml"
    if config_path.exists():
        with open(config_path, 'r') as f:
            config_content = f.read()
            if "#7C3AED" in config_content:
                print("✅ Config.toml updated with new theme colors")
            else:
                print("⚠️  Config.toml exists but may need color update")
    else:
        print("⚠️  Config.toml not found")
except Exception as e:
    print(f"⚠️  Config check failed: {e}")

# Test 5: Check documentation files
docs = [
    "UI_REDESIGN_STATUS.md",
    "UI_COMPONENT_REFERENCE.md",
    "UI_TESTING_CHECKLIST.md"
]
for doc in docs:
    doc_path = Path(__file__).parent / doc
    if doc_path.exists():
        print(f"✅ Documentation: {doc}")
    else:
        print(f"⚠️  Missing: {doc}")

print("\n" + "="*60)
print("🎉 PHASE 1 VERIFICATION COMPLETE!")
print("="*60)
print("\n✅ All critical imports working")
print("✅ Theme system ready")
print("✅ Components library loaded")
print("✅ Chart helpers available")
print("\n🚀 Ready to launch:")
print("   streamlit run app/main.py")
print("\n📖 Read documentation:")
print("   • UI_COMPONENT_REFERENCE.md - Usage examples")
print("   • UI_TESTING_CHECKLIST.md - Test cases")
print("   • UI_REDESIGN_STATUS.md - Roadmap")
