import pandas as pd
import streamlit as st
import pydeck as pdk
import matplotlib.pyplot as plt



volcanoes = pd.read_csv("volcanoes.csv", encoding = 'UTF-8' )
volcanoes= volcanoes.dropna() #This removed ~20 lines
volcanoes.columns = volcanoes.columns.str.replace(' ','_')
volcanoes = volcanoes.rename(columns = {'Elevation_(m)' : 'Elevation', 'Latitude': 'lat', 'Longitude': 'lon'})
volcanoes['lat'] = pd.to_numeric(volcanoes['lat'])
volcanoes['lon'] = pd.to_numeric(volcanoes['lon'])
volcanoes['Elevation'] = pd.to_numeric(volcanoes['Elevation'])

volcanoes.columns.str.encode('ascii', 'ignore').str.decode('ascii')

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
st.title('Query 1')
st.subheader('This query is intended to map the locations of each volcano based on their region and the dominant rock '+
             'type being produced')
regions_list = []
for region in volcanoes['Region']:
        if region not in regions_list:
            regions_list.append(region)
regions_list = sorted(regions_list)
regions_list.insert(0, 'All')
selected_region = st.selectbox('Please select a region', regions_list)

if selected_region == 'All':
        rockset = volcanoes
else:
        rockset = volcanoes[volcanoes.Region == selected_region]

rt_list = []
for type in volcanoes['Dominant_Rock_Type']:
        if type not in rt_list and type != 'No Data (checked)':
            rt_list.append(type)
rt_list = sorted(rt_list)
rt_list.insert(0, 'All') #This allows me to use the rt_list in the next query
select_rt_list = []
for rock in rt_list:
    for line in rockset['Dominant_Rock_Type']:
        if rock == line and rock not in select_rt_list:
            select_rt_list.append(rock)
select_rt_list.insert(0,'All')

selected_rt = st.selectbox('Please select a rock type', select_rt_list)

if selected_rt == 'All':
        finaldf = rockset
else:
        finaldf = rockset[rockset.Dominant_Rock_Type == selected_rt]
newdf = finaldf[['Volcano_Name','Region','Subregion','lat','lon', 'Dominant_Rock_Type']]

view_state = pdk.ViewState(
        latitude=newdf["lat"].mean(),
        longitude=newdf["lon"].mean(),
        zoom=5,
        pitch=0)

layer = pdk.Layer('ScatterplotLayer',
                      data=newdf,
                      get_position='[lon, lat]',
                      get_radius= 20000,
                      get_color=[255,0,0],
                      pickable=True
                      )

tool_tip = {"html":'Name: <b> {Volcano_Name}</b> </br> '+
                   'Region: {Region} </br> '+
                   'Subregion: {Subregion} </br> '+
                   'Rock Type: {Dominant_Rock_Type} </br>'+
                   'Longitude: {lon}</br>'+
                   'Latitude: {lat}</br>',
                "style": { "backgroundColor": "steelblue",
                            "color": "white"}
                }

map = pdk.Deck(
        map_style= 'mapbox://styles/mapbox/outdoors-v11',
        initial_view_state= view_state,
        layers= layer,
        tooltip= tool_tip
        )

st.pydeck_chart(map)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
rt_list1 = []
for type in volcanoes['Dominant_Rock_Type']:
    if type not in rt_list1 and type != 'No Data (checked)':
        rt_list1.append(type)
rt_list1 = sorted(rt_list1)

st.title('Query 2')
st.subheader('This query investigates the relationship between the elevation of volcanoes and the dominant rock type '+
             'produced at that elevation')

max_range = volcanoes['Elevation'].max()
max_range = int(max_range)
min_range = volcanoes['Elevation'].min()
min_range = int(min_range)

values = st.slider(
     'Select a range of elevations',
     min_range, max_range, (-1000, 1000))
st.write('Minimum and Maximum Elevations:', values)

lowrange = values[0]
highrange = values[1]

low_elev_df = volcanoes[volcanoes['Elevation'] > lowrange]
high_elev_df = volcanoes[volcanoes['Elevation'] < highrange]
elev_df = pd.merge(low_elev_df, high_elev_df)


type_count = []
for type in rt_list1:
    count = 0
    for rock in elev_df['Dominant_Rock_Type']:
        if rock == type:
            count += 1
    type_count.append(count)

plt.xticks(rotation = 270)
plt.bar(rt_list1, type_count)
plt.title(f'Distribution of Dominant Rock Type in Elevation Range {lowrange}-{highrange}')
plt.xlabel('Rock Types')
plt.ylabel('Number of Volcanoes')
st.pyplot(plt)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
st.title('Query 3')
st.subheader('This query investigates the relationships between the type of volcano each volcano is and the region it '+
             'appears, the dominant rock type it produces, and the tectonic setting it is found in.')
volcano_list = []
for volcano in volcanoes['Primary_Volcano_Type']:
    if volcano not in volcano_list:
        volcano_list.append(volcano)
volcano_list.insert(0,'All')
volcano_list = sorted(volcano_list)

rt_list2 = []
for type in volcanoes['Dominant_Rock_Type']:
    if type not in rt_list2 and type != 'No Data (checked)':
        rt_list2.append(type)
rt_list2 = sorted(rt_list2)

regions_list1 = []
for region in volcanoes['Region']:
    if region not in regions_list1:
        regions_list1.append(region)
regions_list1 = sorted(regions_list1)

selected_vol = st.selectbox('Select a volcano type', volcano_list)
st.write(selected_vol)

total_elev = 0
if selected_vol == 'All':
    vol_type_df = volcanoes
else:
    vol_type_df = volcanoes[volcanoes.Primary_Volcano_Type == selected_vol]
for volcano in vol_type_df['Elevation']:
    total_elev += int(volcano)
average_elev = total_elev / len(vol_type_df)


max_count = 0
count_list_regions = []
for region in regions_list1:
     count = 0
     for region1 in vol_type_df['Region']:
         if region1 == region:
             count += 1
     if count > max_count:
         max_count = count
     count_list_regions.append(count)
for block in count_list_regions:
    if block == 0:
        spot = count_list_regions.index(block)
        count_list_regions.pop(spot)
        regions_list1.pop(spot)
max_num = max(count_list_regions)
spot = count_list_regions.index(max_num)
most_common_region = regions_list1[spot]


max_count1 = 0
count_list_rocks = []
for type in rt_list2:
    count = 0
    for type1 in vol_type_df['Dominant_Rock_Type']:
        if type1 == type:
            count += 1
    if count > max_count1:
        max_count1 = count
    count_list_rocks.append(count)
for block in count_list_rocks:
    if block == 0:
        spot = count_list_rocks.index(block)
        count_list_rocks.pop(spot)
        rt_list2.pop(spot)
max_spot = max(count_list_rocks)
spot = count_list_rocks.index(max_spot)
most_common_type = rt_list2[spot]


tectonic_list = []
for zone in volcanoes['Tectonic_Setting']:
    if zone not in tectonic_list:
        tectonic_list.append(zone)

max_count2 = 0
count_list_zone = []
for zone in tectonic_list:
    count = 0
    for zone1 in vol_type_df['Tectonic_Setting']:
        if zone1 == zone:
            count += 1
    if count > max_count2:
        max_count2 = count
    count_list_zone.append(count)
for block in count_list_regions:
    if block == 0:
        spot = count_list_zone.index(block)
        count_list_zone.pop(spot)
        tectonic_list.pop(spot)
max_spot = max(count_list_zone)
spot = count_list_zone.index(max_spot)
most_common_tectonic = tectonic_list[spot]
st.header('Statistics:')
st.write(f'{selected_vol} Average Elevation:  {average_elev:0.2f} M')
st.write(f'{selected_vol} Most Common Region: ', most_common_region)
st.write(f'{selected_vol} Most Common Dominant Rock Type: ', most_common_type)
st.write(f'{selected_vol} Most Common Tectonic Setting: ', most_common_tectonic)

st.header('Piecharts:')
st.write('All slices that read 0.0% are incredibly small fractions. If it appears on the pie chart, it appears in the dataset')

st.subheader('Regions')
fig1, ax1 = plt.subplots()
ax1.pie(count_list_regions, labels=regions_list1, autopct='%1.1f%%',)
ax1.axis('equal')
st.pyplot(plt)

st.subheader('Rock Types')
fig1, ax1 = plt.subplots()
ax1.pie(count_list_rocks, labels=rt_list2, autopct='%1.1f%%',)
ax1.axis('equal')
st.pyplot(plt)

st.subheader('Tectonic Settings')
fig1, ax1 = plt.subplots()
ax1.pie(count_list_zone, labels=tectonic_list, autopct='%1.1f%%',)
ax1.axis('equal')
st.pyplot(plt)
