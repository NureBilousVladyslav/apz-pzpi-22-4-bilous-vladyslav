package com.example.tirepresure.data.api

import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory

object RetrofitInstance {
    private const val BASE_URL = "https://tire-presure-backend-dpg3ejcpgpbnfmeh.northeurope-01.azurewebsites.net/"

    val authApi: AuthApi by lazy {
        retrofit.create(AuthApi::class.java)
    }

    val carApi: CarApi by lazy {
        retrofit.create(CarApi::class.java)
    }

    val tireApi: TireApi by lazy {
        retrofit.create(TireApi::class.java)
    }

    val userApi: UserApi by lazy {
        retrofit.create(UserApi::class.java)
    }

    val okHttpClient: OkHttpClient by lazy {
        OkHttpClient.Builder()
            .addInterceptor(ErrorInterceptor())
            .addInterceptor(HttpLoggingInterceptor().apply {
                level = HttpLoggingInterceptor.Level.BODY
            })
            .build()
    }

    private val retrofit by lazy {
        Retrofit.Builder()
            .baseUrl(BASE_URL)
            .client(okHttpClient)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
    }
}