import os
import pandas as pd
import ast  # For safely parsing dictionary-like strings

# Paths
input_dir = "/bigdata/stajichlab/shared/projects/Herptile/Metagenome/Fecal/results_bins_checkm"
output_dir = "/bigdata/stajichlab/lshad003/HerptileMAGs"

# Ensure the output directory exists
os.makedirs(output_dir, exist_ok=True)

# Create lists to store high-quality and medium-quality MAGs
high_quality_mags = []
medium_quality_mags = []

# Loop through each sample directory
for sample_dir in os.listdir(input_dir):
    storage_dir = os.path.join(input_dir, sample_dir, "storage")
    
    # Check if the storage directory exists
    if not os.path.exists(storage_dir):
        continue
    
    # Path to bin_stats_ext.tsv
    stats_file = os.path.join(storage_dir, "bin_stats_ext.tsv")
    
    # Check if the stats file exists
    if not os.path.isfile(stats_file):
        continue

    # Read the file line by line
    with open(stats_file, "r") as f:
        for line in f:
            parts = line.strip().split("\t")
            if len(parts) != 2:
                continue
            
            mag_name, stats_str = parts
            try:
                # Safely evaluate the stats string into a dictionary
                stats = ast.literal_eval(stats_str)
                completeness = stats.get("Completeness", 0)
                contamination = stats.get("Contamination", 100)
                
                # Classify MAGs based on quality
                if completeness > 90 and contamination < 5:
                    high_quality_mags.append([sample_dir, mag_name, completeness, contamination])
                elif completeness > 50 and contamination < 5:
                    medium_quality_mags.append([sample_dir, mag_name, completeness, contamination])
            except (SyntaxError, ValueError):
                print(f"Error parsing stats for MAG {mag_name} in {stats_file}")
                continue

# Convert to DataFrames
high_quality_df = pd.DataFrame(high_quality_mags, columns=["Sample", "MAG", "Completeness", "Contamination"])
medium_quality_df = pd.DataFrame(medium_quality_mags, columns=["Sample", "MAG", "Completeness", "Contamination"])

# Save results to TSV files
high_quality_output = os.path.join(output_dir, "high_quality_mags.tsv")
medium_quality_output = os.path.join(output_dir, "medium_quality_mags.tsv")

high_quality_df.to_csv(high_quality_output, sep="\t", index=False)
medium_quality_df.to_csv(medium_quality_output, sep="\t", index=False)

print(f"High-quality MAGs saved to: {high_quality_output}")
print(f"Medium-quality MAGs saved to: {medium_quality_output}")

