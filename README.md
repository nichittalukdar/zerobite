# ShareBite Frontend

ShareBite is a food-sharing platform designed to connect food donors with people who need food, while helping reduce unnecessary food waste.

This repository contains the **frontend implementation** of ShareBite.

## 🚀 Features

### 🏠 Homepage
- ShareBite landing page
- Navigation between Donor and Receiver dashboards
- About section
- How It Works section
- Responsive-friendly layout structure

### 👤 Donor Dashboard
- Donor dashboard interface
- Food donation form
- Food name, quantity, servings and pickup location
- Optional food description
- Form validation
- Donation cards
- Saved donations using browser `localStorage`
- Donations remain available after refreshing the page

### 🍱 Receiver Dashboard
- Available food listing
- Search food functionality
- Food quantity and serving information
- Pickup location display
- Claim Food functionality
- Claimed food is removed from Available Food
- Claim timestamp
- My Claims section
- Claims remain saved after refreshing the page

## 💾 Data Storage

The current frontend uses **browser `localStorage`** for temporary data storage.

Food information is stored using:

`shareBiteFoods`

### Current Data Flow

Donor  
↓  
Donation Form  
↓  
localStorage  
↓  
Available Food  
↓  
Receiver  
↓  
Claim Food  
↓  
My Claims

The current `localStorage` system is being used for frontend development and testing. It can later be replaced or connected to the ShareBite FastAPI backend.

## 📁 Project Structure

```text
frontend1/
├── index.html
├── css/
│   └── style.css
├── js/
│   └── script.js
└── pages/
    ├── donor.html
    └── receiver.html