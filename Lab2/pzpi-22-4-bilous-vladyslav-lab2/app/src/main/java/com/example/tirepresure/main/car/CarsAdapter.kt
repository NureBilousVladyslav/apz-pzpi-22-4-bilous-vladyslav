package com.example.tirepresure.main.car

import android.view.LayoutInflater
import android.view.ViewGroup
import android.widget.TextView
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView
import com.example.tirepresure.R
import com.example.tirepresure.databinding.ItemCarBinding
import com.example.tirepresure.data.model.Car
import com.google.android.material.button.MaterialButton
import com.google.android.material.dialog.MaterialAlertDialogBuilder

class CarsAdapter(
    private val onItemClick: (Car) -> Unit
) : ListAdapter<Car, CarsAdapter.CarViewHolder>(CarDiffCallback()) {

    class CarViewHolder(
        private val binding: ItemCarBinding,
        private val onItemClick: (Car) -> Unit
    ) : RecyclerView.ViewHolder(binding.root) {
        fun bind(car: Car) {
            binding.brandTextView.text = car.make
            binding.modelTextView.text = car.model
            binding.propertiesImageView.setOnClickListener {
                showAddCarDialog(car)
            }
            binding.root.setOnClickListener { onItemClick(car) }
        }

        private fun showAddCarDialog(car: Car) {
            val dialogView = LayoutInflater.from(binding.root.context).inflate(R.layout.dialog_car_properties, null)
            val titleTextView = dialogView.findViewById<TextView>(R.id.titleTextView)
            val deleteButton = dialogView.findViewById<MaterialButton>(R.id.deleteButton)

            titleTextView.setText(car.make)
            deleteButton.setOnClickListener {
                onItemClick(car)asd
            }

            MaterialAlertDialogBuilder(binding.root.context, R.style.CustomDialogStyle)
                .setView(dialogView)
                .setNegativeButton("Cancel", null)
                .show()
        }
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): CarViewHolder {
        val binding = ItemCarBinding.inflate(
            LayoutInflater.from(parent.context),
            parent,
            false
        )
        return CarViewHolder(binding, onItemClick)
    }

    override fun onBindViewHolder(holder: CarViewHolder, position: Int) {
        holder.bind(getItem(position))
    }

    private class CarDiffCallback : DiffUtil.ItemCallback<Car>() {
        override fun areItemsTheSame(oldItem: Car, newItem: Car): Boolean {
            return oldItem.carId == newItem.carId
        }

        override fun areContentsTheSame(oldItem: Car, newItem: Car): Boolean {
            return oldItem == newItem
        }
    }
}