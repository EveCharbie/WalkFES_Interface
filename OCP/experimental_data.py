import ezc3d
import biorbd
import numpy as np
import matplotlib.pyplot as plt



def moving_average(x, window_size):
    if window_size % 2 == 0:
        raise ValueError("window_size must be an odd number")
    x_averaged = np.zeros_like(x)
    for i in range(len(x)):
        if i < window_size // 2:
            x_averaged[i] = np.mean(x[:i + window_size // 2 + 1])
        elif i >= len(x) - window_size // 2:
            x_averaged[i] = np.mean(x[i - window_size // 2:])
        else:
            x_averaged[i] = np.mean(x[i - window_size // 2:i + window_size //
                                        2 + 1])
    return x_averaged


class ExperimentalData:
    def __init__(self, file_path: str, biorbd_model_path:str):
        self.file_path = file_path
        self.biorbd_model_path = biorbd_model_path
        self.initial_treatment()
        self.events = {"right_leg_heel_touch": [],  # heel strike
                "right_leg_toes_touch": [],  # beginning of flat foot
                "right_leg_heel_off": [],  # end of flat foot
                "right_leg_toes_off": [],  # beginning of swing
                "left_leg_heel_touch": [],  # heel strike
                "left_leg_toes_touch": [],  # beginning of flat foot
                "left_leg_heel_off": [],  # end of flat foot
                "left_leg_toes_off": []}  # beginning of swing
        self.phases_right_leg = {"flat_foot": np.zeros((self.nb_analog_frames, )),
                          "toes_only": np.zeros((self.nb_analog_frames, )),
                          "swing": np.zeros((self.nb_analog_frames, )),
                          "heel_only": np.zeros((self.nb_analog_frames, ))}
        self.phases_left_leg = {"flat_foot": np.zeros((self.nb_analog_frames, )),
                              "toes_only": np.zeros((self.nb_analog_frames, )),
                              "swing": np.zeros((self.nb_analog_frames, )),
                              "heel_only": np.zeros((self.nb_analog_frames, ))}


    def initial_treatment(self):

        # Load model
        model = biorbd.Model(self.biorbd_model_path)
        model_marker_names = [m.to_string() for m in model.markerNames()]
        model_muscle_names = [m.to_string() for m in model.muscleNames()]

        # Get an array of the position of the experimental self.markers
        c3d = ezc3d.c3d(self.file_path)
        markers = c3d["data"]["points"]
        markers_dt = 1 / c3d["header"]["points"]["frame_rate"]
        self.nb_marker_frames = markers.shape[2]
        exp_marker_names = c3d["parameters"]["POINT"]["LABELS"]["value"]
        markers_sorted = np.zeros((3, len(model_marker_names), self.nb_marker_frames))
        for i_marker, name in enumerate(model_marker_names):
            marker_idx = exp_marker_names.index(name)
            markers_sorted[:, marker_idx, :] = markers[:3, marker_idx, :]
        self.markers_sorted = markers_sorted
        self.right_leg_grf = np.vstack((markers[:3, exp_marker_names.index("moment2"), :],
                                   markers[:3, exp_marker_names.index("force2"), :]))
        self.left_leg_grf = np.vstack((markers[:3, exp_marker_names.index("moment1"), :],
                                  markers[:3, exp_marker_names.index("force1"), :]))

        # Get an array of the experimental muscle activity
        analogs = c3d["data"]["analogs"]
        self.nb_analog_frames = analogs.shape[2]
        analogs_dt = 1 / c3d["header"]["analogs"]["frame_rate"]
        analog_names = c3d["parameters"]["ANALOG"]["LABELS"]["value"]
        print(analog_names)
        emg_sorted = np.zeros((len(model_muscle_names), self.nb_analog_frames))
        for i_muscle, name in enumerate(model_muscle_names):
            muscle_idx = analog_names.index(name)
            emg_sorted[i_muscle, :] = analogs[muscle_idx, :]
        # TODO: Charbie -> treatment of the EMG signal to remove stimulation artifacts

        # Get the experimental ground reaction forces
        force_platform_1_channels = c3d["parameters"]["FORCE_PLATFORM"]["CHANNEL"]["value"][:, 0]
        force_platform_2_channels = c3d["parameters"]["FORCE_PLATFORM"]["CHANNEL"]["value"][:, 1]
        grf_sorted = np.zeros((2, 6, self.nb_analog_frames))
        for i in range(6):
            platform_1_idx = analog_names.index(f"Channel_{force_platform_1_channels[i]:02d}")
            platform_2_idx = analog_names.index(f"Channel_{force_platform_2_channels[i]:02d}")
            grf_sorted[0, i, :] = analogs[0, platform_1_idx, :]
            grf_sorted[1, i, :] = analogs[0, platform_2_idx, :]
        self.grf_sorted = grf_sorted

        # from scipy import signal
        # b, a = signal.butter(2, 1/50, btype='low')
        # y = signal.filtfilt(b, a, grf_sorted[0, 2, :], padlen=150)
        # # 4th 6-10

        # marker_time_vector = np.linspace(0, markers_dt*self.nb_marker_frames, self.nb_marker_frames)
        self.analogs_time_vector = np.linspace(0, analogs_dt * self.nb_analog_frames, self.nb_analog_frames)
        # plt.figure()
        # plt.plot(marker_time_vector, right_leg_grf[5, :], 'or')
        # plt.plot(analogs_time_vector, grf_sorted[0, 0, :], '-r')
        # plt.plot(analogs_time_vector, grf_sorted[0, 1, :], '-g')
        # plt.plot(analogs_time_vector, grf_sorted[0, 2, :], '.b')
        # plt.plot(analogs_time_vector, y, '-b')
        # plt.plot(analogs_time_vector, grf_sorted[0, 3, :], '-m')
        # plt.plot(analogs_time_vector, grf_sorted[0, 4, :], '-c')
        # plt.plot(analogs_time_vector, grf_sorted[0, 5, :], '-k')
        # plt.xlim(0, 1.4)
        # plt.show()


    def detect_swing_phases(self):
        minimal_vertical_force_threshold = 0.007
        grf_right_z_filtered = moving_average(self.grf_sorted[0, 3, :], 21)
        grf_left_z_filtered = moving_average(self.grf_sorted[1, 3, :], 21)
        self.phases_left_leg["swing"][:] = np.abs(grf_right_z_filtered) < minimal_vertical_force_threshold
        self.phases_right_leg["swing"][:] = np.abs(grf_left_z_filtered) < minimal_vertical_force_threshold
        return

    def detect_heel_only_phases(self):
        maximal_forward_force_threshold = 0.05

        swing_timings = np.where(self.phases_left_leg["swing"])[0]
        left_swing_sequence = np.array_split(
            swing_timings, np.flatnonzero(np.diff(swing_timings) > 1) + 1
        )
        for i_swing, swing_phase in enumerate(left_swing_sequence):
            idx = swing_phase[-1]
            while idx < self.nb_analog_frames - 1 and np.abs(self.grf_sorted[0, 1, idx]) < maximal_forward_force_threshold:
                idx += 1
            if idx <= self.nb_analog_frames - 1:
                self.events["left_leg_heel_touch"] += [int((swing_phase[-1] + idx - 1) / 2)]


    def find_event_timestamps(self):
        self.detect_swing_phases()
        self.detect_heel_only_phases()
        self.plot_events()


    def plot_events(self):
        fig, axs = plt.subplots(2, 1, figsize=(15, 7))
        # axs[0].plot(grf_sorted[0, 0, :], '-r', label='Medio-lateral')
        axs[0].plot(self.grf_sorted[0, 1, :], '-g', label='Antero-posterior')
        axs[0].plot(self.grf_sorted[0, 2, :], '-b', label='Vertical')
        # axs[0].plot(grf_right_z_filtered, '-k', label='Z filtered')
        axs[0].plot(np.where(self.phases_left_leg["swing"])[0], self.grf_sorted[0, 3, np.where(self.phases_left_leg["swing"])[0]], 'ok')
        axs[0].plot(np.array(self.events["left_leg_heel_touch"]), self.grf_sorted[0, 3, np.array(self.events["left_leg_heel_touch"])], 'om')
        axs[0].set_ylabel('Left leg GRF')
        axs[0].legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0.)
        axs[0].set_xlim(0, 40000)
        # axs[1].plot(grf_sorted[1, 0, :], '-r', label='Medio-lateral')
        axs[1].plot(self.grf_sorted[1, 1, :], '-g', label='Antero-posterior')
        axs[1].plot(self.grf_sorted[1, 2, :], '-b', label='Vertical')
        axs[1].plot(np.where(self.phases_right_leg["swing"])[0], self.grf_sorted[1, 3, np.where(self.phases_right_leg["swing"])[0]], 'ok')
        axs[1].set_ylabel('Right leg GRF')
        axs[1].set_xlim(0, 40000)
        plt.savefig("GRF.png")
        plt.show()
    
