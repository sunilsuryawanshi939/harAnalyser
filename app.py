import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
import time 
import time as t
import helper ,downloader , rules ,calculate

import json ,re
import pandas as pd
from datetime import datetime
import pytz
import base64


#----------------------




#Page_config---------------------------------------------------
st.set_page_config(
    page_title="HTTP archive Explorer",
    layout="wide",
    # initial_sidebar_state="collapsed",
    )

#------------------------------Hiding the menus---------------------------------------- 
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
                    footer {visibility: hidden;}
                    footer:after {
                        content:'Developed By : Sunil Suryawanshi'; 
                        visibility: visible;
                        display: block;
                        font-size: 21px;
                        text-align: center;
                        #color:#ff0000;
                        position: relative;
                        #background-color: black;
                        padding: 5px;
                        top: 2px;
                    }
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True) 
#---------------------------------------------------------------------------------------
st.sidebar.title("HTTP Archive Data Explorer")
st.header('Data Explorer')
introSlot = st.empty()
introCont =introSlot.container()

flag = 0 
nflag = 0
df = pd.DataFrame()

uploaded_file = st.sidebar.file_uploader("Drop a .har file",help="Upload your .har file here", type=["har"])


if (uploaded_file is not None):
    filename = uploaded_file.name
    filename_without_ext = uploaded_file.name.rsplit('.', 1)[0]
    st.write(f"You uploaded a file named: {filename}")

    if(flag==0 and nflag==0):
      introSlot.empty()
      my_slot1 = st.empty()
      progress = st.progress(0)
      for i in range(100):
          time.sleep(0.01)
          progress.progress(i+1)
          waitMsg ='Processing your request ...'+' Progress : '
          progressCount = str(i+1)
          my_slot1.text(waitMsg + progressCount)
    progress.empty()

    my_slot1.text('')
    my_slot1.text('Changes applied successfully . Click on Show Analysis')

    # df = pd.read_csv(uploaded_file) #,encoding = 'unicode_escape'
    # # st.write(df['is_txn'].value_counts(dropna=False)[2])  ########################
    # # st.write(df[df.is_txn == False].shape[0])

    # Read the uploaded file and parse JSON content
    har = json.loads(uploaded_file.read().decode('utf-8'))
    # Process the .har file as needed
    st.write("File uploaded successfully!")


    # # fetch unique users
    # user_list = df['vcexternaldeviceid'].unique().tolist()
    # user_list.sort()
    # user_list.insert(0,"Overall")

    # selected_user = st.sidebar.selectbox("Show analysis wrt",user_list)

    # df = pd.read_csv(uploaded_file)
    # st.write(df)

    # #number of unique devices
    # st.write(df.vcexternaldeviceid.unique())
    # st.write(df.vcexternaldeviceid.nunique(dropna=True))

    
    #------------------------------------------------
#------------------------------------------------------------------#

    if st.sidebar.button("Show Analysis"):
        # Stats Area
        my_slot1.text('')
        flag=1
        st.spinner()
        spinnerWait    =  "The analysis is being done ..Please Wait"
        successChatmsg ="The HTTP archive data has been analysed"

        with st.spinner(text=spinnerWait):
            t.sleep(0.5)

        st.success(successChatmsg)
       
        #create a dataframe
        dat_clean = helper.createDataFrame(har)

        #Top statistics
        results = calculate.analyze_har_dataframe(dat_clean)

        with st.expander("Top Statistics"):
            st.header("Top statistics")
            st.subheader(f"File uploaded : :blue[{filename}]")
            # st.write(results)

            col1, col2, col3 , col4  = st.columns(4)
            with col1:
                st.header("Har Start")
                st.subheader(f':green[{results["harStarted"]}]')
            with col2:
                st.header("Har End")
                st.subheader(f':red[{results["harEnded"]}]')
            with col3:
                st.header("Exchanges")
                st.subheader(f':blue[{results["exchanges"]}]')
            with col4:
                st.header("Symbols")
                st.subheader(f':blue[{results["symbols"]}]')

            col5 , col6 ,col7 ,col8= st.columns(4)
            with col5:
                st.header("1newservice")
                st.subheader(f':green[{results["count1newserviceapis"]}]')
            with col6:
                st.header("60newservice")
                st.subheader(f':green[{results["count60newserviceapis"]}]')
            with col7:
                st.header("xhr")
                typeCountsDict = results.get("type_counts_dict",{})
                xhrcount = typeCountsDict.get('xhr',0)
                st.subheader(f':green[{xhrcount}]')
            with col8:
                st.header("fetch")
                typeCountsDict = results.get("type_counts_dict", {})  # Use get() method with a default value of empty dictionary
                fetchcount = typeCountsDict.get('fetch', 0)  # Use get() method again to fetch the value with a default of 0
                st.subheader(f':green[{fetchcount}]')

            col9 ,col10 ,col11, col12 = st.columns(4)
            with col9:
                st.header("Stylesheets")
                typeCountsDict = results.get("type_counts_dict", {})
                stylesheetcount = typeCountsDict.get('stylesheet',0)
                st.subheader(f':green[{stylesheetcount}]')

            with col10:
                st.header("Scripts")
                typeCountsDict = results.get("type_counts_dict",{})
                scriptcount = typeCountsDict.get('script',0)
                st.subheader(f':green[{scriptcount}]')  

            with col11:
                st.header("Images")
                typeCountsDict = results.get("type_counts_dict",{})
                imagecount = typeCountsDict.get('image',0)
                st.subheader(f':green[{imagecount}]')
            
            with col12:
                st.header("ping")
                typeCountsDict = results.get("type_counts_dict",{})
                pingcount = typeCountsDict.get('ping',0)
                st.subheader(f':green[{pingcount}]')
            
            col13, col14, col15, col16 = st.columns(4)

            with col13:
                st.header("preflight")
                typeCountsDict = results.get("type_counts_dict",{})
                preflightcount = typeCountsDict.get('preflight',0)
                st.subheader(f':green[{preflightcount}]')
            
            with col14:
                st.header("websocket")
                typeCountsDict = results.get("type_counts_dict", {})  # Use get() method with a default value of empty dictionary
                websocketcount = typeCountsDict.get('websocket', 0)  # Use get() method again to fetch the value with a default of 0
                st.subheader(f':green[{websocketcount}]')
            
            with col15:
                st.header("document")
                typeCountsDict = results.get("type_counts_dict",{})
                documentcount = typeCountsDict.get('document',0)
                st.subheader(f':green[{documentcount}]')
            
            with col16:
                st.header("font")
                typeCountsDict = results.get("type_counts_dict",{})
                fontcount = typeCountsDict.get('font',0)
                st.subheader(f':green[{fontcount}]')
                    
            typeCountsDict = results["type_counts_dict"]
        
            # Call the function to plot the chart with counts
            calculate.plot_horizontal_bar_chart(typeCountsDict)

            # # Optionally, call the function to plot the chart with percentages
            # calculate.plot_horizontal_bar_chart(typeCountsDict, display_percentages=True)        

            col17, col18 ,col19 = st.columns(3)
            with col17:
                st.header("assetTypes")
                st.subheader(f':blue[{results["assetTypes"]}]')
            with col18:
                st.header("intervalsIncluded")
                st.subheader(f':blue[{results["intervalsIncluded"]}]')
            with col19:
                st.header("EquityCoCode")
                st.subheader(f':blue[{results["EquityCoCode"]}]')        

        
        with st.expander("HTTP archive dataset"):
            #display the main dataset
            st.header('The HTTP archive dataset')
            st.write(dat_clean)


            # #download as csv
            # csv_string = downloader.download_dataframe_as_csv(dat_clean)
            # st.download_button(
            # label="Download Data as CSV",
            # data=csv_string,
            # file_name= str(filename_without_ext)+".csv",
            # mime="text/csv",
            # )


        with st.expander("Filtered newserviceapi logs"):
            #show filtered newserviceapi logs
            st.subheader("Filtered newserviceapi logs")
            filtered_newserviceapis_dataset = calculate.filter_newserviceapis(dat_clean)
            st.write(calculate.filter_newserviceapis(dat_clean))
            
            timings_data = calculate.calculate_timing_stats(filtered_newserviceapis_dataset)

            col1, col2 ,col3 = st.columns(3)
            with col1:
                st.header("Minimum TTFB")
                ttfb_min = timings_data['ttfb_min']
                st.subheader(f':green[{ttfb_min}] ms')
            with col2:
                st.header("Average TTFB")
                ttfb_avg = timings_data['ttfb_avg']
                st.subheader(f':blue[{ttfb_avg}] ms')
            with col3:
                st.header("Maximum TTFB")
                ttfb_max = timings_data['ttfb_max']
                st.subheader(f':red[{ttfb_max}] ms')    

            col4, col5 ,col6 = st.columns(3)
            with col4:
                st.header("Minimum Time")
                time_min = timings_data['time_min']
                st.subheader(f':green[{time_min}] ms')
            with col5:
                st.header("Average Time")
                time_avg = timings_data['time_avg']
                st.subheader(f':blue[{time_avg}] ms')
            with col6:
                st.header("Maximum Time")
                time_max = timings_data['time_max']
                st.subheader(f':red[{time_max}] ms')    


            # # Calculate interval sum
            # interval_sum_micro, interval_sum_seconds ,included_row_ids= calculate.calculate_interval_sum(dat_clean)    
            # st.subheader(f"First time loading chart takes : :red[{interval_sum_micro} ms] OR :blue[{interval_sum_seconds} sec]")
            # st.subheader(f"Included row ids: :blue[{included_row_ids}]")


            # Calculate the total time until the first successful tradingviewdata api call and all the css,images,js etc
            total_time_combined, first_target_id, second_target_id, time_after_target, row_ids_used = calculate.calculate_first_load_time(dat_clean)
            st.subheader(f"First load time (Loading js,css,font etc and first api call with tradingviewdata ): :red[{total_time_combined}] ms or :blue[{total_time_combined/1000}] sec")
            st.subheader(f"Rowid - First instance where isTradingViewData exists : :blue[{first_target_id}]")
            st.subheader(f"Rowid - Second instance where isTradingViewData exists : :blue[{second_target_id}]")
            # st.subheader(f"Time between first and second instance : :blue[{time_after_target}] ms")
            st.subheader(f"Row ids used for calculating the time  : :blue[{row_ids_used}]")

            # Display the rowid
            st.subheader("Row with second instance of interval change ")
            st.subheader(calculate.calculate_rowid(dat_clean))  

            # Display the maximum duration row
            st.subheader("Row with Maximum Time: ")
            st.dataframe(calculate.find_max_time_row(filtered_newserviceapis_dataset))     


