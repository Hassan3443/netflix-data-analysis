import pandas as pd
import matplotlib.pyplot as plt

# Load dataset
df = pd.read_csv("E:/netflix/netflix_titles.csv")

# Display first few rows
print(df.head())

print("\n" + "="*50 + "\n")

# Check missing values
print("Missing Values:")
print(df.isnull().sum())

print("\n" + "="*50 + "\n")

# Remove rows with missing country values
df = df.dropna(subset=['country'])

# Split multiple countries into lists
df['country'] = df['country'].str.split(',')

# Expand list into separate rows
df = df.explode('country')

# Remove extra spaces from country names
df['country'] = df['country'].str.strip()

# Count number of Movies vs TV Shows
type_counts = df['type'].value_counts()
print(type_counts)

print("\n" + "="*50 + "\n")

# Identify top 10 countries by content production
top_countries = df['country'].value_counts().head(10)
print(top_countries)

print("\n" + "="*50 + "\n")

# Analyze content distribution over years
year_counts = df['release_year'].value_counts().sort_index()
print(year_counts)

print("\n" + "="*50 + "\n")

# Plot distribution of content types
type_counts.plot(kind='bar')
plt.title("Movies vs TV Shows")
plt.xlabel("Type")
plt.ylabel("Count")
plt.show()

# Plot top 10 countries
top_countries.plot(kind='bar')
plt.title("Top 10 Countries by Content")
plt.xlabel("Country")
plt.ylabel("Count")
plt.xticks(rotation=45)
plt.show()

# Plot content trend over time
year_counts.plot()
plt.title("Content Released Over Years")
plt.xlabel("Year")
plt.ylabel("Count")
plt.show()