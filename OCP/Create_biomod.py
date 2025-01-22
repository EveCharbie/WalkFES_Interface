import biorbd
import osim_to_biomod as otb

# --- To change here --- #
subject_name = "VIF_04"
# ---------------------- #

model_path = "data/"
model_name = "wholebody_florian"

muscles_to_ignore = ["ant_delt_r",
                    "ant_delt_l",
                    "medial_delt_l",
                    "post_delt_r",
                    "post_delt_l",
                    "medial_delt_r",
                    "ercspn_r",
                    "ercspn_l",
                    "rect_abd_r",
                    "rect_abd_l",
                    "r_stern_mast",
                    "l_stern_mast",
                    "r_trap_acr",
                    "l_trap_acr",
                    "TRIlong",
                    "TRIlong_l",
                    "TRIlat",
                    "TRIlat_l",
                    "BIClong",
                    "BIClong_l",
                    "BRD",
                    "BRD_l",
                    "FCR",
                    "FCR_l",
                    "ECRL",
                    "ECRL_l",
                    "PT",
                    "PT_l",
                    "LAT2",
                    "LAT2_l",
                    "PECM2",
                    "PECM2_l",
                     ]

muscles_to_igonre_for_now = ["glut_med1_r",
                             "semiten_r",
                             "bifemlh_r",
                             "sar_r",
                             "tfl_r",
                             "vas_med_r",
                             "vas_lat_r",
                             "glut_med1_l",
                             "semiten_l",
                             "bifemlh_l",
                             "sar_l",
                             "tfl_l",
                             "vas_med_l",
                             "vas_lat_l"]
converter = otb.Converter(
    model_path + model_name + '_' + subject_name + ".bioMod",  # .bioMod file to export to
    model_path + model_name + '_' + subject_name + ".osim",  # .osim file to convert from
    ignore_muscle_applied_tag=False,
    ignore_fixed_dof_tag=False,
    ignore_clamped_dof_tag=False,
    mesh_dir=model_path + "/Geometry",  # folder where all opensim's vtp files are stored
    muscle_type=otb.MuscleType.HILL,
    state_type=otb.MuscleStateType.DEGROOTE,
    print_warnings=True,
    print_general_informations=True,
    vtp_polygons_to_triangles=True,
    muscles_to_ignore=muscles_to_ignore+muscles_to_igonre_for_now,
)
converter.convert_file()




