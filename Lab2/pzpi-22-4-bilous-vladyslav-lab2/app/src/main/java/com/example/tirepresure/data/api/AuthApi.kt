package com.example.tirepresure.data.api

import com.example.tirepresure.data.model.AddDeviceRequest
import com.example.tirepresure.data.model.FirebaseLoginRequest
import com.example.tirepresure.data.model.MessageResponse
import com.example.tirepresure.data.model.ResetPasswordRequest
import com.example.tirepresure.data.model.ResetPasswordResponse
import com.example.tirepresure.data.model.SignUpResponse
import com.example.tirepresure.data.model.SignInRequest
import com.example.tirepresure.data.model.SignUpRequest
import com.example.tirepresure.data.model.SignInResponse
import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.Header
import retrofit2.http.Headers
import retrofit2.http.POST

interface AuthApi {
    @POST("token_login")
    @Headers(
        "Content-Type: application/json"
    )
    suspend fun signIn(@Body request: SignInRequest): Response<SignInResponse>

    @POST("register")
    @Headers(
        "Content-Type: application/json"
    )
    suspend fun signUp(@Body request: SignUpRequest): Response<SignUpResponse>

    @POST("reset_password")
    @Headers(
        "Content-Type: application/json"
    )
    suspend fun resetPassword(@Body request: ResetPasswordRequest): Response<ResetPasswordResponse>

    /*@POST("login_firebase")
    @Headers(
        "Content-Type: application/json"
    )
    suspend fun firebaseLogin(@Body request: FirebaseLoginRequest): Response<SignInResponse>

    @POST("devices")
    @Headers(
        "Content-Type: application/json"
    )
    suspend fun addDevice(
        @Header("Authorization") token: String,
        @Body request: AddDeviceRequest
    ): Response<MessageResponse>*/
}