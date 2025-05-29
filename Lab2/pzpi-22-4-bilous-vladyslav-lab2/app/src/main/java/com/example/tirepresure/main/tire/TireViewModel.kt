package com.example.tirepresure.main.tire

import android.util.Log
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.tirepresure.data.api.RetrofitInstance
import com.example.tirepresure.data.model.AddTireRequest
import com.example.tirepresure.data.model.DeleteTireRequest
import com.example.tirepresure.data.model.Tire
import com.example.tirepresure.data.model.ErrorResponse
import com.example.tirepresure.data.repo.TokenRepository
import com.google.gson.Gson
import com.google.gson.JsonSyntaxException
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

class TireViewModel (
    private var tokenRepository: TokenRepository,
    private var vehicleId: String,
): ViewModel(){
    private val _tiresState = MutableStateFlow<List<Tire>>(emptyList())
    val tiresState: StateFlow<List<Tire>> = _tiresState.asStateFlow()

    init {
        loadTires(vehicleId)
    }

    fun loadTires(vehicleId: String) {
        viewModelScope.launch {
            try {
//                val token = tokenRepository.getToken()
                val response = RetrofitInstance.tireApi.getTires(vehicleId)

                if (response.isSuccessful) {
                    _tiresState.value = response.body()!!.tires
                    Log.e("TireViewModel", "Successfully")
                } else {
                    val errorBody = response.errorBody()?.string()
                    val errorMessage = try {
                        Gson().fromJson(errorBody, ErrorResponse::class.java).message
                    } catch (e: JsonSyntaxException) {
                        "Unknown error"
                    }
                    _tiresState.value = emptyList()
                    Log.e("TireViewModel", errorMessage)
                }
            } catch (e: Exception) {
                Log.e("TireViewModel", "Network error: ${e.message}")
            }
        }
    }

    suspend fun getTire(vehicleId: String): Tire? {
        return try {
            val token = tokenRepository.getToken()
            val response = RetrofitInstance.tireApi.getTire(token, vehicleId)
            if (response.isSuccessful) {
                response.body()
            } else {
                val errorBody = response.errorBody()?.string()
                val errorMessage = try {
                    Gson().fromJson(errorBody, ErrorResponse::class.java).message
                } catch (e: JsonSyntaxException) {
                    "Failed to get vehicle details"
                }
                Log.e("TireViewModel", errorMessage)
                null
            }
        } catch (e: Exception) {
            Log.e("TireViewModel", "Network error while getting tire: ${e.message}")
            null
        }
    }

     fun addTire(carId: String, name: String, optimalPressure: Float, unit: String, alertType: String) {
        viewModelScope.launch {
            try {
                val token = tokenRepository.getToken()
                val request = AddTireRequest(carId, name, optimalPressure, unit, alertType)
                val response = RetrofitInstance.tireApi.addTire(token, request)

                if (response.isSuccessful) {
                    val addTireResponse = response.body()
                    val newTireId = addTireResponse?.tire_id

                    if (newTireId != null) {
                        val newTire = getTire(newTireId)
                        if (newTire != null) {
                            val updatedTires = _tiresState.value.toMutableList().apply { add(newTire) }
                            _tiresState.value = updatedTires
                            Log.e("TireViewModel", "Tire added successfully")
                        } else {
                            Log.e("TireViewModel", "Failed to retrieve new tire details")
                        }
                    }
                } else {
                    val errorBody = response.errorBody()?.string()
                    val errorMessage = try {
                        Gson().fromJson(errorBody, ErrorResponse::class.java).message
                    } catch (e: JsonSyntaxException) {
                        "Unknown error"
                    }
                    Log.e("TireViewModel", errorMessage)
                }
            } catch (e: Exception) {
                Log.e("TireViewModel", "Network error: ${e.message}")
            }
        }
    }

    suspend fun deleteTire(tireId: String){
        val request = DeleteTireRequest(tireId)

        try {
            val token = tokenRepository.getToken()
            val response = RetrofitInstance.tireApi.deleteTire(token, request)
            if (response.isSuccessful) {
                response.body()
            } else {
                val errorBody = response.errorBody()?.string()
                val errorMessage = try {
                    Gson().fromJson(errorBody, ErrorResponse::class.java).message
                } catch (e: JsonSyntaxException) {
                    "Failed to get vehicle details"
                }
                Log.e("TireViewModel", errorMessage)
                null
            }
        } catch (e: Exception) {
            Log.e("TireViewModel", "Network error while getting tire: ${e.message}")
            null
        }
    }
}