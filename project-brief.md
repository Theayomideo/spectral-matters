# Electron Spectroscopy Analyzer

Electron spectroscopy involves examining matter by radiating it with bright light and measuring the kinetic energy of ejected electrons. When both the photonic energy of the light and the kinetic energy of the electrons are known, it's possible to derive the force required to eject the electrons. This process, termed **photoionization**, sheds light on a material's electron structure and its chemical and physical properties. The ejected electrons in this context are referred to as **photoelectrons**.

This project is designed to allow users to analyze the photoionization spectrum of elements using simulated data. While the primary focus is on argon, the tool's versatility accommodates other elements.

## Core Features

- **Interactive GUI**: Facilitates ease of operation and visualization.
- **Data Loading**: Seamlessly import data, process, and structure it for analysis.
- **Data Visualization**: Plotting capabilities with labeled axes.
- **Noise Management**: Manual noise subtraction through user-selected data points.
- **Intensity Calculation**: Evaluate peak intensities with a click.
- **Data Export**: Save the processed plot for external use.

## Libraries and Tools

This project leans heavily on Python and uses the following libraries:
- **numpy**: For mathematical operations.
- **matplotlib**: For plotting and data visualization.
- **TkInter-based GUI library**: A custom-built library that provides a simplified interface for GUI operations. Refer to `guilib.py` for details.

## Data Details

The provided simulated data comprises multiple measurements, each stored in separate files named in the `measurement_i.txt` format. These files consist of:
- **Binding Energy**: The energy required to bind electrons (measured in electronvolts).
- **Intensity**: Corresponds to the number of electrons measured at a specific binding energy.

The primary objective is to aggregate intensity values across files to reduce noise. The spectral data, due to the measurement equipment, may contain a linear background that needs to be subtracted for accurate analysis.

## How to Use

1. **GUI Interaction**: The user interface, designed with simplicity in mind, allows straightforward operations.
2. **Loading Data**: Use the "Load Data" button and select the desired data file.
3. **Visualizing Data**: The "Plot Data" button presents the loaded data. Axes are well-labeled for clarity.
4. **Noise Reduction**: The "Remove Linear Background" option lets users select two data points. The program then fits a line across these points and subtracts it from the data.
5. **Analyzing Peaks**: Use the "Calculate Intensities" option. The program estimates the area under the peaks to gauge their intensity.
6. **Saving Data**: Processed plots can be saved for external use.

## User Interface Design Philosophy

The project adopts the typical design philosophy of user interface programming, where the main loop resides within the employed library. User actions trigger handler functions, ensuring a dynamic interaction. The interface is built with various components, from simple buttons to complex file dialogs. A unique aspect of this project is the use of a mutable dictionary to maintain program state across functions, ensuring smooth operations.
