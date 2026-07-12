# 🚀 Celebal Excellence Internship (CEI) 2026

Welcome to my repository for the *Celebal Excellence Internship (CEI) 2026*.

This repository serves as a centralized collection of all assignments, hands-on exercises, projects, and learning outcomes completed throughout the internship. The goal is to document my progress and showcase practical skills developed in Python, SQL, Data Analysis, Data Engineering, and Artificial Intelligence.

---

## 👨‍💻 About Me

*Nikhil*  
B.Tech Computer Science Engineering  
DIT University, Dehradun

*Domain:* Data Engineering

---

## 📂 Repository Structure

⁠ text
CEI-2026/
│
├── Week-1/
├── Week-2/
├── Week-3/
├── Week-4/
├── Week-5/
└── README.md
 ⁠

Each folder contains the assignment, notebook, datasets (if applicable), and supporting files for that week.

---

## 📅 Weekly Progress

| Week | Topic | Status |
|------|-------|--------|
| Week 1 | Basic Data Exploration and Cleaning using Pandas | ✅ Completed |
| Week 2 | SQL-Based Sales Data Analysis | ✅ Completed |
| Week 3 | Advanced SQL using Subqueries, CTEs & Window Functions | ✅ Completed |
| Week 4 | To be Updated | ⏳ |
| Week 5 | To be Updated | ⏳ |

---

## 📊 Week 1 Highlights

### Topic

*Basic Data Exploration and Cleaning using Pandas*

### Key Tasks

•⁠  ⁠Loaded CSV dataset into a Pandas DataFrame
•⁠  ⁠Explored dataset structure and statistics
•⁠  ⁠Identified and handled missing values
•⁠  ⁠Performed filtering and column selection
•⁠  ⁠Removed duplicate records
•⁠  ⁠Created derived features
•⁠  ⁠Exported cleaned dataset

### Technologies Used

•⁠  ⁠Python
•⁠  ⁠Pandas
•⁠  ⁠Jupyter Notebook

### Deliverables

•⁠  ⁠Jupyter Notebook (⁠ analysis_shopping.ipynb ⁠)
•⁠  ⁠Cleaned Dataset (⁠ cleaned_shopping_dataset.csv ⁠)

---

## 🗄️ Week 2 Highlights

### Topic

*SQL-Based Sales Data Analysis*

### Key Tasks

•⁠  ⁠Loaded the Superstore sales dataset into a SQL database
•⁠  ⁠Explored table schema and sample records
•⁠  ⁠Applied filtering using ⁠ WHERE ⁠ clauses
•⁠  ⁠Performed aggregations using ⁠ GROUP BY ⁠
•⁠  ⁠Calculated sales, quantities, and averages
•⁠  ⁠Identified top-performing products and categories
•⁠  ⁠Analyzed monthly sales trends
•⁠  ⁠Identified top customers based on sales
•⁠  ⁠Detected duplicate records
•⁠  ⁠Validated data quality using row counts and null-value checks
•⁠  ⁠Generated business insights through SQL queries

### Technologies Used

•⁠  ⁠SQL
•⁠  ⁠SQLite
•⁠  ⁠Google Colab
•⁠  ⁠Pandas

### Deliverables

•⁠  ⁠Jupyter Notebook (⁠ superstore_analysis.ipynb ⁠)
•⁠  ⁠SQL Script (⁠ sql_analysis.sql ⁠)

---

## 🗄️ Week 3 Highlights

### Topic

*Advanced SQL using Subqueries, CTEs & Window Functions*

### Key Tasks

•⁠  ⁠Imported the Superstore dataset into a SQL database
•⁠  ⁠Created normalized tables (⁠ customers ⁠, ⁠ orders ⁠, and ⁠ products ⁠)
•⁠  ⁠Performed advanced filtering using Subqueries
•⁠  ⁠Used Common Table Expressions (CTEs) for reusable aggregations
•⁠  ⁠Applied Window Functions (⁠ RANK() ⁠ and ⁠ ROW_NUMBER() ⁠)
•⁠  ⁠Ranked customers based on total sales
•⁠  ⁠Identified top and bottom customers
•⁠  ⁠Analyzed customers with above-average sales
•⁠  ⁠Determined customers who placed only one order
•⁠  ⁠Calculated the highest order value for each customer
•⁠  ⁠Combined ⁠ JOIN ⁠, ⁠ CTE ⁠, and ⁠ Window Functions ⁠ to generate customer sales insights

### Technologies Used

•⁠  ⁠SQL
•⁠  ⁠SQLite
•⁠  ⁠Google Colab
•⁠  ⁠Pandas

### Deliverables

•⁠  ⁠Jupyter Notebook (⁠ week3_advanced_sql.ipynb ⁠)
•⁠  ⁠SQL Script (⁠ superstore_advanced_queries.sql ⁠)

---

# ☁️ Week 4 — Azure Data Factory & Blob Storage Integration

### Objective

Design and implement a cloud-based ETL workflow using Microsoft Azure services to transfer a CSV file between Azure Blob Storage containers while validating file metadata before processing.

### Key Learning Outcomes

•⁠  ⁠Provisioned Azure cloud resources including Resource Group, Storage Account, and Azure Data Factory.
•⁠  ⁠Configured Blob Storage containers for source and destination data.
•⁠  ⁠Established connectivity through Azure Blob Storage Linked Service.
•⁠  ⁠Created source and sink datasets for CSV files.
•⁠  ⁠Developed an Azure Data Factory pipeline using:
  - *Get Metadata* activity to verify source file properties.
  - *Copy Data* activity to transfer data between containers.
•⁠  ⁠Configured and validated Azure IAM permissions to enable secure communication between Azure Data Factory and Blob Storage.
•⁠  ⁠Validated, published, and successfully executed the pipeline.
•⁠  ⁠Confirmed successful file transfer by verifying the output in the destination container.

### Mini Project

An end-to-end Azure Data Factory pipeline was developed to automate CSV file movement within Azure Blob Storage. Before copying the file, metadata such as file existence, size, and last modified time was validated using the Get Metadata activity. After successful validation, the Copy Data activity transferred the file to the destination container. The project concluded with successful pipeline execution and verification of the copied output.

### Deliverables

•⁠  ⁠Azure Resource Group
•⁠  ⁠Azure Storage Account
•⁠  ⁠Blob Storage Containers
•⁠  ⁠Azure Data Factory Instance
•⁠  ⁠Linked Service Configuration
•⁠  ⁠Source & Sink Datasets
•⁠  ⁠Get Metadata Activity
•⁠  ⁠Copy Data Activity
•⁠  ⁠IAM Role Configuration
•⁠  ⁠Published Pipeline
•⁠  ⁠Successful Pipeline Execution
•⁠  ⁠Output Verification

### Technologies Used

•⁠  ⁠Microsoft Azure
•⁠  ⁠Azure Resource Manager
•⁠  ⁠Azure Blob Storage
•⁠  ⁠Azure Data Factory
•⁠  ⁠Azure IAM
•⁠  ⁠Get Metadata Activity
•⁠  ⁠Copy Data Activity
•⁠  ⁠CSV Dataset

## 🛠️ Skills Developed

Throughout this internship, I aim to strengthen my skills in:

•⁠  ⁠Python Programming
•⁠  ⁠SQL & Database Management
•⁠  ⁠Data Analysis
•⁠  ⁠Data Cleaning & Preprocessing
•⁠  ⁠Business Analytics
•⁠  ⁠Data Engineering
•⁠  ⁠Database Design
•⁠  ⁠Advanced SQL (Subqueries, CTEs & Window Functions)
•⁠  ⁠Data Visualization
•⁠  ⁠Artificial Intelligence

---

## 🎯 Internship Goal

To gain practical industry experience by solving real-world business problems, building data-driven solutions, and applying modern Data Engineering, SQL, and AI techniques through structured weekly assignments and projects.

---

## 📌 Note

This repository will be updated regularly as new assignments and projects are completed during the CEI 2026 program.

---

⭐ Thank you for visiting this repository. Feedback and suggestions are always welcome.
