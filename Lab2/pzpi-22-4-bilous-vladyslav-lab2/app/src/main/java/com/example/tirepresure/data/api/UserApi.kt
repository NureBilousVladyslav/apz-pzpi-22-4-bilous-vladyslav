package com.example.tirepresure.data.api

import com.example.tirepresure.data.model.GetUserResponse
import retrofit2.Response
import retrofit2.http.GET
import retrofit2.http.Header
import retrofit2.http.Headers

interface UserApi {
    @GET("profile")
    @Headers(
        "Content-Type: application/json"
    )
    suspend fun getUserInfo(
        @Header("Authorization") token: String?,
    ): Response<GetUserResponse>
}