DEFINES_H_EXCERPT = """
// DATA - event logging
#define DATA_AP_STATE                       7
// 8 was DATA_SYSTEM_TIME_SET
#define DATA_INIT_SIMPLE_BEARING            9
#define DATA_ARMED                          10
#define DATA_DISARMED                       11
#define DATA_AUTO_ARMED                     15
#define DATA_LAND_COMPLETE_MAYBE            17
#define DATA_LAND_COMPLETE                  18
#define DATA_NOT_LANDED                     28
#define DATA_LOST_GPS                       19
#define DATA_FLIP_START                     21
#define DATA_FLIP_END                       22
#define DATA_SET_HOME                       25
#define DATA_SET_SIMPLE_ON                  26
#define DATA_SET_SIMPLE_OFF                 27
#define DATA_SET_SUPERSIMPLE_ON             29
#define DATA_AUTOTUNE_INITIALISED           30
#define DATA_AUTOTUNE_OFF                   31
#define DATA_AUTOTUNE_RESTART               32
#define DATA_AUTOTUNE_SUCCESS               33
#define DATA_AUTOTUNE_FAILED                34
#define DATA_AUTOTUNE_REACHED_LIMIT         35
#define DATA_AUTOTUNE_PILOT_TESTING         36
#define DATA_AUTOTUNE_SAVEDGAINS            37
#define DATA_SAVE_TRIM                      38
#define DATA_SAVEWP_ADD_WP                  39
#define DATA_FENCE_ENABLE                   41
#define DATA_FENCE_DISABLE                  42
#define DATA_ACRO_TRAINER_DISABLED          43
#define DATA_ACRO_TRAINER_LEVELING          44
#define DATA_ACRO_TRAINER_LIMITED           45
#define DATA_GRIPPER_GRAB                   46
#define DATA_GRIPPER_RELEASE                47
#define DATA_PARACHUTE_DISABLED             49
#define DATA_PARACHUTE_ENABLED              50
#define DATA_PARACHUTE_RELEASED             51
#define DATA_LANDING_GEAR_DEPLOYED          52
#define DATA_LANDING_GEAR_RETRACTED         53
#define DATA_MOTORS_EMERGENCY_STOPPED       54
#define DATA_MOTORS_EMERGENCY_STOP_CLEARED  55
#define DATA_MOTORS_INTERLOCK_DISABLED      56
#define DATA_MOTORS_INTERLOCK_ENABLED       57
#define DATA_ROTOR_RUNUP_COMPLETE           58  // Heli only
#define DATA_ROTOR_SPEED_BELOW_CRITICAL     59  // Heli only
#define DATA_EKF_ALT_RESET                  60
#define DATA_LAND_CANCELLED_BY_PILOT        61
#define DATA_EKF_YAW_RESET                  62
#define DATA_AVOIDANCE_ADSB_ENABLE          63
#define DATA_AVOIDANCE_ADSB_DISABLE         64
#define DATA_AVOIDANCE_PROXIMITY_ENABLE     65
#define DATA_AVOIDANCE_PROXIMITY_DISABLE    66
#define DATA_GPS_PRIMARY_CHANGED            67
#define DATA_WINCH_RELAXED                  68
#define DATA_WINCH_LENGTH_CONTROL           69
#define DATA_WINCH_RATE_CONTROL             70
#define DATA_ZIGZAG_STORE_A                 71
#define DATA_ZIGZAG_STORE_B                 72
"""

event_ids_map = {}
for line in DEFINES_H_EXCERPT.split("\n"):
    if not line.startswith("#define"):
        continue
    event_ids_map[int(line.split()[2])] = line.split()[1]


class Print:
    def __init__(self, description, x_axis="TimeUS", x_scale=1.e6):
        self.desired_values = []
        self.x_axis = x_axis
        self.x_scale = x_scale
        self.desired_values = []
        self.parse(description)

        self.data_sets = []

    def parse(self, description):
        for val in description.split(","):
            tmp = val.split(".")
            self.desired_values += [(tmp[0].strip(), tmp[1].strip())]

    def feed(self, data_point):
        for v in self.desired_values:
            if data_point.name == v[0]:
                self.data_sets += [(data_point.values[self.x_axis],
                                    ".".join(v),
                                    data_point.values[v[1]])]

    def print_(self):
        print("------------------------------------------------")
        for s in self.data_sets:
            time = s[0]/self.x_scale
            name = s[1]
            val = s[2]
            if name == "EV.Id" and val in event_ids_map:
                val = event_ids_map[val]

            print("%.2f: %20s: %s" % (time, name, val))
        print("------------------------------------------------")


if __name__ == '__main__':
    import sys
    from log_file import LogFile

    logf = LogFile(sys.argv[1])

    if len(sys.argv) > 2:
        plot = Print(" ".join(sys.argv[2:]))
        for v in logf.read():
            plot.feed(v)

        plot.print_()
    else:
        all_formats = {}
        for v in logf.read():
            if v.name not in all_formats:
                all_formats[v.name] = [k for k in v.values]

        for fmt in sorted(all_formats.keys()):
            print("%4s: %s" % (fmt, ", ".join(all_formats[fmt])))
