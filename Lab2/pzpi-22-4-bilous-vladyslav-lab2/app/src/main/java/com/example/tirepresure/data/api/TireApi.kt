package com.example.tirepresure.data.api

import com.example.tirepresure.data.model.AddTireRequest
import com.example.tirepresure.data.model.AddTireResponse
import com.example.tirepresure.data.model.Tire
import com.example.tirepresure.data.model.TiresGetResponse
import com.example.tirepresure.data.model.MessageResponse
import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.DELETE
import retrofit2.http.GET
import retrofit2.http.Header
import retrofit2.http.Headers
import retrofit2.http.POST
import retrofit2.http.Query

interface TireApi {
    @GET("vehicle_tires/vehicle")
    @Headers(
        "Content-Type: application/json"
    )
    suspend fun getTiresFromCar(
        @Header("Authorization") token: String?,
        @Query("vehicle") vehicleId: String,
    ): Response<TiresGetResponse>

    @GET("tire/tire")
    @Headers(
        "Content-Type: application/json"
    )
    suspend fun getTire(
        @Header("Authorization") token: String?,
        @Query("tire") tireId: String,
    ): Response<Tire>

    @POST("add_tire")
    @Headers(
        "Content-Type: application/json"
    )
    suspend fun addTire(
        @Header("Authorization") token: String?,
        @Body request: AddTireRequest,
    ): Response<AddTireResponse>

    @DELETE("delete_tire/tire")
    @Headers(
        "Content-Type: application/json"
    )
    suspend fun deleteTire(
        @Header("Authorization") token: String?,
        @Query("tire") tireId: String,
    ): Response<MessageResponse>
}