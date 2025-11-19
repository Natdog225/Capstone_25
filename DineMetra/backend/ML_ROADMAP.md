# ML Development Roadmap

## Week 1: Foundation ✓
- [x] Set up ml_service.py with baseline predictions
- [x] Create prediction schemas
- [ ] Document feature requirements
- [ ] Share API contract with Ariel

## Week 2: Wait Time Model
- [ ] Analyze wait_times table data
- [ ] Feature engineering (rolling averages, time patterns)
- [ ] Train Random Forest model
- [ ] Validate on test set (target: 80%+ accuracy)
- [ ] Integrate with API

## Week 3: Additional Models
- [ ] Build busyness classification model
- [ ] Build item sales forecasting (time series)
- [ ] Add confidence scoring
- [ ] Optimize prediction speed

## Week 4: Polish
- [ ] Add error handling for edge cases
- [ ] Model performance documentation
- [ ] Demo preparation

## Feature Requirements

### Wait Time Model Needs:
- Historical wait_times data (quoted vs actual)
- Current occupancy snapshot
- Time features (hour, day_of_week)
- Party size distribution

### Data Quality Checks:
- [ ] Verify no negative wait times
- [ ] Check for missing timestamps
- [ ] Validate party_size range (1-20)