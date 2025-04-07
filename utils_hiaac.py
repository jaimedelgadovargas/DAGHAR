def plot_fun_acc(sinal_xyz,tempo,timstamp=False):
    if timstamp:        
      tempo = np.cumsum(tempo)
        
    acc=np.array(sinal_xyz,dtype=float)
    #time_=pd.to_datetime(tempo[1:-1], unit='ms').tz_localize('UTC').tz_convert('Etc/GMT+3')
    #time_v=pd.DataFrame({'date':time_})
    #time_v['date']=pd.to_datetime(time_v['date'])
    #time_v['time']=time_v['date'].dt.strftime('%H:%M:%S')
    #time=time_v['time'].to_numpy()
    time = tempo
    if len(acc[:,0]) != len(time):
        print(f"Error len(acc):{acc[:,0].shape} != len(time):{len(time)}")
        return
    label_acc=[' acc X',' acc Y','acc Z']
    color_acc=['r','b','g']
    Accelerometer_X_axis_data = acc[:,0] #x
    Accelerometer_Y_axis_data = acc[:,1] #y
    Accelerometer_Z_axis_data = acc[:,2] #z
    col_=1
    row_=3  
    
    fig, axs = plt.subplots(ncols=col_, nrows=row_, figsize=(20, 10),layout="constrained")
    
    for row in range(row_):
        for col in range(col_):
            axs[row].plot( time, acc[:,row], color_acc[row], linewidth=0.8)
            axs[row].title.set_text(label_acc[row])
            axs[row].set_xlabel('datatime->')
            axs[row].set_ylabel('Acceleration (m/s^2)')
            axs[row].grid(True)
            #axs[row].xaxis.set_major_locator(ticker.MultipleLocator(40)) 
            #axs[row].tick_params(axis='x', rotation=90)    
    plt.show()
def daghar_path(dataset_path, j, i):
    # List of datasets and labels
    dataset = ["KuHar", "RealWorld_thigh", "RealWorld_waist", "WISDM", "MotionSense", "UCI","HIAAC"]
    labels = ['sit', 'stand', 'walk', 'upstairs', 'downstairs', 'run']
    split_v = ["train", "validation", "test"]
    file_name = f"/{split_v[j]}.csv"
    path = dataset_path + dataset[i] + file_name
    print(path)
    return path

def read_csv_data(df):       
        accel_x = df.filter(regex='^accel-x').values
        accel_y = df.filter(regex='^accel-y').values
        accel_z = df.filter(regex='^accel-z').values
        gyro_x = df.filter(regex='^gyro-x').values
        gyro_y = df.filter(regex='^gyro-y').values
        gyro_z = df.filter(regex='^gyro-z').values
        standard_activity_code = df['standard activity code'].values
        return accel_x, accel_y, accel_z, gyro_x, gyro_y, gyro_z, standard_activity_code
def merge_info(accel_x, accel_y, accel_z, gyro_x, gyro_y, gyro_z, standard_activity_code,f=100):
    y_data = standard_activity_code
    x_data = np.stack((accel_x, accel_y, accel_z, gyro_x, gyro_y, gyro_z), axis=-1)
    x_data = x_data.reshape(x_data.shape[0], x_data.shape[2], x_data.shape[1])
    [w,ch,d]=x_data.shape
    d=[]
    l=[]
    for i in range(w):
        l.append(np.ones(f*3)*y_data[i])    
        d.append(x_data[i,:,:])
    x = np.concatenate(d, axis=1)
    y = np.concatenate(l, axis=0)
    print(x.shape,y.shape)
    return x,y   