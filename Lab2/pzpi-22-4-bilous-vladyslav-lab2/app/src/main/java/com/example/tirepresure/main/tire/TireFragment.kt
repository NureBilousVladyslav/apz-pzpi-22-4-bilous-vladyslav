package com.example.tirepresure.main.tire

import android.os.Bundle
import androidx.fragment.app.Fragment
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.EditText
import android.widget.Toast
import androidx.core.content.ContextCompat
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.lifecycleScope
import androidx.lifecycle.repeatOnLifecycle
import androidx.recyclerview.widget.LinearLayoutManager
import com.example.tirepresure.R
import com.example.tirepresure.data.model.Car
import com.example.tirepresure.data.repo.TokenRepository
import com.example.tirepresure.databinding.FragmentTireBinding
import com.example.tirepresure.main.car.CarsAdapter
import com.example.tirepresure.main.tire.TireViewModel
import com.example.tirepresure.main.tire.TiresAdapter
import com.google.android.material.button.MaterialButton
import com.google.android.material.dialog.MaterialAlertDialogBuilder
import kotlinx.coroutines.launch

class TireFragment(
    val carId: String
) : Fragment() {
    private lateinit var binding: FragmentTireBinding
    private lateinit var tiresAdapter: TiresAdapter
    private lateinit var tokenRepository: TokenRepository
    private lateinit var tireViewModel: TireViewModel
    private lateinit var car_id: String

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        car_id = arguments?.getString("car_id")!!
    }

    override fun onCreateView(
        inflater: LayoutInflater, container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        tokenRepository = TokenRepository(requireContext())
        tireViewModel = TireViewModel(tokenRepository, car_id)
        binding = FragmentTireBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        setupRecyclerView()
        observeTireState()

        binding.addTireButton.setOnClickListener {
            showAddTireDialog()
        }
    }

    private fun observeTireState() {
        viewLifecycleOwner.lifecycleScope.launch {
            viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
                tireViewModel.tiresState.collect { tire ->
                    if (tire.isNotEmpty()) {
                        tiresAdapter.submitList(tire)
                    }
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

    private fun showAddTireDialog() {
        val dialogView = layoutInflater.inflate(R.layout.dialog_add_tire, null)
        val nameEditText = dialogView.findViewById<EditText>(R.id.nameEditText)
        val optimalPressureEditText = dialogView.findViewById<EditText>(R.id.optimalPressureEditText)
        val barButton = dialogView.findViewById<MaterialButton>(R.id.barButton)
        val psiButton = dialogView.findViewById<MaterialButton>(R.id.psiButton)
        val kPaButton = dialogView.findViewById<MaterialButton>(R.id.kPaButton)
        var selectedUnit: String = toggleUnitButton(barButton, psiButton, kPaButton)

        barButton.setOnClickListener { selectedUnit = toggleUnitButton(barButton, psiButton, kPaButton) }
        psiButton.setOnClickListener { selectedUnit = toggleUnitButton(barButton, psiButton, kPaButton) }
        kPaButton.setOnClickListener { selectedUnit = toggleUnitButton(barButton, psiButton, kPaButton) }

        MaterialAlertDialogBuilder(requireContext(), R.style.CustomDialogStyle)
            .setView(dialogView)
            .setPositiveButton("Save") { _, _ ->
                val name = nameEditText.text.toString()
                val optimalPressure = optimalPressureEditText.text.toString().toFloatOrNull() ?: 0f

                if (name.isBlank() || optimalPressure <= 0) {
                    Toast.makeText(requireContext(), "Field is empty or invalid", Toast.LENGTH_LONG).show()
                    return@setPositiveButton
                }

                tireViewModel.addTire(carId, name, optimalPressure, selectedUnit, "normal")
                Toast.makeText(requireContext(), "Adding tire...", Toast.LENGTH_SHORT).show()
            }
            .setNegativeButton("Cancel", null)
            .show()
    }

    private fun toggleUnitButton(barButton: MaterialButton, psiButton: MaterialButton, kPaButton: MaterialButton): String {
        val buttons = listOf(barButton, psiButton, kPaButton)

        val activeButton = buttons.find { !it.isEnabled } ?: barButton

        activeButton.isEnabled = false
        activeButton.backgroundTintList = ContextCompat.getColorStateList(requireContext(), R.color.primary)

        buttons.filter { it != activeButton }.forEach { button ->
            button.isEnabled = true
            button.backgroundTintList = ContextCompat.getColorStateList(requireContext(), R.color.onPrimaryVariant)
        }

        return when (activeButton.id) {
            R.id.barButton -> "bar"
            R.id.psiButton -> "psi"
            R.id.kPaButton -> "kPa"
            else -> "bar"
        }
    }
}