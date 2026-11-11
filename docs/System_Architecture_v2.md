# System Architecture (v2)

```mermaid
graph TD
    subgraph Mobile Client "Flutter Mobile App"
        UI[UI Layer]
        Offline[Local SQLite & Sync]
        QR[QR Scanner]
        Lang[Multi-Language Provider]
        UI <--> Offline
        UI --> QR
        UI --> Lang
    end

    subgraph Web Client "React Admin Dashboard"
        AdminUI[Dashboard UI]
        GIS[GIS Leaflet Map]
        Charts[Chart.js Analytics]
        AdminUI --> GIS
        AdminUI --> Charts
    end

    subgraph Backend Server "Flask API"
        API[RESTful API Routes]
        AI[NLP/AI Classifier]
        Esc[Escalation Engine]
        PDF[PDF Report Generator]
        
        API --> AI
        API --> Esc
        API --> PDF
    end

    subgraph Database Layer "MySQL & Firebase"
        DB[(MySQL v8)]
        FB[Firebase Storage]
    end

    Mobile Client <--> |JSON / HTTPS| Backend Server
    Web Client <--> |JSON / HTTPS| Backend Server
    Backend Server <--> DB
    Backend Server <--> FB
```
