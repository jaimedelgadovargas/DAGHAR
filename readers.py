from typing import List, Dict
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import interpolate
from natsort import natsorted
from zipfile import ZipFile
import os


# Set the seed for reproducibility
np.random.seed(42)
# pd.np.random.seed(42)


def read_kuhar(kuhar_dir_path: str) -> pd.DataFrame:
    """Read the Kuhar dataset and return a DataFrame with the data (coming from all CSV files)
    The returned dataframe has the following columns:
    - accel-x: Acceleration on the x axis
    - accel-y: Acceleration on the y axis
    - accel-z: Acceleration on the z axis
    - gyro-x: Angular velocity on the x axis
    - gyro-y: Angular velocity on the y axis
    - gyro-z: Angular velocity on the z axis
    - accel-start-time: Start time of the acceleration window
    - gyro-start-time: Start time of the gyroscope window
    - activity code: Activity code
    - index: Index of the sample coming from the csv
    - user: User code
    - serial: Serial number of the activity
    - csv: Name of the CSV file

    Parameters
    ----------
    kuhar_dir_path : str
        Path to the Kuhar dataset

    Returns
    -------
    pd.DataFrame
        DataFrame with the data from the Kuhar dataset
    """
    kuhar_dir_path = Path(kuhar_dir_path)

    # Create a dictionary with the data types of each column
    feature_dtypes = {
        "accel-start-time": np.float32,
        "accel-x": np.float32,
        "accel-y": np.float32,
        "accel-z": np.float32,
        "gyro-start-time": np.float32,
        "gyro-x": np.float32,
        "gyro-y": np.float32,
        "gyro-z": np.float32,
    }

    dfs = []
    for i, f in enumerate(sorted(kuhar_dir_path.rglob("*.csv"))):
        # Get the name of the activity (folder name, e.g. 5.Lay)
        # Get the name of the CSV file (ex.: 1052_F_1.csv)
        # Split the activity number and the name (ex.: [5, 'Lay'])
        activity_no, activity_name = f.parents[0].name.split(".")
        activity_no = int(activity_no)

        # Split the user code, the activity type and the serial number (ex.: [1055, 'G', 1])
        csv_splitted = f.stem.split("_")
        user = int(csv_splitted[0])
        serial = "_".join(csv_splitted[2:])

        # Read the CSV file
        df = pd.read_csv(
            f, names=list(feature_dtypes.keys()), dtype=feature_dtypes
        )

        # Remove dataframes that contain NaN
        if df.isnull().values.any():
            continue

        # Only reordering the columns (no column is removed)
        df = df[
            [
                "accel-x",
                "accel-y",
                "accel-z",
                "gyro-x",
                "gyro-y",
                "gyro-z",
                "accel-start-time",
                "gyro-start-time",
            ]
        ]

        # ----- Add auxiliary columns and metadata ------
        # Since it is a simple instant of time (without duration), the start and end time are the same
        df["accel-end-time"] = df["accel-start-time"]
        df["gyro-end-time"] = df["gyro-start-time"]
        # Add the activity code column
        df["activity code"] = activity_no
        # Add the index column (index of the sample in the CSV file)
        df["index"] = range(len(df))
        # Add the user column
        df["user"] = user
        # Add the serial column (the serial number of the activity)
        df["serial"] = serial
        # Add the csv column (the name of the CSV file)
        df["csv"] = "/".join(f.parts[-2:])
        # ----------------------------------------------------
        dfs.append(df)
    return pd.concat(dfs)


def read_motionsense(motionsense_path: str) -> pd.DataFrame:
    """Read the MotionSense dataset and return a DataFrame with the data (coming from all CSV files)
    The returned dataframe has the following columns:
    - attitude.roll: Rotation around the x axis
    - attitude.pitch: Rotation around the y axis
    - attitude.yaw: Rotation around the z axis
    - gravity.x: Gravity around the x axis
    - gravity.y: Gravity around the y axis
    - gravity.z: Gravity around the z axis
    - rotationRate.x: Angular velocity around the x axis
    - rotationRate.y: Angular velocity around the y axis
    - rotationRate.z: Angular velocity around the z axis
    - userAcceleration.x: Acceleration on the x axis
    - userAcceleration.y: Acceleration on the y axis
    - userAcceleration.z: Acceleration on the z axis
    - activity code: Activity code
    - index: Index of the sample coming from the csv
    - user: User code
    - serial: Serial number of the activity
    - csv: Name of the CSV file

    Parameters
    ----------
    motionsense_path : str
        Path to the MotionSense dataset

    Returns
    -------
    pd.DataFrame
        DataFrame with the data from the MotionSense dataset
    """
    motionsense_path = Path(motionsense_path)
    activity_names = {
        0: "dws",
        1: "ups",
        2: "sit",
        3: "std",
        4: "wlk",
        5: "jog",
    }
    activity_codes = {v: k for k, v in activity_names.items()}

    feature_dtypes = {
        "attitude.roll": np.float32,
        "attitude.pitch": np.float32,
        "attitude.yaw": np.float32,
        "gravity.x": np.float32,
        "gravity.y": np.float32,
        "gravity.z": np.float32,
        "rotationRate.x": np.float32,
        "rotationRate.y": np.float32,
        "rotationRate.z": np.float32,
        "userAcceleration.x": np.float32,
        "userAcceleration.y": np.float32,
        "userAcceleration.z": np.float32,
    }

    dfs = []
    for i, f in enumerate(sorted(motionsense_path.rglob("*.csv"))):
        # Get the name of the activity (folder name, e.g. 5.Lay)
        activity_name = f.parents[0].name
        # Partition the name of the activity into the activity code and the serial number
        activity_name, serial = activity_name.split("_")
        activity_code = activity_codes[activity_name]

        user = int(f.stem.split("_")[1])
        df = pd.read_csv(
            f,
            names=list(feature_dtypes.keys()),
            dtype=feature_dtypes,
            skiprows=1,
        )
        # Remove dataframes that contain NaN
        if df.isnull().values.any():
            continue

        # ----- Add auxiliary columns and metadata ------
        df["activity code"] = activity_code
        df["index"] = range(len(df))
        df["user"] = user
        df["serial"] = serial
        df["csv"] = "/".join(f.parts[-2:])
        # ----------------------------------------------------
        dfs.append(df)

    # return pd.concat(dfs[:10])
    return pd.concat(dfs)


def read_uci(uci_path: str) -> pd.DataFrame:
    """Read the UCI-HAR dataset and return a DataFrame with the data (coming from all txt files)
    The returned dataframe has the following columns:
    - accel-x: Acceleration on the x axis
    - accel-y: Acceleration on the y axis
    - accel-z: Acceleration on the z axis
    - gyro-x: Angular velocity on the x axis
    - gyro-y: Angular velocity on the y axis
    - gyro-z: Angular velocity on the z axis
    - txt: Name of the TXT file
    - user: User code
    - serial: Serial number of the activity
    - activity code: Activity code
    - index: Index of the sample coming from the csv

    Parameters
    ----------
    uci_path : str
        Path to the UCI-HAR dataset

    Returns
    -------
    pd.DataFrame
        DataFrame with the data from the UCI-HAR dataset
    """
    activity_names = {
        1: "WALKING",
        2: "WALKING_UPSTAIRS",
        3: "WALKING_DOWNSTAIRS",
        4: "SITTING",
        5: "STANDING",
        6: "LAYING",
        7: "STAND_TO_SIT",
        8: "SIT_TO_STAND",
        9: "SIT_TO_LIE",
        10: "LIE_TO_SIT",
        11: "STAND_TO_LIE",
        12: "LIE_TO_STAND",
    }

    feature_columns = [
        "accel-x",
        "accel-y",
        "accel-z",
        "gyro-x",
        "gyro-y",
        "gyro-z",
    ]

    df_labels = pd.read_csv(uci_path / "labels.txt", header=None, sep=" ")
    df_labels.columns = ["serial", "user", "activity code", "start", "end"]

    uci_path = Path(uci_path)

    dfs = []
    data_path = list(uci_path.glob("*.txt"))
    new_data_path = [
        elem.name.split("_") + [elem] for elem in sorted(data_path)
    ]
    df = pd.DataFrame(
        new_data_path, columns=["sensor", "serial", "user", "file"]
    )
    for key, df2 in df.groupby(["serial", "user"]):
        acc, gyr = None, None
        for row_index, row in df2.iterrows():
            data = pd.read_csv(row["file"], header=None, sep=" ")
            if row["sensor"] == "acc":
                acc = data
            else:
                gyr = data
        new_df = pd.concat([acc, gyr], axis=1)
        new_df.columns = feature_columns

        user = int(key[1].split(".")[0][4:])
        serial = int(key[0][3:])

        new_df["txt"] = row["file"]

        new_df["user"] = user
        new_df["serial"] = serial

        for row_index, row in df_labels.loc[
            (df_labels["serial"] == serial) & (df_labels["user"] == user)
        ].iterrows():
            start = row["start"]
            end = row["end"] + 1
            activity = row["activity code"]
            resumed_df = new_df.loc[start:end].copy()
            resumed_df["index"] = [i for i in range(start, end + 1)]
            resumed_df["activity code"] = activity

            # Remove dataframes that contain NaN
            if resumed_df.isnull().values.any():
                continue

            dfs.append(resumed_df)

    df = pd.concat(dfs)
    df.reset_index(inplace=True, drop=True)
    return df


def read_wisdm(wisdm_path: str, interpol=True) -> pd.DataFrame:
    """Read the WISDM dataset and return a DataFrame with the data (coming from all txt files)
    The returned dataframe has the following columns:
    - accel-x: Acceleration on the x axis
    - accel-y: Acceleration on the y axis
    - accel-z: Acceleration on the z axis
    - gyro-x: Angular velocity on the x axis
    - gyro-y: Angular velocity on the y axis
    - gyro-z: Angular velocity on the z axis
    - user: User code
    - activity code: Activity code
    - window: Window number
    - timestamp-accel: Timestamp of the acceleration window
    - timestamp-gyro: Timestamp of the gyroscope window

    Parameters
    ----------
    wisdm_path : str
        Path to the WISDM dataset
        interpol : bool, optional
            If True, the data will be interpolated, by default True

    Returns
    -------
    pd.DataFrame
        DataFrame with the data from the WISDM dataset
    """
    feature_columns_acc = [
        "user",
        "activity code",
        "timestamp-accel",
        "accel-x",
        "accel-y",
        "accel-z",
    ]
    feature_columns_gyr = [
        "user",
        "activity code",
        "timestamp-gyro",
        "gyro-x",
        "gyro-y",
        "gyro-z",
    ]

    # List of capital letters from A to S without N
    labels: List[str] = [chr(i) for i in range(65, 84) if chr(i) != "N"]

    dfs = []
    window = 1
    for user in range(1600, 1651):
        window = 1
        # Read the accelerometer data
        df_acc = pd.read_csv(
            wisdm_path / f"accel/data_{user}_accel_phone.txt",
            sep=",|;",
            header=None,
            engine="python",
        )
        df_acc = df_acc[df_acc.columns[0:-1]]
        df_acc.columns = feature_columns_acc
        df_acc["timestamp-accel"] = df_acc["timestamp-accel"].astype(np.int64)

        # Read the gyroscope data
        df_gyr = pd.read_csv(
            wisdm_path / f"gyro/data_{user}_gyro_phone.txt",
            sep=",|;",
            header=None,
            engine="python",
        )
        df_gyr = df_gyr[df_gyr.columns[0:-1]]
        df_gyr.columns = feature_columns_gyr
        df_gyr["timestamp-gyro"] = df_gyr["timestamp-gyro"].astype(np.int64)

        for activity in labels:
            # Get the data from the current activity
            acc = df_acc[df_acc["activity code"] == activity].copy()
            gyr = df_gyr[df_gyr["activity code"] == activity].copy()

            time_acc = np.array(acc["timestamp-accel"])
            time_gyr = np.array(gyr["timestamp-gyro"])

            # Flag to check if the data will be interpolated
            if interpol:
                # Set the initial time to 0
                if len(time_acc) > 0 and len(time_gyr) > 0:
                    time_acc = (time_acc - time_acc[0]) / 1000000000
                    time_gyr = (time_gyr - time_gyr[0]) / 1000000000

                    # Removing the intervals without samples (empty periods)
                    if np.any(np.diff(time_acc) < 0):
                        pos = np.nonzero(np.diff(time_acc) < 0)[0].astype(int)
                        for k in pos:
                            time_acc[k + 1 :] = (
                                time_acc[k + 1 :] + time_acc[k] + 1 / 20
                            )
                    if np.any(np.diff(time_gyr) < 0):
                        pos = np.nonzero(np.diff(time_gyr) < 0)[0].astype(int)
                        for k in pos:
                            time_gyr[k + 1 :] = (
                                time_gyr[k + 1 :] + time_gyr[k] + 1 / 20
                            )

                    # Interpolating the data to fix the sampling rate to 20 Hz
                    sigs_acc = []
                    sigs_gyr = []
                    for sig_acc, sig_gyr in zip(
                        acc[feature_columns_acc[2:]],
                        gyr[feature_columns_gyr[2:]],
                    ):
                        fA = np.array(acc[sig_acc])
                        fG = np.array(gyr[sig_gyr])

                        intp1 = interpolate.interp1d(time_acc, fA, kind="cubic")
                        intp2 = interpolate.interp1d(time_gyr, fG, kind="cubic")
                        nt1 = np.arange(0, time_acc[-1], 1 / 20)
                        nt2 = np.arange(0, time_gyr[-1], 1 / 20)
                        sigs_acc.append(intp1(nt1))
                        sigs_gyr.append(intp2(nt2))

                    # Getting the minimum length of the signals (accelerometer and gyroscope)
                    tam = min(len(nt1), len(nt2))

                    new_acc = pd.DataFrame()
                    new_gyr = pd.DataFrame()

                    # Truncating the signals
                    for x, y in zip(sigs_acc, sigs_gyr):
                        x = x[:tam]
                        y = y[:tam]

                    # Truncating the timestamps
                    new_acc["timestamp-accel"] = nt1[:tam]
                    new_gyr["timestamp-gyro"] = nt2[:tam]

                    # Adding the other columns
                    for sig_acc, sig_gyr, column_acc, column_gyr in zip(
                        sigs_acc,
                        sigs_gyr,
                        feature_columns_acc[2:],
                        feature_columns_gyr[2:],
                    ):
                        new_acc[column_acc] = sig_acc[:tam]
                        new_gyr[column_gyr] = sig_gyr[:tam]
            else:
                tam = min(len(time_acc), len(time_gyr))
                new_acc = acc[feature_columns_acc[2:]].iloc[:tam]
                new_gyr = gyr[feature_columns_gyr[2:]].iloc[:tam]

            # Concatenating the accelerometer and gyroscope dataframes
            df = pd.concat([new_acc, new_gyr], axis=1)
            # Adding the other columns
            df["activity code"] = activity
            df["user"] = user
            df["window"] = window

            # Drop samples with NaN
            df = df.dropna()

            dfs.append(df)
    # Concatenating the dataframes
    df = pd.concat(dfs)
    df.reset_index(inplace=True, drop=True)

    # Converting the data types
    for column in feature_columns_acc[2:] + feature_columns_gyr[2:]:
        df[column] = df[column].astype(np.float32)
    df["user"] = df["user"].astype(np.int32)

    return df.dropna().reset_index(drop=True)


def read_realworld(workspace: str, users: List[str]) -> pd.DataFrame:
    """Read the RealWorld dataset and return a DataFrame with the data (coming from all files)
    The returned dataframe has the following columns:
    - accel-x: Acceleration on the x axis
    - accel-y: Acceleration on the y axis
    - accel-z: Acceleration on the z axis
    - gyro-x: Angular velocity on the x axis
    - gyro-y: Angular velocity on the y axis
    - gyro-z: Angular velocity on the z axis
    - user: User code
    - position: Position of the sensor
    - activity code: Activity code
    - index: Index of the sample coming from the csv

    Parameters
    ----------
    workspace : str
        Path to the RealWorld dataset
    users : List[str]
        List of users that you want to read

    Returns
    -------
    pd.DataFrame
        DataFrame with the data from the RealWorld dataset
    """

    # List of activities
    activities: List[str] = [
        "climbingdown",
        "climbingup",
        "jumping",
        "lying",
        "running",
        "sitting",
        "standing",
        "walking",
    ]

    # List to filter the positions
    position: List[str] = ["thigh", "upperarm", "waist"]

    # List of features
    feature_acc: List[str] = [
        "index",
        "accel-start-time",
        "accel-x",
        "accel-y",
        "accel-z",
    ]
    feature_gyr: List[str] = [
        "index",
        "gyro-start-time",
        "gyro-x",
        "gyro-y",
        "gyro-z",
    ]

    # List to store the dataframes
    dfs: List[pd.DataFrame] = []

    for p in position:
        for user in users:
            # List of files from the accelerometer and gyroscope sensors of the current user
            filesacc = sorted(
                os.listdir(
                    workspace / "realworld2016_dataset_organized" / user / "acc"
                )
            )
            filesgyr = sorted(
                os.listdir(
                    workspace / "realworld2016_dataset_organized" / user / "gyr"
                )
            )

            pos = []
            # Get the indexes of the files that contain the current position
            for i in range(len(filesacc)):
                if filesacc[i].find(p) > -1:
                    pos.append(i)

            for i in pos:
                # Read the accelerometer and gyroscope data
                acc = pd.read_csv(
                    workspace
                    / "realworld2016_dataset_organized"
                    / user
                    / "acc"
                    / filesacc[i]
                )
                acc.columns = feature_acc
                gyr = pd.read_csv(
                    workspace
                    / "realworld2016_dataset_organized"
                    / user
                    / "gyr"
                    / filesgyr[i]
                )
                gyr.columns = feature_gyr

                for activity in activities:
                    if filesacc[i].find(activity) > -1:
                        break

                # Work around to remove the samples that are less problematic (the samples that have a difference of 200 samples or more)
                if not abs(acc.shape[0] - gyr.shape[0]) < 200:
                    # Remove all rows from the dataframes
                    acc.drop(acc.index, inplace=True)
                    gyr.drop(gyr.index, inplace=True)

                tam = min(acc.shape[0], gyr.shape[0])

                new_acc = acc[feature_acc].iloc[:tam]
                new_gyr = gyr[feature_gyr[1:]].iloc[:tam]

                # Concatenating the accelerometer and gyroscope dataframes
                df = pd.concat([new_acc, new_gyr], axis=1)
                # Adding the other columns
                df["user"] = user
                df["position"] = p
                df["activity code"] = activity

                # Drop samples with NaN
                if df.isnull().values.any():
                    continue

                dfs.append(df)

    # Concatenating the dataframes
    df = pd.concat(dfs, ignore_index=True)
    df.reset_index(inplace=True, drop=True)
    return df


def getfiles(user, activity, workspace, root):
    """This function will get the files from the real world dataset and move them to the realworld2016_dataset_organized folder

    Parameters
    ----------
    user : str
        User code
    activity : str
        Activity code
    workspace : str
        Path to the RealWorld dataset organized
    root : str
        Path to the raw RealWorld dataset

    Returns
    -------
    None
    """

    folder = workspace / "realworld2016_dataset_organized"

    for sensor in ["acc", "gyr"]:
        file = root / user / f"data/{sensor}_{activity}_csv.zip"
        with ZipFile(file, "r") as zip:
            zip.extractall(workspace / "junk")

        for i in os.listdir(workspace / "junk"):
            if i.find("zip") > -1:
                file = workspace / "junk" / i
                with ZipFile(file, "r") as zip:
                    zip.extractall(workspace / "junk")

        for files in os.listdir(workspace / "junk"):
            if os.path.isfile(workspace / "junk" / files):
                if files.find(activity) > -1 and files.find("zip") < 0:
                    os.rename(workspace / "junk" / files, folder / user / files)
                else:
                    os.remove(workspace / "junk" / files)

        os.rmdir(workspace / "junk")


def real_world_organize():
    """This function will organize the real world dataset in a friendly way, creating folders for each user and separating the accelerometer and gyroscope data
    in another folder. It is a good idea to run this function before reading the dataset because it will make the reading process easier.

    Returns
    -------
    workspace : str
        Path to the RealWorld dataset organized
    users : List[str]
        List of users that you want to read
    """
    # Path to organize the dataset and the root of the dataset
    workspace = Path("data/processed/RealWorld")
    root = Path("data/original/RealWorld/realworld2016_dataset")

    # List of users and activities
    users = natsorted(os.listdir(root))
    activities: List[str] = [
        "climbingdown",
        "climbingup",
        "jumping",
        "lying",
        "running",
        "sitting",
        "standing",
        "walking",
    ]
    SAC: List[str] = [
        "sitting",
        "standing",
        "walking",
        "climbingup",
        "climbingdown",
        "running",
    ]

    # Create a folder to unzip the files .zip if it doesn't exist
    if not os.path.isdir(workspace / "junk"):
        os.makedirs(workspace / "junk")
    os.path.isdir(workspace / "junk")
    # and the same folder to organize the unzipped files in a friendly way
    if not os.path.isdir(workspace / "realworld2016_dataset_organized"):
        os.mkdir(workspace / "realworld2016_dataset_organized")
    os.path.isdir(workspace / "realworld2016_dataset_organized")

    # Create a folder for each user
    for i in users:
        if not os.path.isdir(workspace / "realworld2016_dataset_organized" / i):
            os.mkdir(workspace / "realworld2016_dataset_organized" / i)

    # Get the files from the dataset and move them to the right folder
    for user in users:
        for activity in activities:
            getfiles(user, activity, workspace, root)
    # Create a folder for the accelerometer and gyroscope data for each user
    for user in users:
        if not os.path.isdir(
            workspace / "realworld2016_dataset_organized" / user / "acc"
        ):
            os.mkdir(
                workspace / "realworld2016_dataset_organized" / user / "acc"
            )
        if not os.path.isdir(
            workspace / "realworld2016_dataset_organized" / user / "gyr"
        ):
            os.mkdir(
                workspace / "realworld2016_dataset_organized" / user / "gyr"
            )
    # Move the accelerometer and gyroscope data to the right folder
    for user in users:
        for files in os.listdir(
            workspace / "realworld2016_dataset_organized" / user
        ):
            if files.find("acc") > -1 and os.path.isfile(
                workspace / "realworld2016_dataset_organized" / user / files
            ):
                origin = (
                    workspace / "realworld2016_dataset_organized" / user / files
                )
                destiny = (
                    workspace
                    / "realworld2016_dataset_organized"
                    / user
                    / "acc"
                    / files
                )
                os.rename(origin, destiny)
            if files.find("Gyr") > -1 and os.path.isfile(
                workspace / "realworld2016_dataset_organized" / user / files
            ):
                origin = (
                    workspace / "realworld2016_dataset_organized" / user / files
                )
                destiny = (
                    workspace
                    / "realworld2016_dataset_organized"
                    / user
                    / "gyr"
                    / files
                )
                os.rename(origin, destiny)
    # Verify if all users have the same number of accelerometer and gyroscope files
    flag = 1
    for user in users:
        files_acc = os.listdir(
            workspace / "realworld2016_dataset_organized" / user / "acc"
        )
        files_gyr = os.listdir(
            workspace / "realworld2016_dataset_organized" / user / "gyr"
        )
        if len(files_acc) != len(files_gyr):
            flag = 0
            print(
                f"User {user} has {len(files_acc)} acc files and {len(files_gyr)} gyr files"
            )
            flag = -1
    if flag == 1:
        print("All users have the same number of acc and gyr files")

    return workspace, users


def sanity_function(train_df, val_df, test_df):
    """This function will print some information about the datasets, such as the size of each dataset, the number of samples per user and activity, etc.
    And it will also check if all users have the same number of samples per activity in each dataset.

    Parameters
    ----------
    train_df : pd.DataFrame
        Train dataset
    val_df : pd.DataFrame
        Validation dataset
    test_df : pd.DataFrame
        Test dataset

    Returns
    -------
    None
    """

    train_size: int = train_df.shape[0]
    val_size: int = val_df.shape[0]
    test_size: int = test_df.shape[0]
    total: int = train_size + val_size + test_size

    # Print some information about the datasets
    print(f"Train size: {train_size} ({train_size/total*100:.2f}%)")
    print(f"Validation size: {val_size} ({val_size/total*100:.2f}%)")
    print(f"Test size: {test_size} ({test_size/total*100:.2f}%)")

    print(f"Train activities: {train_df['standard activity code'].unique()}")
    print(f"Validation activities: {val_df['standard activity code'].unique()}")
    print(f"Test activities: {test_df['standard activity code'].unique()}")

    dataframes: Dict[str, pd.DataFrame] = {
        "Train": train_df,
        "Validation": val_df,
        "Test": test_df,
    }
    # Check if all users have the same number of samples per activity in each dataset
    for name, df in dataframes.items():
        users = df["user"].unique()
        activities = df["standard activity code"].unique()

        tam = len(
            df[
                (df["user"] == users[0])
                & (df["standard activity code"] == activities[0])
            ]
        )
        flag = True
        for user in users:
            for activity in activities:
                if (
                    len(
                        df[
                            (df["user"] == user)
                            & (df["standard activity code"] == activity)
                        ]
                    )
                    != tam
                ):
                    # print(
                    #     f"User {user} has different size for activity {activity}"
                    # )
                    flag = False
        if flag:
            # print(
            #     f"All users have the same size per activity in {name} dataset - Samples per user and activity: {tam}"
            # )
            pass

    users = train_df["user"].unique()
    activities = train_df["standard activity code"].unique()
    # Print the number of samples per user and activity in each set (train, validation and test)
    print(f"Users in train: {train_df['user'].unique()}")
    print(f"Users in validation: {val_df['user'].unique()}")
    print(f"Users in test: {test_df['user'].unique()}\n")


def read_hiacc_smartphone_V1(hiacc_path: str) -> pd.DataFrame:
    """
    Parâmetros
    ----------
    hiacc_path : str
        Caminho para a pasta raiz "HIAAC".
        
    Retorna
    -------
    pd.DataFrame
        DataFrame contendo as colunas:
          - accel-x, accel-y, accel-z
          - gyro-x, gyro-y, gyro-z
          - timestamp-server-accel, timestamp-server-gyro (ajustados para iniciar em 0)
          - activity code, user, window, pos
    """
    hiacc_path = Path(hiacc_path)
    
    # Pastas de posição
    positions: List[str] = ["Bolso_direito", "Mochila"]
    
    # Colunas esperadas nos arquivos CSV
    feature_columns_acc = ["Timestamp Server", "Value 1", "Value 2", "Value 3"]
    feature_columns_gyr = ["Timestamp Server", "Value 1", "Value 2", "Value 3"]
    
    dfs = []
    print("Iniciando leitura do dataset HIACC...")
    
    for pos in positions:
        pos_path = hiacc_path / pos
        if not pos_path.exists():
            print(f"A pasta {pos_path} não existe. Pulando...")
            continue
        
        for user_folder in sorted(pos_path.iterdir()):
            if not user_folder.is_dir():
                print(f"{user_folder} não é uma pasta. Pulando...")
                continue
            try:
                user = int(user_folder.name)
            except ValueError:
                print(f"Nome da pasta {user_folder} não é um número. Pulando...")
                continue            
            # Define os arquivos conforme a posição
            if pos == "Bolso_direito":
                acc_file = user_folder / "Accelerometer_Bolso Direito.csv"
                gyr_file = user_folder / "Gyroscope_Bolso Direito.csv"
            elif pos == "Mochila":
                acc_file = user_folder / "Accelerometer_Mochila.csv"
                gyr_file = user_folder / "Gyroscope_Mochila.csv"
            else:
                print(f"Posição {pos} não reconhecida. Pulando...")
                continue
            if not acc_file.exists() or not gyr_file.exists():
                print(f"Arquivos {acc_file} ou {gyr_file} não existem. Pulando...")
                continue
            
            try:
                df_acc = pd.read_csv(acc_file, engine="python")
                df_acc["timestamp-server-accel"] = df_acc["Timestamp Server"].astype(np.int64)
                df_acc = df_acc[["timestamp-server-accel", "Value 1", "Value 2", "Value 3"]].copy()
                df_acc.columns = ["timestamp-server-accel", "accel-x", "accel-y", "accel-z"]
                df_acc["user"] = user
                df_acc["position"] = pos
            except Exception:
                print(f"Erro ao ler o arquivo {acc_file}. Pulando...")
                continue
            
            try:
                df_gyr = pd.read_csv(gyr_file, engine="python")
                df_gyr["timestamp-server-gyro"] = df_gyr["Timestamp Server"].astype(np.int64)
                df_gyr = df_gyr[["timestamp-server-gyro", "Value 1", "Value 2", "Value 3"]].copy()
                df_gyr.columns = ["timestamp-server-gyro", "gyro-x", "gyro-y", "gyro-z"]
            except Exception:
                print(f"Erro ao ler o arquivo {gyr_file}. Pulando...")
                continue
            
            # Ajusta para que o giroscópio tenha o mesmo número de amostras que o acelerômetro
            len_min = min(len(df_acc), len(df_gyr))
            df_acc = df_acc.iloc[:len_min].reset_index(drop=True)
            df_gyr = df_gyr.iloc[:len_min].reset_index(drop=True)
            
            # Ajusta os timestamps para iniciar em 0 (milissegundos)
            df_acc["timestamp-server-accel"] -= df_acc["timestamp-server-accel"].iloc[0]
            df_gyr["timestamp-server-gyro"] -= df_gyr["timestamp-server-gyro"].iloc[0]
            
            # Leitura do arquivo de labels
            label_file = user_folder / f"{user_folder.name}_label_vitor.csv"
            if not label_file.exists():
                print(f"Arquivo de labels {label_file} não existe. Pulando...")
                continue
            try:
                df_label = pd.read_csv(label_file)
                if "L" not in df_label.columns:
                    print(f"Coluna 'L' não encontrada no arquivo {label_file}. Pulando...")
                    continue
                df_label["L"] = df_label["L"].astype(str).str.strip()
                df_label["activity code"] = df_label["L"]
            except Exception:
                print(f"Erro ao ler o arquivo {label_file}. Pulando...")
                continue
            
            # Define número de janelas (cada janela = 300 amostras)
            num_windows = min(len(df_acc) // 300, len(df_label))
            df_acc = df_acc.iloc[:num_windows * 300].reset_index(drop=True)
            df_gyr = df_gyr.iloc[:num_windows * 300].reset_index(drop=True)
            df_label = df_label.iloc[:num_windows].reset_index(drop=True)
            # Cria a coluna 'trial' para identificar cada janela
            df_acc["trial"] = df_acc.index // 300            
                     
            
            try:
                # Merge dos labels com o acelerômetro (inner on "trial")
                df_acc = df_acc.merge(
                df_label[["activity code"]].reset_index().rename(columns={"index": "trial"}),
                on= "trial",
                how="inner"
                ).reset_index(drop=True)

                # Combina os dados dos sensores
                data_df = pd.concat([df_acc, df_gyr], axis=1)
                data_df_final = data_df[["timestamp-server-accel", "timestamp-server-gyro",
                                         "accel-x", "accel-y", "accel-z",
                                         "gyro-x", "gyro-y", "gyro-z", "position", "activity code", "trial", "user"]].copy()
                data_df_final = data_df_final.astype({'activity code':'int'})


            except Exception:
                print(f"Erro ao combinar os dados dos sensores para o usuário {user} e atividade. Pulando...")
                continue
            dfs.append(data_df_final)
    
    if dfs:
        df_final = pd.concat(dfs, ignore_index=True)
    else:
        df_final = pd.DataFrame()
    
    print("Processamento concluído.")
    return df_final

def read_hiacc_smartphone(hiaac_path: str) -> pd.DataFrame:
    """
    Read the HIAAC dataset (all sensor variants + shared labels) and return a single DataFrame.

    The returned DataFrame has columns:
        - timestamp-server-accel, timestamp-server-gyro
        - accel-x, accel-y, accel-z
        - gyro-x, gyro-y, gyro-z
        - position      # e.g. 'RightPocket', 'CrossBag', etc.
        - activity code
        - trial
        - user

    Parameters
    ----------
    hiaac_path : str
        Root path to the HIAAC dataset. Expects subfolders:
            {user_id}/accelerometer_*.csv
                      /gyroscope_*.csv
        plus a sibling `Label/{user_id}/Annotations.csv` for each user.

    Returns
    -------
    pd.DataFrame
        Concatenated data from all users and all sensor variants.
    """
    root = Path(hiaac_path)
    all_dfs: List[pd.DataFrame] = []
    print("Starting to read the HIAAC dataset...")

    # label mapping dictionary
    label_map = {
        "STANDING":               0,
        "SITTING":                1,
        "W_SPONT":                2,
        "WALKING_SPONTANEOUS":    2,
        "UPSTAIRS":               3,
        "DOWNSTAIRS":             4,
        "W_FAST":                 5,
        "RUN":                    6,
        "ELEV_UP":                7,
        "ELEVATOR_UP":            7,
        "ELEV_DOWN":              8,
        "ELEVATOR_DOWN":          8,
        "W_IN_DOOR":              9,
        "w_DISTRACTED":          10,
        "-1":                -1,
    }

    # Iterate over each user folder
    for user_folder in sorted(root.iterdir()):
        if not user_folder.is_dir():
            continue
        try:
            user = int(user_folder.name)
        except ValueError:
            continue

        # --- load and map this user's labels once ---
        label_path = root / "Label" / user_folder.name / "Annotations.csv"
        if not label_path.exists():
            print(f"Labels file not found for user {user}: {label_path}")
            continue
        try:
            df_label = pd.read_csv(label_path)
            if "pro_label" not in df_label.columns:
                print(f"Column 'pro_label' missing in {label_path.name}.")
                continue

            df_label["pro_label"] = df_label["pro_label"].astype(str).str.strip()
            df_label["activity code"] = df_label["pro_label"].map(label_map)
            
            df_label["activity code"] = df_label["activity code"].astype(int)


        except Exception as e:
            print(f"Error reading labels for user {user}: {e}")
            continue

        # --- find all accelerometer files for this user ---
        acc_files = sorted(user_folder.glob("accelerometer_*.csv"))
        if not acc_files:
            print(f"No accelerometer files in {user_folder}.")
            continue

        for acc_file in acc_files:
            variant = acc_file.stem.split("_", 1)[1]  # e.g. 'RightPocket'
            if variant == "Annotator" or variant == "LeftHand":
                continue
            gyr_file = user_folder / f"gyroscope_{variant}.csv"
            if not gyr_file.exists():
                print(f"Missing gyro file for {variant} of user {user}.")
                continue

            # read accelerometer
            try:
                df_acc = pd.read_csv(acc_file, engine="python")
                df_acc["timestamp-server-accel"] = df_acc["Timestamp Server"].astype(np.int64)
                df_acc = df_acc[
                    ["timestamp-server-accel", "Value 1", "Value 2", "Value 3"]
                ].copy()
                df_acc.columns = ["timestamp-server-accel", "accel-x", "accel-y", "accel-z"]
                df_acc["user"] = user
                df_acc["position"] = f"HIAAC_{variant}"
            except Exception as e:
                print(f"Error reading {acc_file.name}: {e}")
                continue

            # read gyroscope
            try:
                df_gyr = pd.read_csv(gyr_file, engine="python")
                df_gyr["timestamp-server-gyro"] = df_gyr["Timestamp Server"].astype(np.int64)
                df_gyr = df_gyr[
                    ["timestamp-server-gyro", "Value 1", "Value 2", "Value 3"]
                ].copy()
                df_gyr.columns = ["timestamp-server-gyro", "gyro-x", "gyro-y", "gyro-z"]
            except Exception as e:
                print(f"Error reading {gyr_file.name}: {e}")
                continue

            # align lengths and normalize timestamps
            min_len = min(len(df_acc), len(df_gyr))
            df_acc = df_acc.iloc[:min_len].reset_index(drop=True)
            df_gyr = df_gyr.iloc[:min_len].reset_index(drop=True)
            df_acc["timestamp-server-accel"] -= df_acc["timestamp-server-accel"].iloc[0]
            df_gyr["timestamp-server-gyro"] -= df_gyr["timestamp-server-gyro"].iloc[0]

            # windowing: 300 samples per trial
            num_windows = min(len(df_acc) // 300, len(df_label))
            df_acc = df_acc.iloc[: num_windows * 300].reset_index(drop=True)
            df_gyr = df_gyr.iloc[: num_windows * 300].reset_index(drop=True)
            df_label_slice = df_label.iloc[:num_windows * 300].reset_index(drop=True)

            df_acc["trial"] = df_acc.index // 300

            # merge and finalize
            try:
                
                combined = pd.concat([df_acc, df_gyr], axis=1)
                
                merged = pd.concat([combined, df_label_slice], axis=1)
                
                final = merged[[
                    "timestamp-server-accel", "timestamp-server-gyro",
                    "accel-x", "accel-y", "accel-z",
                    "gyro-x", "gyro-y", "gyro-z",
                    "position", "activity code", "trial", "user"
                ]].copy()
                final = final.astype({"activity code": "int"})
                all_dfs.append(final)
            except Exception as e:
                print(f"Error combining data for user {user}, variant {variant}: {e}")
                continue

    if all_dfs:
        df_all = pd.concat(all_dfs, ignore_index=True)
    else:
        df_all = pd.DataFrame()

    print("Processing completed.")
    return df_all
