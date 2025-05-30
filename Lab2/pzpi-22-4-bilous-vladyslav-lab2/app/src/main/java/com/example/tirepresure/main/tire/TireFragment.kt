package com.example.tirepresure.main.tire

import android.os.Bundle
import androidx.fragment.app.Fragment
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.EditText
import android.widget.TextView
import android.widget.Toast
import androidx.core.content.ContextCompat
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.lifecycleScope
import androidx.lifecycle.repeatOnLifecycle
import androidx.navigation.fragment.findNavController
import androidx.recyclerview.widget.LinearLayoutManager
import com.example.tirepresure.R
import com.example.tirepresure.data.model.Car
import com.example.tirepresure.data.repo.TokenRepository
import com.example.tirepresure.databinding.FragmentTireBinding
import com.example.tirepresure.main.MainActivity
import com.example.tirepresure.main.car.CarViewModel
import com.google.android.material.button.MaterialButton
import com.google.android.material.dialog.MaterialAlertDialogBuilder
import kotlinx.coroutines.launch

class TireFragment : Fragment() {
    private lateinit var binding: FragmentTireBinding
    private lateinit var tiresAdapter: TiresAdapter
    private lateinit var tokenRepository: TokenRepository
    private lateinit var tireViewModel: TireViewModel
    private val carViewModel: CarViewModel by lazy {
        (requireActivity() as MainActivity).provideCarViewModel()
    }
    private lateinit var carId: String

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        carId = arguments?.getString("car_id")!!
    }

    override fun onCreateView(
        inflater: LayoutInflater, container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        tokenRepository = TokenRepository(requireContext())
        tireViewModel = TireViewModel(tokenRepository, carId)
        binding = FragmentTireBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        setupRecyclerView()
        observeTireState()

        binding.apply {
            val brand: String = arguments?.getString("car_brand")!!
            brandTextView.text = brand
            modelTextView.text = arguments?.getString("car_model")!!

            addTireButton.setOnClickListener {
                showAddTireDialog()
            }

            propertiesImageView.setOnClickListener {
                showPropertiesCarDialog(carId, brand)
            }
        }

    }

    private fun observeTireState() {
        viewLifecycleOwner.lifecycleScope.launch {
            viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
                tireViewModel.tiresState.collect { tire ->
                    tiresAdapter.submitList(tire)
                }
            }
        }
    }

    private fun setupRecyclerView() {
        tiresAdapter = TiresAdapter { tire ->
            viewLifecycleOwner.lifecycleScope.launch {
                tireViewModel.deleteTire(tire.tire_id)
            }
        }
        binding.carRecyclerView.layoutManager = LinearLayoutManager(context)
        binding.carRecyclerView.adapter = tiresAdapter
    }

    private fun showPropertiesCarDialog(carId: String, brand: String) {
        val dialogView = LayoutInflater.from(binding.root.context).inflate(R.layout.dialog_car_properties, null)
        val titleTextView = dialogView.findViewById<TextView>(R.id.titleTextView)
        val deleteButton = dialogView.findViewById<MaterialButton>(R.id.deleteButton)

        titleTextView.text = brand

        MaterialAlertDialogBuilder(binding.root.context, R.style.CustomDialogStyle)
            .setView(dialogView)
            .setNegativeButton("Cancel", null)
            .create()
            .apply {
                show()
                deleteButton.setOnClickListener {
                    viewLifecycleOwner.lifecycleScope.launch {
                        carViewModel.deleteCar(carId)

                        findNavController().navigate(R.id.action_tireFragment_to_navigation_car)
                    }
                    dismiss()
                }
            }
    }

    private fun showAddTireDialog() {
        val dialogView = layoutInflater.inflate(R.layout.dialog_add_tire, null)
        val nameEditText = dialogView.findViewById<EditText>(R.id.nameEditText)
        val optimalPressureEditText = dialogView.findViewById<EditText>(R.id.optimalPressureEditText)
        val barButton = dialogView.findViewById<MaterialButton>(R.id.barButton)
        val psiButton = dialogView.findViewById<MaterialButton>(R.id.psiButton)
        val kPaButton = dialogView.findViewById<MaterialButton>(R.id.kPaButton)

        var selectedUnit: String = toggleUnitButton(barButton, barButton, psiButton, kPaButton)

        barButton.setOnClickListener {
            selectedUnit = toggleUnitButton(barButton, barButton, psiButton, kPaButton)
        }
        psiButton.setOnClickListener {
            selectedUnit = toggleUnitButton(psiButton, barButton, psiButton, kPaButton)
        }
        kPaButton.setOnClickListener {
            selectedUnit = toggleUnitButton(kPaButton, barButton, psiButton, kPaButton)
        }

        MaterialAlertDialogBuilder(requireContext(), R.style.CustomDialogStyle)
            .setView(dialogView)
            .setPositiveButton("Save") { _, _ ->
                val name = nameEditText.text.toString()
                val optimalPressure = optimalPressureEditText.text.toString().toFloatOrNull() ?: 0f

                if (name.isBlank() || optimalPressure <= 0) {
                    Toast.makeText(requireContext(), "Field is empty or invalid", Toast.LENGTH_LONG).show()
                    return@setPositiveButton
                }

                tireViewModel.addTire(carId, name, optimalPressure, selectedUnit)
                Toast.makeText(requireContext(), "Adding tire...", Toast.LENGTH_SHORT).show()
            }
            .setNegativeButton("Cancel", null)
            .show()
    }

    private fun toggleUnitButton(
        clickedButton: MaterialButton,
        barButton: MaterialButton,
        psiButton: MaterialButton,
        kPaButton: MaterialButton
    ): String {
        val buttons = listOf(barButton, psiButton, kPaButton)

        clickedButton.isEnabled = false
        clickedButton.backgroundTintList = ContextCompat.getColorStateList(requireContext(), R.color.primary)

        buttons.filter { it != clickedButton }.forEach { button ->
            button.isEnabled = true
            button.backgroundTintList = ContextCompat.getColorStateList(requireContext(), R.color.onPrimaryVariant)
        }

        return when (clickedButton.id) {
            R.id.barButton -> "bar"
            R.id.psiButton -> "psi"
            R.id.kPaButton -> "kPa"
            else -> "bar"
        }
    }
}