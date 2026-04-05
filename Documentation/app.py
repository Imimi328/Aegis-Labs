import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

def generate_tensor_heatmap():
    # --- 1. PARAMETERS ---
    # Based on the paper's methodology
    N = 12  # Number of source frames
    M = 16  # Number of candidate target frames

    # --- 2. SIMULATE TENSOR DATA (C = T @ S.T) ---
    # Generate background noise (low cosine similarity for non-matching frames)
    # Using values between 0.15 and 0.40
    C = np.random.uniform(0.15, 0.40, (M, N))

    # Inject a simulated positive match (diagonal correlation)
    # Simulating a pirated clip starting at Target Frame 3 (index 2)
    start_offset = 2
    for i in range(N):
        if i + start_offset < M:
            # High cosine similarity for the matching sequence (0.75 to 0.95)
            # Satisfies the > 0.65 Final Score and > 0.75 Average conditions
            C[i + start_offset, i] = np.random.uniform(0.75, 0.95)

    # --- 3. PLOT CONFIGURATION ---
    # Set the style for a clean, academic look
    sns.set_theme(style="white")
    plt.figure(figsize=(12, 9))

    # Generate the heatmap
    ax = sns.heatmap(
        C, 
        cmap="viridis",      # Viridis is standard for academic heatmaps (colorblind friendly)
        annot=True,          # Show the similarity scores in the cells
        fmt=".2f",           # Format to 2 decimal places
        vmin=0.0,            # Cosine similarity min
        vmax=1.0,            # Cosine similarity max
        linewidths=.5,       # Add gridlines between cells
        cbar_kws={'label': 'Cosine Similarity Score'}
    )

    # --- 4. LABELS & TYPOGRAPHY ---
    # Labels for the X and Y axes
    ax.set_xticklabels([f"Src F{i+1}" for i in range(N)], rotation=45, ha="right", fontsize=10)
    ax.set_yticklabels([f"Tgt F{i+1}" for i in range(M)], rotation=0, fontsize=10)

    # Titles and Axis Labels
    plt.title("Figure 2: Frame-to-Frame Cosine Similarity Matrix ($C = T S^\\top$)", fontsize=14, pad=20)
    plt.xlabel("Source Embeddings (N=12)", fontsize=12, labelpad=15)
    plt.ylabel("Candidate Target Embeddings (M)", fontsize=12, labelpad=15)

    # Adjust layout so labels aren't cut off
    plt.tight_layout()

    # --- 5. SAVE AND SHOW ---
    # Save as a high-resolution PNG for your paper
    output_filename = "tensor_heatmap_fig2.png"
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    print(f"Heatmap successfully saved as {output_filename}")

    # Display the plot
    plt.show()

if __name__ == "__main__":
    generate_tensor_heatmap()