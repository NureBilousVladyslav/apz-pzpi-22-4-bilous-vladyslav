package com.example.tirepresure.auth.resetPassword

import android.os.Bundle
import androidx.fragment.app.Fragment
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Toast
import androidx.lifecycle.lifecycleScope
import com.example.tirepresure.auth.utils.ValidatorUtils
import com.example.tirepresure.data.api.RetrofitInstance
import com.example.tirepresure.data.model.ErrorResponse
import com.example.tirepresure.data.model.ResetPasswordRequest
import com.example.tirepresure.databinding.FragmentResetPasswordBinding
import com.google.gson.Gson
import com.google.gson.JsonSyntaxException
import kotlinx.coroutines.launch

class ResetPasswordFragment : Fragment() {
    private lateinit var binding: FragmentResetPasswordBinding

    override fun onCreateView(
        inflater: LayoutInflater, container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        binding = FragmentResetPasswordBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        binding.apply {
            resetPswdButton.setOnClickListener {
                val email = emailEditText.text.toString().trim()
                userResetPswdRequest(email)
            }
        }
    }

    private fun userResetPswdRequest(email: String) {
        when {
            !ValidatorUtils.isNotBlank(email) -> {
                Toast.makeText(context, "Email is empty", Toast.LENGTH_LONG).show()
            }
            !ValidatorUtils.isValidEmail(email) -> {
                Toast.makeText(context, "Email is incorrect", Toast.LENGTH_LONG).show()
            }
            else -> {
                val request = ResetPasswordRequest(email)

                viewLifecycleOwner.lifecycleScope.launch {
                    try {
                        val response = RetrofitInstance.authApi.resetPassword(request)
                        if (response.isSuccessful) {
                            val body = response.body()
                            Toast.makeText(context, body.toString(), Toast.LENGTH_LONG).show()
                            requireActivity().supportFragmentManager.popBackStack()
                        } else {
                            val errorBody = response.errorBody()?.string()
                            val errorMessage = try {
                                val errorResponse = Gson().fromJson(errorBody, ErrorResponse::class.java)
                                errorResponse.message
                            } catch (e: JsonSyntaxException) {
                                "Unknown error: $e"
                            }

                            Toast.makeText(context, errorMessage, Toast.LENGTH_LONG).show()
                        }
                    } catch (e: Exception) {
                        Toast.makeText(context, e.toString(), Toast.LENGTH_LONG).show()
                    }
                }
            }
        }
    }
}