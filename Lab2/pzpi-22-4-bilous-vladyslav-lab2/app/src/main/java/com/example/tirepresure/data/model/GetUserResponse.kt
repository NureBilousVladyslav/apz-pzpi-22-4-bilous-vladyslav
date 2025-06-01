package com.example.tirepresure.data.model

data class GetUserResponse(
    val user_id: String,
    val name: String,
    val email: String,
    val birthday: String,
    val role: String,
    val created_at: String,
    val email_confirmed: String,
    val vehicles_count: String,
)