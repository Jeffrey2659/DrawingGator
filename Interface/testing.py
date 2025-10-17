from svgpathtools import svg2paths
import numpy as np
import csv

def extract_path_coordinates(svg_path, num_points=100):
    """
    Extracts (x, y) coordinates from all <path> elements in an SVG file.
    Uses svgpathtools to sample evenly along each path segment.
    """
    # Read SVG paths and their attributes
    paths, attributes = svg2paths(svg_path)

    coordinates = []

    # Loop over all path elements
    for path in paths:
        for segment in path:
            # Sample points along each segment
            for t in np.linspace(0, 1, num_points):
                point = segment.point(t)
                coordinates.append((point.real, point.imag))

    print(f"✅ Extracted {len(coordinates)} coordinates from {svg_path}")
    return coordinates


def save_coordinates_to_csv(coordinates, output_csv="coordinates.csv"):
    """
    Saves a list of (x, y) coordinate tuples to a CSV file.
    """
    with open(output_csv, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["x", "y"])  # header
        writer.writerows(coordinates)
    print(f"✅ Saved {len(coordinates)} coordinates to {output_csv}")


# Example usage:
if __name__ == "__main__":
    svg_file = "output.svg"
    coords = extract_path_coordinates(svg_file, num_points=10)
    save_coordinates_to_csv(coords, "path_coordinates.csv")

    # Optional: preview the first few points
    print("Sample coordinates:")
    for pt in coords[:10]:
        print(pt)
