# NeerNiti — Project Specification

## 1. Project Identity

**Project Name:** NeerNiti

**Project Type:** AI-Powered Agricultural Decision-Support System

**Domain:** Agriculture Technology / Artificial Intelligence / Machine Learning

**Primary Users:** Farmers

**Primary Goal:**

NeerNiti is a cloud-based AI agricultural decision-support platform that helps farmers make more informed decisions about soil condition, crop selection, fertilizer usage, and weather-related agricultural risks.

The system allows farmers to manually enter their farm and soil information instead of depending on physical IoT sensors. The information is stored in a cloud PostgreSQL database and can be combined with machine-learning models and weather information to generate personalized agricultural insights.

---

# 2. Project Vision

NeerNiti aims to transform manually available farm and soil information into understandable, personalized agricultural recommendations.

The system should answer three major questions:

### Understand

> What is happening to my soil?

### Recommend

> What crop and fertilizer may be suitable for my current conditions?

### Predict

> What agricultural risks may arise from upcoming weather and changing conditions?

The platform should prioritize:

- Simplicity
- Explainability
- Personalization
- Data-driven recommendations
- Modular architecture
- Responsible AI
- Maintainability

---

# 3. Core Project Concept

The farmer interacts with a web application.

The basic workflow is:

Farmer
→ Signup/Login
→ Farmer Profile
→ Farm Profile
→ Manual Soil Data Entry
→ Cloud PostgreSQL
→ ML Models + Weather API
→ Decision Engine
→ Recommendations
→ Farmer Dashboard
→ Historical Analysis

The system does NOT require physical sensors for the MVP.

---

# 4. MVP Scope

The Minimum Viable Product must contain the following:

1. Farmer signup
2. Farmer login
3. Farmer profile
4. Farm profile
5. Manual soil-data entry
6. Cloud PostgreSQL storage
7. Soil-health analysis
8. Crop recommendation
9. Fertilizer recommendation
10. Weather information
11. Weather-aware agricultural risk
12. Recommendation history
13. Soil history
14. Basic charts/trends
15. Basic recommendation explainability

The MVP should be completed and tested before implementing advanced features.

---

# 5. Features Explicitly NOT Required in MVP

The following must NOT be introduced as core MVP requirements:

- Physical pH sensors
- EC sensors
- NPK sensors
- Soil-moisture sensors
- ESP32
- MQTT
- IoT telemetry
- Automatic fertigation hardware
- Automatic irrigation hardware
- Physical fertilizer dispensing
- Deep-learning models unless later justified
- Exact guaranteed fertilizer dosage
- Guaranteed crop yield prediction
- Automated agricultural actions

IoT functionality may be considered as a future extension but is not part of the current core architecture.

---

# 6. Primary Functional Modules

## 6.1 Authentication

The system must support:

- Signup
- Login
- Logout
- Authenticated user retrieval
- Password hashing
- JWT-based authentication
- Protected API routes

Passwords must never be stored as plaintext.

---

## 6.2 Farmer Profile

A farmer profile may contain:

- Name
- Email
- Phone
- Location
- District
- State
- Account creation timestamp

The profile belongs to one authenticated user.

---

## 6.3 Farm Management

A farmer can create and manage one or more farms.

Farm information may include:

- Farm name
- Location
- Latitude
- Longitude
- Land area
- Soil type
- Water source
- Creation timestamp
- Updated timestamp

One farmer can own multiple farms.

A farmer must only be able to access their own farms.

---

# 7. Manual Soil Data

The system must allow farmers to manually enter soil readings.

Possible parameters:

- Nitrogen
- Phosphorus
- Potassium
- pH
- Soil moisture
- Electrical conductivity
- Organic carbon

Not every parameter must be mandatory if the selected ML model does not require it.

The exact required fields must be determined by the finalized dataset and ML pipeline.

Each soil test must belong to a specific farm.

Example:

```text
Farm
    |
    ├── Soil Test 1
    ├── Soil Test 2
    └── Soil Test 3