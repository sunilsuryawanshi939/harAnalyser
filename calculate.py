import pandas as pd
import streamlit as st
import altair as alt

# Function to filter DataFrame based on selected colors and custom rules
def filter_dataframe(df, selected_tags, tags_rules):
  filtered_df = df.copy()  # Avoid modifying original DataFrame
  for color in selected_tags:
    if color in tags_rules:
      rule = tags_rules[color]
      for col, val in rule.items():
        filtered_df = filtered_df[filtered_df[col] == val]
  return filtered_df


#return filtered dataset for newserviceapis
def filter_newserviceapis(df):
    """Filters a DataFrame to include rows where '1newserviceapi' or '60newserviceapi' is 'Y'.

    Args:
        df: The DataFrame to filter.

    Returns:
        A DataFrame containing the filtered rows.


    """
    
    filtered_df = df[(df['1newserviceapi'] == 'Y') | (df['60newserviceapi'] == 'Y')]
    filtered_df = filtered_df[(df['isFetch'] == 'Y')]

    return filtered_df

def analyze_har_dataframe(df):
    """Analyzes a DataFrame and returns various statistics.

    Args:
        df: The DataFrame to analyze.

    Returns:
        A dictionary containing the analysis results.
    """
    # 1) harStarted
    harStarted = df['startedDateTime'].iloc[0] if not df.empty else "N/A"

    # 2) harEnded
    harEnded = df['startedDateTime'].iloc[-1] if not df.empty else "N/A"

    # 3) exchanges
    exchanges = df['exchange'].unique()
    exchanges = [exchange for exchange in exchanges if exchange != 'N']

    # 4) count1newserviceapis
    count1newserviceapis = df[(df['1newserviceapi'] == 'Y') & (df['type'] == 'xhr')].shape[0]

    # 5) count60newserviceapis
    count60newserviceapis = df[(df['60newserviceapi'] == 'Y') & (df['type'] == 'xhr')].shape[0]

    # 6) countFetchAPIs
    countFetchAPIs = df[df['isFetch'] == 'Y'].shape[0]
    
    # 7) symbols
    symbols = df['symbol'].unique()
    symbols = [symbol for symbol in symbols if symbol != 'N']

    # 8) assetTypes
    assetTypes = df['asset'].unique()
    assetTypes = [asset for asset in assetTypes if asset != 'N']

    # 9) intervalsIncluded
    intervalsIncluded = df['interval'].unique()
    intervalsIncluded = [interval for interval in intervalsIncluded if interval != 'N']

    # 10) EquityCoCode
    EquityCoCode = df['cc_code'].unique()
    EquityCoCode = [code for code in EquityCoCode if code != 'N']

    # 11) Calculate the count of each unique value in the 'type' column
    type_counts = df['type'].value_counts()
    type_counts_dict = type_counts.to_dict()

    # Return the values
    return {
        "harStarted": harStarted,
        "harEnded": harEnded,
        "exchanges": exchanges,
        "count1newserviceapis": count1newserviceapis,
        "count60newserviceapis": count60newserviceapis,
        "countFetchAPIs": countFetchAPIs,
        "symbols": symbols,
        "assetTypes": assetTypes,
        "intervalsIncluded": intervalsIncluded,
        "EquityCoCode": EquityCoCode,
        "type_counts_dict": type_counts_dict,
    }


def plot_horizontal_bar_chart(data, display_percentages=False, height=400):
    """
    Function to plot a horizontal bar chart in Streamlit.

    Parameters:
        - data (dict or pandas.DataFrame): Dictionary or DataFrame containing the types of requests
                                            and their respective counts.
        - display_percentages (bool): Flag indicating whether to display percentages. Default is False.
        - height (int): Height of the chart. Default is 200.

    Returns:
        None
    """
    if isinstance(data, dict):
        # Convert dictionary to DataFrame
        df = pd.DataFrame.from_dict(data, orient='index', columns=['Count'])
        df.index.name = 'Type'
    elif isinstance(data, pd.DataFrame):
        df = data
    else:
        raise ValueError("Data must be a dictionary or pandas DataFrame.")

    # Calculate total count
    total_count = df['Count'].sum()

    # Calculate percentage
    if display_percentages:
        df['Percentage'] = (df['Count'] / total_count) * 100

    # Plotting the horizontal bar chart using Altair
    if display_percentages:
        chart = alt.Chart(df.reset_index()).mark_bar().encode(
            y=alt.Y('Type:N', title=None, sort='-x'),
            x='Percentage:Q',
            tooltip=['Type', 'Percentage']
        ).properties(height=height)
    else:
        chart = alt.Chart(df.reset_index()).mark_bar().encode(
            y=alt.Y('Type:N', title=None, sort='-x'),
            x='Count:Q',
            tooltip=['Type', 'Count']
        ).properties(height=height)

    st.altair_chart(chart, use_container_width=True)

    # Display the total count
    st.write(f"Total count: {total_count}")


def calculate_timing_stats(df):


    """
    Calculate the minimum, average, and maximum of the 'ttfb' and 'duration' columns in the DataFrame.

    Args:
        df: The DataFrame containing 'ttfb' and 'duration' columns.

    Returns:
        A dictionary containing the calculated statistics rounded to two decimal places.
    """
    stats = {}

    # Convert 'ttfb' and 'duration' columns to numeric, ignoring errors
    df['ttfb'] = pd.to_numeric(df['ttfb'], errors='coerce')
    df['time'] = pd.to_numeric(df['time'], errors='coerce')

    # Calculate statistics for 'ttfb'
    ttfb_min = round(df['ttfb'].min(), 2)
    ttfb_avg = round(df['ttfb'].mean(), 2)
    ttfb_max = round(df['ttfb'].max(), 2)

    stats['ttfb_min'] = ttfb_min
    stats['ttfb_avg'] = ttfb_avg
    stats['ttfb_max'] = ttfb_max

    # Calculate statistics for 'duration'
    time_min = round(df['time'].min(), 2)
    time_avg = round(df['time'].mean(), 2)
    time_max = round(df['time'].max(), 2)

    stats['time_min'] = time_min
    stats['time_avg'] = time_avg
    stats['time_max'] = time_max

    return stats



def find_max_time_row(http_df):
    # Find row with maximum time
    max_time_row = http_df.loc[http_df['time'].idxmax()]
    return max_time_row


# def calculate_interval_sum(http_df):
#     """
#     Calculates the total duration (in microseconds and seconds) of HTTP requests
#     and records row IDs for rows included in the calculation, considering interval changes.

#     Args:
#         http_df (pandas.DataFrame): A DataFrame containing columns 'time', 'interval',
#                                    'isTradingViewData', and 'rowid' (optional).

#     Returns:
#         tuple: A tuple containing three elements:
#             - interval_sum_micros (float): Total duration in microseconds (rounded to 3 decimal places).
#             - interval_sum_seconds (float): Total duration in seconds (rounded to 3 decimal places).
#             - row_ids (list): List of row IDs for rows included in the calculation.
#     """

#     # Convert 'duration' column to float (assuming 'time' represents duration)
#     http_df['time'] = http_df['time'].astype(float)

#     # Initialize variables
#     interval_sum_micros = 0
#     interval_sum_seconds = 0
#     counting = False
#     current_interval = None
#     row_ids = []

#     # Iterate through the rows
#     for i, row in http_df.iterrows():
#         # Check for interval change or start of data
#         if row['interval'] != current_interval and row['interval'] != 'N':
#             counting = True  # Start summing for a new interval (except 'N')
#             current_interval = row['interval']
#             interval_sum_micros = 0  # Reset sum for the new interval
#             row_ids.clear()  # Clear previously included row IDs

#         if counting:
#             interval_sum_micros += row['time']
#             row_ids.append(row['rowid'])

#         # Stop summing if encounter 'N' after a non-'N' interval
#         if row['interval'] == 'N' and current_interval is not None:
#             counting = False

#     # Convert sum from microseconds to seconds and round to 3 decimal places
#     interval_sum_seconds = round(interval_sum_micros / 1000, 3)
#     interval_sum_micros = round(interval_sum_micros, 3)

#     return interval_sum_micros, interval_sum_seconds, row_ids


def calculate_rowid(http_df):
  """
  Finds the `row['id']` of the second instance where `row['isTradingViewData']` is 'Y'
  and `row['interval']` is not 'N'.

  Args:
      http_df (pandas.DataFrame): A DataFrame containing columns 'id', 'time',
                                   'interval', and 'isTradingViewData'.

  Returns:
      int: The `row['rowid']` of the second matching row, or None if not found.
  """

  # Initialize counter to track occurrences
  count = 0
  target_id = None

  # Iterate through the rows
  for i, row in http_df.iterrows():
    if row['isTradingViewData'] == 'Y' and row['interval'] != 'N':
      count += 1
      if count == 2:
        target_id = row['rowid']
        break  # Stop iterating once the second instance is found

  return target_id


def calculate_first_load_time(http_df):
    """
    Calculates the following:
    - Total duration (in microseconds) from the first row to the second instance
      where `row['isTradingViewData']` is 'Y' and `row['interval']` is not 'N'.
    - `row['rowid']` of that instance.
    - Time taken for the first subsequent API call (in microseconds): This is the
      sum of `row['time']` from the row after the target row (exclusive) to the
      first row where `row['isTradingViewData']` is 'Y' (excluding the target row).

    Args:
        http_df (pandas.DataFrame): A DataFrame containing columns 'rowid', 'time',
                                     'interval', and 'isTradingViewData'.

    Returns:
        tuple: A tuple containing five elements:
            - total_time_combined (float): Combined total duration (microseconds, rounded to 3 decimal places).
            - first_target_rowid (int): The `row['rowid']` of the second matching row for the first instance, or None if not found.
            - second_target_rowid (int): The `row['rowid']` of the third matching row for the second instance, or None if not found.
            - time_after_target (float): Time taken for the first subsequent API call (microseconds, rounded to 3 decimal places), excluding the time of the row with the second target ID.
            - row_ids_used (dict): Dictionary containing the row IDs used for calculating `total_time_combined`.
    """

    # Initialize variables
    total_time_to_first_target = 0
    total_time_to_second_target = 0
    first_target_rowid = None
    second_target_rowid = None
    time_after_target = 0  # Renamed for clarity
    row_ids_used = {}  # Dictionary to store row IDs used for calculating total_time_combined

    # Efficiently locate target row using boolean indexing for the first instance
    first_target_row = http_df[(http_df['isTradingViewData'] == 'Y') & (http_df['interval'] != 'N')]
    if len(first_target_row) >= 2:
        first_target_rowid = first_target_row.iloc[1]['rowid']  # Get row ID of the second matching row for the first instance

    # Efficiently locate target row using boolean indexing for the second instance
    second_target_row = http_df[(http_df['isTradingViewData'] == 'Y') & (http_df['interval'] != 'N')].iloc[2:]
    if not second_target_row.empty:
        second_target_rowid = second_target_row.iloc[0]['rowid']  # Get row ID of the third matching row for the second instance

    # Convert 'time' column to float before calculations
    http_df['time'] = http_df['time'].astype(float)

    # Calculate total time to the first target row ID (for the first instance)
    if first_target_rowid is not None:
        total_time_to_first_target = http_df.loc[http_df['rowid'] <= first_target_rowid, 'time'].sum()
        row_ids_used['total_time_to_first_target'] = list(http_df.loc[http_df['rowid'] <= first_target_rowid, 'rowid'])

    # Calculate time after target (if first_target_rowid exists) and locate the third instance (second target)
    if first_target_rowid is not None and second_target_rowid is not None:
        # Calculate total time to the second target row ID (for the second instance)
        total_time_to_second_target = http_df.loc[(http_df['rowid'] > first_target_rowid) & (http_df['rowid'] <= second_target_rowid), 'time'].sum()
        row_ids_used['total_time_to_second_target'] = list(http_df.loc[(http_df['rowid'] > first_target_rowid) & (http_df['rowid'] <= second_target_rowid), 'rowid'])

        # Calculate time_after_target as the sum of time between the first and second target row IDs, excluding the time of the row with the second target ID
        time_after_target = http_df.loc[(http_df['rowid'] > first_target_rowid) & (http_df['rowid'] < second_target_rowid), 'time'].sum()
        row_ids_used['time_after_target'] = list(http_df.loc[(http_df['rowid'] > first_target_rowid) & (http_df['rowid'] < second_target_rowid), 'rowid'])

    # Combine total times and round the result
    total_time_combined = round(total_time_to_first_target + time_after_target, 3)

    return total_time_combined, first_target_rowid, second_target_rowid, time_after_target, row_ids_used


