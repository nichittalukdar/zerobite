# Transparent Receiver Matching

Each factor is normalized to a score from 0–100, then combined as:

`match = distance × 0.30 + quantity × 0.20 + expiry urgency × 0.25 + receiver need × 0.25`.

- **Distance (30%)**: Haversine straight-line distance against a configurable search radius. This is not a road route; a routing provider can replace it later.
- **Quantity compatibility (20%)**: compares the remaining donation quantity with the receiver's declared `needed_quantity`; unknown needs use a neutral score of 70.
- **Expiry urgency (25%)**: prioritizes non-expired donations that need collection soon; expired donations are excluded.
- **Receiver need (25%)**: uses the receiver's `need_priority` (`low`, `medium`, `high`, `urgent`).

Recommendations are ranked descending and include component scores for transparency. This is a deterministic rule-based ranking, not a trained machine-learning model.
