package com.example.tirepresure.auth.signIn

import android.content.Intent
import android.os.Bundle
import androidx.fragment.app.Fragment
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Toast
import androidx.activity.ComponentActivity
import androidx.activity.result.contract.ActivityResultContracts
import androidx.navigation.NavController
import androidx.navigation.fragment.findNavController
import com.example.tirepresure.R
import com.example.tirepresure.auth.utils.PasswordVisibilityUtils
import com.example.tirepresure.auth.utils.ValidatorUtils
import com.example.tirepresure.databinding.FragmentSignInBinding
import com.example.tirepresure.main.MainActivity

class SignInFragment : Fragment() {
    private lateinit var binding: FragmentSignInBinding
    private lateinit var navController: NavController
    private var _isPasswordVisible = false
    private val googleSignInLauncher = registerForActivityResult(ActivityResultContracts.StartActivityForResult()) { result ->

    }

    override fun onCreateView(
        inflater: LayoutInflater, container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        binding = FragmentSignInBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        navController = findNavController()

        binding.signInButton.setOnClickListener {
            val email = binding.emailEditText.text.toString().trim()
            val password = binding.pswdEditText.text.toString().trim()

            checkUserAuthorization(email,password)
        }

        binding.googleButton.setOnClickListener {
//            val signInIntent = authViewModel.getGoogleSignInIntent(requireContext())
//            googleSignInLauncher.launch(signInIntent)
        }

        binding.resetPswdButton.setOnClickListener {
            navController.navigate(R.id.action_signInFragment_to_resetPasswordFragment)
        }

        binding.signUpButton.setOnClickListener {
            navController.navigate(R.id.action_signInFragment_to_signUpFragment)
        }

        binding.eyeButton.setOnClickListener {
            _isPasswordVisible = !_isPasswordVisible
            PasswordVisibilityUtils.togglePasswordVisibility(binding.pswdEditText, binding.eyeButton, _isPasswordVisible)
        }
    }

    private fun startActivity(activityClass: Class<out ComponentActivity>) {
        val intent = Intent(context, activityClass)
        intent.flags = Intent.FLAG_ACTIVITY_CLEAR_TOP or Intent.FLAG_ACTIVITY_SINGLE_TOP
        startActivity(intent)
    }

    private fun checkUserAuthorization(email: String, password: String) {
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
            else -> {
                /*val result = authUseCase.isUserAuthorized(email, password)
                if (result.isNoEmpty())
                    startActivity(MainActivity::class.java)*/
            }
        }
    }
}