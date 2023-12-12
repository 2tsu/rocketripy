import folium
def lonlat_plotter(lonlat_list):
    # Create a map centered at the first coordinates
    m = folium.Map(location=[lonlat_list[0][1], lonlat_list[0][0]], zoom_start=13)

    # Add a marker for each tuple in the list
    for lonlat in lonlat_list:
        folium.Marker([lonlat[1], lonlat[0]]).add_to(m)

    # Display the map
    return m


data = [[(139.98762798926342, 40.23751508443996), (139.98775542270428, 40.23852048922672), (139.98813095855294, 40.23901561524854), (139.98846905058, 40.2386507845928), (139.98863334912545, 40.23752242671944), (139.988497237512, 40.23639187713105), (139.98816821545432, 40.23602218102055)], [(139.98744677113743, 40.23751376003852), (139.98771913558102, 40.239403697928765), (139.98838615239674, 40.24045443310403), (139.9892179575835, 40.23986848932796), (139.9895193411556, 40.23752889009052), (139.98927615651837, 40.23518527661823), (139.98845903543372, 40.23458737402584)]]
# Call the function with a list of tuples
# Flatten the list of lists into a single list
flat_data = [item for sublist in data for item in sublist]
# Call the function with the flattened list
map = lonlat_plotter(flat_data)
map.save('map.html')
