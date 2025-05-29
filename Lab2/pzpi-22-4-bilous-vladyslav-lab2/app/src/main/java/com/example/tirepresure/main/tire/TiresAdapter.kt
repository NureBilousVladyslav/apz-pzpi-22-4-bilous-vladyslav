package com.example.tirepresure.main.tire

import android.view.LayoutInflater
import android.view.ViewGroup
import android.widget.SeekBar
import android.widget.TextView
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView
import com.example.tirepresure.R
import com.example.tirepresure.databinding.ItemTireBinding
import com.example.tirepresure.data.model.Tire
import com.google.android.material.button.MaterialButton
import com.google.android.material.dialog.MaterialAlertDialogBuilder

class TiresAdapter(
    private val onItemClick: (Tire) -> Unit
) : ListAdapter<Tire, TiresAdapter.TireViewHolder>(TireDiffCallback()) {

    class TireViewHolder(
        private val binding: ItemTireBinding,
        private val onItemClick: (Tire) -> Unit
    ) : RecyclerView.ViewHolder(binding.root) {
        fun bind(tire: Tire) {
            binding.nameTextView.text = tire.label
            binding.statusTextView.text = tire.current_alert_type

            val unit = tire.pressure_unit ?: "bar"
            binding.currentPressureTextView.text = "Current pressure: ${tire.current_pressure} $unit"
            binding.normalPressureTextView.text = "Optimal pressure: ${tire.optimal_pressure} $unit"
            setupPressureRange(tire)
            binding.propertiesImageView.setOnClickListener {
                showAddCarDialog(tire)
            }
        }

        private fun showAddCarDialog(tire: Tire) {
            val dialogView = LayoutInflater.from(binding.root.context).inflate(R.layout.dialog_tire_properties, null)
            val titleTextView = dialogView.findViewById<TextView>(R.id.titleTextView)
            val paringCodeTextView = dialogView.findViewById<TextView>(R.id.paringCodeTextView)
            val deleteButton = dialogView.findViewById<MaterialButton>(R.id.deleteButton)

            titleTextView.setText(tire.label)
            paringCodeTextView.setText(tire.sensor_code)
            deleteButton.setOnClickListener {
                onItemClick(tire)
            }

            MaterialAlertDialogBuilder(binding.root.context, R.style.CustomDialogStyle)
                .setView(dialogView)
                .setNegativeButton("Cancel", null)
                .show()
        }

        private fun setupPressureRange(tire: Tire) {
            val scale = 100
            val optimalPressure = tire.optimal_pressure
            val currentPressure = tire.current_pressure ?: optimalPressure
            val unit = tire.pressure_unit ?: "bar"

            val (minPressure, maxPressure) = when (unit) {
                "bar" -> {
                    val rangeFactor = 0.2f
                    val minPressure = optimalPressure * (1 - rangeFactor)
                    val maxPressure = optimalPressure * (1 + rangeFactor)
                    Pair(minPressure, maxPressure)
                }
                "psi" -> {
                    val optimalPsi = optimalPressure * 14.5f
                    val rangeFactor = 0.2f // ±20%
                    val minPressure = optimalPsi * (1 - rangeFactor)
                    val maxPressure = optimalPsi * (1 + rangeFactor)
                    Pair(minPressure, maxPressure)
                }
                "kPa" -> {
                    val optimalKPa = optimalPressure * 100f
                    val rangeFactor = 0.2f // ±20%
                    val minPressure = optimalKPa * (1 - rangeFactor)
                    val maxPressure = optimalKPa * (1 + rangeFactor)
                    Pair(minPressure, maxPressure)
                }
                else -> Pair(optimalPressure - 0.5f, optimalPressure + 0.5f)
            }

            val minProgress = (minPressure * scale).toInt()
            val maxProgress = (maxPressure * scale).toInt()
            val currentProgress = (currentPressure * scale).toInt()

            val adjustedMin = maxOf(0, minProgress)
            val range = maxProgress - adjustedMin

            binding.pressureRange.max = range
            binding.pressureRange.progress = currentProgress - adjustedMin

            binding.pressureRange.setOnSeekBarChangeListener(object : SeekBar.OnSeekBarChangeListener {
                override fun onProgressChanged(seekBar: SeekBar?, progress: Int, fromUser: Boolean) {
                    val actualPressure = (progress + adjustedMin) / scale.toFloat()
                    binding.currentPressureTextView.text = "Current pressure: $actualPressure $unit"
                }

                override fun onStartTrackingTouch(seekBar: SeekBar?) {}
                override fun onStopTrackingTouch(seekBar: SeekBar?) {}
            })
        }
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): TireViewHolder {
        val binding = ItemTireBinding.inflate(
            LayoutInflater.from(parent.context),
            parent,
            false
        )
        return TireViewHolder(binding, onItemClick)
    }

    override fun onBindViewHolder(holder: TireViewHolder, position: Int) {
        holder.bind(getItem(position))
    }

    private class TireDiffCallback : DiffUtil.ItemCallback<Tire>() {
        override fun areItemsTheSame(oldItem: Tire, newItem: Tire): Boolean {
            return oldItem.tire_id == newItem.tire_id
        }

        override fun areContentsTheSame(oldItem: Tire, newItem: Tire): Boolean {
            return oldItem == newItem
        }
    }
}