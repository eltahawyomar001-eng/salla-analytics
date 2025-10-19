# 🔄 Dynamic Mapper Enhancement Plan

## 🎯 Current Problems (Static Implementation)

### 1. **Hardcoded Schema**
```python
# ❌ STATIC - Can't adapt to new fields
CANONICAL_FIELDS = {
    "order_id": {"required": True, "type": "string"},
    "order_date": {"required": True, "type": "datetime"},
    # ... 20+ hardcoded fields
}
```

**Problems**:
- Can't add new fields without code changes
- Different platforms (Shopify, WooCommerce, Magento) have different fields
- Custom fields from Salla extensions ignored
- Hard to maintain across updates

---

### 2. **Static Synonyms**
```yaml
# ❌ STATIC - header_synonyms.yaml
synonyms:
  order_id:
    english: ["Order ID", "Order Number", "Reference"]
    arabic: ["رقم الطلب", "معرف الطلب"]
```

**Problems**:
- New synonym requires file edit + deployment
- Can't learn from user corrections
- Platform-specific terms not covered
- Language variations limited

---

### 3. **No Learning System**
- User manually fixes mappings every time
- Same corrections needed for similar files
- No memory of previous successful mappings
- Doesn't improve over time

---

### 4. **No Flexibility**
- Can't handle custom fields (e.g., "Gift Message", "Loyalty Points")
- Doesn't detect optional fields automatically
- Can't adapt to different export formats
- One-size-fits-all approach

---

## ✅ Dynamic Solution (Production-Ready)

### **Architecture Overview**

```
┌─────────────────────┐
│  Schema Registry    │ ← Dynamic field definitions
│  (JSON Config)      │ ← Platform templates
└──────────┬──────────┘
           │
┌──────────▼──────────┐
│  Smart Mapper       │ ← AI-powered detection
│  (ML + Fuzzy Match) │ ← Learn from corrections
└──────────┬──────────┘
           │
┌──────────▼──────────┐
│  Mapping Store      │ ← Save user corrections
│  (SQLite/JSON)      │ ← Build knowledge base
└─────────────────────┘
```

---

## 🚀 Implementation Plan

### **Phase 1: Dynamic Schema Registry** (Day 1)

#### A. Flexible Field Definitions
```python
# ✅ DYNAMIC - schema_registry.json
{
  "platforms": {
    "salla": {
      "core_fields": {
        "order_id": {
          "required": true,
          "type": "string",
          "validators": ["non_empty", "unique"],
          "synonyms": ["رقم الطلب", "Order ID", "Order Number"],
          "auto_detect_patterns": ["^order", "^رقم", "id$", "number$"],
          "sample_values": ["ORD-123", "12345"]
        },
        "order_date": {
          "required": true,
          "type": "datetime",
          "validators": ["valid_date", "not_future"],
          "synonyms": ["تاريخ الطلب", "Order Date", "Created At"],
          "auto_detect_patterns": ["date", "تاريخ", "created", "time"],
          "formats": ["%Y-%m-%d", "%d/%m/%Y", "%Y-%m-%d %H:%M:%S"]
        }
      },
      "optional_fields": {
        "gift_message": {
          "type": "string",
          "category": "custom",
          "auto_detect": true
        }
      }
    },
    "shopify": {
      "core_fields": {
        "order_id": {
          "synonyms": ["Name", "Order", "#"],
          "auto_detect_patterns": ["^#\\d+", "^order"]
        }
      }
    }
  },
  "custom_fields": {
    "allow_detection": true,
    "max_custom_fields": 50,
    "categories": ["marketing", "logistics", "custom"]
  }
}
```

#### B. Schema Registry Class
```python
class SchemaRegistry:
    """Dynamic schema management with multi-platform support."""
    
    def __init__(self):
        self.schemas = self._load_schemas()
        self.custom_fields = {}
    
    def get_platform_schema(self, platform: str = "salla") -> dict:
        """Get schema for specific platform (Salla, Shopify, etc.)"""
        return self.schemas['platforms'].get(platform, {})
    
    def add_custom_field(self, field_name: str, config: dict):
        """Dynamically add custom field"""
        self.custom_fields[field_name] = config
        self._save_custom_fields()
    
    def detect_platform(self, columns: List[str]) -> str:
        """Auto-detect platform from column names"""
        # Score each platform based on column matches
        # Return best match
        pass
    
    def get_required_fields(self, platform: str = "salla") -> List[str]:
        """Get required fields for platform"""
        schema = self.get_platform_schema(platform)
        return [
            field for field, config in schema['core_fields'].items()
            if config.get('required', False)
        ]
    
    def suggest_field_type(self, column_name: str, sample_data: pd.Series) -> str:
        """Intelligently detect field type from data"""
        # Analyze sample values, patterns, statistics
        pass
```

---

### **Phase 2: ML-Powered Smart Mapper** (Day 2)

#### A. Intelligent Column Detection
```python
class SmartMapper:
    """AI-powered column mapping with learning."""
    
    def __init__(self, schema_registry: SchemaRegistry):
        self.registry = schema_registry
        self.learning_store = MappingLearningStore()
        self.ml_matcher = MLColumnMatcher()
    
    def auto_detect_columns(
        self, 
        df: pd.DataFrame,
        platform: str = "auto",
        use_ml: bool = True
    ) -> Tuple[Dict[str, str], Dict[str, float]]:
        """
        Multi-strategy column detection:
        1. Exact match (100% confidence)
        2. Fuzzy matching (80-99% confidence)
        3. Pattern matching (70-90% confidence)
        4. ML prediction (60-80% confidence)
        5. User history (90-100% confidence if seen before)
        """
        
        # Auto-detect platform if needed
        if platform == "auto":
            platform = self.registry.detect_platform(df.columns)
        
        mappings = {}
        confidence = {}
        
        # Strategy 1: Check learning store (previous mappings)
        learned = self.learning_store.get_mappings(
            columns=list(df.columns),
            platform=platform
        )
        
        # Strategy 2: Fuzzy + Pattern matching
        fuzzy_matches = self._fuzzy_match(df.columns, platform)
        
        # Strategy 3: ML predictions (if enabled)
        if use_ml:
            ml_matches = self.ml_matcher.predict(df, platform)
        
        # Combine strategies with confidence weighting
        final_mappings = self._combine_strategies(
            learned, fuzzy_matches, ml_matches
        )
        
        return final_mappings
    
    def learn_from_correction(
        self, 
        source_column: str,
        canonical_field: str,
        platform: str = "salla"
    ):
        """Learn from user corrections to improve future mappings"""
        self.learning_store.save_mapping(
            source=source_column,
            target=canonical_field,
            platform=platform,
            confidence=1.0,
            source="user_correction"
        )
```

#### B. ML Column Matcher (Simple Implementation)
```python
class MLColumnMatcher:
    """Simple ML-based column matching using TF-IDF + cosine similarity"""
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            analyzer='char_wb',
            ngram_range=(2, 4)
        )
        self.trained = False
    
    def train(self, known_mappings: List[Tuple[str, str]]):
        """Train on known column name → canonical field mappings"""
        if len(known_mappings) < 10:
            return  # Need minimum data
        
        source_columns = [m[0] for m in known_mappings]
        self.vectorizer.fit(source_columns)
        self.trained = True
    
    def predict(self, columns: List[str], canonical_fields: List[str]) -> Dict:
        """Predict canonical field for each column"""
        if not self.trained:
            return {}
        
        # Vectorize input columns
        column_vectors = self.vectorizer.transform(columns)
        field_vectors = self.vectorizer.transform(canonical_fields)
        
        # Calculate cosine similarity
        similarities = cosine_similarity(column_vectors, field_vectors)
        
        # Get best matches above threshold
        predictions = {}
        for i, col in enumerate(columns):
            best_idx = similarities[i].argmax()
            confidence = similarities[i][best_idx]
            
            if confidence > 0.6:  # 60% threshold
                predictions[canonical_fields[best_idx]] = {
                    "source": col,
                    "confidence": confidence,
                    "method": "ml"
                }
        
        return predictions
```

---

### **Phase 3: Learning & Memory System** (Day 3)

#### A. Mapping Store (SQLite)
```python
# Database schema
class MappingHistory(SQLModel, table=True):
    """Store successful mappings for learning"""
    id: Optional[int] = Field(default=None, primary_key=True)
    source_column: str
    canonical_field: str
    platform: str = "salla"
    confidence: float
    source_type: str  # "auto", "user_correction", "ml"
    file_hash: str  # Hash of column names for similarity
    usage_count: int = 0
    success_rate: float = 1.0
    created_at: datetime = Field(default_factory=datetime.now)
    last_used: datetime = Field(default_factory=datetime.now)

class MappingLearningStore:
    """Persistent storage for mapping knowledge"""
    
    def __init__(self, db_path: str = "mappings.db"):
        self.engine = create_engine(f"sqlite:///{db_path}")
        SQLModel.metadata.create_all(self.engine)
    
    def save_mapping(self, source: str, target: str, **kwargs):
        """Save a successful mapping"""
        with Session(self.engine) as session:
            mapping = MappingHistory(
                source_column=source,
                canonical_field=target,
                **kwargs
            )
            session.add(mapping)
            session.commit()
    
    def get_mappings(
        self, 
        columns: List[str],
        platform: str = "salla",
        min_confidence: float = 0.8
    ) -> Dict[str, Tuple[str, float]]:
        """Retrieve best mappings based on history"""
        with Session(self.engine) as session:
            # Calculate file hash for similarity
            file_hash = self._calculate_hash(columns)
            
            # Find similar previous mappings
            matches = session.exec(
                select(MappingHistory)
                .where(MappingHistory.platform == platform)
                .where(MappingHistory.confidence >= min_confidence)
                .order_by(MappingHistory.usage_count.desc())
            ).all()
            
            # Return best matches
            results = {}
            for match in matches:
                if match.source_column in columns:
                    results[match.canonical_field] = (
                        match.source_column,
                        match.confidence
                    )
            
            return results
    
    def increment_usage(self, source: str, target: str):
        """Increment usage counter for successful mapping"""
        # Update usage_count and last_used
        pass
```

---

### **Phase 4: Dynamic UI** (Day 4)

#### A. Smart Mapping Interface
```python
def render_smart_mapping_ui(df: pd.DataFrame):
    """Dynamic mapping UI with learning feedback"""
    
    st.markdown("### 🧠 Smart Column Mapping")
    
    # Initialize smart mapper
    registry = SchemaRegistry()
    mapper = SmartMapper(registry)
    
    # Auto-detect platform
    detected_platform = registry.detect_platform(df.columns)
    st.info(f"🔍 Detected platform: **{detected_platform.title()}**")
    
    # Get smart mappings
    auto_mappings, confidence = mapper.auto_detect_columns(
        df, 
        platform=detected_platform
    )
    
    # Show confidence summary
    high_conf = sum(1 for c in confidence.values() if c >= 0.9)
    medium_conf = sum(1 for c in confidence.values() if 0.7 <= c < 0.9)
    low_conf = sum(1 for c in confidence.values() if c < 0.7)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("High Confidence", high_conf, "≥90%")
    with col2:
        st.metric("Medium Confidence", medium_conf, "70-89%")
    with col3:
        st.metric("Needs Review", low_conf, "<70%")
    
    # Group fields by confidence
    high_confidence_fields = {
        k: v for k, v in auto_mappings.items() 
        if confidence.get(k, 0) >= 0.9
    }
    
    medium_confidence_fields = {
        k: v for k, v in auto_mappings.items()
        if 0.7 <= confidence.get(k, 0) < 0.9
    }
    
    low_confidence_fields = {
        k: v for k, v in auto_mappings.items()
        if confidence.get(k, 0) < 0.7
    }
    
    # Show high confidence (auto-approved)
    with st.expander("✅ High Confidence Mappings (Auto-Approved)", expanded=False):
        for canonical, source in high_confidence_fields.items():
            conf = confidence[canonical]
            st.success(f"**{canonical}** ← `{source}` ({conf*100:.0f}% confidence)")
    
    # Show medium confidence (review recommended)
    with st.expander("⚠️ Medium Confidence Mappings (Review Recommended)", expanded=True):
        for canonical, source in medium_confidence_fields.items():
            conf = confidence[canonical]
            
            col1, col2, col3 = st.columns([2, 2, 1])
            with col1:
                st.write(f"**{canonical}**")
            with col2:
                # Allow user to change mapping
                new_source = st.selectbox(
                    f"Source for {canonical}",
                    options=[""] + list(df.columns),
                    index=list(df.columns).index(source) + 1 if source in df.columns else 0,
                    key=f"map_{canonical}"
                )
                if new_source and new_source != source:
                    # User corrected mapping - learn from it!
                    mapper.learn_from_correction(new_source, canonical, detected_platform)
                    auto_mappings[canonical] = new_source
            with col3:
                st.caption(f"{conf*100:.0f}%")
    
    # Show unmapped fields
    unmapped_required = registry.get_required_fields(detected_platform)
    unmapped_required = [f for f in unmapped_required if f not in auto_mappings]
    
    if unmapped_required:
        with st.expander("❌ Missing Required Fields", expanded=True):
            st.error(f"The following required fields need mapping:")
            for field in unmapped_required:
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.write(f"**{field}** ⚠️")
                with col2:
                    auto_mappings[field] = st.selectbox(
                        f"Map {field} to:",
                        options=[""] + list(df.columns),
                        key=f"req_{field}"
                    )
    
    # Custom fields detection
    custom_fields = [col for col in df.columns if col not in auto_mappings.values()]
    if custom_fields:
        with st.expander(f"➕ Custom Fields Detected ({len(custom_fields)})", expanded=False):
            st.info("These columns don't match standard fields. You can add them as custom fields.")
            
            for custom_col in custom_fields[:10]:  # Show first 10
                if st.checkbox(f"Include `{custom_col}` as custom field", key=f"custom_{custom_col}"):
                    field_type = st.selectbox(
                        f"Type for {custom_col}:",
                        options=["string", "number", "date", "boolean"],
                        key=f"type_{custom_col}"
                    )
                    
                    # Add to registry
                    registry.add_custom_field(custom_col, {
                        "type": field_type,
                        "category": "custom",
                        "source": custom_col
                    })
    
    return auto_mappings, confidence
```

---

### **Phase 5: Platform Templates** (Day 5)

#### A. Pre-built Templates
```python
PLATFORM_TEMPLATES = {
    "salla": {
        "name": "Salla (Saudi Arabia)",
        "language": "ar",
        "currency": "SAR",
        "date_format": "%Y-%m-%d",
        "common_fields": ["رقم الطلب", "تاريخ الطلب", "اسم العميل"],
        "skip_patterns": ["Unnamed:", "Total", "Notes"]
    },
    "shopify": {
        "name": "Shopify",
        "language": "en",
        "currency": "USD",
        "date_format": "%Y-%m-%d %H:%M:%S",
        "common_fields": ["Name", "Email", "Financial Status"],
        "skip_patterns": ["Lineitem", "Billing", "Shipping"]
    },
    "woocommerce": {
        "name": "WooCommerce",
        "language": "en",
        "currency": "USD",
        "date_format": "%Y-%m-%d",
        "common_fields": ["Order ID", "Order Date", "Status"],
        "skip_patterns": []
    }
}

def suggest_template(columns: List[str]) -> str:
    """Auto-suggest platform template based on columns"""
    scores = {}
    
    for platform, config in PLATFORM_TEMPLATES.items():
        score = 0
        for common_field in config['common_fields']:
            if any(common_field.lower() in col.lower() for col in columns):
                score += 1
        
        scores[platform] = score / len(config['common_fields'])
    
    best_platform = max(scores.items(), key=lambda x: x[1])
    return best_platform[0] if best_platform[1] > 0.3 else "custom"
```

---

## 🎯 Benefits of Dynamic Approach

### **For Users**:
- ✅ Faster mapping (learns from corrections)
- ✅ Works with ANY e-commerce platform
- ✅ Handles custom fields automatically
- ✅ Less manual work over time
- ✅ Platform auto-detection

### **For Developers**:
- ✅ No code changes for new fields
- ✅ Easy to add new platforms
- ✅ Configuration-driven (JSON/YAML)
- ✅ Extensible architecture
- ✅ Testable components

### **For Business**:
- ✅ Production-ready for any client
- ✅ Self-improving system
- ✅ Multi-tenant capable
- ✅ Scalable to 100+ platforms
- ✅ Lower maintenance cost

---

## 📊 Migration Strategy (Zero Downtime)

### **Week 1: Parallel Implementation**
1. Build new dynamic mapper alongside existing
2. Add feature flag: `USE_DYNAMIC_MAPPER = False`
3. Test with sample data
4. Compare results with static mapper

### **Week 2: Gradual Rollout**
1. Enable for new uploads only
2. Keep static mapper as fallback
3. Monitor success rate
4. Collect user feedback

### **Week 3: Full Migration**
1. Enable by default
2. Deprecate static mapper
3. Clean up old code
4. Update documentation

---

## 🚀 Quick Wins (Implement First)

### **Priority 1: Schema Registry** (4 hours)
- Extract CANONICAL_FIELDS to JSON
- Add platform support
- Enable custom field registration

### **Priority 2: Learning Store** (4 hours)
- SQLite database for mappings
- Save user corrections
- Retrieve previous mappings

### **Priority 3: Smart UI** (4 hours)
- Confidence indicators
- Quick review interface
- Custom field detection

**Total**: 12 hours to transform static → dynamic!

---

## 📝 Summary

**Current State**: Static, hardcoded, single-platform  
**Target State**: Dynamic, learning, multi-platform  
**Migration Risk**: LOW (parallel implementation)  
**User Impact**: POSITIVE (less work, more accuracy)  
**Development Time**: ~3-5 days  

**Ready to implement?** Let me know and I'll start with Priority 1!
