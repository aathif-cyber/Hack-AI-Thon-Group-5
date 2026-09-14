# 🌱 GreenGrid — Smart Energy Consumption & Carbon Tracker

> **Turn electricity data into clear actions for lower cost, lower consumption, and lower carbon impact.**

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![OOP](https://img.shields.io/badge/Design-OOP-green)
![SDG 7](https://img.shields.io/badge/SDG-7-yellow)
![SDG 11](https://img.shields.io/badge/SDG-11-orange)
![SDG 13](https://img.shields.io/badge/SDG-13-red)

---

## 🏆 Hack-AI-Thon 2026

**Theme:** Python Fundamentals + Object-Oriented Programming (OOP) + Sustainable Development Goals (SDGs)

**Project:** GreenGrid – Smart Energy Consumption & Carbon Tracker

GreenGrid is a Python-based energy-management application that records electricity usage for appliances, rooms, homes, or institutions and converts raw usage data into understandable **energy, cost, and carbon insights**.

The challenge requires a functional prototype, meaningful sample/test data, and a primarily Python/OOP implementation. The required core classes are `Appliance`, `EnergyRecord`, and `EnergyReport`.

---

# 🌍 The Problem

Electricity bills tell us **how much electricity was consumed**, but they often do not clearly show:

* Which appliance consumes the most energy?
* How much energy does each appliance use?
* How much does that usage cost?
* What is the estimated carbon impact?
* Which action should be taken first to reduce consumption?

Without this information, users may know that their electricity bill is high but still struggle to identify the actual sources of consumption.

---

# 💡 Our Solution

**GreenGrid** transforms appliance usage data into actionable sustainability insights.

The system records:

* Appliance name
* Power rating
* Usage hours
* Date/period

It then calculates:

⚡ **Energy Consumption (kWh)**
💰 **Estimated Electricity Cost**
🌍 **Estimated Carbon Emissions**
🏆 **Highest Energy-Consuming Appliances**
💡 **Energy-Saving Recommendations**

---

# 🎯 Main Objectives

1. Monitor appliance-level energy consumption.
2. Calculate estimated electricity usage in kWh.
3. Estimate electricity cost using a configurable tariff.
4. Estimate carbon emissions using a configurable emission factor.
5. Identify the highest-consuming appliances.
6. Provide practical energy-saving recommendations.
7. Demonstrate Python fundamentals and Object-Oriented Programming.
8. Promote awareness of sustainable energy consumption.

---

# 🌱 SDG Alignment

| SDG            | Goal                             | GreenGrid Contribution                                                 |
| -------------- | -------------------------------- | ---------------------------------------------------------------------- |
| ⚡ **SDG 7**    | Affordable & Clean Energy        | Helps users understand and reduce unnecessary electricity consumption. |
| 🏙️ **SDG 11** | Sustainable Cities & Communities | Encourages energy-aware homes and institutions.                        |
| 🌍 **SDG 13**  | Climate Action                   | Makes carbon impact visible and encourages lower-emission behavior.    |

---

# 🧮 Calculation Logic

### Energy Consumption

```text
Energy (kWh) = Power (W) × Usage Hours ÷ 1000
```

### Estimated Cost

```text
Cost = Energy (kWh) × Tariff per kWh
```

### Estimated Carbon Emissions

```text
Carbon (kg CO₂e) = Energy (kWh) × Emission Factor
```

---

## Authors

Aathif, Paras, Vetri, Sanket

---

