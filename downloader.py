import pandas as pd

# Download as csv ----------------------------------------------------
def download_dataframe_as_csv(dataframe):
  """
  This function converts a Pandas DataFrame to a CSV string and returns it.
  """
  csv_string = dataframe.to_csv(index=False).encode('utf-8')
  return csv_string
