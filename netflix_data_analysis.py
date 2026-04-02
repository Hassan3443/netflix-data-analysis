# Import required libraries
import pandas as pd
import matplotlib.pyplot as plt

# Use default style for cleaner visuals
plt.style.use('default')

# Load dataset
df = pd.read_csv("E:/netflix/netflix_titles.csv")

# Preview first rows
print(df.head())

print("\n" + "-"*50 + "\n")

# -------------------------------
# Data Cleaning
# -------------------------------

# Remove rows with missing country values
df = df.dropna(subset=['country'])

# Split multiple countries into lists
df['country'] = df['country'].str.split(',')

# Expand lists into separate rows
df = df.explode('country')

# Remove extra spaces
df['country'] = df['country'].str.strip()

# -------------------------------
# Movies vs TV Shows
# -------------------------------

type_counts = df['type'].value_counts()
print(type_counts)

plt.figure(figsize=(8,5))

type_counts.plot(kind='bar')

plt.title("Movies vs TV Shows", fontsize=14)
plt.xlabel("Type", fontsize=12)
plt.ylabel("Count", fontsize=12)

plt.xticks(rotation=0)
plt.tight_layout()

plt.show()

print("\n" + "-"*50 + "\n")

# -------------------------------
# Top 10 Countries
# -------------------------------

top_countries = df['country'].value_counts().head(10)
print(top_countries)

plt.figure(figsize=(10,6))

top_countries.plot(kind='bar')

plt.title("Top 10 Countries Producing Netflix Content", fontsize=14)
plt.xlabel("Country", fontsize=12)
plt.ylabel("Count", fontsize=12)

plt.xticks(rotation=45)
plt.tight_layout()

plt.show()

print("\n" + "-"*50 + "\n")

# -------------------------------
# Content Over Years
# -------------------------------

# Convert release_year to numeric if needed
df['release_year'] = pd.to_numeric(df['release_year'], errors='coerce')

# Count content per year
content_per_year = df['release_year'].value_counts().sort_index()

plt.figure(figsize=(10,6))

content_per_year.plot(kind='line')

plt.title("Growth of Netflix Content Over Time", fontsize=14)
plt.xlabel("Year", fontsize=12)
plt.ylabel("Count", fontsize=12)

plt.tight_layout()

plt.show()