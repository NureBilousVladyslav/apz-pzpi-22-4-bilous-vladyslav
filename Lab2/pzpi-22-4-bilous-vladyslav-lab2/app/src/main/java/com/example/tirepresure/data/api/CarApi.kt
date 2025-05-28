package com.example.tirepresure.data.api

import com.example.tirepresure.data.model.AddCarRequest
import com.example.tirepresure.data.model.AddCarResponse
import com.example.tirepresure.data.model.Car
import com.example.tirepresure.data.model.CarsGetResponse
import com.example.tirepresure.data.model.DeleteCarRequest
import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.DELETE
import retrofit2.http.GET
import retrofit2.http.Header
import retrofit2.http.Headers
import retrofit2.http.POST
import retrofit2.http.Path

interface CarApi {
    @GET("user_vehicles")
    @Headers(
        "Content-Type: application/json"
    )
    suspend fun getCars(
        @Header("Authorization") token: String?,
    ): Response<CarsGetResponse>

    @GET("get_vehicle")
    @Headers(
        "Content-Type: application/json"
    )
    suspend fun getCar(
        @Header("Authorization") token: String?,
        @Path("vehicle_id") vehicleId: String,
    ): Response<Car>

    @POST("add_vehicle")
    @Headers(
        "Content-Type: application/json"
    )
    suspend fun addCar(
        @Header("Authorization") token: String?,
        @Body request: AddCarRequest,
    ): Response<AddCarResponse>

    @DELETE("delete_vehicle/vehicle")
    @Headers(
        "Content-Type: application/json"
    )
    suspend fun deleteCar(
        @Header("Authorization") token: String?,
        @Body request: DeleteCarRequest
    ): Response<AddCarResponse>
}