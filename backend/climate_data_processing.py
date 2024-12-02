import pandas as pd
import numpy as np
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
import time

# Function to fetch latitude and longitude using geocoding with improved error handling
def get_coordinates(country):
    geolocator = Nominatim(user_agent="climate-impact-analyzer", timeout=10)  # Set timeout to 10 seconds
    try:
        location = geolocator.geocode(country)
        if location:
            return location.latitude, location.longitude
        else:
            # Return None if coordinates are not found
            return None, None
    except GeocoderTimedOut:
        print(f"Geocoding service timed out for {country}. Retrying...")
        time.sleep(2)  # Wait for 2 seconds before retrying
        return get_coordinates(country)  # Retry the request
    except GeocoderUnavailable:
        print(f"Geocoding service unavailable for {country}. Skipping...")
        return None, None
    except Exception as e:
        print(f"An error occurred while geocoding {country}: {e}")
        return None, None

def load_climate_data(file1, file2):
    """
    Loads and merges the climate data from two CSV files:
    - Annual_Surface_Temperature_Change (1961-2022)
    - Land_Ocean_Temperature_Index (with Year, No_Smoothing, Lowess(5))

    The data is merged based on the 'Year' column and includes latitude and longitude for each country.
    """
    # Load the CSV files into pandas DataFrames
    df1 = pd.read_csv(file1)  # Annual Surface Temperature Change data
    df2 = pd.read_csv(file2)  # Land Ocean Temperature Index data

    # Print columns for debugging
    print("Columns in df1 (Annual_Surface_Temperature_Change):", df1.columns)
    print("Columns in df2 (Land_Ocean_Temperature_Index):", df2.columns)

    # Check if 'Year' exists in both datasets
    if 'Year' not in df1.columns:
        print("Year column not found in df1. Attempting to reshape.")
        df1 = pd.melt(df1, id_vars=['Country', 'ISO2', 'ISO3', 'Indicator', 'Unit', 'Source'],
                      var_name='Year', value_name='Temperature_Change')

        # Extract year from columns like 'F1961', 'F1962', etc.
        df1['Year'] = df1['Year'].str.extract('(\d+)')
        df1['Year'] = pd.to_numeric(df1['Year'], errors='coerce')
        df1 = df1.dropna(subset=['Year'])
        df1['Year'] = df1['Year'].astype(int)

    # Ensure 'Year' exists in the second dataset (df2)
    if 'Year' not in df2.columns:
        raise ValueError("The second dataset does not have a 'Year' column.")

    # Merge the two datasets on 'Year'
    merged_data = pd.merge(df1, df2, on="Year", how="inner")

    # Geocode latitude and longitude for each country (Handle errors gracefully)
    merged_data['Latitude'], merged_data['Longitude'] = zip(*merged_data['Country'].apply(get_coordinates))

    # Optional: Drop rows where latitude or longitude could not be found
    merged_data = merged_data[merged_data['Latitude'].notna() & merged_data['Longitude'].notna()]

    # Log merged data for inspection
    print("Merged data with coordinates:\n", merged_data.head())

    return merged_data

def calculate_correlation(data):
    """
    Calculates the Pearson correlation matrix for the climate data.
    """
    required_columns = ['Temperature_Change', 'No_Smoothing', 'Lowess(5)']
    
    if not all(col in data.columns for col in required_columns):
        raise ValueError(f"Data must contain the following columns: {', '.join(required_columns)}")

    # Calculate the correlation matrix
    correlation_matrix = data[required_columns].corr()

    # Log the correlation matrix for verification
    print("Correlation Matrix:\n", correlation_matrix)

    # Convert the correlation matrix to a dictionary for easy JSON serialization
    correlation_dict = correlation_matrix.to_dict()

    return correlation_dict
