from shiny import App, render, ui
import pandas as pd
import matplotlib.pyplot as plt
import geopandas

# Define our ui and our input options.
app_ui = ui.page_fluid(
    ui.h2("Interactive Chicago Map by Zip Code"),
    ui.row(
        ui.column(2, ui.input_radio_buttons(id='slct_lines',
                                            label='L Lines',
                                            choices=list(['Off', 'On']))),
        ui.column(2, ui.input_select(id="dta",
                                     label="Choose a Data Set",
                                     choices=['Police Stations', 
                                              'Percentage of Population having Completed Vaccine Series by Zip Code']))
    ),
    ui.row(ui.output_plot('interactive_plot'))
)

# Open our CTA Rail Lines and Zip code shape files.
df_rails = geopandas.read_file('CTA_RailLines/CTA_RailLines.shp')
df_zip = geopandas.read_file('Boundaries - ZIP Codes/geo_export_bcda710a-bdf0-41ae-af2d-f8e7aa5fac95.shp')
df_zip = df_zip.to_crs('EPSG:3435') 

# Code from lecture to color the L lines.
def get_col(l):
    if 'Blue' in l:
        return 'b'
    elif 'Red' in l:
        return 'r'
    elif 'Purple' in l:
        return 'purple'
    elif 'Brown' in l:
        return 'brown'
    elif 'Yellow' in l:
        return 'yellow'
    elif 'Green' in l:
        return 'green'
    elif 'Pink' in l:
        return 'pink'
    elif 'Orange' in l:
        return 'orange'
color_dict = {l:get_col(l) for l in df_rails['LINES'].unique()}


# Import our Covid Vaccination by Zip CodeDataset. 
# Selecting only the data of completed series vaccine by percent of population.
covid_one_dose_df = pd.read_csv('COVID-19_Vaccinations_by_ZIP_Code.csv')
covid_one_dose_df = covid_one_dose_df[['Zip Code','Vaccine Series Completed  - Percent Population']]
covid_one_dose_df.columns = ['zip', 'complete_vaccine_perc']

# Merge Covid data with shape cip file for plotting.
df_zip_merged = df_zip.merge(covid_one_dose_df, on='zip', how='left')
df_zip_merged['complete_vaccine_perc'] = pd.to_numeric(df_zip_merged['complete_vaccine_perc'])


# Load Police Station data.
police_station_df = pd.read_csv('Police_Stations.csv')
police_station_df.columns = police_station_df.columns.str.lower()
police_station_df = police_station_df[['zip', 'x coordinate', 'y coordinate']]

g_police_station_df = geopandas.GeoDataFrame(police_station_df, 
                                             geometry=geopandas.points_from_xy(police_station_df['x coordinate'], 
                                                                               police_station_df['y coordinate']))



# Plotting function that is customized based on input.
def server(input, output, session):  
    @output
    @render.plot
    def interactive_plot():
        fig, ax = plt.subplots(figsize=(15,15))
        ax = df_zip.plot(ax=ax, color='white', alpha=0.5, edgecolor='black', label='Zip ')
        ax.axis('off')
        if input.slct_lines() == 'On':
            for line in df_rails['LINES'].unique():
                c = color_dict[line]
                df_rails[df_rails['LINES'] == line].plot(ax=ax, color=c, alpha=0.5, linewidth=2)
            ax.set_title('(With L Lines)')
        elif input.slct_lines() == 'Off':
            ax.set_title('(Without L Lines)')
        if input.dta() == 'Police Stations':
            g_police_station_df.plot(ax=ax, color='red', markersize=5)
            fig.suptitle('Police Stations', fontsize=16)
        elif input.dta() == 'Percentage of Population having Completed Vaccine Series by Zip Code':
            ax = df_zip_merged.plot(ax=ax, 
                                    column='complete_vaccine_perc',  
                                    alpha=0.5, 
                                    edgecolor='black',
                                    legend=True)
            fig.suptitle('Percentage of Population having Completed Vaccine Series', fontsize=16, ha='left')
    

app = App(app_ui, server)

# Please note that the choropleth takes a while to render when switching between datasets. (20 seconds)
# The professor said this was fine as it is due to a very large covid dataset being shown.














