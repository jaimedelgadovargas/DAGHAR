"""Check the signal quality searching for nan values or amplitude higher than a threshold of mean frequency higher than the reference frequency.

Parameters
----------
vector : pd.DataFrame
    The vector of signal as an example an axis of accelerometer
timestamp : A Timestamp Local vector
ref_frequency : Reference frequency value of the dataset as ex 100Hz 
ref_amplitude : Reference amplitude value of the dataset as ex 50 m/s^2  
"""

def check_quality(vector,timespamp,ref_frequency,ref_amplitud):
    
    if vector.isna().any().any():
        print("...nan")
        return False

    if vector.max() > ref_amplitud or abs(vector.min()) > ref_amplitud:
        print("...amplitude", vector.max() , vector.min())
        return False
        

    w_start, w_end = timespamp.iloc[0], timespamp.iloc[-1]
    w_duration = w_end - w_start
    period=w_duration/timespamp.size
    ref_period= (1/ref_frequency)*1000
    if period>=ref_period:
        print("...period", period)
        return False

    return True

    
"""Generate a plot figure with the timestamp_server_data and timestamp_local_data from the datasets. The figure will have a subplot for each dataset. 
Each subplot will have a trace for each timestamp server and local as a histogram of each one.

Parameters
----------
dff : pd.DataFrame
    The datasets that you want to plot

    """
def plot_fun_t(tempo,timestap=False):
    t_server=np.array(tempo,dtype=int)
    label_t=['T Server','T local']
    color_t=['r','b']
    if timestap == False:
        timestamp_server_data = np.diff(t_server)
    else:
        timestamp_server_data = t_server
    col_=1
    row_= 2
    
    fig, axs = plt.subplots(ncols=col_, nrows=row_, figsize=(20, 6),
                        layout="constrained")
    row=0
    axs[row].plot( timestamp_server_data, color_t[row], linewidth=0.5)
    axs[row].title.set_text(label_t[row])
    axs[row].set_xlabel('time (ms) ->')
    axs[row].set_ylabel('Latency (ms)')
    axs[row].grid(True)
    row=1
    axs[row].hist(timestamp_server_data, bins=30,color='red')
    axs[row].set_xlabel('Latency (ms)')
    axs[row].set_ylabel('Count ')
    #plt.save
    plt.show()

def print_peak_time(sinal_xyz,tempo,th, title_,path_out,timestap=False):
    t_server=np.array(tempo,dtype=int)
    if timestap == False:
        timestamp_server_data = np.diff(t_server)
    else:
        timestamp_server_data = t_server
    time_=np.absolute(timestamp_server_data)
    id_peak, _ = find_peaks(time_, height=th)
    return id_peak