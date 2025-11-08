# Data Folder Overview

This folder contains all the data related to the image processing experiments, organized to keep raw and processed information separate and easy to manage.

## Raw
Contains the original, unmodified images and the temperature logs. Data is organized into batches. Each batch has:
- A folder with the raw images
- A temperature_log.txt file containing temperature and time readings from the sensor

*Temperature Log*
This text file records the experimental steps along with corresponding temperature and time data.

## Processed
Contains images after they have been processed by the pipeline. 

Processed images are organized by batches, matching the raw data batches.

Inside this folder, there is a metrics/ subfolder where CSV files store numerical results (metrics) extracted from the images for each batch.

## Metadata
Contains files that combine the image metrics with the corresponding temperature log data.

This unified data enables analysis by linking image-derived metrics with the temperature and time information from the experiments.