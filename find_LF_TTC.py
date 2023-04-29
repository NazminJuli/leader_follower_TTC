import pandas as pd
import numpy as np
from math import radians, sin, cos, sqrt, atan2

data_T1 = pd.read_csv("data/T3.csv")
data_T2 = pd.read_csv("data/T4.csv")

# Merge trajectories based on time stamps
merged = pd.merge(data_T1, data_T2, on="Time (s)")
print(merged)

# Calculate distance between the two trajectories using Haversine formula

merged["lat_x"] = merged["Latitude_x"].apply(radians)
merged["lon_x"] = merged["Longitude_x"].apply(radians)
merged["lat_y"] = merged["Latitude_y"].apply(radians)
merged["lon_y"] = merged["Longitude_y"].apply(radians)

merged["dlat"] = merged["lat_y"] - merged["lat_x"]
merged["dlon"] = merged["lon_y"] - merged["lon_x"]
R = 6371  # Earth's radius in km

merged["a"] = np.sin(merged["dlat"]/2)**2 + np.cos(merged["lat_x"]) * np.cos(merged["lat_y"]) * np.sin(merged["dlon"]/2)**2
merged["c"] = 2 * np.arcsin(np.sqrt(merged["a"]))
merged["distance"] = R * merged["c"] * 1000


# Estimate the leader and follower based on the distance between the two trajectories
merged["vehicle_length_x"] = merged["vehicle_length_y"] = 3  # Vehicle length of trajectory 1,2 in meters
merged["effective_distance"] = merged["distance"] - merged["vehicle_length_x"]
print("distance in meter :",merged["effective_distance"])

# Calculate the relative velocity between the two trajectories
merged["time_diff"] = merged["Time (s)"].diff()

merged["velocity"] = merged["distance"].diff() / merged["time_diff"]


# Determine which trajectory is the leader and which one is the follower based on effective distance
merged["leader"] = np.where(merged["effective_distance"] < 0, "y", "x") # y means trajectory 2, x means trajectory 1
merged["follower"] = np.where(merged["leader"] == "x", "y", "x")


# Calculate the minimum time to collision based on the leader-follower relationship
merged["t_collision"] = merged["effective_distance"] / merged["velocity"]

min_t_collision_idx = merged["t_collision"].idxmin()
min_t_collision = merged.loc[min_t_collision_idx, "t_collision"]

print(f"Leader: {merged.loc[min_t_collision_idx, 'leader']}")
print(f"Follower: {merged.loc[min_t_collision_idx, 'follower']}")
print(f"Minimum time to collision: {min_t_collision} seconds")