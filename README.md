# DineMetra

## Description
Web App for Restaurant Managers that predicts how busy a restaurant will be depending on factors such as past sales data, weather, and other events in the area.

## Schema Setup
psql -U your_username -d rushradar_db -f backend/database/schema.sql

## Flowchart
```mermaid
flowchart TB
        A(["Sales Data"]) --> E{"Database"}
        B(["Weather Data"]) --> E{"Database"}
        C(["Events Data"]) --> E{"Database"}
        D(["Geolocation Data"]) --> E{"Database"}
       
        E --> F["Prediction Engine/Scoring System"]
        F --> G["Database Table"]
        G --> H["API"]
        H --> I["Login Page"]
        I --> J["Dashboard & Search"]
        J --> K["Calendar View"]
