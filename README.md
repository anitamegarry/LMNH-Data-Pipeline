# Liverpool Museum of Natural History: Kiosk Data Pipeline  

## Overview  
The Liverpool Museum of Natural History (LMNH) is enhancing its visitor experience with a new system for collecting, storing, and analysing real-time feedback from *Smiley Face Survey Kiosks*. This project will provide LMNH staff with actionable insights through an automated ETL pipeline, real-time database updates, and a live data dashboard.  

---

## Current Focus: Real-Time ETL Pipeline and Dashboard  

The main focus is to assemble the full ETL pipeline to process live kiosk interaction data and provide real-time analytics through a Tableau dashboard.  

---

## Requirements  

### **Live Data Stream**  
- LMNH’s kiosk interactions are streamed in real-time using Kafka.  
- The pipeline will connect to the Kafka stream, clean incoming data, and insert it into the database.  

### **Data Validation**  
Incoming live data must be filtered for validity. Invalid data includes:  
1. **Human Error**: Accidental kiosk interactions (e.g., staff use after hours).  
2. **Mechanical Failure**: Stuck buttons or physical interference.  
3. **Wireless Interference**: Noise from unrelated devices.  
4. **Incorrect Exhibits**: Interactions from kiosks outside the project’s scope.  

#### **Validation Rules**:  
- **Time Constraints**: Only process interactions between 8:45 AM and 6:15 PM.  
- **Rating Constraints**: Ratings must be between `0–4`, and `type` values only `0` (assistance) or `1` (emergency).  
- **Exhibit Constraints**: Ignore interactions from exhibits not included in AWS S3 metadata.  
- **Message Structure**: Ignore messages with missing or invalid keys.  

### **Pipeline Hosting**  
The ETL pipeline will be hosted on an AWS EC2 instance to ensure continuous operation and real-time database updates.  

### **Dashboard Visualisation**  
A Tableau dashboard will provide museum staff with real-time insights, including:  
- Visitor satisfaction ratings by exhibit.  
- Trends in assistance/emergency requests.  
- Key metrics for optimising exhibition performance and visitor safety.  

---

## Deliverables  

### ETL Pipeline  
1. **Kafka Connection**: Script to consume and process live kiosk data from the Kafka stream.  
2. **Data Cleaning**: Real-time validation to ensure only valid interactions are stored.  
3. **Pipeline Hosting**: Deploy the ETL pipeline on an AWS EC2 instance for continuous updates.  

### Tableau Dashboard  
Interactive visualisations of kiosk data to support decision-making for stakeholders.  

---

## Stakeholders  

### **Exhibitions Manager**  
- Real-time data insights will help identify successful exhibitions and adapt quickly.  

### **Head of Security & Visitor Safety**  
- Visualising assistance and emergency trends will improve visitor safety and optimise staffing.  

---

## Architecture  

The final architecture includes the following components:  
1. **Kafka Data Stream**: Raw kiosk interaction data streamed in real-time.  
2. **ETL Pipeline**:  
   - Hosted on AWS EC2.  
   - Consumes Kafka messages, cleans the data, and updates the database.  
3. **Database**: Cloud-based storage for validated kiosk and exhibit data.  
4. **Tableau Dashboard**: Live visualisations of key metrics for museum staff.  

This real-time system will enable LMNH staff to make data-driven decisions, improving visitor engagement and safety.  