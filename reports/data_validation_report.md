# Data Validation Report

Generated at: `2026-08-26T04:37:05+00:00`

## Table Summary

| Table | Rows | Columns | Primary Key | Duplicate Keys | Invalid Coordinates |
|---|---:|---:|---|---:|---:|
| data_sources | 7 | 7 | source_id | 0 | 0 |
| places | 1063 | 29 | place_id | 0 | 10 |
| reviews | 1266 | 13 | review_id | 0 | 0 |
| toilets | 789 | 13 | toilet_id | 0 | 0 |
| tactile_indicators | 357 | 6 | asset_id | 0 | 0 |
| council_data_reference | 172 | 8 | council_id | 0 | 0 |
| reference_map_points | 25 | 5 | point_id | 0 | 0 |
| accessibility_features | 9307 | 8 | feature_id | 0 | 0 |
| conflict_candidates | 74 | 20 | candidate_id | 0 | 0 |
| walking_nodes | 357 | 7 | node_id | 0 | 0 |
| walking_edges | 0 | 7 | edge_id | 0 | 0 |

## Relationship Checks

- `reviews_without_matching_place`: 0
- `features_without_matching_place`: 0
- `conflicts_without_matching_place`: 0

## Top Missing Values

- `data_sources`: no major missing values in checked columns
- `places`: `lat`=10, `lng`=2
- `reviews`: no major missing values in checked columns
- `toilets`: `address`=79, `parking_accessible`=74, `opening_hours`=74, `accessible`=2
- `tactile_indicators`: `road_segment`=41
- `council_data_reference`: `constraints`=157, `last_updated`=137, `town`=122, `accessibility_categories`=24, `format`=24, `link`=22
- `reference_map_points`: no major missing values in checked columns
- `accessibility_features`: `review_id`=4243
- `conflict_candidates`: no major missing values in checked columns
- `walking_nodes`: no major missing values in checked columns
- `walking_edges`: no major missing values in checked columns
