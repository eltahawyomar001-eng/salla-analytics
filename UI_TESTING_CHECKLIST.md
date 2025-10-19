# ✅ UI Redesign Testing Checklist

## Before You Start Testing

### 1. Prerequisites
- [ ] Backend is running (`uvicorn api_main:app --reload`)
- [ ] ngrok tunnel is active (if testing Salla import)
- [ ] Browser window is at least 1280px wide
- [ ] Open browser DevTools (F12) to check for errors

### 2. Clear Cache
```powershell
# Remove Streamlit cache
Remove-Item -Recurse -Force .streamlit\cache -ErrorAction SilentlyContinue

# Start fresh
streamlit run app/main.py --server.headless true
```

---

## 🎨 Phase 1 Testing (Current Implementation)

### Visual Design Tests

#### Sidebar
- [ ] Purple gradient header displays correctly
- [ ] App title and subtitle visible
- [ ] Version badge shows "v2.0.0 - Geographic Analytics Edition"
- [ ] Data status indicator shows (red if no data, green if loaded)
- [ ] Navigation menu items have icons and labels
- [ ] Footer has gradient background

#### Language Toggle
- [ ] 🇬🇧 English button is clickable
- [ ] 🇸🇦 عربي button is clickable
- [ ] Active language button shows as "primary" (blue)
- [ ] Inactive button shows as "secondary" (gray)
- [ ] Clicking toggles language and reloads page
- [ ] Text direction changes for Arabic (RTL)

#### Page Layout
- [ ] Page has brain emoji favicon (🧠)
- [ ] Content area has proper padding
- [ ] No horizontal scrolling
- [ ] Streamlit branding is hidden (footer/menu)
- [ ] Layout is clean and modern

#### Typography
- [ ] Font appears as Inter (or system fallback)
- [ ] Headings are properly sized (H1 > H2 > H3)
- [ ] Text is readable with good contrast
- [ ] Line heights are comfortable

### Functional Tests

#### Session State
- [ ] `st.session_state.language` initializes correctly
- [ ] `st.session_state.rtl` is set based on language
- [ ] `st.session_state.welcome_seen` is False initially
- [ ] `st.session_state.data_loaded` is False initially

#### Theme Injection
- [ ] No CSS errors in browser console
- [ ] CSS variables are defined (check with DevTools)
- [ ] Card styles are applied (if any cards visible)
- [ ] Button styles are modern (rounded, shadowed)

#### Navigation
- [ ] All page links work without errors
- [ ] Selected page is highlighted
- [ ] Page transitions are smooth
- [ ] No broken imports

---

## 🎯 Component Testing (After Implementation)

### KPI Cards
When implemented on pages:
- [ ] Cards have rounded corners (16px radius)
- [ ] Shadow effect visible on hover
- [ ] Delta indicators show correct colors (green=positive, red=negative)
- [ ] Numbers are formatted with commas
- [ ] Help text appears on hover

### Stepper Component
When implemented on Upload page:
- [ ] Horizontal layout with 3 steps
- [ ] Active step is highlighted (purple)
- [ ] Completed steps show checkmark (✓)
- [ ] Connecting lines between steps
- [ ] Step labels are readable

### Card Containers
When implemented:
- [ ] White background with shadow
- [ ] Rounded corners (16px)
- [ ] Hover effect (slight lift)
- [ ] Title has bottom border
- [ ] Footer is separated by top border

### File Uploader
When styled:
- [ ] Dashed border (3px)
- [ ] Folder icon (📁) displays
- [ ] Hover changes border color to purple
- [ ] Drag-over state shows
- [ ] Upload progress is visible

### Badges
When used:
- [ ] Success badge is green background
- [ ] Warning badge is yellow background
- [ ] Error badge is red background
- [ ] Info badge is blue background
- [ ] Text is uppercase and small

### Charts (Plotly)
When implemented:
- [ ] Inter font is used
- [ ] Colors match theme (purple, blue, green)
- [ ] Grid lines are subtle (#F3F4F6)
- [ ] Margins are consistent (60/40/80/60)
- [ ] Hover tooltips have white background
- [ ] Legends are styled consistently

---

## 📱 Responsive Testing

### Desktop (1920px)
- [ ] Layout uses full width appropriately
- [ ] KPI cards in 3-column grid
- [ ] Charts are large and readable
- [ ] Sidebar is comfortable width

### Laptop (1280px)
- [ ] No layout breaking
- [ ] Content fits without scrolling
- [ ] KPI cards in 3-column grid
- [ ] Charts scale properly

### Tablet (768px)
- [ ] KPI cards stack to 2 columns
- [ ] Sidebar still accessible
- [ ] Text remains readable
- [ ] Charts are responsive

### Mobile (375px)
- [ ] Sidebar collapses to hamburger
- [ ] KPI cards stack to 1 column
- [ ] Text size adjusts
- [ ] Charts are scrollable

---

## ♿ Accessibility Testing

### Keyboard Navigation
- [ ] Tab key moves between interactive elements
- [ ] Enter/Space activates buttons
- [ ] Focus indicators are visible (purple outline)
- [ ] Skip to content link available
- [ ] All form inputs are keyboard accessible

### Color Contrast
- [ ] Body text: #374151 on white = 4.57:1 ✓
- [ ] Heading text: #111827 on white = 16.12:1 ✓
- [ ] Button text: white on #7C3AED = 4.51:1 ✓
- [ ] Secondary text: #6B7280 on white = 4.56:1 ✓
- [ ] Link text: #2563EB on white = 5.07:1 ✓

### Screen Reader
- [ ] Page has proper heading structure (H1 → H2 → H3)
- [ ] Images have alt text (if any)
- [ ] Buttons have descriptive labels
- [ ] Forms have labels associated
- [ ] ARIA landmarks are present

### RTL (Arabic)
- [ ] Text aligns to right
- [ ] Padding/margins flip correctly
- [ ] Icons remain in correct position
- [ ] Numbers stay LTR (English numerals)
- [ ] Navigation flows right-to-left

---

## 🚀 Performance Testing

### Initial Load
- [ ] Page loads in < 3 seconds
- [ ] CSS loads without blocking
- [ ] No layout shift (CLS score good)
- [ ] Images load progressively
- [ ] No FOUC (flash of unstyled content)

### Interactions
- [ ] Button clicks are instant
- [ ] Language toggle is smooth
- [ ] Page navigation is fast
- [ ] No janky animations
- [ ] Charts render smoothly

### Browser Console
- [ ] No JavaScript errors
- [ ] No CSS warnings
- [ ] No failed network requests
- [ ] No deprecated API warnings
- [ ] Lighthouse score > 80

---

## 🐛 Common Issues & Fixes

### Issue: Theme CSS not loading
**Fix:** Ensure `inject_theme_css()` is called before any Streamlit components
```python
# In app/main.py, right after set_page_config:
inject_theme_css()
```

### Issue: Components not found
**Fix:** Check imports in page files
```python
from app.ui.components import kpi, kpi_row, card, section
from app.ui.charts import line_trend, bar_compare
```

### Issue: RTL not working
**Fix:** Verify session state
```python
if st.session_state.language == 'ar':
    st.session_state.rtl = True
else:
    st.session_state.rtl = False
```

### Issue: Fonts not loading
**Fix:** Check config.toml
```toml
[theme]
font = "sans serif"  # Streamlit will use system fonts
```

### Issue: Colors not applying
**Fix:** Verify CSS variables in browser DevTools
```css
:root {
  --primary: #7C3AED;  /* Should appear in DevTools */
}
```

---

## 📊 Phase 2 Testing (Upcoming)

### Upload Page Wizard
- [ ] Step 1: File upload dropzone works
- [ ] Step 2: Column mapping is responsive
- [ ] Step 3: Review shows data preview
- [ ] Stepper updates correctly
- [ ] Success toast appears after processing
- [ ] "Jump to insights" CTA works

### Executive Summary
- [ ] KPI row shows 4 metrics
- [ ] Charts use new theme
- [ ] Cards wrap content sections
- [ ] Empty state if no data
- [ ] Expandable "Why/How" sections

### All Pages
- [ ] Consistent header on each page
- [ ] Section dividers used appropriately
- [ ] Charts all use theme
- [ ] No visual regressions
- [ ] Performance remains good

---

## ✅ Sign-Off

### Phase 1 Approval
- [ ] All visual tests pass
- [ ] No console errors
- [ ] Language toggle works
- [ ] Theme loads correctly
- [ ] Ready for Phase 2

**Tested By:** _____________
**Date:** _____________
**Browser:** _____________
**Screen Size:** _____________
**Notes:** _____________

---

## 📝 Test Report Template

```markdown
# Test Report - [Date]

## Environment
- OS: Windows 10/11
- Browser: Chrome 119 / Firefox 120 / Edge 119
- Screen: 1920x1080 / 1280x720
- Streamlit: 1.28.0

## Test Results

### Visual Design: ✅ / ⚠️ / ❌
- Sidebar gradient: ✅
- Language toggle: ✅
- Typography: ✅
- Layout: ✅

### Functionality: ✅ / ⚠️ / ❌
- Theme injection: ✅
- Session state: ✅
- Navigation: ✅
- RTL support: ✅

### Performance: ✅ / ⚠️ / ❌
- Load time: 2.3s ✅
- No console errors: ✅
- Smooth interactions: ✅

## Issues Found
1. [None] or [List issues here]

## Recommendations
1. Proceed to Phase 2
2. [Any other notes]

## Screenshots
[Attach screenshots if available]
```

---

**Last Updated:** October 18, 2025
**Version:** 2.0.0 - Phase 1
