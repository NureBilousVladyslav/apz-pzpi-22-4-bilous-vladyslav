package com.example.tirepresure.main.car

import android.util.Log
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.tirepresure.data.api.RetrofitInstance
import com.example.tirepresure.data.model.AddCarRequest
import com.example.tirepresure.data.model.Car
import com.example.tirepresure.data.model.DeleteCarRequest
import com.example.tirepresure.data.model.DeleteTireRequest
import com.example.tirepresure.data.model.ErrorResponse
import com.example.tirepresure.data.repo.TokenRepository
import com.google.gson.Gson
import com.google.gson.JsonSyntaxException
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

class CarViewModel (
    private var tokenRepository: TokenRepository
): ViewModel(){
    private val _carsState = MutableStateFlow<List<Car>>(emptyList())
    val carsState: StateFlow<List<Car>> = _carsState.asStateFlow()

    init {
        loadCars()
    }

    fun loadCars() {
        viewModelScope.launch {
            try {
                val token = tokenRepository.getToken()
                val response = RetrofitInstance.carApi.getCars(token)

                if (response.isSuccessful) {
                    _carsState.value = response.body()!!.cars
                    Log.e("CarViewModel", "Successfully")
                } else {
                    val errorBody = response.errorBody()?.string()
                    val errorMessage = try {
                        Gson().fromJson(errorBody, ErrorResponse::class.java).message
                    } catch (e: JsonSyntaxException) {
                        "Unknown error"
                    }
                    _carsState.value = emptyList()
                    Log.e("CarViewModel", errorMessage)
                }
            } catch (e: Exception) {
                Log.e("CarViewModel", "Network error: ${e.message}")
            }
        }
    }

    suspend fun getCar(vehicleId: String): Car? {
        return try {
            val token = tokenRepository.getToken()
            val response = RetrofitInstance.carApi.getCar(token, vehicleId)
            if (response.isSuccessful) {
                response.body()
            } else {
                val errorBody = response.errorBody()?.string()
                val errorMessage = try {
                    Gson().fromJson(errorBody, ErrorResponse::class.java).message
                } catch (e: JsonSyntaxException) {
                    "Failed to get vehicle details"
                }
                Log.e("CarViewModel", errorMessage)
                null
            }
        } catch (e: Exception) {
            Log.e("CarViewModel", "Network error while getting car: ${e.message}")
            null
        }
    }

    fun addCar(brand: String, model: String, year: String) {
        viewModelScope.launch {
            try {
                val token = tokenRepository.getToken()
                val request = AddCarRequest(brand, model, year)
                val response = RetrofitInstance.carApi.addCar(token, request)

                if (response.isSuccessful) {
                    val addCarResponse = response.body()
                    val newVehicleId = addCarResponse?.vehicle_id

                    if (newVehicleId != null) {
                        val date = Date()
                        val newCar = Car(newVehicleId, brand, model, year, SimpleDateFormat("dd/MM/yyyy", Locale.getDefault()).format(date))
                        val updatedCars = _carsState.value.toMutableList().apply { add(newCar) }

                        _carsState.value = updatedCars
                        Log.e("CarViewModel", "Car added successfully")
                    }
                } else {
                    val errorBody = response.errorBody()?.string()
                    val errorMessage = try {
                        Gson().fromJson(errorBody, ErrorResponse::class.java).message
                    } catch (e: JsonSyntaxException) {
                        "Unknown error"
                    }
                    Log.e("CarViewModel", errorMessage)
                }
            } catch (e: Exception) {
                Log.e("CarViewModel", "Network error: ${e.message}")
            }
        }
    }

    suspend fun deleteCar(carId: String){
        val request = DeleteCarRequest(carId)

        try {
            val token = tokenRepository.getToken()
            val response = RetrofitInstance.carApi.deleteCar(token, request)
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