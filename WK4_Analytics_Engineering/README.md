# Analytics Engineering

Analytics Engineering serves as sort of a hybrid field between Data Analytics and Data Engineering. Data Engineers server in more of a software engineering role in data architecture development, whereas Data Analysts focus heavily on interpretation and consumption of results. An Analytics Engineer can bridge the gap between these two fields - providing good software engineering practices to the analytics and machine learning efforts of Data Analyts and Data Scientists.

Analytics Engineers work across all areas of the data ingestion and presentation process, including
* Data Loading
* Data Storing
* Data Modeling
* Data Presentation

The focus in this course for Analytics Engineering will be on **Data Modeling** and **Data Presentation**

## Data Modeling

Two major methods exist for obtaining and integrating data into a datawarehouse
* Extract, Transform, Load (ETL)
* Extract, Load, Transform (ELT)

In ETL processes the data is transformed prior to being loaded into a datawarehouse. This can have higher cost and be be longer to implement as transformations are applied in the pipeline, but leads to cleaner results in the data warehouse. Conversely ELT pipelines will be faster and more flexible due to data being loaded as is before performing transformations. ELT pipelines can also take advantage of lower storage and compute costs when the data is present in cloud data warehouses

One popular strategy for data modeling is **Kimball's Dimensional Modeling**, focusing on prioritizing user understandability and query performance over non-redundant data. This data modeling strategy focuses on using a star-schema containing facts and dimension tables
* *fact tables* contain measures, metrics, or facts related to business processes such as sales, cost, etc.
* *dimension tables* contain information on business entities such as customer, product, etc.

A useful representation of Kimball's modeling architecture is the kitchen analogy. This describes breaking down a data warehouse architecture and ETL process can be broken down into the following groups
* Stage Area (Sourcing and Stocking)
  * Contains raw data and has limited access by users
* Processing Area (Kitchen)
  * Raw data is processed in data models by data team
  * Focuses on efficiency and ensuring data standards are met
* Presentation Area (Dining Hall)
  * Final data presentation
  * Broad user access by stakeholders