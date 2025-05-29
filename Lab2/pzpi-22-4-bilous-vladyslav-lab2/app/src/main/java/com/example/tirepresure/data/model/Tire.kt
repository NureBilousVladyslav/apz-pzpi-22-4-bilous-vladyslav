package com.example.tirepresure.data.model

data class Tire(
    val tire_id: String,
    val vehicle_id: String?,
    val label: String,
    val pressure_unit: String,
    val optimal_pressure: Float,
    val sensor_code: String,
    val installed_at: String,
    val current_alert_type: String,
    val current_pressure: Float,
    val pressure_updated_at: String,
)