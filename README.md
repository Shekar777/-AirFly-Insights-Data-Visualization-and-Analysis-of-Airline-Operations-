✈️ Airfly Insights
Data Visualization and Analysis of Airline Operations

📌 Project Overview
Airfly Insights is a data analytics project focused on analyzing airline flight operations to identify patterns in delays, routes, and operational performance using historical flight data.

Dataset: https://www.kaggle.com/datasets/mahoora00135/flights

📌 Milestone 1: Data Understanding, Cleaning & Feature Engineering
✅ Tasks Completed

1️. Data Understanding
      Explored the airline flights dataset to understand structure and data types.
      Identified key operational columns such as departure delay, arrival delay, route, and time attributes.
      Analyzed the presence and impact of missing values.
2️. Data Cleaning
3. Feature Engineering

      Created meaningful derived columns to support airline operations analysis:
      Flight Date – Combined year, month, and day into a datetime column
      Month – Extracted for seasonal trend analysis
      Day of Week – Derived to analyze weekday vs weekend patterns
      Hour – Extracted from scheduled departure time to study congestion trends
      Route – Created using origin and destination airports
      Delay Severity – Categorized using arrival delay values
      Is Weekend – Flag created to identify weekend vs weekday flights
      Departure Period – Categorized departure times into time-of-day buckets
      (Night, Morning, Afternoon, Evening, Late Night)
      Departure Delay Flag – Identifies whether a flight departed on time or was delayed
      Arrival Delay Flag – Identifies whether a flight arrived on time or was delayed
      Distance Category – Classified flights into Short, Medium, and Long distances
   
5. Preprocessed Data Storage

      Saved the cleaned and feature-engineered dataset as a separate file
      Enabled fast reuse without repeating preprocessing steps
