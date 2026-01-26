import React from "react";
import { Bar } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";
import styles from "./ProgressChart.module.css";

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

const ProgressChart = ({ data }) => {
  const labels = data.map((d) => d.day);
  const values = data.map((d) => d.words);

  const chartData = {
    labels,
    datasets: [
      {
        label: "Số từ học",
        data: values,
        backgroundColor: "#4ade80",
        borderRadius: 8,
      },
    ],
  };

  const options = {
    responsive: true,
    plugins: {
      legend: { display: false },
      title: {
        display: true,
        text: "Tiến trình học tập tuần này",
        font: { size: 16 },
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        ticks: { stepSize: 5 },
      },
    },
  };

  return (
    <div className={styles.chartContainer}>
      <Bar data={chartData} options={options} />
    </div>
  );
};

export default ProgressChart;
