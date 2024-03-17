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
    df['duration'] = pd.to_numeric(df['duration'], errors='coerce')

    # Calculate statistics for 'ttfb'
    ttfb_min = round(df['ttfb'].min(), 2)
    ttfb_avg = round(df['ttfb'].mean(), 2)
    ttfb_max = round(df['ttfb'].max(), 2)

    stats['ttfb_min'] = ttfb_min
    stats['ttfb_avg'] = ttfb_avg
    stats['ttfb_max'] = ttfb_max

    # Calculate statistics for 'duration'
    duration_min = round(df['duration'].min(), 2)
    duration_avg = round(df['duration'].mean(), 2)
    duration_max = round(df['duration'].max(), 2)

    stats['duration_min'] = duration_min
    stats['duration_avg'] = duration_avg
    stats['duration_max'] = duration_max

    return stats