package com.example.tirepresure.main.car

import com.google.android.material.dialog.MaterialAlertDialogBuilder
import com.example.tirepresure.R
import android.os.Bundle
import androidx.fragment.app.Fragment
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.EditText
import android.widget.Toast
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.lifecycleScope
import androidx.lifecycle.repeatOnLifecycle
import androidx.navigation.fragment.findNavController
import androidx.recyclerview.widget.LinearLayoutManager
import com.example.tirepresure.data.repo.TokenRepository
import com.example.tirepresure.databinding.FragmentCarBinding
import com.example.tirepresure.main.MainActivity
import kotlinx.coroutines.launch

class CarFragment : Fragment() {
    private lateinit var binding: FragmentCarBinding
    private lateinit var carsAdapter: CarsAdapter
    private val carViewModel: CarViewModel by lazy {
        (requireActivity() as MainActivity).provideCarViewModel()
    }

    override fun onCreateView(
        inflater: LayoutInflater, container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        binding = FragmentCarBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        setupRecyclerView()
        observeCarState()

        binding.addCarButton.setOnClickListener {
            showAddCarDialog()
        }
    }

    private fun observeCarState() {
        viewLifecycleOwner.lifecycleScope.launch {
            viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
                carViewModel.carsState.collect { cars ->
                    carsAdapter.submitList(cars)
                }
            }
        }
    }

    private fun setupRecyclerView() {
        carsAdapter = CarsAdapter(
            onItemClick = { car ->
                val bundle = Bundle().apply {
                    putString("car_id", car.vehicle_id)
                    putString("car_brand", car.make)
                    putString("car_model", car.model)
                }
                findNavController().navigate(R.id.action_carFragment_to_tireFragment, bundle)
            },
            onDeleteClick = { carId ->
                viewLifecycleOwner.lifecycleScope.launch {
                    carViewModel.deleteCar(carId)
                }
            }
        )
        binding.carRecyclerView.layoutManager = LinearLayoutManager(context)
        binding.carRecyclerView.adapter = carsAdapter
    }

    private fun showAddCarDialog() {
        val dialogView = layoutInflater.inflate(R.layout.dialog_add_car, null)
        val brandEditText = dialogView.findViewById<EditText>(R.id.brandEditText)
        val modelEditText = dialogView.findViewById<EditText>(R.id.modelEditText)
        val yearEditText = dialogView.findViewById<EditText>(R.id.yearEditText)

        MaterialAlertDialogBuilder(requireContext(), R.style.CustomDialogStyle)
            .setView(dialogView)
            .setPositiveButton("Save") { _, _ ->
                val brand = brandEditText.text.toString()
                val model = modelEditText.text.toString()
                val year = yearEditText.text.toString()

                if ((brand + model + year).isBlank()){
                    Toast.makeText(requireContext(), "Field is empty", Toast.LENGTH_LONG).show()
                    return@setPositiveButton
                }
                carViewModel.addCar(brand, model, year.toInt())
                Toast.makeText(requireContext(), "Adding car...", Toast.LENGTH_SHORT).show()
            }
            .setNegativeButton("Cancel", null)
            .show()
    }
}