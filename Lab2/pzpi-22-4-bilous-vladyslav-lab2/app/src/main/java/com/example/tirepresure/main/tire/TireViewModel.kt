package com.example.tirepresure.main.tire

import android.util.Log
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.tirepresure.data.api.RetrofitInstance
import com.example.tirepresure.data.model.AddTireRequest
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
    private var carId: String,
): ViewModel(){
    private val _tiresState = MutableStateFlow<List<Tire>>(emptyList())
    val tiresState: StateFlow<List<Tire>> = _tiresState.asStateFlow()

    init {
        loadTires(carId)
    }

    fun loadTires(carId: String) {
        viewModelScope.launch {
            try {
                val token = tokenRepository.getToken()
                val response = RetrofitInstance.tireApi.getTiresFromCar(token, carId)

                if (response.isSuccessful) {
                    _tiresState.value = response.body()?.tires!!
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

     fun addTire(carId: String, name: String, optimalPressure: Float, unit: String) {
        viewModelScope.launch {
            try {
                val token = tokenRepository.getToken()
                val request = AddTireRequest(carId, name, optimalPressure, unit)
                val response = RetrofitInstance.tireApi.addTire(token, request)

                if (response.isSuccessful) {
                    val addTireResponse = response.body()
                    val newTireId = addTireResponse?.tire_id

                    if (newTireId != null) {
                        val newTire = getTire(newTireId)
                        if (newTire != null) {
                            val updatedTires = _tiresState.value.toMutableList().apply { add(newTire) }
                            _tiresState.value = updatedTires
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
        try {
            val token = tokenRepository.getToken()
            val response = RetrofitInstance.tireApi.deleteTire(token, tireId)
            if (response.isSuccessful) {
                _tiresState.value = _tiresState.value.filter { it.tire_id != tireId }
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