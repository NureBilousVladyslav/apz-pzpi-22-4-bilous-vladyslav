package com.example.tirepresure.data.api

import com.example.tirepresure.data.model.AddTireRequest
import com.example.tirepresure.data.model.AddTireResponse
import com.example.tirepresure.data.model.Tire
import com.example.tirepresure.data.model.TiresGetResponse
import com.example.tirepresure.data.model.DeleteTireRequest
import com.example.tirepresure.data.model.MessageResponse
import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.DELETE
import retrofit2.http.GET
import retrofit2.http.Header
import retrofit2.http.Headers
import retrofit2.http.POST
import retrofit2.http.Path

interface TireApi {
    @GET("get_vehicle_tires")
    @Headers(
        "Content-Type: application/json"
    )
    suspend fun getTires(
        @Header("Authorization") vehicleId: String?,
    ): Response<TiresGetResponse>

    @GET("get_tire")
    @Headers(
        "Content-Type: application/json"
    )
    suspend fun getTire(
        @Header("Authorization") tireId: String?,
        @Path("vehicle_id") vehicleId: String,
    ): Response<Tire>

    @POST("add_tire")
    @Headers(
        "Content-Type: application/json"
    )
    suspend fun addTire(
        @Header("Authorization") token: String?,
        @Body request: AddTireRequest,
    ): Response<AddTireResponse>

    @DELETE("delete_vehicle/vehicle")
    @Headers(
        "Content-Type: application/json"
    )
    suspend fun deleteTire(
        @Header("Authorization") token: String?,
        @Body request: DeleteTireRequest
    ): Response<MessageResponse>
}