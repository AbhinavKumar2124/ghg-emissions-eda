import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

#----------------------------------------------------------------------------------------Reading the Dataset-----------------------------------------------------------------------#
df = pd.read_excel(r"\data\GHG's Emmission_Removals of top 25 GDPs.xlsx", sheet_name="Sheet2")

#--------------------------------------------------------------------------------Data overview and basic exploration---------------------------------------------------------------#
print("Head of the DataFrame:")
print(df.head(10))

print("\nBasic info:")
print(df.info())

print("\nSummary Statistics:")
print(df.describe().round(2))

#---------------------------------------------------------------------------------------------Preprocessing------------------------------------------------------------------------#
df['Emission (Mt of CO2 equivalent)'] = df['Emission (Mt of CO2 equivalent)']/1000 #Converting Million Metric Tons (Mt) of CO2 to Billion Metric Tons (Gt) of CO2
df.columns = [
    "object_id",
    "country",
    "gdp_2023_trillion_usd",
    "industry",
    "gas_type",
    "year",
    "emission_gt_co2e"
]
print("\nRenamed Columns:")
print(df.columns)

#Converting the Data Type of 'year' to integer
df['year'] = df['year'].dt.year.astype('int64')

print("\nMissing Values in Each Column:")
print(df.isnull().sum())

print("\nNumber of Duplicate Rows:", df.duplicated().sum())

#Unique values
print("Unique Countries:")
print(df['country'].unique())

print("\nUnique Industries:")
print(df['industry'].unique())

print("\nUnique Gas Types:")
print(df['gas_type'].unique())

print("\nUnique Years:")
print(df['year'].unique())

#New DataFrame to work upon
df_clean = df[df['country'] != "World"]

industries_to_keep = ['1. Energy', '2. Industrial Processes and Product Use', '3. Agriculture','4. Land-use, land-use change and forestry', '5. Waste', '6. Other']
df_clean = df_clean[df_clean['industry'].isin(industries_to_keep)]

df_clean['industry'] = df_clean['industry'].replace({
    '1. Energy':'Energy',
    '2. Industrial Processes and Product Use':'Industrial Processes and Product Use',
    '3. Agriculture':'Agriculture',
    '4. Land-use, land-use change and forestry':'Land-use change and forestry',
    '5. Waste':'Waste',
    '6. Other':'Other'
})

#df_clean = df_clean[df_clean['year'] >= 1990]

# Verifying basic info to confirm it's correctly assigned
print("\nShape of df_clean:", df_clean.shape)
print("Columns in df_clean:", df_clean.columns)
print("Year range:", df_clean['year'].min(), "to", df_clean['year'].max())
print("Unique countries:", len(df_clean['country'].unique()))
print("Unique industries:", df_clean['industry'].unique())


#================================================================================= OBJEECTIVE 1: Trend Analysis of GHG Emissions Over Time ===============================================================#
print()
df_ghg_only = df_clean[df_clean['gas_type'] == 'Greenhouse gas']
emission_trend_global = df_ghg_only.groupby('year')['emission_gt_co2e'].sum().reset_index()
emission_trend_global.columns = ['year', 'total_emission_gt_co2e']
print(emission_trend_global.head())

plt.figure(figsize=(14, 7))
main_color = "#2E8B57"
sns.lineplot(
    data=emission_trend_global,
    x='year',
    y='total_emission_gt_co2e',
    marker='o',
    color=main_color
)
plt.fill_between(
    emission_trend_global['year'],
    emission_trend_global['total_emission_gt_co2e'],
    color=main_color,
    alpha=0.1
)
plt.title("Global GHG Emissions Trend (1970–2023)", fontsize=18, weight='bold', pad=15)
plt.xlabel("Year", fontsize=13)
plt.ylabel("Total Emissions (Gigatonnes CO2 eq.)", fontsize=13)
plt.xticks(rotation=45)
plt.gca().set_axisbelow(True)
plt.grid(visible=True, which='major', linestyle='--', alpha=0.5)
plt.tight_layout()
plt.show()


#==================================================================================== OBJEECTIVE 2: Total Emissions Over Time by Country =================================================================#
print()
emission_trend_country = df_ghg_only.groupby(['year', 'country'])['emission_gt_co2e'].sum().reset_index()
print(emission_trend_country.head(10))

# Total emissions per country (1970–2023)
top_emitters = df_ghg_only.groupby('country')['emission_gt_co2e'].sum().sort_values(ascending=False).head(6).index.tolist()
# Filtering only for top 6 countries
top_emitters_data = emission_trend_country[emission_trend_country['country'].isin(top_emitters)]
top_emitters_data.columns = ['year', 'country', 'total_emission_gt_co2e']
print(top_emitters_data.head(10))

plt.figure(figsize=(14, 7))
sns.lineplot(
    data=top_emitters_data,
    x='year',
    y='total_emission_gt_co2e',
    hue='country',
    marker='o'
)

plt.title("GHG Emissions Trend of Top 6 Countries (1970–2023)", fontsize=16, weight='bold', pad=15)
plt.xlabel("Year", fontsize=12)
plt.ylabel("Emissions (Gigatonnes CO2 eq.)", fontsize=12)
plt.xticks(rotation=45)
plt.legend(title='Country', fontsize='8', loc='upper left')
plt.gca().set_axisbelow(True)
plt.grid(visible=True, which='major', linestyle='--', linewidth=0.5, alpha=0.7)
plt.tight_layout()
plt.show()

#======================================================================================== OBJEECTIVE 3: Industry-wise Emission Analysis =================================================================#
print()
#Worldwide
industry_emission_global = df_ghg_only.groupby('industry')['emission_gt_co2e'].sum().reset_index()
industry_emission_global = industry_emission_global.sort_values(by='emission_gt_co2e', ascending=False)

total_emissions = industry_emission_global['emission_gt_co2e'].sum()
industry_emission_global['normalized_emission_percentage'] = round((industry_emission_global['emission_gt_co2e'] / total_emissions) * 100, 2)
industry_emission_global.columns = ['industry', 'emission_gt_co2e', 'Normalized emission percentage']
print(industry_emission_global)

plt.figure(figsize=(12, 7))
sns.barplot(
    data=industry_emission_global,
    x='Normalized emission percentage',
    y='industry',
    hue='Normalized emission percentage'
)

plt.title("GHG Emissions by Industry as Percentage of Total", fontsize=15, weight='bold', pad=15)
plt.xlabel("Percentage of Total Emissions", fontsize=12)
plt.ylabel("Industry", fontsize=12)
plt.gca().set_axisbelow(True)
plt.grid(visible=True, which='major', linestyle='--', linewidth=0.5, alpha=0.7)
plt.tight_layout()
plt.show()

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
print()
#Country wise
industry_emission_country = df_ghg_only[df_ghg_only['country'].isin(top_emitters)].groupby(['country', 'industry'])['emission_gt_co2e'].sum().reset_index()
print(industry_emission_country.head(10))

ordered_industries = industry_emission_country.groupby("industry")["emission_gt_co2e"].sum().sort_values(ascending=False).index

plt.figure(figsize=(14, 8))
barplot = sns.barplot(
    data=industry_emission_country,
    x='emission_gt_co2e',
    y='industry',
    hue='country',
    order=ordered_industries,
    edgecolor='black'
)

plt.title("Industry-wise GHG Emissions for Top 6 Countries", fontsize=17, weight='bold', pad=15)
plt.xlabel("Emissions (Gigatonnes CO2 eq)", fontsize=12)
plt.ylabel("Industry", fontsize=12)

plt.gca().set_axisbelow(True)
plt.grid(axis='x', linestyle='--', alpha=0.4)
plt.legend(title="Country", fontsize=8, title_fontsize=11, loc='lower right', frameon=True)
sns.despine(left=True, bottom=True)

for spine in plt.gca().spines.values():
    spine.set_visible(True)
    spine.set_edgecolor('black')
    spine.set_linewidth(1.2)

plt.tight_layout()
plt.show()

#=========================================================================================== OBJEECTIVE 4: Global Emissions by Gas Type =============================================================================#
print()
df_gases_only = df_clean[df_clean['gas_type'] != 'Greenhouse gas']
gas_type_global = df_gases_only.groupby('gas_type')['emission_gt_co2e'].sum().reset_index()
gas_type_global = gas_type_global.sort_values(by='emission_gt_co2e', ascending=False)
print(gas_type_global)

total_emissions = gas_type_global['emission_gt_co2e'].sum()
gas_type_global['Percentage'] = (gas_type_global['emission_gt_co2e'] / total_emissions * 100).round(2)

plt.figure(figsize=(8, 7))
colors = sns.color_palette("coolwarm", len(gas_type_global))

wedges, texts, autotexts = plt.pie(
    gas_type_global['Percentage'], 
    labels=gas_type_global['gas_type'],
    autopct='%1.1f%%',
    startangle=140,
    colors=colors,
    wedgeprops=dict(width=0.4)
)

plt.setp(autotexts, size=12, weight="bold")
plt.setp(texts, size=12)
plt.title("Global GHG Emissions by Gas Type (%)", fontsize=15, fontweight='bold', pad=20)
plt.tight_layout()
plt.show()

#============================================================================================== OBJEECTIVE 5: Global Yearly Emissions by Gas Type ==================================================================#
print()
gas_trend_year = df_gases_only.groupby(['year', 'gas_type'])['emission_gt_co2e'].sum().reset_index()

plt.figure(figsize=(14, 7))

sns.lineplot(
    data=gas_trend_year,
    x='year',
    y='emission_gt_co2e',
    hue='gas_type'
)

for gas in gas_trend_year['gas_type'].unique():
    gas_data = gas_trend_year[gas_trend_year['gas_type'] == gas]
    plt.fill_between(gas_data['year'], gas_data['emission_gt_co2e'], alpha=0.15)

plt.title("GHG Emission Trends by Gas Type Over Years", fontsize=15, fontweight='bold', pad=20)
plt.xlabel("Year", fontsize=12)
plt.ylabel("Emissions (Gigatonnes CO2 eq.)", fontsize=12)
plt.legend(title='Gas Type')
plt.gca().set_axisbelow(True)
plt.grid(visible=True, which='major', linestyle='--', linewidth=0.5, alpha=0.7)
plt.tight_layout()
plt.show()

#================================================================================================ OBJEECTIVE 6: Emission Efficiency Analysis =======================================================================#
print()
emission_efficiency = df_ghg_only.groupby('country').agg({
    'gdp_2023_trillion_usd': 'first',          # GDP remains the same per country
    'emission_gt_co2e': 'sum'                  # Total GHG emissions (1990–2023)
}).reset_index()

emission_efficiency.columns = ['country', 'gdp_2023_trillion_usd', 'total_ghg_emission_gt_co2e']
emission_efficiency['emission_per_gdp'] = (emission_efficiency['total_ghg_emission_gt_co2e'] / emission_efficiency['gdp_2023_trillion_usd'])

emission_efficiency = round((emission_efficiency.sort_values(by='emission_per_gdp', ascending=False)), 2)
print(emission_efficiency.head(10))

plt.figure(figsize=(14, 7))
sns.barplot(
    data=emission_efficiency,
    x='country',
    y='emission_per_gdp',
    hue='country',
    palette='Reds_r'
)

plt.title("GHG Emissions per Trillion USD GDP (1970–2023)", fontsize=15, weight='bold', pad=15)
plt.ylabel("Emission Intensity (Gigatonnes CO2 eq per Trillion USD)", fontsize=12)
plt.xlabel("Country", fontsize=12)
plt.xticks(rotation=45, ha='right')
plt.gca().set_axisbelow(True)
plt.grid(visible=True, which='major', linestyle='--', linewidth=0.5, alpha=0.7)
plt.tight_layout()
plt.show()

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
print()
min_val = emission_efficiency['emission_per_gdp'].min()
max_val = emission_efficiency['emission_per_gdp'].max()
emission_efficiency['green_score'] = 100 * (1 - ((emission_efficiency['emission_per_gdp'] - min_val) / (max_val - min_val)))
emission_efficiency['green_score'] = emission_efficiency['green_score'].round(2)
emission_efficiency = emission_efficiency.sort_values(by='green_score', ascending=False)
print(emission_efficiency.head(10))

plt.figure(figsize=(14, 7))
sns.barplot(
    data=emission_efficiency,
    x='country',
    y='green_score',
    hue='country',
    palette='Greens'
)

plt.title("Green Score by Country (Emission Efficiency)", fontsize=15, weight='bold', pad=15)
plt.ylabel("Green Score (0–100)", fontsize=12)
plt.xlabel("Country", fontsize=12)
plt.xticks(rotation=45, ha='right')
plt.gca().set_axisbelow(True)
plt.grid(visible=True, which='major', linestyle='--', linewidth=0.5, alpha=0.7)
plt.tight_layout()
plt.show()

#========================================================================================== OBJEECTIVE 7: Correlation Between Key Metrics ==========================================================================#
print()
corr_df = emission_efficiency[['gdp_2023_trillion_usd', 'total_ghg_emission_gt_co2e', 'emission_per_gdp']]
corr_df.columns = ['GDP(2023)', 'Net Emission', 'Emission Efficiency']

correlation_matrix = corr_df.corr().round(2)
print(correlation_matrix)

plt.figure(figsize=(8, 6))
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt='.2f')

plt.title("Correlation Between GDP, Emissions & Efficiency Metrics", fontsize=14, weight='bold', pad=15)
plt.tight_layout()
plt.show()

