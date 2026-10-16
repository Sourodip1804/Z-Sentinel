# Feature contract `txn_features_v1`

Shared by training, simulation, and `/api/predict`.

| Field | Type | Inference use | Notes |
| --- | --- | --- | --- |
| `amount` | float > 0 | yes | Required |
| `currency` | ISO code | stored | Not a model feature |
| `merchant_category` | enum | yes | grocery, electronics, travel, restaurant, fuel, online, other |
| `hour_of_day` | 0-23 | yes | Imputed to 12 if missing |
| `device_novelty` | 0-1 | yes | Imputed to 0 if missing |
| `location_deviation` | 0-1 | yes | Imputed to 0.20 if missing |
| `transaction_velocity` | >= 0 | yes | Caller-supplied prior-window count; imputed to 2 if missing |
| `unusual_time` | 0-1 | yes | Derived from hour if omitted |
| `channel` | enum | stored | online, pos, atm, other |
| `is_fraud` | 0/1 | **training only** | Never sent to the live model |

Unavailable live fields are listed in `unavailable_fields` / `imputed_fields`. PayPal capture webhooks do not include device, location, or velocity; those stay unavailable rather than being invented.
