package com.example.tirepresure.auth.signUp

import android.app.AlertDialog
import android.os.Bundle
import androidx.fragment.app.Fragment
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.fragment.app.viewModels
import android.widget.EditText
import android.widget.NumberPicker
import android.widget.Toast
import androidx.core.content.ContextCompat
import androidx.lifecycle.lifecycleScope
import com.example.tirepresure.R
import com.example.tirepresure.data.model.DateModel
import com.example.tirepresure.databinding.FragmentSignUpBinding
import com.example.tirepresure.auth.utils.PasswordVisibilityUtils
import com.example.tirepresure.auth.utils.ValidatorUtils
import com.example.tirepresure.common.viewModel.DatePickerViewModel
import com.example.tirepresure.data.api.RetrofitInstance
import com.example.tirepresure.data.model.ErrorResponse
import com.example.tirepresure.data.model.SignUpRequest
import com.google.gson.Gson
import com.google.gson.JsonSyntaxException
import kotlinx.coroutines.launch

class SignUpFragment : Fragment() {
    private var _binding: FragmentSignUpBinding? = null
    private val binding get() = _binding!!

    private var _isPasswordVisible = false
    private var _isConfirmPasswordVisible = false

    private val datePickerViewModel: DatePickerViewModel by viewModels()

    override fun onCreateView(
        inflater: LayoutInflater, container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        _binding = FragmentSignUpBinding.inflate(inflater, container, false)

        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        binding.registerButton.setOnClickListener {
            binding.apply {
                val name = giveTextFromEditText(nameEditText)
                val email = giveTextFromEditText(emailEditText)
                val password = giveTextFromEditText(pswdEditText)
                val confirmPassword = giveTextFromEditText(pswdConfirmEditText)
                val date = datePickerViewModel.selectedDate.value

                when {
                    !ValidatorUtils.isNotBlank(email, password) -> {
                        Toast.makeText(context, "Email or password is empty", Toast.LENGTH_LONG).show()
                    }

                    !ValidatorUtils.isValidEmail(email) -> {
                        Toast.makeText(context, "Email is incorrect", Toast.LENGTH_LONG).show()
                    }

                    !ValidatorUtils.isValidPassword(password) -> {
                        Toast.makeText(context, "Password must be 8 characters or more", Toast.LENGTH_LONG).show()
                    }

                    !ValidatorUtils.isNotBlank(name) -> {
                        Toast.makeText(context, "Name is empty", Toast.LENGTH_LONG).show()
                    }

                    !ValidatorUtils.isDateSelected(date) -> {
                        Toast.makeText(context, "Date not selected", Toast.LENGTH_LONG).show()
                    }

                    !ValidatorUtils.isPasswordConfirmed(password, confirmPassword) -> {
                        Toast.makeText(context, "Passwords do not match", Toast.LENGTH_LONG).show()
                    }

                    !ValidatorUtils.isUserAtLeast18(date!!) -> {
                        Toast.makeText(context, "You must be at least 18 years old", Toast.LENGTH_LONG).show()
                    }

                    else -> {
                        val request = SignUpRequest(name, email, password, date.toFormattedString())

                        viewLifecycleOwner.lifecycleScope.launch {
                            try {
                                val response = RetrofitInstance.authApi.signUp(request)
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

        binding.dateEditText.setOnClickListener {
            showDatePickerDialog(binding.dateEditText)
        }

        binding.eyeButton.setOnClickListener {
            _isPasswordVisible = !_isPasswordVisible
            PasswordVisibilityUtils.togglePasswordVisibility(binding.pswdEditText, binding.eyeButton, _isPasswordVisible)
        }

        binding.eyeConfirmButton.setOnClickListener {
            _isConfirmPasswordVisible = !_isConfirmPasswordVisible
            PasswordVisibilityUtils.togglePasswordVisibility(binding.pswdConfirmEditText, binding.eyeConfirmButton, _isConfirmPasswordVisible)
        }
    }

    private fun giveTextFromEditText(editText: EditText) : String {
        return editText.text.toString().trim()
    }

    private fun showDatePickerDialog(editText: EditText) {
        val dialogView = layoutInflater.inflate(R.layout.dialog_date_picker, null)

        val monthPicker = dialogView.findViewById<NumberPicker>(R.id.monthPicker)
        val dayPicker = dialogView.findViewById<NumberPicker>(R.id.dayPicker)
        val yearPicker = dialogView.findViewById<NumberPicker>(R.id.yearPicker)

        monthPicker.minValue = 0
        monthPicker.maxValue = DateModel.months.size - 1
        monthPicker.displayedValues = DateModel.months

        yearPicker.minValue = 1900
        yearPicker.maxValue = 2025

        fun isLeapYear(year: Int): Boolean = (year % 4 == 0 && year % 100 != 0) || (year % 400 == 0)

        fun updateDaysInMonth(year: Int, month: Int) {
            val daysInMonth = when (month) {
                1 -> if (isLeapYear(year)) 29 else 28
                3, 5, 8, 10 -> 30
                else -> 31
            }
            dayPicker.minValue = 1
            dayPicker.maxValue = daysInMonth
            if (dayPicker.value > daysInMonth) dayPicker.value = daysInMonth
        }

        val currentDate = datePickerViewModel.selectedDate.value ?: DateModel.DEFAULT

        updateDaysInMonth(currentDate.year, currentDate.month)
        monthPicker.value = currentDate.month
        dayPicker.value = currentDate.day
        yearPicker.value = currentDate.year

        monthPicker.setOnValueChangedListener { _, _, newMonth ->
            updateDaysInMonth(yearPicker.value, newMonth)
        }

        yearPicker.setOnValueChangedListener { _, _, newYear ->
            updateDaysInMonth(newYear, monthPicker.value)
        }

        AlertDialog.Builder(requireContext(), R.style.RoundedDialog)
            .setTitle(getString(R.string.select_date))
            .setView(dialogView)
            .setPositiveButton(getString(R.string.ok)) { _, _ ->
                datePickerViewModel.setDate(monthPicker.value, dayPicker.value, yearPicker.value)
                editText.setText(datePickerViewModel.selectedDate.value?.toFormattedString() ?: DateModel.DEFAULT.toFormattedString())
            }
            .setNegativeButton(getString(R.string.cancel), null)
            .create()
            .apply {
                show()
                getButton(AlertDialog.BUTTON_POSITIVE).setTextColor(
                    ContextCompat.getColor(context, android.R.color.holo_blue_dark)
                )
                getButton(AlertDialog.BUTTON_NEGATIVE).setTextColor(
                    ContextCompat.getColor(context, android.R.color.holo_red_light)
                )
            }
    }
}