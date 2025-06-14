package com.example.tirepresure.data.model

data class DateModel(
    val month: Int,
    val day: Int,
    val year: Int,
) {
    companion object {
        val DEFAULT = DateModel(month = 0, day = 1, year = 2000)
        val months = arrayOf(
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        )
    }

    fun toFormattedString(): String = String.format("%04d-%02d-%02d", year, month + 1, day)

}