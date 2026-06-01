# Gnoci Control


## action/joint-observation ordering.

┌───────┬────────────────────────────┐
│ Index │           Joint            │
├───────┼────────────────────────────┤
│ 0     │ head__left_yoke            │
├───────┼────────────────────────────┤
│ 1     │ left_yoke__hip             │
├───────┼────────────────────────────┤
│ 2     │ left_hip__upper_leg        │
├───────┼────────────────────────────┤
│ 3     │ left_upper_leg__lower_leg  │
├───────┼────────────────────────────┤
│ 4     │ left_lower_leg__foot       │
├───────┼────────────────────────────┤
│ 5     │ head__right_yoke           │
├───────┼────────────────────────────┤
│ 6     │ right_yoke__hip            │
├───────┼────────────────────────────┤
│ 7     │ right_hip__upper_leg       │
├───────┼────────────────────────────┤
│ 8     │ right_upper_leg__lower_leg │
├───────┼────────────────────────────┤
│ 9     │ right_lower_leg__foot      │
└───────┴────────────────────────────┘

left the right -> head__..._yoke, yoke__hip, hip__upper_leg, upper_leg__lower_leg, lower_leg__foot