## Summary

Add ensemble learning to combine multiple models for better predictions.

## Methods
- **voting**: Majority vote (classification) or average (regression)  
- **stacking**: Base model predictions as features for meta-learner

## Endpoints
- `POST /model/ensemble/create` - Register ensemble
- `POST /model/ensemble/predict` - Ensemble prediction

## Backend Lint: Pass