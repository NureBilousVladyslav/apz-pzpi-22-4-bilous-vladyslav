package com.example.tirepresure.data.model

data class AddTireRequest(
    val vehicle_id: String,
    val label: String,
    val optimal_pressure: Float,
    val pressure_unit: String,
    val current_alert_type: String,
)